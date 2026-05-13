import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Profile Alergies",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from auth_utils import require_login

require_login()

username = st.session_state.get("username", "")
email = st.session_state.get("email", "")

if username == "":
    st.error("Username information is missing. Please logout and login again.")
    st.stop()


API_URL_POST = "http://localhost:8000/api/profile"
API_URL_GET = f"http://localhost:8000/api/profile/{username}"

st.title("👤 User Profile")
st.write("Your dietary preferences and allergies will be collected here.")

current_email = email
current_diet = "None"
current_allergies = []

try:
    response = requests.get(API_URL_GET)

    if response.status_code == 200:
        data = response.json()

        if data.get("status") == "success":
            current_email = data.get("email", email)
            current_diet = data.get("diet", "None")
            current_allergies = data.get("allergies", [])

except requests.exceptions.ConnectionError:
    st.error("🚨 CONNECTION ERROR: Backend is not running.")


st.subheader("📋 Your Current Preferences")

if current_diet != "None" or len(current_allergies) > 0:
    st.info(f"**Current Diet:** {current_diet}")

    if len(current_allergies) > 0:
        st.warning(f"**Current Allergies:** {', '.join(current_allergies)}")
    else:
        st.success("**Current Allergies:** None")
else:
    st.info("No preferences found in the database. Please select them below.")

st.divider()

st.subheader("⚙️ Update Preferences")

col1, col2 = st.columns(2)

with col1:
    diet_options = ["None", "Vegan", "Vegetarian", "Keto", "Gluten-Free"]

    default_diet_index = (
        diet_options.index(current_diet) if current_diet in diet_options else 0
    )

    diet = st.selectbox(
        "Do you follow a specific diet?", diet_options, index=default_diet_index
    )

with col2:
    allergy_options = ["Peanuts", "Dairy", "Egg", "Soy", "Seafood"]

    # Database'den gelen ama listede olmayan allergy değerleri hata vermesin diye filtreliyoruz
    valid_current_allergies = [
        allergy for allergy in current_allergies if allergy in allergy_options
    ]

    allergies = st.multiselect(
        "Select your allergies:", allergy_options, default=valid_current_allergies
    )

if st.button("Save Preferences", use_container_width=True):

    with st.spinner("Saving to SQLite database..."):

        payload = {
            "username": username,
            "email": email,
            "diet": diet,
            "allergies": allergies,
        }

        try:
            post_response = requests.post(API_URL_POST, json=payload)

            if post_response.status_code == 200:
                response_data = post_response.json()

                st.success(
                    f"✅ {response_data.get('message', 'Profile successfully saved!')}"
                )
                time.sleep(1.5)
                st.rerun()

            else:
                st.error("Backend Error: Failed to save preferences.")
                st.write(post_response.text)

        except requests.exceptions.ConnectionError:
            st.error("🚨 CONNECTION ERROR: Backend is not running.")
