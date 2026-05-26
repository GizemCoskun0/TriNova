import difflib

CUSTOM_MAPPINGS = {
    "mlk": "milk",
    "grlc": "garlic",
    "ches": "cheese",
    "chckn": "chicken",
    "eg": "egg",
    "domates": "tomato",
    "soğan": "onion",
    "sogan": "onion",
    "patates": "potato",
}

VALID_ENGLISH_INGREDIENTS = [
    "tomato",
    "potato",
    "onion",
    "garlic",
    "carrot",
    "broccoli",
    "spinach",
    "mushroom",
    "cucumber",
    "pepper",
    "bell pepper",
    "lettuce",
    "cabbage",
    "lemon",
    "apple",
    "banana",
    "strawberry",
    "orange",
    "milk",
    "cheese",
    "butter",
    "yogurt",
    "cream",
    "egg",
    "chicken",
    "beef",
    "pork",
    "fish",
    "salmon",
    "shrimp",
    "sausage",
    "bacon",
    "flour",
    "sugar",
    "salt",
    "olive oil",
    "vegetable oil",
    "rice",
    "pasta",
    "water",
    "bread",
    "honey",
    "vinegar",
    "soy sauce",
    "mayonnaise",
    "mustard",
]


def correct_ingredient_name(user_input: str) -> tuple[str, bool]:

    normalized_input = user_input.strip().lower()

    if normalized_input in CUSTOM_MAPPINGS:
        corrected_word = CUSTOM_MAPPINGS[normalized_input]
        return corrected_word.capitalize(), True

    if normalized_input in VALID_ENGLISH_INGREDIENTS:
        return normalized_input.capitalize(), False

    cutoff_val = 0.5 if len(normalized_input) <= 4 else 0.65

    possible_matches = difflib.get_close_matches(
        normalized_input,
        VALID_ENGLISH_INGREDIENTS,
        n=1,
        cutoff=cutoff_val,
    )

    if possible_matches:
        best_match = possible_matches[0]
        return best_match.capitalize(), True

    return user_input.strip().capitalize(), False
