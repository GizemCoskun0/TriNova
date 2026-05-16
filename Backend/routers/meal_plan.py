from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json
import asyncio
import models
from database import get_db
from api_process import AsyncRecipeAPI
from schemas import MealPlanGenerateRequest, MealPlanItemRequest, SingleMealAddRequest
from services.recipe_filter_service import recipe_matches_user_preferences
from services.ingredient_service import compare_recipe_with_inventory
from schemas import MealPlanCategoryRequest  # Yukarıya importlara eklemeyi unutma

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
    for api_category, meal_types in categories_to_fetch.items():
        # Öğle ve Akşam yemeği için günde 2, diğerleri için günde 1 tarif lazım
        needed_recipes = days * 2 if type(meal_types) == list else days

        # AsyncRecipeAPI içindeki fonksiyonunu kullanarak tarifleri çekiyoruz
        recipes = await AsyncRecipeAPI.get_categorized_recipes(
            diets=user_diets,
            allergies=user_allergies,
            category=api_category,
            number=needed_recipes,
        )
        await asyncio.sleep(1.5)
        if not recipes:
            continue  # Tarif bulunamazsa diğer kategoriye geç

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

    recipes = await AsyncRecipeAPI.get_categorized_recipes(
        diets=user_diets,
        allergies=user_allergies,
        category=request.category,
        number=5,  # Her sekme için 5 tarif yeterli
    )

    if not recipes:
        return {
            "status": "error",
            "message": "No suitable recipes found for this category.",
        }

    return {"status": "success", "data": recipes}
