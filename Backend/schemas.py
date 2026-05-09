from pydantic import BaseModel
from typing import List


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
class ItemToggleRequest(BaseModel):
    is_checked: bool    

class FavoriteAddRequest(BaseModel):
    email: str
    recipe_id: int
    recipe_title: str
    recipe_image: str | None = None
    source_url: str | None = None 
    ingredients_json: str | None = '{"ingredients": []}'   

class SingleMealAddRequest(BaseModel):
    email: str
    recipe_id: int
    recipe_title: str
    recipe_image: str = None
    day: str
    meal_type: str
    ingredients_json: str    