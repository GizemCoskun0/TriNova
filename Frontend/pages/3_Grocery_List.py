import streamlit as st
import requests

if "recipes" not in st.session_state:
    st.session_state.recipes = []

if "to_buy" not in st.session_state:
    st.session_state.to_buy = {}


st.subheader("🍽️ Recipe Suggestions")
st.write("Find recipe suggestions based on the ingredients you have at home.")

if st.button("Find Recipe Suggestions", use_container_width=True):
    test_ingredients = ["tomato", "cheese", "garlic"]

    with st.spinner("Finding recipe suggestions..."):
        try:
            ingredients_str = ",".join(test_ingredients)
            api_url = f"http://localhost:8000/api/recipes?ingredients={ingredients_str}"

            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()

                if data["status"] == "success":
                    st.success("✅ Recipe suggestions loaded successfully!")

                    recipes = data["data"]

                    # Tarifleri session_state içine kaydediyoruz
                    st.session_state.recipes = recipes

                else:
                    st.error(f"Backend Error: {data['message']}")

            else:
                st.error("🚨 Recipe service is currently unavailable. Please make sure the backend is running.")

        except requests.exceptions.ConnectionError:
            st.error(
                "🚨 CONNECTION ERROR: Unable to reach the FastAPI server! "
                "Make sure you start the backend with the command "
                "'uvicorn main:app --reload' from the terminal."
            )



if st.session_state.recipes:
    st.divider()
    st.subheader("🍲 Select a Recipe")

    recipe_titles = [recipe["title"] for recipe in st.session_state.recipes]

    selected_recipe_title = st.selectbox(
        "Choose a recipe to add its missing ingredients to your shopping list:",
        recipe_titles
    )

    selected_recipe = None

    for recipe in st.session_state.recipes:
        if recipe["title"] == selected_recipe_title:
            selected_recipe = recipe
            break

    if selected_recipe:
        st.info(
            f"Selected Recipe: **{selected_recipe['title']}** "
            f"(Number of Missing Materials: {selected_recipe['missedIngredientCount']})"
        )

        if "missedIngredients" in selected_recipe:
            st.write("Missing ingredients for this recipe:")

            for ingredient in selected_recipe["missedIngredients"]:
                name = ingredient.get("name", "Unknown ingredient")
                amount = ingredient.get("amount", 1)
                unit = ingredient.get("unit", "")

                if unit:
                    st.warning(f"➖ {name}: {amount} {unit}")
                else:
                    st.warning(f"➖ {name}: {amount}")

        if st.button("➕ Add Missing Ingredients to Shopping List", use_container_width=True):
            if "missedIngredients" in selected_recipe:
                for ingredient in selected_recipe["missedIngredients"]:
                    name = ingredient.get("name", "Unknown ingredient")
                    amount = ingredient.get("amount", 1)
                    unit = ingredient.get("unit", "")

                    if unit:
                        item_name = f"{name} ({unit})"
                    else:
                        item_name = name

                    if item_name in st.session_state.to_buy:
                        st.session_state.to_buy[item_name] += amount
                    else:
                        st.session_state.to_buy[item_name] = amount

                st.success("✅ Missing ingredients added to the shopping list!")

            else:
                st.warning("This recipe does not contain missing ingredient information.")


st.divider()

st.title("🛒 Automatic Grocery List")
st.write("Here is your smart shopping list. We've subtracted the items you already have at home!")

required_items = {
    "Tomatoes": 6,
    "Pasta (packs)": 2,
    "Milk (L)": 2,
    "Eggs": 12,
    "Chicken (kg)": 1.5
}

home_items = {
    "Tomatoes": 2,
    "Milk (L)": 1,
    "Eggs": 6,
    "Apples": 4
}

# Fake weekly required list'i ilk açılışta alışveriş listesine ekliyoruz
if "base_items_added" not in st.session_state:
    for item, needed_qty in required_items.items():
        home_qty = home_items.get(item, 0)

        if needed_qty > home_qty:
            st.session_state.to_buy[item] = needed_qty - home_qty

    st.session_state.base_items_added = True


col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Currently at Home (AI Detected)")

    for item, qty in home_items.items():
        st.info(f"✅ {item}: {qty}")

with col2:
    st.subheader("🛒 Missing (To Buy)")

    if not st.session_state.to_buy:
        st.success("You have everything you need for the week! 🎉")
    else:
        for item, qty in st.session_state.to_buy.items():
            st.error(f"➖ {item}: {qty}")


st.divider()

st.subheader("📝 Your Shopping Checklist")

if not st.session_state.to_buy:
    st.success("Your shopping checklist is empty.")
else:
    for item, qty in st.session_state.to_buy.items():
        st.checkbox(f"Buy {qty}x {item}")


if st.button("🗑️ Clear Shopping List", use_container_width=True):
    st.session_state.to_buy = {}
    st.session_state.base_items_added = False
    st.success("Shopping list cleared!")
    st.rerun()


if st.button("📤 Send to WhatsApp / Mail", use_container_width=True):
    st.success("Message sent! (Integration coming soon)")