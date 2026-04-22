import streamlit as st
import pandas as pd
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Backend.api_process import AsyncRecipeAPI

st.title("📅 Weekly Meal Plan")
st.write("Here is your 7-day meal plan based on your dietary preferences and home inventory.")

weekly_data = {
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "Breakfast": ["Oatmeal & Berries", "Scrambled Eggs", "Avocado Toast", "Pancakes", "Smoothie Bowl", "Omelette", "French Toast"],
    "Lunch": ["Chicken Salad", "Lentil Soup", "Quinoa Bowl", "Turkey Wrap", "Pasta Salad", "Grilled Cheese", "Beef Stew"],
    "Dinner": ["Grilled Salmon", "Spaghetti Bolognese", "Vegetable Stir-fry", "Roast Chicken", "Tacos", "Pizza", "Steak & Mash"]
}

df_plan = pd.DataFrame(weekly_data)
st.dataframe(df_plan, use_container_width=True, hide_index=True)
st.divider()
st.subheader("🌐 Live Backend Connection Test")
st.write("Let''s ask the Spoonacular API for real recipes based on some test ingredients!")

if st.button("Fetch Real Recipes via API", use_container_width=True):
    test_ingredients = ["tomato", "cheese", "garlic"] # Şimdilik test için
    
    with st.spinner("Connecting to Spoonacular API asynchronously..."):
        # Streamlit senkron çalışır, asenkron API''yi çalıştırmak için asyncio.run kullanıyoruz
        recipes = asyncio.run(AsyncRecipeAPI.search_by_ingredients(test_ingredients))
        
        if recipes:
            st.success("✅ Successfully fetched data from API!")
            for recipe in recipes:
                st.info(f"🍲 **{recipe['title']}** (Missing Ingredients: {recipe['missedIngredientCount']})")
        else:
            st.error("No recipes found. Make sure your .env file has a valid SPOONACULAR_API_KEY!")

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Regenerate Plan", use_container_width=True):
        st.success("Request sent to AI model! Generating a new plan...")
with col2:
    if st.button("📥 Export to PDF", use_container_width=True):
        st.info("PDF export feature will be available soon.")
