import streamlit as st
import requests

st.set_page_config(
    page_title="Grocery List", layout="wide", initial_sidebar_state="collapsed"
)
from auth_utils import require_login

require_login()

USERNAME = st.session_state.username
EMAIL = st.session_state.email

API_INVENTORY = f"http://localhost:8000/api/inventory/{USERNAME}"
API_SHOPPING_LIST = f"http://localhost:8000/api/shopping-list/{EMAIL}"
API_TOGGLE_ITEM = "http://localhost:8000/api/shopping-list/toggle"
API_CLEAR_CHECKED = f"http://localhost:8000/api/shopping-list/clear/{EMAIL}"
API_RECALCULATE_SHOPPING_LIST = (
    f"http://localhost:8000/api/shopping-list/recalculate/{EMAIL}"
)

st.title("🛒 My Grocery List")
st.write("Here you can see your home inventory and the items you need to buy.")


def toggle_item(item_id, current_status):
    try:
        requests.put(
            f"{API_TOGGLE_ITEM}/{item_id}", json={"is_checked": not current_status}
        )
    except Exception:
        st.toast("🚨 Error updating item status!")


def clear_checked_items():
    try:
        response = requests.delete(API_CLEAR_CHECKED)
        if response.status_code == 200:
            st.success("✅ Checked items removed from list!")
        else:
            st.error("Failed to clear items.")
    except Exception:
        st.error("Backend connection error!")


if st.button("🔄 Recalculate Shopping List", use_container_width=True):
    try:
        response = requests.post(API_RECALCULATE_SHOPPING_LIST)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success":
                st.success("✅ Shopping list recalculated successfully!")
                st.rerun()
            else:
                st.error(data.get("message", "Failed to recalculate shopping list."))
        else:
            st.error("Backend Error: Failed to recalculate shopping list.")
            st.write(response.text)

    except Exception:
        st.error("🚨 CONNECTION ERROR: Backend is not running.")

home_items = []
try:
    inv_res = requests.get(API_INVENTORY)
    if inv_res.status_code == 200 and inv_res.json().get("status") == "success":
        home_items = inv_res.json().get("data", [])
except:
    st.error("🚨 CONNECTION ERROR: Backend is not running.")

shopping_items = []
try:
    shop_res = requests.get(API_SHOPPING_LIST)
    if shop_res.status_code == 200 and shop_res.json().get("status") == "success":
        shopping_items = shop_res.json().get("data", [])
except:
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
            item_id = item.get("id")

            st.checkbox(
                f"{amount} {unit} {item_name}",
                value=is_checked,
                key=f"shopping_item_{item_id}",
                on_change=toggle_item,
                args=(item_id, is_checked),
            )

        if any(item.get("is_checked") for item in shopping_items):
            st.write("")  # Boşluk
            if st.button("🗑️ Clear Purchased Items", use_container_width=True):
                clear_checked_items()
                st.rerun()
    else:
        st.success("Your shopping list is empty. 🥳")



st.divider()

# PDF İndirme Butonu Bölümü
try:
    API_PDF_URL = f"http://localhost:8000/api/shopping-list/{EMAIL}/pdf"
    pdf_response = requests.get(API_PDF_URL)
    
    if pdf_response.status_code == 200:
        st.download_button(
            label="📥 Download Grocery List (PDF)",
            data=pdf_response.content,
            file_name=f"grocery_list_{USERNAME}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    else:
        st.button("📥 Download Grocery List (PDF)", disabled=True, use_container_width=True)
except Exception:
    st.button("📥 PDF Server Offline", disabled=True, use_container_width=True)