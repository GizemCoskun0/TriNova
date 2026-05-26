import os
import asyncio
import aiohttp
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"


class AsyncRecipeAPI:
    @staticmethod
    async def search_by_ingredients(
        ingredients_list, diets=None, allergies=None, number=5
    ):
        ingredients_str = ",".join(ingredients_list)
        endpoint = f"{BASE_URL}/complexSearch"

        params = {
            "includeIngredients": ingredients_str,
            "number": 15,
            "sort": "min-missing-ingredients",
            "ignorePantry": "true",
            "instructionsRequired": "true",
            "addRecipeInformation": "true",
            "fillIngredients": "true",
            "apiKey": API_KEY,
        }

        if diets:
            params["diet"] = ",".join(diets)
        if allergies:
            params["intolerances"] = ",".join(allergies)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])

                        sorted_results = sorted(
                            results, key=lambda x: x.get("missedIngredientCount", 99)
                        )

                        return sorted_results[:number]

                    return None
            except Exception as e:
                print(f"Connection error occurred: {e}")
                return None

    @staticmethod
    async def get_random_meal_plan(diets=None, allergies=None, number=9):
        endpoint = f"{BASE_URL}/complexSearch"

        params = {
            "sort": "random",
            "number": number,
            "instructionsRequired": "true",
            "addRecipeInformation": "true",
            "fillIngredients": "true",
            "apiKey": API_KEY,
        }

        if diets:
            params["diet"] = ",".join(diets)
        if allergies:
            params["intolerances"] = ",".join(allergies)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    return None
            except Exception as e:
                print(f"Connection error occurred: {e}")
                return None

    @staticmethod
    async def get_categorized_recipes(
        diets: list, allergies: list, category: str, number: int = 5, **kwargs
    ):
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": API_KEY,
            "type": category,
            "number": number,
            "addRecipeInformation": "true",
            "fillIngredients": "true",
            "instructionsRequired": "true",
        }
        if diets:
            params["diet"] = ",".join(diets)
        if allergies:
            params["intolerances"] = ",".join(allergies)

        if kwargs:
            params.update(kwargs)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            return []
