import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API Key securely
API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"

class AsyncRecipeAPI:
    """Class to handle asynchronous (non-blocking) communication with the Spoonacular API."""

    @staticmethod
    async def search_by_ingredients(ingredients_list):
        """Searches for recipes based on the provided ingredients list."""
        
        ingredients_str = ",".join(ingredients_list)
        
        # The exact endpoint for finding recipes by ingredients
        endpoint = f"{BASE_URL}/findByIngredients"
        
        # Parameters to send to the API
        params = {
            "ingredients": ingredients_str,
            "number": 5, # Fetch the top 5 recipes 
            "apiKey": API_KEY
        }

        # Make an asynchronous HTTP request using aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                # Await the response without blocking the main thread
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"API Error! Status Code: {response.status}")
                        return None
            except Exception as e:
                print(f"Connection error occurred: {e}")
                return None

# A small runtime block for testing asynchronous code
async def main():
    print("Sending ingredients to the API...")
    
    my_ingredients = ["tomato", "cheese", "garlic"] 
    
    recipes = await AsyncRecipeAPI.search_by_ingredients(my_ingredients)
    
    if recipes:
        print("\n--- FOUND RECIPES ---")
        for recipe in recipes:
            print(f"🍲 {recipe['title']} (Missing Ingredients: {recipe['missedIngredientCount']})")
        print("------------------------\n")
    else:
        print("No recipes found or API key is invalid.")

if __name__ == "__main__":

    asyncio.run(main())