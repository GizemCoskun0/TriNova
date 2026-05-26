import asyncio
import io
import json
import re
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import models
from api_process import AsyncRecipeAPI
from database import get_db
from schemas import (
    MealPlanCategoryRequest,
    MealPlanGenerateRequest,
    MealPlanItemRequest,
    SingleMealAddRequest,
)
from services.ingredient_service import compare_recipe_with_inventory
from services.recipe_filter_service import recipe_matches_user_preferences

# --- REPORTLAB (PDF) IMPORTLARI ---
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak

router = APIRouter(prefix="/api", tags=["Meal Plan"])


@router.post("/meal-plan/auto-generate")
async def auto_generate_full_plan(
    request: MealPlanGenerateRequest, db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()
    if not db_user:
        return {"status": "error", "message": "User not found."}

    # Kullanıcının diyet ve alerjilerini İngilizce formatta hazırlama
    CEVIRI = {
        "vejetaryen": "vegetarian",
        "vegan": "vegan",
        "glütensiz": "gluten free",
        "ketojenik": "ketogenic",
        "yumurta": "egg",
        "süt": "dairy",
        "fıstık": "peanut",
        "yer fıstığı": "peanut",
        "deniz ürünleri": "seafood",
        "soya": "soy",
        "buğday": "wheat",
    }
    user_allergies = [
        CEVIRI.get(a.name.lower(), a.name.lower()) for a in db_user.allergies
    ]
    user_diets = [CEVIRI.get(d.name.lower(), d.name.lower()) for d in db_user.diets]

    days = request.days  # Varsayılan 3 gün

    # Hangi kategorilerden tarif çekeceğimiz ve sistemdeki öğün isimleri
    categories_to_fetch = {
        "breakfast": "Breakfast",
        "main course": [
            "Lunch",
            "Dinner",
        ],  # Ana yemekten günde 2 tane lazım (Öğle ve Akşam)
        "soup": "Soup",
        "salad": "Salad",
        "dessert": "Dessert",
        "beverage": "Drink",
    }

    # Eski planı temizlemek istersen (isteğe bağlı)
    db.query(models.MealPlan).filter(
        models.MealPlan.user_email == request.email
    ).delete()
    db.commit()

    generated_count = 0

    # Her kategori için API'ye istek at
    # Her kategori için API'ye istek at
    for api_category, meal_types in categories_to_fetch.items():
        needed_recipes = days * 2 if type(meal_types) == list else days

        # 🌟 YENİ: Dinamik filtrelerimizi hazırlıyoruz (Karıştırma + Kahvaltı Filtresi)
        extra_filters = {"sort": "random"}
        if api_category == "breakfast":
            extra_filters["excludeIngredients"] = "smoothie, juice, shake, drink"

        # AsyncRecipeAPI içindeki fonksiyonunu kullanarak tarifleri çekiyoruz
        recipes = await AsyncRecipeAPI.get_categorized_recipes(
            diets=user_diets,
            allergies=user_allergies,
            category=api_category,
            number=needed_recipes,
            **extra_filters,  # Sihirli filtreleri buraya yolluyoruz
        )
        await asyncio.sleep(1.5)

        if not recipes:
            continue

        # 💡 GARANTİ FİLTRE (Fail-safe): Genel plan için de başlık temizliği yapıyoruz
        if api_category == "breakfast":
            recipes = [
                r
                for r in recipes
                if "smoothie" not in r.get("title", "").lower()
                and "shake" not in r.get("title", "").lower()
                and "juice" not in r.get("title", "").lower()
            ]

        recipe_index = 0
        for day in range(1, days + 1):
            day_str = f"Day {day}"

            # Eğer main course ise hem Lunch hem Dinner için dön
            types_for_day = meal_types if type(meal_types) == list else [meal_types]

            for meal_type in types_for_day:
                if recipe_index < len(recipes):
                    rec = recipes[recipe_index]

                    # Talimatları düzenle
                    raw_instr = rec.get("instructions", "")
                    if not raw_instr and rec.get("analyzedInstructions"):
                        steps = rec["analyzedInstructions"][0].get("steps", [])
                        raw_instr = "\n".join(
                            [f"{s['number']}. {s['step']}" for s in steps]
                        )

                    # Veritabanına kaydet
                    new_plan = models.MealPlan(
                        user_id=db_user.id,
                        user_email=db_user.email,
                        plan_day=day_str,
                        meal_type=meal_type,
                        recipe_id=rec["id"],
                        recipe_title=rec["title"],
                        recipe_image=rec.get("image", ""),
                        ingredients=json.dumps(
                            {
                                "ingredients": rec.get("usedIngredients", [])
                                + rec.get("missedIngredients", [])
                            }
                        ),
                        instructions=raw_instr or "No instructions available.",
                        ready_in_minutes=rec.get("readyInMinutes", 45),
                        servings=rec.get("servings", 4),
                    )
                    db.add(new_plan)
                    generated_count += 1
                    recipe_index += 1

    db.commit()

    # EĞER HİÇ YEMEK BULUNAMADIYSA UI'A HATA GÖNDER
    if generated_count == 0:
        return {
            "status": "error",
            "message": "Tarifler çekilemedi. API hız sınırına takılmış olabilirsiniz.",
        }

    return {
        "status": "success",
        "message": f"Successfully generated {generated_count} meal items for {days} days.",
    }


# ------------------- Tek öğün ekleme endpoint'i ------------------
@router.post("/meal-plan/add-single")
def add_single_meal_to_plan(
    request: SingleMealAddRequest, db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if not db_user:
        return {"status": "error", "message": "User not found."}

    # AYNI GÜN VE ÖĞÜNDE BAŞKA YEMEK VARSA SİL (Üst üste binmesin)
    existing_meal = (
        db.query(models.MealPlan)
        .filter(
            models.MealPlan.user_email == request.email,
            models.MealPlan.plan_day == request.day,
            models.MealPlan.meal_type == request.meal_type,
        )
        .first()
    )

    if existing_meal:
        db.delete(existing_meal)
        db.commit()

    # --- YENİ EKLENEN KISIM BAŞLIYOR ---
    # Frontend'den o dakika ve porsiyonları alabilmemiz lazım ama
    # şu an SingleMealAddRequest içinde o alanlar olmayabilir.
    # Güvenli yoldan alıyoruz: Eğer request'in içinde gönderildiyse al, gönderilmediyse varsayılan yaz.
    req_dict = request.dict(exclude_unset=True)
    ready_time = req_dict.get("ready_in_minutes", 45)  # Yoksa 45 yaz
    serv = req_dict.get("servings", 4)  # Yoksa 4 yaz
    inst = req_dict.get("instructions") or "No instructions available."
    new_plan = models.MealPlan(
        user_id=db_user.id,
        user_email=db_user.email,
        plan_day=request.day,
        meal_type=request.meal_type,
        recipe_id=request.recipe_id,
        recipe_title=request.recipe_title,
        recipe_image=request.recipe_image,
        ingredients=request.ingredients_json,
        instructions=inst,
        # İŞTE AMELİYAT YAPTIĞIMIZ YER: Bu iki sütunu dolduruyoruz
        ready_in_minutes=ready_time,
        servings=serv,
    )
    # --- YENİ EKLENEN KISIM BİTTİ ---

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    # Envanter ile Karşılaştır ve Eksikleri Frontend'e Gönder (Otomatik listeye atma)
    available_items, missing_items = compare_recipe_with_inventory(
        new_plan, db_user, db
    )

    return {
        "status": "success",
        "message": f"✅ {request.day} {request.meal_type} added to the plan",
        "meal_plan_id": new_plan.id,
        "missing_items": missing_items,
        "available_items": available_items,
    }


@router.post("/meal-plan/check-ingredients")
def check_meal_plan_ingredients(
    request: MealPlanItemRequest, db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if not db_user:
        return {"status": "error", "message": "User not found."}

    meal_plan_item = (
        db.query(models.MealPlan)
        .filter(
            models.MealPlan.id == request.meal_plan_id,
            models.MealPlan.user_email == request.email,
        )
        .first()
    )

    if not meal_plan_item:
        return {"status": "error", "message": "Meal plan item not found."}

    available_items, missing_items = compare_recipe_with_inventory(
        meal_plan_item, db_user, db
    )

    return {
        "status": "success",
        "recipe_title": meal_plan_item.recipe_title,
        "available_items": available_items,
        "missing_items": missing_items,
    }


@router.get("/meal-plan/{email}")
def get_meal_plan(email: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == email).first()

    if not db_user:
        return {"status": "error", "message": "User not found."}

    meal_plan_items = (
        db.query(models.MealPlan)
        .filter(models.MealPlan.user_email == email)
        .order_by(models.MealPlan.id)
        .all()
    )

    return {
        "status": "success",
        "meal_plan": [
            {
                "id": item.id,
                "plan_day": item.plan_day,
                "meal_type": item.meal_type,
                "recipe_id": item.recipe_id,
                "recipe_title": item.recipe_title,
                "recipe_image": item.recipe_image,
                "source_url": item.source_url,
                "ready_in_minutes": item.ready_in_minutes,
                "servings": item.servings,
                "ingredients": item.ingredients,
                "instructions": item.instructions,
            }
            for item in meal_plan_items
        ],
    }


@router.post("/meal-plan/generate-category")
async def generate_category_plan(
    request: MealPlanCategoryRequest, db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()
    if not db_user:
        return {"status": "error", "message": "User not found."}

    CEVIRI = {
        "vejetaryen": "vegetarian",
        "vegan": "vegan",
        "glütensiz": "gluten free",
        "ketojenik": "ketogenic",
        "yumurta": "egg",
        "süt": "dairy",
        "fıstık": "peanut",
        "yer fıstığı": "peanut",
        "deniz ürünleri": "seafood",
        "soya": "soy",
        "buğday": "wheat",
    }

    user_allergies = [
        CEVIRI.get(a.name.lower(), a.name.lower()) for a in db_user.allergies
    ]
    user_diets = [CEVIRI.get(d.name.lower(), d.name.lower()) for d in db_user.diets]

    category = request.category.lower()

    # Ekstra parametreleri toplamak için bir dinamik sözlük oluşturuyoruz
    extra_filters = {}

    # Eğer kategori kahvaltıysa, smoothie ve içecek türevlerini hariç tutması için Spoonacular'a bildir
    if category == "breakfast":
        extra_filters["excludeIngredients"] = "smoothie, juice, shake, drink"

    recipes = await AsyncRecipeAPI.get_categorized_recipes(
        diets=user_diets,
        allergies=user_allergies,
        category=category,
        number=5,
        **extra_filters,  # 🌟 Hazırladığımız ekstra filtreleri buraya serpiştiriyoruz
    )

    # 💡 GARANTİ FİLTRE (Fail-safe): Spoonacular bazen 'excludeIngredients' kısmına
    # rağmen başlığında smoothie geçen yemekleri kahvaltı diye getirebilir.
    # İşi şansa bırakmamak için Python tarafında da küçük bir temizlik yapalım:
    if category == "breakfast" and recipes:
        recipes = [
            r
            for r in recipes
            if "smoothie" not in r.get("title", "").lower()
            and "shake" not in r.get("title", "").lower()
        ]

    if not recipes:
        return {
            "status": "error",
            "message": f"No suitable recipes found for {category}.",
        }

    return {"status": "success", "data": recipes}


@router.get("/meal-plan/{email}/pdf")
def export_meal_plan_pdf(email: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if not db_user:
        return {"status": "error", "message": "User not found."}

    # Veritabanından verileri çekiyoruz
    raw_items = (
        db.query(models.MealPlan).filter(models.MealPlan.user_email == email).all()
    )

    # --- GÜNLERİ VE ÖĞÜNLERİ MANTIKSAL SIRAYA SOKMA ---
    meal_order = ["Breakfast", "Lunch", "Dinner", "Soup", "Salad", "Dessert", "Drink"]

    def sort_logic(item):
        # "Day 1", "Day 2" içindeki numarayı al
        day_num = (
            int(item.plan_day.split()[-1])
            if item.plan_day and item.plan_day.split()[-1].isdigit()
            else 0
        )
        # Öğünün listedeki sırasını bul
        meal_idx = (
            meal_order.index(item.meal_type) if item.meal_type in meal_order else 99
        )
        return (day_num, meal_idx)

    # Verileri hem Güne hem de Öğün Sırasına (Kahvaltı -> Öğle -> Akşam) göre sırala
    meal_plan_items = sorted(raw_items, key=sort_logic)

    # PDF'i bellekte (RAM) oluşturmak için BytesIO kullanılıyor
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title=f"Meal Plan - {db_user.username}",
        author="Smart Kitchen Assistant",
    )
    story = []

    pdf_styles = getSampleStyleSheet()

    # PDF Başlığı
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=pdf_styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#ff4b4b"),
        spaceAfter=15,
        alignment=1,  # Center
    )
    story.append(Paragraph("SmartKitchen - 3-Day Meal Plan", title_style))
    story.append(
        Paragraph(f"Prepared for: {db_user.username} ({email})", pdf_styles["Normal"])
    )
    story.append(Spacer(1, 20))

    # Öğünleri Gün Gün PDF'e Ekleme
    current_day = ""
    for item in meal_plan_items:
        if item.plan_day != current_day:
            if current_day != "":
                story.append(PageBreak())  # Yeni güne geçerken sayfa atla
            current_day = item.plan_day

            # Gün Başlığı (H2 Seviyesi)
            day_style = ParagraphStyle(
                "DayStyle",
                parent=pdf_styles["Heading2"],
                fontSize=18,
                textColor=colors.HexColor("#1f2937"),
                spaceBefore=18,
                spaceAfter=8,
            )
            story.append(Paragraph(f"<b>{current_day}</b>", day_style))

        meal_style = ParagraphStyle(
            "MealStyle",
            parent=pdf_styles["Heading3"],
            fontSize=14,
            textColor=colors.HexColor("#ff4b4b"),
            spaceBefore=10,
            spaceAfter=4,
        )
        story.append(
            Paragraph(
                f"• {item.meal_type}: {item.recipe_title}",
                meal_style,
            )
        )

        # Süre ve Porsiyon Bilgisi
        meta_text = f"<i>Time: {item.ready_in_minutes} min | Portion: {item.servings} People</i>"
        story.append(Paragraph(meta_text, pdf_styles["Normal"]))
        story.append(Spacer(1, 4))

        # --- MALZEMELERİN YAZDIRILMASI ---
        story.append(Paragraph("<b>Ingredients:</b>", pdf_styles["Normal"]))
        try:
            ing_data = json.loads(item.ingredients)
            ingredients = ing_data.get("ingredients", []) or ing_data.get(
                "usedIngredients", []
            ) + ing_data.get("missedIngredients", [])

            for ing in ingredients:
                ing_text = f"- {ing.get('amount', '')} {ing.get('unit', '')} {ing.get('name', '')}"
                story.append(Paragraph(ing_text, pdf_styles["Normal"]))
        except:
            story.append(
                Paragraph(
                    "- Material information could not be parsed.",
                    pdf_styles["Normal"],
                )
            )

        story.append(Spacer(1, 4))

        # --- TALİMATLARIN YAZDIRILMASI ---
        clean_instructions = (
            re.sub("<.*?>", "", item.instructions)
            if item.instructions
            else "No instructions available."
        )
        story.append(
            Paragraph(f"<b>Preparation:</b> {clean_instructions}", pdf_styles["Normal"])
        )

        # Öğünler arasına boşluk
        story.append(Spacer(1, 15))

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=meal_plan_{db_user.username}.pdf"
        },
    )
