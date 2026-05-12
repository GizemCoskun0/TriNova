from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

import models
from database import get_db
from api_process import AsyncRecipeAPI
from schemas import MealPlanGenerateRequest, MealPlanItemRequest, SingleMealAddRequest
from services.recipe_filter_service import recipe_matches_user_preferences
from services.ingredient_service import compare_recipe_with_inventory

router = APIRouter(
    prefix="/api",
    tags=["Meal Plan"]
)

@router.post("/meal-plan/generate")
async def generate_meal_plan(request: MealPlanGenerateRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()
    if not db_user:
        return {"status": "error", "message": "User not found."}

    # Çeviri sözlüğü (Diyet ve Alerjiler için)
    CEVIRI = {
        "vejetaryen": "vegetarian", "vegan": "vegan", "glütensiz": "gluten free",
        "ketojenik": "ketogenic", "yumurta": "egg", "süt": "dairy",
        "fıstık": "peanut", "yer fıstığı": "peanut", "deniz ürünleri": "seafood",
        "soya": "soy", "buğday": "wheat"
    }
    
    user_allergies = [CEVIRI.get(a.name.lower(), a.name.lower()) for a in db_user.allergies]
    user_diets = [CEVIRI.get(d.name.lower(), d.name.lower()) for d in db_user.diets]

    # Tercihlere göre rastgele 10 aday tarif çekiyoruz
    recipes = await AsyncRecipeAPI.get_random_meal_plan(
        diets=user_diets,
        allergies=user_allergies,
        number=10
    )

    if not recipes:
        return {"status": "error", "message": "No suitable recipes found."}

    # 🚨 DİKKAT: Veritabanına kayıt yapmıyoruz, sadece listeyi döndürüyoruz.
    return {
        "status": "success",
        "data": recipes 
    }

#------------------- Tek öğün ekleme endpoint'i ------------------
@router.post("/meal-plan/add-single")
def add_single_meal_to_plan(request: SingleMealAddRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not db_user:
        return {"status": "error", "message": "User not found."}

    # AYNI GÜN VE ÖĞÜNDE BAŞKA YEMEK VARSA SİL (Üst üste binmesin)
    existing_meal = db.query(models.MealPlan).filter(
        models.MealPlan.user_email == request.email,
        models.MealPlan.plan_day == request.day,
        models.MealPlan.meal_type == request.meal_type
    ).first()

    if existing_meal:
        db.delete(existing_meal)
        db.commit()

    # --- YENİ EKLENEN KISIM BAŞLIYOR ---
    # Frontend'den o dakika ve porsiyonları alabilmemiz lazım ama 
    # şu an SingleMealAddRequest içinde o alanlar olmayabilir.
    # Güvenli yoldan alıyoruz: Eğer request'in içinde gönderildiyse al, gönderilmediyse varsayılan yaz.
    req_dict = request.dict(exclude_unset=True)
    ready_time = req_dict.get("ready_in_minutes", 45) # Yoksa 45 yaz
    serv = req_dict.get("servings", 4)                # Yoksa 4 yaz

    new_plan = models.MealPlan(
        user_id=db_user.id,
        user_email=db_user.email,
        plan_day=request.day,
        meal_type=request.meal_type,
        recipe_id=request.recipe_id,
        recipe_title=request.recipe_title,
        recipe_image=request.recipe_image,
        ingredients=request.ingredients_json,
        instructions="Instructions unavailable",
        # İŞTE AMELİYAT YAPTIĞIMIZ YER: Bu iki sütunu dolduruyoruz
        ready_in_minutes=ready_time,
        servings=serv
    )
    # --- YENİ EKLENEN KISIM BİTTİ ---

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    # Envanter ile Karşılaştır ve Eksikleri Frontend'e Gönder (Otomatik listeye atma)
    available_items, missing_items = compare_recipe_with_inventory(new_plan, db_user, db)

    return {
        "status": "success", 
        "message": f"✅ {request.day} {request.meal_type} added to the plan",
        "meal_plan_id": new_plan.id,
        "missing_items": missing_items,
        "available_items": available_items
    }

@router.post("/meal-plan/check-ingredients")
def check_meal_plan_ingredients(request: MealPlanItemRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if not db_user:
        return {"status": "error", "message": "User not found."}

    meal_plan_item = db.query(models.MealPlan).filter(
        models.MealPlan.id == request.meal_plan_id,
        models.MealPlan.user_email == request.email
    ).first()

    if not meal_plan_item:
        return {"status": "error", "message": "Meal plan item not found."}

    available_items, missing_items = compare_recipe_with_inventory(meal_plan_item, db_user, db)

    return {
        "status": "success",
        "recipe_title": meal_plan_item.recipe_title,
        "available_items": available_items,
        "missing_items": missing_items
    }

@router.get("/meal-plan/{email}")
def get_meal_plan(email: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == email).first()

    if not db_user:
        return {"status": "error", "message": "User not found."}

    meal_plan_items = db.query(models.MealPlan).filter(
        models.MealPlan.user_email == email
    ).order_by(models.MealPlan.id).all()

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
                "ingredients": item.ingredients
            }
            for item in meal_plan_items
        ]
    }