import streamlit as st

st.title("📸 Smart Kitchen Inventory")
st.write("Manage your ingredients using AI camera or manual entry.")
st.divider()

# --- SESSION STATE ---
# Sayfa yenilense de malzemelerin silinmemesi için bir liste oluşturuyoruz
if "my_ingredients" not in st.session_state:
    st.session_state.my_ingredients = []

# Ekranı iki ana sütuna bölüyoruz
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 AI Camera Scanner")
    st.info("Show your ingredients to the camera to detect them automatically.")
    
    # Streamlit''in hazır kamera bileşeni
    picture = st.camera_input("Take a photo of your fridge or counter")

    if picture:
        st.image(picture, caption="Captured Image", use_container_width=True)
        if st.button("🔍 Analyze with AI"):
            with st.spinner("AI is identifying ingredients..."):
                # BURASI: Dev 1 (AI''cı) arkadaşının YOLO fonksiyonunu çağıracağımız yer.
                # Şimdilik örnek bir sonuç ekleyelim:
                detected_items = ["Tomato", "Cheese"] 
                for item in detected_items:
                    if item not in st.session_state.my_ingredients:
                        st.session_state.my_ingredients.append(item)
                st.success(f"Detected: {', '.join(detected_items)}")

with col2:
    st.subheader("✍️ Manual Add & Current Stock")
    
    # Manuel Ürün Ekleme Alanı
    new_item = st.text_input("Search or type an ingredient (e.g., Milk, Flour):", placeholder="Enter item name...")
    if st.button("➕ Add to My Kitchen"):
        if new_item:
            if new_item.capitalize() not in st.session_state.my_ingredients:
                st.session_state.my_ingredients.append(new_item.capitalize())
                st.toast(f"{new_item} added!")
            else:
                st.warning("This item is already in your list.")

    st.divider()

    # Mevcut Malzemelerin Listesi
    st.write("### 🧺 Items in Your Kitchen:")
    if not st.session_state.my_ingredients:
        st.write("Your kitchen is empty. Start adding some items!")
    else:
        # Malzemeleri şık bir liste veya etiket (tag) olarak gösterelim
        for i, item in enumerate(st.session_state.my_ingredients):
            c1, c2 = st.columns([4, 1])
            c1.write(f"✅ {item}")
            if c2.button("🗑️", key=f"del_{i}"):
                st.session_state.my_ingredients.pop(i)
                st.rerun() # Listeyi güncellemek için sayfayı yenile

st.divider()
if st.button("🚀 Generate Meal Plan with These Ingredients", use_container_width=True):
    st.switch_page("📅 Weekly Plan") # Kullanıcıyı direkt planlama sayfasına yönlendir
