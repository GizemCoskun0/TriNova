from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json

import models
from database import get_db
from api_process import AsyncRecipeAPI
from schemas import MealPlanGenerateRequest, MealPlanItemRequest
from services.recipe_filter_service import recipe_matches_user_preferences
from services.ingredient_service import compare_recipe_with_inventory

router = APIRouter(
    prefix="/api",
    tags=["Meal Plan"]
)


# Meal plan generation endpoint - This is the core of the meal planning feature and will be called when the user clicks the "Generate Meal Plan" button in Streamlit.
@router.post("/meal-plan/generate")
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

    meal_types = ["Breakfast", "Lunch", "Dinner"]
    total_needed = request.days * len(meal_types)

    if len(suitable_recipes) < total_needed:
        return {
            "status": "error",
            "message": f"Not enough suitable recipes found. Needed {total_needed}, but found {len(suitable_recipes)}."
        }

    # Eski planı siliyoruz, yeni 3 günlük planı kaydedeceğiz
    db.query(models.MealPlan).filter(
        models.MealPlan.user_email == request.email
    ).delete()

    saved_plan = []
    recipe_index = 0

    for day_index in range(request.days):
        plan_day = f"Day {day_index + 1}"

        for meal_type in meal_types:
            recipe = suitable_recipes[recipe_index]
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
                ingredients=json.dumps(ingredients_data),
                instructions=recipe.get("instructions", "Instructions will be available soon.")
            )

            db.add(new_plan_item)
            saved_plan.append(new_plan_item)

    db.commit()

    return {
        "status": "success",
        "message": "3-day meal plan generated successfully.",
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
                "instructions": item.instructions
            }
            for item in saved_plan
        ]
    }

# Meal plan item ingredient check endpoint - This will be called when the user clicks the "Check Ingredients" button for a specific meal in Streamlit.
@router.post("/meal-plan/check-ingredients")
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
@router.get("/meal-plan/{email}")
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
