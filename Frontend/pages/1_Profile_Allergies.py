import streamlit as st
import requests
import time

# 1. GÜVENLİK KONTROLÜ
if not st.session_state.get('logged_in', False):
    st.warning("🚨 Please login from the main page first!")
    st.stop()

# Giriş yapan kullanıcının adını alıyoruz
username = st.session_state.username

API_URL_POST = "http://localhost:8000/api/profile"
API_URL_GET = f"http://localhost:8000/api/profile/{username}"

st.title("👤 User Profile")
st.write("Your dietary preferences and allergies will be collected here.")

# --- VERİTABANINDAN GERÇEK VERİLERİ ÇEKME (GET) ---
current_email = ""
current_diet = "None"
current_allergies = []

try:
    response = requests.get(API_URL_GET)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            current_email = data.get("email", "")
            current_diet = data.get("diet", "None")
            current_allergies = data.get("allergies", [])
except requests.exceptions.ConnectionError:
    st.error("🚨 CONNECTION ERROR: Backend is not running.")

# --- EKRANDA MEVCUT TERCİHLERİ GÖSTERME ---
st.subheader("📋 Your Current Preferences (From Database)")

if current_diet != "None" or len(current_allergies) > 0:
    st.info(f"**Current Diet:** {current_diet}")
    if len(current_allergies) > 0:
        st.warning(f"**Current Allergies:** {', '.join(current_allergies)}")
    else:
        st.success("**Current Allergies:** None")
else:
    st.info("No preferences found in the database. Please select them below.")

st.divider()

# --- TERCİHLERİ GÜNCELLEME ALANI ---
st.subheader("⚙️ Update Preferences")

col1, col2 = st.columns(2)

with col1:
    diet_options = ["None", "Vegan", "Vegetarian", "Keto", "Gluten-Free"]
    # Veritabanından gelen diyeti varsayılan olarak seçili yapıyoruz
    default_diet_index = diet_options.index(current_diet) if current_diet in diet_options else 0
    diet = st.selectbox("Do you follow a specific diet?", diet_options, index=default_diet_index)

with col2:
    # Veritabanından gelen alerjileri varsayılan olarak kutuya yerleştiriyoruz
    allergies = st.multiselect("Select your allergies:", 
                               ["Peanuts", "Dairy", "Egg", "Soy", "Seafood"],
                               default=current_allergies)

if st.button("Save Preferences", use_container_width=True):
    # Girinti (boşluk) hatası düzeltildi!
    with st.spinner("Saving to SQLite database..."):
        generated_email = f"{username}@smartkitchen.com"
        payload = {
            "username": username,
            "email": generated_email, 
            "diet": diet,
            "allergies": allergies
        }
        
        try:
            post_response = requests.post(API_URL_POST, json=payload)
            
            if post_response.status_code == 200:
                response_data = post_response.json()
                st.success(f"✅ {response_data.get('message', 'Profile successfully saved!')}")
                time.sleep(1.5)
                # Sayfayı yenile. Sayfa yenilenince en baştaki GET isteği tekrar çalışacak
                # ve az önce veritabanına yazdığımız en güncel veriyi ekrana getirecek!
                st.rerun() 
            else:
                st.error("Backend Error: Failed to save preferences.")
        except requests.exceptions.ConnectionError:
            st.error("🚨 CONNECTION ERROR: Backend is not running.")