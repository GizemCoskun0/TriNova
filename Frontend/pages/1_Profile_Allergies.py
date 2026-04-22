import streamlit as st

st.title("User Profile")
st.write("User dietary preferences and allergies will be collected here.")
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
    # Şimdilik sadece arayüzde gösterelim, veritabanı kısmını 
    # giriş ekranı gelince oradaki kullanıcı ID''sine göre güncelleyeceğiz.
    st.success(f"Saved! Diet: {diet}, Allergies: {', '.join(allergies) if allergies else 'None'}")
