import streamlit as st
import requests

# --- 1. GÜVENLİK VE OTURUM KONTROLÜ (Diğer sayfalarındaki gibi) ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🚨 Please login from the main page first!")
    st.stop()

if "username" not in st.session_state or st.session_state.username == "":
    st.error("Username information is missing. Please logout and login again.")
    st.stop()

# --- 2. KULLANICI ADINI OTURUMDAN KESİN OLARAK ALIYORUZ ---
USERNAME = st.session_state.username
API_URL = "http://localhost:8000/api/inventory"

st.title("📸 Smart Kitchen Inventory")
st.write("Manage your ingredients using AI camera or manual entry. (Connected to Database 🚀)")
st.divider()

st.sidebar.subheader("👤 Active User")
# Sadece bilgi amaçlı gösteriyoruz. Kutuyu kilitledik (disabled=True). 
# Giriş yapan "Beyza" ise hep Beyza kalacak!
st.sidebar.text_input("Username", value=USERNAME, disabled=True)

# --- FONKSİYONLAR ---
def fetch_inventory():
    try:
        response = requests.get(f"{API_URL}/{USERNAME}")
        if response.status_code == 200 and response.json()["status"] == "success":
            return response.json()["data"]
    except Exception:
        st.error("Backend connection error! Is Uvicorn working?")
    return []

def add_item(item_name, amount=1.0):
    if not USERNAME:
        return {"status": "error", "message": "Please enter a username first!"}

    payload = {"username": USERNAME, "item_name": item_name, "amount": float(amount), "unit": "unit"}
    try:
        response = requests.post(API_URL, json=payload)
        return response.json()
    except Exception:
        st.error("Backend connection error! Is Uvicorn working?")
        return {"status": "error", "message": "Backend connection error!"}

def delete_item(item_id):
    try:
        response = requests.delete(f"{API_URL}/{item_id}")
        return response.json()
    except Exception:
        st.error("Backend connection error! Is Uvicorn working?")
        return {"status": "error", "message": "Backend connection error!"}

# --- ARAYÜZ (UI) ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 AI Scanner & Uploader")
    st.info("Show your ingredients to the camera or upload a photo to detect them automatically.")
    
    tab1, tab2 = st.tabs(["📸 Camera", "📂 Upload Image"])
    
    with tab1:
        camera_picture = st.camera_input("Take a photo of your fridge or counter")
    
    with tab2:
        uploaded_picture = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])

    picture = camera_picture if camera_picture else uploaded_picture

    if picture:
        st.image(picture, caption="Selected Image", use_container_width=True)
        if st.button("🔍 Analyze with AI"):
            with st.spinner("AI is identifying ingredients..."):
                detected_items = ["Tomato", "Cheese"] 
                for item in detected_items:
                    res = add_item(item)
                    if res.get("status") == "success":
                        st.success(f"✅ '{item}' added!")
                    else:
                        st.warning(f"⚠️ {res.get('message')}")
            st.rerun() 

with col2:
    st.subheader("✍️ Manual Add & Current Stock")

    input_col1, input_col2 = st.columns([3, 1])
    with input_col1:
        new_item = st.text_input("Ingredient:", placeholder="e.g., Asparagus, Milk")
    with input_col2:
        item_amount = st.number_input("Qty", min_value=0.1, value=1.0, step=1.0)

    if st.button("➕ Add to My Kitchen", use_container_width=True):
        if new_item:
            clean_name = new_item.strip().capitalize()
            res = add_item(clean_name, amount=item_amount)
            if res.get("status") == "success":
                st.toast(f"{item_amount} {clean_name} added to database!")
                st.rerun()
            else:
                st.error(res.get("message"))
                
    st.divider()

    st.write("### 🧺 Items in Your Kitchen:")
    
    inventory_items = fetch_inventory()
    
    if not inventory_items:
        st.write("Your kitchen is empty. Start adding some items!")
    else:
        for item in inventory_items:
            c1, c2 = st.columns([4, 1])
            c1.write(f"🧀 **{item['name']}** ({item['amount']} {item['unit']})")

            if c2.button("🗑️", key=f"del_{item['id']}"):
                delete_item(item['id'])
                st.rerun()
st.divider()
if st.button("🚀 Go to Weekly Plan to Generate", use_container_width=True):
    st.switch_page("pages/2_Weekly_Plan.py")