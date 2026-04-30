import streamlit as st
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

API_INVENTORY = f"http://localhost:8000/api/inventory/{username}"
API_SHOPPING_LIST = f"http://localhost:8000/api/shopping-list/{email}"

st.title("🛒 My Grocery List")
st.write("Here you can see your home inventory and the items you need to buy.")

home_items = []

try:
    inventory_response = requests.get(API_INVENTORY)

    if inventory_response.status_code == 200:
        inventory_data = inventory_response.json()

        if inventory_data.get("status") == "success":
            home_items = inventory_data.get("data", [])
        else:
            st.warning(inventory_data.get("message", "No inventory data found."))

    else:
        st.error("Backend Error: Failed to load inventory.")
        st.write(inventory_response.text)

except requests.exceptions.ConnectionError:
    st.error("🚨 CONNECTION ERROR: Backend is not running.")

shopping_items = []

try:
    shopping_response = requests.get(API_SHOPPING_LIST)

    if shopping_response.status_code == 200:
        shopping_data = shopping_response.json()

        if shopping_data.get("status") == "success":
            shopping_items = shopping_data.get("data", [])
        else:
            st.info(shopping_data.get("message", "Your shopping list is empty."))

    else:
        st.warning("Shopping list endpoint is not ready yet.")
        st.write(shopping_response.text)

except requests.exceptions.ConnectionError:
    st.error("🚨 CONNECTION ERROR: Backend is not running.")


col1, col2 = st.columns(2)


with col1:
    st.subheader("🏠 Currently at Home")

    if home_items:
        for item in home_items:
            name = item.get("name", "")
            amount = item.get("amount", "")
            unit = item.get("unit", "")

            st.info(f"✅ {name}: {amount} {unit}")
    else:
        st.info("No items found in your inventory.")


with col2:
    st.subheader("🛒 Items To Buy")

    if shopping_items:
        for item in shopping_items:
            item_name = item.get("item_name", "")
            amount = item.get("amount", "")
            unit = item.get("unit", "")
            is_checked = item.get("is_checked", False)

            st.checkbox(
                f"Buy {amount} {unit} {item_name}",
                value=is_checked,
                key=f"shopping_item_{item.get('id')}"
            )
    else:
        st.success("Your shopping list is empty.")

st.divider()

if st.button("📤 Send to WhatsApp / Mail", use_container_width=True):
    st.success("Message sent! Integration coming soon.")