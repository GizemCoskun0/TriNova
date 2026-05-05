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