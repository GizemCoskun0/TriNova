import json
import models

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

    ingredients_text = meal_plan_item.ingredients

    if not ingredients_text:
        return [], []

    try:
        ingredients_data = json.loads(ingredients_text)
    except:
        return [], []

    recipe_ingredients = ingredients_data.get("ingredients", [])

    if not recipe_ingredients:
        recipe_ingredients = ingredients_data.get("missedIngredients", []) + ingredients_data.get("usedIngredients", [])

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