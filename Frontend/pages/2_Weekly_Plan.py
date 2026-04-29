import streamlit as st
import pandas as pd
import requests
import requests

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


col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Regenerate Plan", use_container_width=True):
        st.success("Request sent to AI model! Generating a new plan...")
with col2:
    if st.button("📥 Export to PDF", use_container_width=True):
        st.info("PDF export feature will be available soon.")
