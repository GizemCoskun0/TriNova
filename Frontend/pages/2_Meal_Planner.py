import streamlit as st
import requests

st.set_page_config(
    page_title="Meal Planner",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from auth_utils import require_login
from ui_utils import get_user_favorite_ids
from ui_components import render_recipe_cards, render_current_plan

require_login()

USERNAME = st.session_state.username
EMAIL = st.session_state.email

if "ingredient_checks" not in st.session_state:
    st.session_state.ingredient_checks = {}

API_GET_PLAN = f"http://localhost:8000/api/meal-plan/{EMAIL}"
API_GENERATE_PLAN = "http://localhost:8000/api/meal-plan/generate"
API_PROFILE = f"http://localhost:8000/api/profile/{USERNAME}"
API_INVENTORY = f"http://localhost:8000/api/inventory/{USERNAME}"
API_GENERATE_CATEGORY = "http://localhost:8000/api/meal-plan/generate-category"

user_favorites = get_user_favorite_ids(EMAIL)


def fetch_meal_plan():
    try:
        response = requests.get(API_GET_PLAN)
        if response.status_code == 200 and response.json().get("status") == "success":
            return response.json().get("meal_plan", [])
    except:
        st.error("🚨 CONNECTION ERROR: Backend is not running.")
    return []


def fetch_profile_summary():
    try:
        response = requests.get(API_PROFILE)
        if response.status_code == 200 and response.json().get("status") == "success":
            return response.json().get("diet", "None"), response.json().get(
                "allergies", []
            )
    except:
        pass
    return "None", []


def fetch_inventory_count():
    try:
        response = requests.get(API_INVENTORY)
        if response.status_code == 200 and response.json().get("status") == "success":
            return len(response.json().get("data", []))
    except:
        pass
    return 0


meal_plan = fetch_meal_plan()
if meal_plan:
    meal_plan.sort(
        key=lambda x: (
            int(x["plan_day"].split()[-1])
            if x["plan_day"] and x["plan_day"].split()[-1].isdigit()
            else 0
        )
    )

current_diet, current_allergies = fetch_profile_summary()
inventory_count = fetch_inventory_count()

st.title("🍽️ My Meal Plan")
st.write(
    "Create and manage your personalized meal plan based on your diet, allergies, and home inventory."
)
st.divider()

st.subheader("📌 Plan Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("User", USERNAME)
col2.metric("Diet", current_diet)
col3.metric("Allergies", str(len(current_allergies)))
col4.metric("Inventory Items", inventory_count)

st.caption(
    "Allergies: " + (", ".join(current_allergies) if current_allergies else "None")
)
st.divider()

st.subheader("⚙️ Meal Plan Actions")

tab_main, tab_soup, tab_salad, tab_dessert = st.tabs(
    ["🍛 Main course", "🥣 Soup", "🥗 Salad", "🍰 Dessert"]
)

with tab_main:
    if st.button("🔄 Main Course Recommendations", use_container_width=True):
        with st.spinner("Searching for main courses..."):
            res = requests.post(
                API_GENERATE_CATEGORY, json={"email": EMAIL, "category": "main course"}
            )
            if res.status_code == 200 and res.json().get("status") == "success":
                st.session_state["candidates_main"] = res.json().get("data")
    render_recipe_cards("main", EMAIL, user_favorites)

with tab_soup:
    if st.button("🥣 Soup Recommendations", use_container_width=True):
        with st.spinner("Searching for soups..."):
            res = requests.post(
                API_GENERATE_CATEGORY, json={"email": EMAIL, "category": "soup"}
            )
            if res.status_code == 200 and res.json().get("status") == "success":
                st.session_state["candidates_soup"] = res.json().get("data")
    render_recipe_cards("soup", EMAIL, user_favorites)

with tab_salad:
    if st.button("🥗 Salad Recommendations", use_container_width=True):
        with st.spinner("Searching for salads..."):
            res = requests.post(
                API_GENERATE_CATEGORY, json={"email": EMAIL, "category": "salad"}
            )
            if res.status_code == 200 and res.json().get("status") == "success":
                st.session_state["candidates_salad"] = res.json().get("data")
    render_recipe_cards("salad", EMAIL, user_favorites)

with tab_dessert:
    if st.button("🍰 Dessert Recommendations", use_container_width=True):
        with st.spinner("Searching for desserts..."):
            res = requests.post(
                API_GENERATE_CATEGORY, json={"email": EMAIL, "category": "dessert"}
            )
            if res.status_code == 200 and res.json().get("status") == "success":
                st.session_state["candidates_dessert"] = res.json().get("data")
    render_recipe_cards("dessert", EMAIL, user_favorites)

st.divider()

st.subheader("📅 Your Current Plan")

render_current_plan(meal_plan, EMAIL, user_favorites)

st.divider()
if st.button("📥 Export to PDF", use_container_width=True):
    st.info("PDF export feature will be available soon.")
