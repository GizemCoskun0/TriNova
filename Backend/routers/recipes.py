import random
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db
from api_process import AsyncRecipeAPI

router = APIRouter(
    prefix="/api",
    tags=["Recipes"]
)

@router.get("/recipes")
async def get_recipes(ingredients: str, username: str, number: int = 5, db: Session = Depends(get_db)):

    all_ingredients = [i.strip() for i in ingredients.split(",")]

    # 1. API çökmesin diye rastgele 2 malzeme seçip yolluyoruz
    if len(all_ingredients) > 2:
        core_ingredients = random.sample(all_ingredients, 2)
    else:
        core_ingredients = all_ingredients

    user = db.query(models.User).filter(models.User.username == username).first()
    
    CEVIRI = {
        "vejetaryen": "vegetarian", "vegan": "vegan", "glütensiz": "gluten free",
        "ketojenik": "ketogenic", "yumurta": "egg", "süt": "dairy",
        "fıstık": "peanut", "yer fıstığı": "peanut", "deniz ürünleri": "seafood",
        "soya": "soy", "buğday": "wheat"
    }
    
    user_diets = []
    user_allergies = []
    
    if user:
        user_diets = [CEVIRI.get(diet.name.lower(), diet.name.lower()) for diet in user.diets]
        user_allergies = [CEVIRI.get(allergy.name.lower(), allergy.name.lower()) for allergy in user.allergies]

    # 2. API'ye sor (İyileri seçebilmek için 15 tane çekiyoruz)
    recipes = await AsyncRecipeAPI.search_by_ingredients(
        ingredients_list=core_ingredients,
        diets=user_diets,          
        allergies=user_allergies,
        number=15 
    )

    # 3. Yedek Plan (Bulamazsa tek malzemeyle dene)
    if (recipes is None or len(recipes) == 0) and len(core_ingredients) > 1:
        recipes = await AsyncRecipeAPI.search_by_ingredients(
            ingredients_list=[core_ingredients[0]],
            diets=user_diets,
            allergies=user_allergies,
            number=15
        )

    if recipes:
        # 🚀 API'nin yalanlarını düzeltiyoruz: Bizde olan malzemeyi eksik saymasını engelle
        all_ing_lower = [i.lower() for i in all_ingredients]
        
        for recipe in recipes:
            real_missing = []
            real_used = recipe.get("usedIngredients", [])
            
            for missing_ing in recipe.get("missedIngredients", []):
                ing_name = missing_ing["name"].lower()
                
                is_actually_owned = any(ing_name in owned or owned in ing_name for owned in all_ing_lower)
                
                if is_actually_owned:
                    real_used.append(missing_ing)
                else:
                    real_missing.append(missing_ing)
            
            recipe["missedIngredients"] = real_missing
            recipe["usedIngredients"] = real_used
            recipe["missedIngredientCount"] = len(real_missing)
            recipe["usedIngredientCount"] = len(real_used)

        # 🚀 KATI KURAL: Sadece ve sadece eksik malzemesi SIFIR olanları filtrele
        strictly_zero_missing = [r for r in recipes if r["missedIngredientCount"] == 0]
        
        if strictly_zero_missing:
            # Eğer SIFIR eksikli mükemmel tarifler bulduysa SADECE onları gönder
            return {"status": "success", "data": strictly_zero_missing[:number]}
        else:
            # SIFIR eksikli hiçbir şey yoksa mecburen en az eksikli olanları sırala
            sorted_recipes = sorted(recipes, key=lambda x: x["missedIngredientCount"])
            return {"status": "success", "data": sorted_recipes[:number]}

    return {"status": "error", "message": "Tarif bulunamadı."}