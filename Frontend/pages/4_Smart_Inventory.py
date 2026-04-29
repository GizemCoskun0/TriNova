import streamlit as st
import requests

st.title("📸 Smart Kitchen Inventory")
st.write("Manage your ingredients using AI camera or manual entry. (Connected to Database 🚀)")
st.divider()

st.sidebar.subheader("👤 Active User")
USERNAME = st.sidebar.text_input("Username", value="beyza_dev")
API_URL = "http://localhost:8000/api/inventory"


def fetch_inventory():
    try:
        response = requests.get(f"{API_URL}/{USERNAME}")
        if response.status_code == 200 and response.json()["status"] == "success":
            return response.json()["data"]
    except Exception:
        st.error("Backend connection error! Is Uvicorn working?")
    return []

def add_item(item_name):
    payload = {"username": USERNAME, "item_name": item_name, "amount": 1.0, "unit": "unit"}
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


col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 AI Scanner & Uploader")
    st.info("Show your ingredients to the camera or upload a photo to detect them automatically.")
    
    # --- YENİ EKLENEN KISIM: Kamera ve Dosya Yükleme Sekmeleri ---
    tab1, tab2 = st.tabs(["📸 Camera", "📂 Upload Image"])
    
    with tab1:
        camera_picture = st.camera_input("Take a photo of your fridge or counter")
    
    with tab2:
        uploaded_picture = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])

    # Kullanıcı kamerayı mı kullandı yoksa dosya mı yükledi kontrolü
    picture = camera_picture if camera_picture else uploaded_picture
    # -------------------------------------------------------------

    if picture:
        st.image(picture, caption="Selected Image", use_container_width=True)
        if st.button("🔍 Analyze with AI"):
            with st.spinner("AI is identifying ingredients..."):
                
                # Burası şimdilik test listesi, bir sonraki adımda yapay zekadan gelecek!
                detected_items = ["Tomato", "Cheese"] 
                for item in detected_items:
                    res = add_item(item)
                    if res.get("status") == "success":
                        st.success(f"✅ '{item}' eklendi!")
                    else:
                        st.warning(f"⚠️ {res.get('message')}")
            st.rerun() 

with col2:
    st.subheader("✍️ Manual Add & Current Stock")
    
    new_item = st.text_input("Search or type an ingredient:", placeholder="e.g., Milk, Flour")
    if st.button("➕ Add to My Kitchen"):
        if new_item:
            res = add_item(new_item.capitalize())
            if res.get("status") == "success":
                st.toast(f"{new_item} added to database!")
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
            c1.write(f"🧀 **{item['name']}**")

            if c2.button("🗑️", key=f"del_{item['id']}"):
                delete_item(item['id'])
                st.rerun()

st.divider()
if st.button("🚀 Generate Meal Plan with These Ingredients", use_container_width=True):
    st.success("All data is stored in the database! Now a plan can be created.")