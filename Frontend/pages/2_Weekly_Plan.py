import streamlit as st
import pandas as pd
import requests

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if not st.session_state.logged_in:
    st.warning("🚨 Please login from the main page first!")
    st.stop()

username = st.session_state.username
email = st.session_state.email

API_GET_PLAN = f"http://localhost:8000/api/meal-plan/{email}"
API_GENERATE_PLAN = "http://localhost:8000/api/meal-plan/generate"

st.title("📅 3-Day Meal Plan")
st.write("Generate a personalized 3-day meal plan based on your diet and allergy preferences.")

st.info(f"Meal plan for: **{username}**")


if st.button("✨ Generate 3-Day Meal Plan", use_container_width=True):
    payload = {
        "username": username,
        "email": email
    }

    with st.spinner("Generating your personalized meal plan..."):
        try:
            response = requests.post(API_GENERATE_PLAN, json=payload)

            if response.status_code == 200:
                data = response.json()

                if data.get("status") == "success":
                    st.success("✅ Your 3-day meal plan has been generated successfully!")
                    st.rerun()
                else:
                    st.error(data.get("message", "Failed to generate meal plan."))

            else:
                st.error("Backend Error: Failed to generate meal plan.")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error("🚨 CONNECTION ERROR: Backend is not running.")

st.divider()

meal_plan = []

try:
    response = requests.get(API_GET_PLAN)

    if response.status_code == 200:
        data = response.json()

        if data.get("status") == "success":
            meal_plan = data.get("meal_plan", [])

except requests.exceptions.ConnectionError:
    st.error("🚨 CONNECTION ERROR: Backend is not running.")


st.subheader("🍽️ Your Current Meal Plan")

if meal_plan:
    table_data = []

    for item in meal_plan:
        table_data.append({
            "Day": item.get("plan_day", ""),
            "Recipe": item.get("recipe_title", ""),
            "Ready In": str(item.get("ready_in_minutes", "")) + " min",
            "Servings": item.get("servings", "")
        })

    df_plan = pd.DataFrame(table_data)

    st.dataframe(
        df_plan,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("📌 Plan Details")

    for item in meal_plan:
        st.markdown(f"### {item.get('plan_day', '')}: {item.get('recipe_title', '')}")

        if item.get("recipe_image"):
            st.image(item.get("recipe_image"), use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"⏱️ Ready in: {item.get('ready_in_minutes', 'N/A')} minutes")

        with col2:
            st.info(f"🍽️ Servings: {item.get('servings', 'N/A')}")

        if item.get("source_url"):
            st.link_button("View Recipe", item.get("source_url"))

        st.divider()

else:
    st.info("No meal plan found yet. Click the button above to generate your 3-day meal plan.")


if st.button("📥 Export to PDF", use_container_width=True):
    st.info("PDF export feature will be available soon.")