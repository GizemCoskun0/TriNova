from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import MealPlanItemRequest,ItemToggleRequest
from services.ingredient_service import compare_recipe_with_inventory

router = APIRouter(
    prefix="/api",
    tags=["Shopping List"]
)



@router.get("/shopping-list/{email}")
def get_shopping_list(email: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == email).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found."
        }

    shopping_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_email == email
    ).all()

    return {
        "status": "success",
        "data": [
            {
                "id": item.id,
                "item_name": item.item_name,
                "amount": item.amount,
                "unit": item.unit,
                "source_recipe_title": item.source_recipe_title,
                "is_checked": item.is_checked
            }
            for item in shopping_items
        ]
    }

@router.post("/shopping-list/add-missing")
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

@router.put("/shopping-list/toggle/{item_id}")
def toggle_shopping_item(item_id: int, request: ItemToggleRequest, db: Session = Depends(get_db)):
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if item:
        item.is_checked = request.is_checked
        db.commit()
        return {"status": "success"}
    return {"status": "error", "message": "Item not found"}

@router.post("/shopping-list/recalculate/{email}")


def recalculate_shopping_list(email: str, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not db_user:
        return {
            "status": "error",
            "message": "User not found."
        }

    shopping_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_email == email
    ).all()

    inventory_items = db.query(models.Inventory).filter(
        models.Inventory.user_id == db_user.id
    ).all()

    for shop_item in shopping_items:
        total_inv_amount = 0
        
        # Sum all matching inventory items for this shopping item
        for inv_item in inventory_items:
            inventory_name = inv_item.name.lower().strip()
            shopping_name = shop_item.item_name.lower().strip()

            if inventory_name in shopping_name or shopping_name in inventory_name:
                total_inv_amount += inv_item.amount
        
        if total_inv_amount > 0:
            shop_item.amount = shop_item.amount - total_inv_amount
            if shop_item.amount <= 0:
                db.delete(shop_item)

    db.commit()

    updated_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_email == email
    ).all()

    return {
        "status": "success",
        "message": "Shopping list recalculated successfully.",
        "data": [
            {
                "id": item.id,
                "item_name": item.item_name,
                "amount": item.amount,
                "unit": item.unit,
                "source_recipe_title": item.source_recipe_title,
                "is_checked": item.is_checked
            }
            for item in updated_items
        ]
    }

@router.delete("/shopping-list/clear/{email}")
def clear_checked_items(email: str, db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"status": "error", "message": "User not found"}

    checked_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_email == email,
        models.ShoppingListItem.is_checked == True
    ).all()

    for item in checked_items:
        existing_inv_item = db.query(models.Inventory).filter(
            models.Inventory.user_id == user.id,
            models.Inventory.name == item.item_name
        ).first()

        if existing_inv_item:
            existing_inv_item.amount += item.amount
        else:
            new_inv_item = models.Inventory(
                user_id=user.id,
                name=item.item_name,
                amount=item.amount,
                unit=item.unit
            )
            db.add(new_inv_item)

        db.delete(item)

    db.commit()
    return {"status": "success", "message": "Items successfully moved to inventory and removed from shopping list."}