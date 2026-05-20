import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Settings",
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
API_URL_PASSWORD = "http://localhost:8000/api/profile/change-password"


st.title(" Settings ")
st.write("Manage your dietary preferences, allergies, and account security.")

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


st.subheader("Your Current Preferences")

if current_diet != "None" or len(current_allergies) > 0:
    st.info(f"**Current Diet:** {current_diet}")

    if len(current_allergies) > 0:
        st.warning(f"**Current Allergies:** {', '.join(current_allergies)}")
    else:
        st.success("**Current Allergies:** None")
else:
    st.info("No preferences found in the database. Please select them below.")

st.divider()

st.subheader("Update Preferences")

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
    valid_current_allergies = [
        allergy for allergy in current_allergies if allergy in allergy_options
    ]
    allergies = st.multiselect(
        "Select your allergies:", allergy_options, default=valid_current_allergies
    )

if st.button("Save Preferences", use_container_width=True):
    with st.spinner("Saving to database..."):
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



st.divider()
st.subheader("Security Settings")

with st.expander("Change Account Password"):
    
    
    
    with st.form("password_change_form"):
        current_password = st.text_input("Current Password", type="password")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            new_password = st.text_input("New Password", type="password", help="Must be at least 4 characters")
        with col_p2:
            confirm_password = st.text_input("Confirm New Password", type="password")

        submitted = st.form_submit_button("Update Password", use_container_width=True)

        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("❌ Please fill in all password fields.")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match!")
            elif len(new_password) < 4:
                st.error("❌ New password must be at least 4 characters long!")
            else:
                
                with st.spinner("Updating your password..."):
                    pwd_payload = {
                        "username": username,
                        "current_password": current_password,
                        "new_password": new_password
                    }
                    
                    try:
                        pwd_response = requests.put(API_URL_PASSWORD, json=pwd_payload)
                        
                        if pwd_response.status_code == 200:
                            pwd_data = pwd_response.json()
                            if pwd_data.get("status") == "success":
                                st.success("✅ Password updated successfully! Please use your new password next time you log in.")
                            else:
                                st.error(f"❌ Error: {pwd_data.get('message', 'Incorrect current password.')}")
                        else:
                            st.error("❌ Incorrect current password or backend error.")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("🚨 CONNECTION ERROR: Backend is not running.")