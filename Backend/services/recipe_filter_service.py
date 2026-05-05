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
