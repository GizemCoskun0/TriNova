from fastapi import FastAPI
import models
from database import engine
from api_process import AsyncRecipeAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import json

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="SmartKitchen API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the SmartKitchen Backend API.! 🚀"}

@app.get("/api/recipes")
async def get_recipes(ingredients: str):

    ingredients_list = [i.strip() for i in ingredients.split(",")]
    
    recipes = await AsyncRecipeAPI.search_by_ingredients(ingredients_list)
    
    if recipes:
        return {"status": "success", "data": recipes}
    
    return {"status": "error", "message": "Recipe not found or API error."}


class ProfileCreate(BaseModel):
    username: str
    email: str
    diet: str
    allergies: List[str]
class MealPlanGenerateRequest(BaseModel):
    username: str
    email: str
    days: int = 3
class MealPlanItemRequest(BaseModel):
    meal_plan_id: int
    email: str
class InventoryItem(BaseModel):
    username: str
    item_name: str
    amount: float = 1.0
    unit: str = "unit"

def normalize_item_name(name: str):
    return name.strip().lower()


def compare_recipe_with_inventory(meal_plan_item, db_user, db):
    ingredients_text = meal_plan_item.ingredients

    if not ingredients_text:
        return [], []

    ingredients_data = json.loads(ingredients_text)

    recipe_ingredients = ingredients_data.get("ingredients", [])

    inventory_items = db.query(models.Inventory).filter(
        models.Inventory.user_id == db_user.id
    ).all()

    inventory_map = {}

    for item in inventory_items:
        inventory_map[normalize_item_name(item.name)] = item

    available_items = []
    missing_items = []

    for ingredient in recipe_ingredients:
        name = ingredient.get("name", "Unknown ingredient")
        amount = float(ingredient.get("amount", 1) or 1)
        unit = ingredient.get("unit", "unit") or "unit"

        key = normalize_item_name(name)

        if key in inventory_map:
            home_item = inventory_map[key]

            if home_item.amount >= amount:
                available_items.append({
                    "name": name,
                    "required_amount": amount,
                    "home_amount": home_item.amount,
                    "unit": unit
                })
            else:
                missing_items.append({
                    "name": name,
                    "amount": amount - home_item.amount,
                    "unit": unit
                })
        else:
            missing_items.append({
                "name": name,
                "amount": amount,
                "unit": unit
            })

    return available_items, missing_items
def recipe_matches_user_preferences(recipe, user_allergies, user_diets):
    recipe_text = ""

    recipe_text += recipe.get("title", "").lower()

    for ingredient in recipe.get("missedIngredients", []):
        recipe_text += " " + ingredient.get("name", "").lower()

    for ingredient in recipe.get("usedIngredients", []):
        recipe_text += " " + ingredient.get("name", "").lower()

    allergy_keywords = {
        "Peanuts": ["peanut", "peanuts"],
        "Dairy": ["milk", "cheese", "butter", "cream", "yogurt"],
        "Egg": ["egg", "eggs"],
        "Soy": ["soy", "tofu"],
        "Seafood": ["fish", "salmon", "shrimp", "tuna", "seafood"]
    }

    for allergy in user_allergies:
        keywords = allergy_keywords.get(allergy, [allergy.lower()])

        for keyword in keywords:
            if keyword in recipe_text:
                return False

    diet_keywords_to_avoid = {
        "Vegan": [
            "chicken", "beef", "pork", "fish", "salmon", "shrimp",
            "egg", "milk", "cheese", "butter", "cream", "yogurt"
        ],
        "Vegetarian": [
            "chicken", "beef", "pork", "fish", "salmon", "shrimp", "tuna"
        ],
        "Gluten-Free": [
            "bread", "pasta", "flour", "wheat"
        ]
    }

    for diet in user_diets:
        avoid_list = diet_keywords_to_avoid.get(diet, [])

        for keyword in avoid_list:
            if keyword in recipe_text:
                return False

    return True
@app.post("/api/profile")
def save_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    
    db_user = db.query(models.User).filter(models.User.email == profile.email).first()
    
    if not db_user:
        db_user = models.User(username=profile.username, email=profile.email)
        db.add(db_user)
        message = f"New user '{db_user.username}' created successfully!"
    else:
        message = f"User '{db_user.username}' profile updated successfully!"

    db_user.allergies = []
    db_user.diets = []

    for allergy_name in profile.allergies:
        db_allergy = db.query(models.Allergy).filter(models.Allergy.name == allergy_name).first()
        
        if not db_allergy:
            db_allergy = models.Allergy(name=allergy_name)
            db.add(db_allergy)
            
        db_user.allergies.append(db_allergy)

    if profile.diet and profile.diet != "None":
        db_diet = db.query(models.Diet).filter(models.Diet.name == profile.diet).first()
        
        if not db_diet:
            db_diet = models.Diet(name=profile.diet)
            db.add(db_diet)
            
        db_user.diets.append(db_diet)

    db.commit()

    return {
        "status": "success", 
        "message": message,
        "data": {
            "saved_diet": profile.diet, 
            "saved_allergies": profile.allergies
        }
    }


@app.get("/api/inventory/{username}")
def get_inventory(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return {"status": "error", "message": "User not found. Please create a profile first."}
    
    items = db.query(models.Inventory).filter(models.Inventory.user_id == user.id).all()
    
    return {
        "status": "success", 
        "data": [{"id": i.id, "name": i.name, "amount": i.amount, "unit": i.unit} for i in items]
    }

@app.post("/api/inventory")
def add_inventory(item: InventoryItem, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == item.username).first()
    if not user:
        return {"status": "error", "message": "User not found."}
        
    existing_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == user.id, 
        models.Inventory.name == item.item_name
    ).first()
    
    if existing_item:
        return {"status": "error", "message": f"'{item.item_name}' already exists in the inventory!"}

    new_item = models.Inventory(user_id=user.id, name=item.item_name, amount=item.amount, unit=item.unit)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {"status": "success", "message": f"'{item.item_name}' added to the inventory!"}

@app.delete("/api/inventory/{item_id}")
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not item:
        return {"status": "error", "message": "Item not found."}
        
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "Item deleted successfully!"}

# Bu fonksiyon, Streamlit her açıldığında veritabanındaki kayıtları okur
@app.get("/api/profile/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    
    if not db_user:
        return {"status": "error", "message": "User not found"}
        
    email = db_user.email
    diet = db_user.diets[0].name if db_user.diets else "None"
    allergies = [allergy.name for allergy in db_user.allergies]
    
    return {
        "status": "success",
        "email": email,
        "diet": diet,
        "allergies": allergies
    }

# Meal plan generation endpoint - This is the core of the meal planning feature and will be called when the user clicks the "Generate Meal Plan" button in Streamlit.
@app.post("/api/meal-plan/generate")
async def generate_meal_plan(request: MealPlanGenerateRequest, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found. Please login or create a profile first."
        }

    user_allergies = [allergy.name for allergy in db_user.allergies]
    user_diets = [diet.name for diet in db_user.diets]

    inventory_items = db.query(models.Inventory).filter(
        models.Inventory.user_id == db_user.id
    ).all()

    ingredients_list = [item.name for item in inventory_items]

    if not ingredients_list:
        ingredients_list = ["tomato", "cheese", "garlic", "egg", "rice", "chicken"]

    recipes = await AsyncRecipeAPI.search_by_ingredients(ingredients_list)

    if not recipes:
        return {
            "status": "error",
            "message": "No recipes found from the API."
        }

    suitable_recipes = []

    for recipe in recipes:
        if recipe_matches_user_preferences(recipe, user_allergies, user_diets):
            suitable_recipes.append(recipe)

    if not suitable_recipes:
        return {
            "status": "error",
            "message": "No suitable recipes found for your diet and allergies."
        }

    # Eski planı siliyoruz, yeni 3 günlük planı kaydedeceğiz
    db.query(models.MealPlan).filter(
        models.MealPlan.user_email == request.email
    ).delete()

    meal_types = ["Breakfast", "Lunch", "Dinner"]
    saved_plan = []

    recipe_index = 0

    for day_index in range(request.days):
        plan_day = f"Day {day_index + 1}"

        for meal_type in meal_types:
            recipe = suitable_recipes[recipe_index % len(suitable_recipes)]
            recipe_index += 1

            ingredients_data = {
                "ingredients": [
                    {
                        "name": ingredient.get("name"),
                        "amount": ingredient.get("amount", 1),
                        "unit": ingredient.get("unit", "unit")
                    }
                    for ingredient in recipe.get("missedIngredients", []) + recipe.get("usedIngredients", [])
                ]   
            }

            new_plan_item = models.MealPlan(
                user_id=db_user.id,
                user_email=db_user.email,
                plan_day=plan_day,
                meal_type=meal_type,
                recipe_id=recipe.get("id"),
                recipe_title=recipe.get("title", "Unknown Recipe"),
                recipe_image=recipe.get("image"),
                source_url=recipe.get("sourceUrl"),
                ready_in_minutes=recipe.get("readyInMinutes"),
                servings=recipe.get("servings"),
                ingredients=json.dumps(ingredients_data)
            )

            db.add(new_plan_item)
            saved_plan.append(new_plan_item)

    db.commit()

    return {
        "status": "success",
        "message": "3-day meal plan generated successfully.",
        "meal_plan": [
            {
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
            for item in saved_plan
        ]
    }

    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found. Please login or create a profile first."
        }

    user_allergies = [allergy.name for allergy in db_user.allergies]
    user_diets = [diet.name for diet in db_user.diets]

    inventory_items = db.query(models.Inventory).filter(
        models.Inventory.user_id == db_user.id
    ).all()

    ingredients_list = [item.name for item in inventory_items]

    if not ingredients_list:
        ingredients_list = ["tomato", "cheese", "garlic"]

    recipes = await AsyncRecipeAPI.search_by_ingredients(ingredients_list)

    if not recipes:
        return {
            "status": "error",
            "message": "No recipes found from the API."
        }

    suitable_recipes = []

    for recipe in recipes:
        if recipe_matches_user_preferences(recipe, user_allergies, user_diets):
            suitable_recipes.append(recipe)

    if len(suitable_recipes) < request.days:
        return {
            "status": "error",
            "message": "Not enough suitable recipes found for your diet and allergies."
        }

    db.query(models.MealPlan).filter(
        models.MealPlan.user_email == request.email
    ).delete()

    selected_recipes = suitable_recipes[:request.days]

    saved_plan = []

    for index, recipe in enumerate(selected_recipes):
        plan_day = f"Day {index + 1}"

        ingredients_data = {
            "missedIngredients": recipe.get("missedIngredients", []),
            "usedIngredients": recipe.get("usedIngredients", [])
        }

        new_plan_item = models.MealPlan(
            user_id=db_user.id,
            user_email=db_user.email,
            plan_day=plan_day,
            recipe_id=recipe.get("id"),
            recipe_title=recipe.get("title", "Unknown Recipe"),
            recipe_image=recipe.get("image"),
            source_url=recipe.get("sourceUrl"),
            ready_in_minutes=recipe.get("readyInMinutes"),
            servings=recipe.get("servings"),
            ingredients=json.dumps(ingredients_data)
        )

        db.add(new_plan_item)
        saved_plan.append(new_plan_item)

    db.commit()

    return {
        "status": "success",
        "message": "3-day meal plan generated successfully.",
        "meal_plan": [
            {
                "plan_day": item.plan_day,
                "recipe_id": item.recipe_id,
                "recipe_title": item.recipe_title,
                "recipe_image": item.recipe_image,
                "source_url": item.source_url,
                "ready_in_minutes": item.ready_in_minutes,
                "servings": item.servings
            }
            for item in saved_plan
        ]
    }
# Meal plan item ingredient check endpoint - This will be called when the user clicks the "Check Ingredients" button for a specific meal in Streamlit.
@app.post("/api/shopping-list/add-missing")
def add_missing_items_to_shopping_list(request: MealPlanItemRequest, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found."
        }

    meal_plan_item = db.query(models.MealPlan).filter(
        models.MealPlan.id == request.meal_plan_id,
        models.MealPlan.user_email == request.email
    ).first()

    if not meal_plan_item:
        return {
            "status": "error",
            "message": "Meal plan item not found."
        }

    available_items, missing_items = compare_recipe_with_inventory(
        meal_plan_item,
        db_user,
        db
    )

    for item in missing_items:
        existing_item = db.query(models.ShoppingListItem).filter(
            models.ShoppingListItem.user_email == request.email,
            models.ShoppingListItem.item_name == item["name"],
            models.ShoppingListItem.is_checked == False
        ).first()

        if existing_item:
            existing_item.amount += item["amount"]
        else:
            new_item = models.ShoppingListItem(
                user_id=db_user.id,
                user_email=db_user.email,
                item_name=item["name"],
                amount=item["amount"],
                unit=item["unit"],
                source_recipe_title=meal_plan_item.recipe_title,
                is_checked=False
            )

            db.add(new_item)

    db.commit()

    return {
        "status": "success",
        "message": "Missing ingredients added to the shopping list.",
        "added_items": missing_items
    }
# Meal plan item ingredient check endpoint - This will be called when the user clicks the "Check Ingredients" button for a specific meal in Streamlit.
@app.post("/api/meal-plan/check-ingredients")
def check_meal_plan_ingredients(request: MealPlanItemRequest, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == request.email).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found."
        }

    meal_plan_item = db.query(models.MealPlan).filter(
        models.MealPlan.id == request.meal_plan_id,
        models.MealPlan.user_email == request.email
    ).first()

    if not meal_plan_item:
        return {
            "status": "error",
            "message": "Meal plan item not found."
        }

    available_items, missing_items = compare_recipe_with_inventory(
        meal_plan_item,
        db_user,
        db
    )

    return {
        "status": "success",
        "recipe_title": meal_plan_item.recipe_title,
        "available_items": available_items,
        "missing_items": missing_items
    }

# Meal plan retrieval endpoint - This will be called when Streamlit loads to display the current meal plan for the user.
@app.get("/api/meal-plan/{email}")
def get_meal_plan(email: str, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == email).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found."
        }

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

    db_user = db.query(models.User).filter(models.User.email == email).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found."
        }

    meal_plan_items = db.query(models.MealPlan).filter(
        models.MealPlan.user_email == email
    ).order_by(models.MealPlan.id).all()

    return {
        "status": "success",
        "meal_plan": [
            {
                "id": item.id,
                "plan_day": item.plan_day,
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