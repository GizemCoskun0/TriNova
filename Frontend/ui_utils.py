import re
import json
import requests


def clean_html(text):
    if not text:
        return ""
    clean_text = re.sub("<.*?>", "", text)
    return clean_text.strip()


def parse_ingredients(ingredients_text):
    if not ingredients_text:
        return []
    try:
        data = json.loads(ingredients_text)
        if "ingredients" in data:
            return data.get("ingredients", [])
        used = data.get("usedIngredients", [])
        missed = data.get("missedIngredients", [])
        return used + missed
    except:
        return []


def get_meal_emoji(meal_type):
    if meal_type == "Breakfast":
        return "🍳"
    elif meal_type == "Lunch":
        return "🥗"
    elif meal_type == "Dinner":
        return "🍽️"
    return "🍴"


def get_user_favorite_ids(email):
    API_FAVORITES = "http://localhost:8000/api/favorites"
    try:
        res = requests.get(f"{API_FAVORITES}/{email}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                return [int(f["recipe_id"]) for f in data.get("data", [])]
    except:
        pass
    return []
