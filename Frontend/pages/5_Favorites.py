import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Favorites", layout="wide", initial_sidebar_state="collapsed"
)
from auth_utils import require_login

require_login()

USERNAME = st.session_state.username
EMAIL = st.session_state.email

API_FAVORITES = "http://localhost:8000/api/favorites"
API_ADD_SINGLE = "http://localhost:8000/api/meal-plan/add-single"

st.title("❤️ My Favorite Recipes")
st.write("All the recipes you've liked before are here!")
st.divider()


def fetch_favorites():
    try:
        res = requests.get(f"{API_FAVORITES}/{EMAIL}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                return data.get("data", [])
    except Exception:
        st.error("Backend connection error.")
    return []


favorites = fetch_favorites()

if not favorites:
    st.info(
        "You haven't added any favorite recipes yet. Go find some delicious meals! 🍳"
    )
else:
    cols = st.columns(3)

    for index, recipe in enumerate(favorites):
        with cols[index % 3]:
            with st.container(border=True):

                if recipe.get("recipe_image"):
                    st.image(recipe["recipe_image"], use_container_width=True)

                st.markdown(f"**{recipe['recipe_title']}**")

                st.divider()
                st.write("📅 **Add to Plan**")

                col_day, col_meal = st.columns(2)
                with col_day:
                    selected_day = st.selectbox(
                        "Day",
                        ["Day 1", "Day 2", "Day 3"],
                        key=f"day_{recipe['recipe_id']}",
                    )
                with col_meal:
                    selected_meal = st.selectbox(
                        "Meal",
                        [
                            "Breakfast",
                            "Lunch",
                            "Dinner",
                            "Soup",
                            "Desert",
                            "Salad",
                            "Drink",
                        ],
                        key=f"meal_{recipe['recipe_id']}",
                    )

                # Geçici hafıza anahtarı
                plan_state_key = f"plan_info_{recipe['recipe_id']}"

                if st.button(
                    "➕ Add to Plan",
                    key=f"add_plan_{recipe['recipe_id']}",
                    use_container_width=True,
                ):
                    # Eski kayıtlarda ingredients yoksa çökmesin diye kontrol
                    ingredients_json = recipe.get("ingredients")
                    if not ingredients_json:
                        ingredients_json = '{"ingredients": []}'

                    payload = {
                        "email": EMAIL,
                        "recipe_id": recipe["recipe_id"],
                        "recipe_title": recipe["recipe_title"],
                        "recipe_image": recipe.get("recipe_image"),
                        "day": selected_day,
                        "meal_type": selected_meal,
                        "ingredients_json": ingredients_json,
                    }

                    with st.spinner("Adding to plan and checking kitchen inventory..."):
                        res = requests.post(API_ADD_SINGLE, json=payload)
                        if res.status_code == 200:
                            data = res.json()
                            # Dönen eksikleri Streamlit hafızasına kaydediyoruz
                            st.session_state[plan_state_key] = {
                                "meal_plan_id": data.get("meal_plan_id"),
                                "missing_items": data.get("missing_items", []),
                            }
                            st.success(data.get("message"))
                        else:
                            st.error("Failed to add to plan.")

                if plan_state_key in st.session_state:
                    missing_items = st.session_state[plan_state_key]["missing_items"]
                    meal_plan_id = st.session_state[plan_state_key]["meal_plan_id"]

                    if missing_items:
                        st.warning(
                            f"⚠️ You are missing {len(missing_items)} ingredients:"
                        )
                        for m in missing_items:
                            st.write(f"- {m['name']} ({m['amount']} {m['unit']})")

                        API_ADD_MISSING = (
                            "http://localhost:8000/api/shopping-list/add-missing"
                        )
                        if st.button(
                            "🛒 Add Missing Items to Grocery List",
                            key=f"cart_{recipe['recipe_id']}",
                            use_container_width=True,
                        ):
                            missing_payload = {
                                "meal_plan_id": meal_plan_id,
                                "email": EMAIL,
                            }
                            m_res = requests.post(API_ADD_MISSING, json=missing_payload)
                            if m_res.status_code == 200:
                                st.success("✅ Items added to Grocery List!")
                                del st.session_state[plan_state_key]
                                st.rerun()
                    else:
                        st.success("🎉 You have all the ingredients at home!")

                if st.button(
                    "💔 Remove from Favorites",
                    key=f"remove_{recipe['recipe_id']}",
                    use_container_width=True,
                ):
                    payload = {
                        "email": EMAIL,
                        "recipe_id": recipe["recipe_id"],
                        "recipe_title": recipe["recipe_title"],
                    }
                    res = requests.post(API_FAVORITES, json=payload)
                    if res.status_code == 200:
                        st.rerun()
