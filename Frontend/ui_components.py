import streamlit as st
import requests
import json
from ui_utils import clean_html, parse_ingredients, get_meal_emoji

API_CHECK_INGREDIENTS = "http://localhost:8000/api/meal-plan/check-ingredients"
API_ADD_MISSING = "http://localhost:8000/api/shopping-list/add-missing"
API_FAVORITES = "http://localhost:8000/api/favorites"


def render_recipe_cards(category_key, email, user_favorites):
    recipes = st.session_state.get(f"candidates_{category_key}", [])

    if not recipes:
        return

    st.markdown(f"**💡 Suggested {category_key.capitalize()}s**")

    for recipe in recipes:
        with st.expander(f"🍲 {recipe['title']}"):
            col_img, col_info = st.columns([1, 2])

            with col_img:
                st.image(recipe["image"], use_container_width=True)

            with col_info:
                target_day = st.selectbox(
                    "Select Day",
                    ["Day 1", "Day 2", "Day 3"],
                    key=f"day_{category_key}_{recipe['id']}",
                )
                target_meal = st.selectbox(
                    "Select Meal",
                    ["Breakfast", "Lunch", "Dinner", "Soup", "Salad", "Dessert"],
                    key=f"meal_{category_key}_{recipe['id']}",
                )
                btn_col1, btn_col2 = st.columns(2)

                with btn_col1:
                    if st.button(
                        f"➕ Add to Plan",
                        key=f"add_{category_key}_{recipe['id']}",
                        use_container_width=True,
                    ):
                        raw_instr = recipe.get("instructions")
                        if not raw_instr or raw_instr == "":
                            analyzed = recipe.get("analyzedInstructions", [])
                            if analyzed and len(analyzed) > 0:
                                steps = analyzed[0].get("steps", [])
                                raw_instr = "\n".join(
                                    [f"{s['number']}. {s['step']}" for s in steps]
                                )

                        final_instr = (
                            raw_instr if raw_instr else "No instructions available."
                        )

                        add_payload = {
                            "email": email,
                            "day": target_day,
                            "meal_type": target_meal,
                            "recipe_id": recipe["id"],
                            "recipe_title": recipe["title"],
                            "recipe_image": recipe["image"],
                            "ready_in_minutes": recipe.get("readyInMinutes")
                            or recipe.get("ready_in_minutes")
                            or 45,
                            "servings": recipe.get("servings") or 4,
                            "instructions": final_instr,
                            "ingredients_json": json.dumps(
                                {
                                    "ingredients": recipe.get("usedIngredients", [])
                                    + recipe.get("missedIngredients", [])
                                }
                            ),
                        }
                        res = requests.post(
                            "http://localhost:8000/api/meal-plan/add-single",
                            json=add_payload,
                        )
                        if res.status_code == 200:
                            st.toast("✅ Added to Plan!")
                            st.rerun()

                with btn_col2:
                    is_fav = recipe["id"] in user_favorites
                    button_label = "❤️ In Favorite" if is_fav else "🤍 Add to Favorite"

                    if st.button(
                        button_label,
                        key=f"fav_suggest_{category_key}_{recipe['id']}",
                        use_container_width=True,
                    ):
                        fav_payload = {
                            "email": email,
                            "recipe_id": recipe["id"],
                            "recipe_title": recipe["title"],
                            "recipe_image": recipe["image"],
                        }
                        res = requests.post(API_FAVORITES, json=fav_payload)
                        if res.status_code == 200:
                            st.toast("⭐ Favorites updated!")
                            st.rerun()


def render_current_plan(meal_plan, email, user_favorites):
    if not meal_plan:
        st.info(
            "No meal plan found yet. Click the button above to generate your personalized meal plan."
        )
        return

    meal_order = ["Breakfast", "Lunch", "Dinner", "Soup", "Salad", "Dessert"]
    days = []
    for item in meal_plan:
        if item.get("plan_day") not in days:
            days.append(item.get("plan_day"))

    for day in days:
        st.markdown(f"## {day}")

        day_items = [item for item in meal_plan if item.get("plan_day") == day]
        day_items = sorted(
            day_items,
            key=lambda x: (
                meal_order.index(x.get("meal_type"))
                if x.get("meal_type") in meal_order
                else 99
            ),
        )

        cols = st.columns(6)

        for index, item in enumerate(day_items):
            meal_plan_id = item.get("id")
            meal_type = item.get("meal_type", "")
            recipe_title = item.get("recipe_title", "")
            meal_emoji = get_meal_emoji(meal_type)

            with cols[index % 6]:
                with st.container(border=True):
                    st.markdown(f"### {meal_emoji} {meal_type}")
                    st.markdown(f"**{recipe_title}**")

                    if item.get("recipe_image"):
                        st.image(item.get("recipe_image"), use_container_width=True)

                    recipe_id = item.get("recipe_id")
                    is_fav = recipe_id in user_favorites
                    heart_icon = "❤️ In Favorites" if is_fav else "🤍 Add to Favorites"

                    if st.button(heart_icon, key=f"fav_meal_{meal_plan_id}"):
                        fav_payload = {
                            "email": email,
                            "recipe_id": recipe_id,
                            "recipe_title": recipe_title,
                            "recipe_image": item.get("recipe_image"),
                            "source_url": item.get("source_url", ""),
                            "ingredients_json": item.get(
                                "ingredients", '{"ingredients": []}'
                            ),
                        }
                        try:
                            res = requests.post(API_FAVORITES, json=fav_payload)
                            if res.status_code == 200:
                                st.rerun()
                        except Exception:
                            st.toast("Error: Backend could not be reached..")

                    ready_time = (
                        item.get("ready_in_minutes")
                        or item.get("readyInMinutes")
                        or "45"
                    )
                    servings = item.get("servings") or "4"

                    st.caption(f"⏱️ {ready_time} min | 🍽️ {servings} servings")

                    with st.expander("View Details"):
                        st.markdown("#### 🧂 Ingredients")
                        ingredients = parse_ingredients(item.get("ingredients"))

                        if ingredients:
                            for ingredient in ingredients:
                                name = ingredient.get("name", "Unknown ingredient")
                                amount = ingredient.get("amount", "")
                                unit = ingredient.get("unit", "")
                                st.write(f"- {name} {amount} {unit}")
                        else:
                            st.info("Ingredients are not available for this recipe.")

                        st.markdown("#### 👩‍🍳 Instructions")
                        instructions = item.get("instructions")

                        if instructions:
                            st.write(clean_html(instructions))
                        else:
                            st.info("Instructions will be available soon.")

                        if item.get("source_url"):
                            st.link_button("View Full Recipe", item.get("source_url"))

                        st.divider()

                        if st.button(
                            "🔍 Check Ingredients",
                            key=f"check_{meal_plan_id}",
                            use_container_width=True,
                        ):
                            payload = {"meal_plan_id": meal_plan_id, "email": email}
                            with st.spinner("Checking your inventory..."):
                                try:
                                    check_response = requests.post(
                                        API_CHECK_INGREDIENTS, json=payload
                                    )
                                    if check_response.status_code == 200:
                                        check_data = check_response.json()
                                        if check_data.get("status") == "success":
                                            st.session_state.ingredient_checks[
                                                str(meal_plan_id)
                                            ] = check_data
                                            st.success("✅ Ingredient check completed!")
                                            st.rerun()
                                        else:
                                            st.error(
                                                check_data.get(
                                                    "message",
                                                    "Ingredient check failed.",
                                                )
                                            )
                                    else:
                                        st.error(
                                            "Backend Error: Failed to check ingredients."
                                        )
                                except requests.exceptions.ConnectionError:
                                    st.error(
                                        "🚨 CONNECTION ERROR: Backend is not running."
                                    )

                        check_result = st.session_state.ingredient_checks.get(
                            str(meal_plan_id)
                        )

                        if check_result:
                            st.divider()
                            st.markdown("#### 🧾 Ingredient Check Result")

                            available_items = check_result.get("available_items", [])
                            missing_items = check_result.get("missing_items", [])

                            if available_items:
                                st.markdown("**🏠 Available at Home**")
                                for available in available_items:
                                    name = available.get("name", "")
                                    required_amount = available.get(
                                        "required_amount", ""
                                    )
                                    home_amount = available.get("home_amount", "")
                                    unit = available.get("unit", "")
                                    st.success(
                                        f"{name} - Required: {required_amount} {unit}, At home: {home_amount} {unit}"
                                    )
                            else:
                                st.info("No matching ingredients found at home.")

                            if missing_items:
                                st.markdown("**🛒 Missing Ingredients**")
                                for missing in missing_items:
                                    name = missing.get("name", "")
                                    amount = missing.get("amount", "")
                                    unit = missing.get("unit", "")
                                    st.error(f"{name}: {amount} {unit}")

                                if st.button(
                                    "➕ Add Missing Items to Shopping List",
                                    key=f"add_missing_{meal_plan_id}",
                                    use_container_width=True,
                                ):
                                    payload = {
                                        "meal_plan_id": meal_plan_id,
                                        "email": email,
                                    }
                                    with st.spinner(
                                        "Adding missing items to shopping list..."
                                    ):
                                        try:
                                            add_response = requests.post(
                                                API_ADD_MISSING, json=payload
                                            )
                                            if add_response.status_code == 200:
                                                add_data = add_response.json()
                                                if add_data.get("status") == "success":
                                                    st.success(
                                                        "✅ Missing items added to your shopping list."
                                                    )
                                                    st.info(
                                                        "You can view them on the Grocery List page."
                                                    )
                                                else:
                                                    st.error(
                                                        add_data.get(
                                                            "message",
                                                            "Failed to add missing items.",
                                                        )
                                                    )
                                            else:
                                                st.error(
                                                    "Backend Error: Failed to add missing items."
                                                )
                                        except requests.exceptions.ConnectionError:
                                            st.error(
                                                "🚨 CONNECTION ERROR: Backend is not running."
                                            )
