import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"


class AsyncRecipeAPI:

    # 1. YETENEK: SMART INVENTORY İÇİN (Malzemeli + Filtreli)
    # 1. YETENEK: SMART INVENTORY İÇİN (Malzemeli + Filtreli)
    @staticmethod
    async def search_by_ingredients(
        ingredients_list, diets=None, allergies=None, number=5
    ):
        ingredients_str = ",".join(ingredients_list)
        endpoint = f"{BASE_URL}/complexSearch"

        params = {
            "includeIngredients": ingredients_str,
            "number": 15,  # 🚀 BİLEREK FAZLA ÇEKİYORUZ (İçinden en iyileri seçeceğiz)
            "sort": "min-missing-ingredients",  # 🚀 HEDEF: Markete en az gönderen tarif
            "ignorePantry": "true",  # 🚀 Tuz, yağ, su gibi temel malzemeleri eksik sayma!
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

                        # 🚀 PYTHON İLE ZEKİ SIRALAMA:
                        # Eksik malzeme sayısı (missedIngredientCount) EN AZ olanları en üste al
                        sorted_results = sorted(
                            results, key=lambda x: x.get("missedIngredientCount", 99)
                        )

                        # Sadece en eksiksiz olan "number" (5) kadarını döndür
                        return sorted_results[:number]

                    return None
            except Exception as e:
                print(f"Connection error occurred: {e}")
                return None

    # 2. YETENEK: MEAL PLANNER İÇİN (Rastgele + Filtreli)
    @staticmethod
    async def get_random_meal_plan(diets=None, allergies=None, number=9):
        endpoint = f"{BASE_URL}/complexSearch"

        params = {
            "sort": "random",  # 🚀 Her seferinde farklı tarifler gelmesini sağlayan satır
            "number": number,  # 🚀 Eksik olan tarif sayısı limiti
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
        diets: list, allergies: list, category: str, number: int = 5
    ):
        # Spoonacular'ın complexSearch servisini kullanıyoruz
        url = "https://api.spoonacular.com/recipes/complexSearch"

        # Mevcut fonksiyonundaki API_KEY'i burada da kullanıyorsun
        params = {
            "apiKey": API_KEY,
            "type": category,
            "number": number,
            "addRecipeInformation": True,
            "fillIngredients": True,
        }

        # Diyet ve alerji kurallarını aynen koruyoruz ki kullanıcının sağlığı tehlikeye girmesin
        if diets:
            params["diet"] = ",".join(diets)
        if allergies:
            params["intolerances"] = ",".join(allergies)

        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            return []
