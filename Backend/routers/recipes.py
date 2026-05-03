from fastapi import APIRouter
from api_process import AsyncRecipeAPI

router = APIRouter(
    prefix="/api",
    tags=["Recipes"]
)


@router.get("/recipes")
async def get_recipes(ingredients: str):

    ingredients_list = [i.strip() for i in ingredients.split(",")]

    recipes = await AsyncRecipeAPI.search_by_ingredients(ingredients_list)

    if recipes:
        return {
            "status": "success",
            "data": recipes
        }

    return {
        "status": "error",
        "message": "Recipe not found or API error."
    }
