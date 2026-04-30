import streamlit as st
import requests
import json
import re


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


if "selected_recipe_check" not in st.session_state:
    st.session_state.selected_recipe_check = None

if "selected_meal_plan_id" not in st.session_state:
    st.session_state.selected_meal_plan_id = None


API_GET_PLAN = f"http://localhost:8000/api/meal-plan/{email}"
API_GENERATE_PLAN = "http://localhost:8000/api/meal-plan/generate"
API_CHECK_INGREDIENTS = "http://localhost:8000/api/meal-plan/check-ingredients"
API_ADD_MISSING = "http://localhost:8000/api/shopping-list/add-missing"


def clean_html(text):
    if not text:
        return ""

    clean_text = re.sub("<.*?>", "", text)
    return clean_text.strip()


def parse_ingredients(ingredients_text):
    if not ingredients_text:
        return []

    try:
        data = json.loads(ingredients_text)

        if "ingredients" in data:
            return data.get("ingredients", [])

        # Eski format varsa onu da desteklesin
        used = data.get("usedIngredients", [])
        missed = data.get("missedIngredients", [])

        return used + missed

    except:
        return []


st.title("📅 3-Day Meal Plan")
st.write("Generate a personalized 3-day meal plan based on your diet, allergies, and home inventory.")

st.info(f"Meal plan for: **{username}**")


if st.button("✨ Generate 3-Day Meal Plan", use_container_width=True):
    payload = {
        "username": username,
        "email": email,
        "days": 3
    }

    with st.spinner("Generating your personalized meal plan..."):
        try:
            response = requests.post(API_GENERATE_PLAN, json=payload)

            if response.status_code == 200:
                data = response.json()

                if data.get("status") == "success":
                    st.session_state.selected_recipe_check = None
                    st.session_state.selected_meal_plan_id = None

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
        else:
            st.warning(data.get("message", "No meal plan found."))

    else:
        st.error("Backend Error: Failed to load meal plan.")
        st.write(response.text)

except requests.exceptions.ConnectionError:
    st.error("🚨 CONNECTION ERROR: Backend is not running.")


st.subheader("🍽️ Your Current 3-Day Meal Plan")

if meal_plan:

    meal_order = ["Breakfast", "Lunch", "Dinner"]

    days = []

    for item in meal_plan:
        if item.get("plan_day") not in days:
            days.append(item.get("plan_day"))

    for day in days:
        st.markdown(f"## {day}")

        day_items = [
            item for item in meal_plan
            if item.get("plan_day") == day
        ]

        day_items = sorted(
            day_items,
            key=lambda x: meal_order.index(x.get("meal_type"))
            if x.get("meal_type") in meal_order else 99
        )

        for item in day_items:
            meal_plan_id = item.get("id")
            meal_type = item.get("meal_type", "")
            recipe_title = item.get("recipe_title", "")

            with st.expander(f"{meal_type}: {recipe_title}"):

                img_col, info_col = st.columns([1, 2])

                with img_col:
                    if item.get("recipe_image"):
                        st.image(item.get("recipe_image"), width=180)
                    else:
                        st.info("No image available.")

                with info_col:
                    st.info(f"⏱️ Ready in: {item.get('ready_in_minutes', 'N/A')} minutes")
                    st.info(f"🍽️ Servings: {item.get('servings', 'N/A')}")

                    if item.get("source_url"):
                        st.link_button("View Full Recipe", item.get("source_url"))

                st.markdown("### 🧂 Ingredients")

                ingredients = parse_ingredients(item.get("ingredients"))

                if ingredients:
                    for ingredient in ingredients:
                        name = ingredient.get("name", "Unknown ingredient")
                        amount = ingredient.get("amount", "")
                        unit = ingredient.get("unit", "")

                        st.write(f"- {name} {amount} {unit}")
                else:
                    st.info("Ingredients are not available for this recipe.")

                st.markdown("### 👩‍🍳 Instructions")

                instructions = item.get("instructions")

                if instructions:
                    st.write(clean_html(instructions))
                else:
                    st.info("Instructions will be available soon.")

                st.divider()

                if st.button(
                    "🔍 Check Ingredients for This Recipe",
                    key=f"check_{meal_plan_id}",
                    use_container_width=True
                ):
                    payload = {
                        "meal_plan_id": meal_plan_id,
                        "email": email
                    }

                    with st.spinner("Checking your inventory for this recipe..."):
                        try:
                            check_response = requests.post(
                                API_CHECK_INGREDIENTS,
                                json=payload
                            )
                            st.write("Status code:", check_response.status_code)
                            st.write("Response:", check_response.text)

                            if check_response.status_code == 200:
                                check_data = check_response.json()

                                if check_data.get("status") == "success":
                                    st.session_state.selected_recipe_check = check_data
                                    st.session_state.selected_meal_plan_id = meal_plan_id

                                    st.success("✅ Ingredient check completed!")
                                    st.rerun()

                                else:
                                    st.error(check_data.get("message", "Ingredient check failed."))

                            else:
                                st.error("Backend Error: Failed to check ingredients.")
                                st.write(check_response.text)

                        except requests.exceptions.ConnectionError:
                            st.error("🚨 CONNECTION ERROR: Backend is not running.")

        st.divider()

else:
    st.info("No meal plan found yet. Click the button above to generate your 3-day meal plan.")


if st.session_state.selected_recipe_check:

    check_data = st.session_state.selected_recipe_check

    st.subheader(f"🧾 Ingredient Check: {check_data.get('recipe_title', '')}")

    available_items = check_data.get("available_items", [])
    missing_items = check_data.get("missing_items", [])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏠 Available at Home")

        if available_items:
            for item in available_items:
                name = item.get("name", "")
                required_amount = item.get("required_amount", "")
                home_amount = item.get("home_amount", "")
                unit = item.get("unit", "")

                st.success(
                    f"✅ {name} - Required: {required_amount} {unit}, "
                    f"At home: {home_amount} {unit}"
                )
        else:
            st.info("No matching ingredients found at home.")

    with col2:
        st.markdown("### 🛒 Missing Ingredients")

        if missing_items:
            for item in missing_items:
                name = item.get("name", "")
                amount = item.get("amount", "")
                unit = item.get("unit", "")

                st.error(f"➖ {name}: {amount} {unit}")
        else:
            st.success("You have all ingredients for this recipe!")

    if missing_items:
        if st.button("➕ Add Missing Items to Shopping List", use_container_width=True):
            payload = {
                "meal_plan_id": st.session_state.selected_meal_plan_id,
                "email": email
            }

            with st.spinner("Adding missing ingredients to your shopping list..."):
                try:
                    add_response = requests.post(
                        API_ADD_MISSING,
                        json=payload
                    )

                    if add_response.status_code == 200:
                        add_data = add_response.json()

                        if add_data.get("status") == "success":
                            st.success("✅ Missing ingredients added to your shopping list!")
                        else:
                            st.error(add_data.get("message", "Failed to add missing items."))

                    else:
                        st.error("Backend Error: Failed to add missing items.")
                        st.write(add_response.text)

                except requests.exceptions.ConnectionError:
                    st.error("🚨 CONNECTION ERROR: Backend is not running.")


st.divider()

if st.button("📥 Export to PDF", use_container_width=True):
    st.info("PDF export feature will be available soon.")