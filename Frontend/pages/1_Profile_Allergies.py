import streamlit as st
import requests

st.title("User Profile")
st.write("User dietary preferences and allergies will be collected here.")

st.subheader("👤 Account Info")
username = st.text_input("Username", value="beyza_dev")
email = st.text_input("Email", value="beyza@smartkitchen.com")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🥗 Dietary Preferences")
    diet = st.selectbox("Do you follow a specific diet?", 
                        ["None", "Vegan", "Vegetarian", "Keto", "Gluten-Free"])

with col2:
    st.subheader("🚫 Allergies")
    allergies = st.multiselect("Select your allergies:", 
                               ["Peanuts", "Dairy", "Egg", "Soy", "Seafood"])

if st.button("Save Preferences", use_container_width=True):
    with st.spinner("Saving to database..."):
        
        payload = {
            "username": username,
            "email": email,
            "diet": diet,
            "allergies": allergies
        }
        
        try:
            response = requests.post("http://localhost:8000/api/profile", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data['message']}")
                st.info(f"Saved Diet: {diet} | Saved Allergies: {', '.join(allergies) if allergies else 'None'}")
            else:
                st.error("An error was returned from the backend.!")
        except requests.exceptions.ConnectionError:
            st.error("🚨 CONNECTION ERROR: Unable to reach FastAPI server!")