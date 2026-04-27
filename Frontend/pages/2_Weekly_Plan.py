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
st.subheader("🌐 Live Backend Connection Test")
st.write("Let''s ask the Spoonacular API for real recipes based on some test ingredients!")

if st.button("Fetch Real Recipes via API", use_container_width=True):
    test_ingredients = ["tomato", "cheese", "garlic"] 
    
    with st.spinner("Connecting to the FastAPI backend..."):
        try:
            ingredients_str = ",".join(test_ingredients)
            api_url = f"http://localhost:8000/api/recipes?ingredients={ingredients_str}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json() 
                
                if data["status"] == "success":
                    st.success("✅ Data was successfully retrieved from the backend and Spoonacular!")
                    recipes = data["data"]
                    for recipe in recipes:
                        st.info(f"🍲 **{recipe['title']}** (Number of Missing Materials: {recipe['missedIngredientCount']})")
                else:
                    st.error(f"Backend Error: {data['message']}")
            else:
                st.error("Failed to retrieve valid response from the server. Are you sure the backend is running?")
                
        except requests.exceptions.ConnectionError:
            st.error("🚨 CONNECTION ERROR: Unable to reach the FastAPI server! Make sure you start the backend with the command 'uvicorn main:app --reload' from the terminal.")

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Regenerate Plan", use_container_width=True):
        st.success("Request sent to AI model! Generating a new plan...")
with col2:
    if st.button("📥 Export to PDF", use_container_width=True):
        st.info("PDF export feature will be available soon.")
