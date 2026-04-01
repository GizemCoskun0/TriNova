import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import pandas as pd
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.database import SessionLocal
from Backend.models import User, Allergy, Diet
from Backend.api_process import AsyncRecipeAPI


st.set_page_config(page_title="Smart Kitchen Assistant", layout="wide", page_icon="🍳")

@st.cache_resource
def start_scheduler():
    scheduler = BackgroundScheduler()
    

    def auto_generate_plan():
        print(f"⏰ [SCHEDULED TASK WORKED- {datetime.datetime.now()}] Weekly meal plans and shopping lists are generated automatically...")
    

    scheduler.add_job(auto_generate_plan, 'interval', seconds=100)
    scheduler.start()
    return scheduler


scheduler = start_scheduler()


st.sidebar.title("🍳 Smart Kitchen")
st.sidebar.write("Menu")
selected_page = st.sidebar.radio(
    "Select the page you want to visit:", 
    ["Home","Smart Inventory","👤 Profile & Allergies", "📅 Weekly Plan", "🛒 Grocery List"]
)

if selected_page == "Home":
    st.title("Welcome to the Smart Kitchen Assistant! 🥗")
    st.write("Please select a page from the left menu to proceed.")
    st.info("💡 Note: APScheduler is currently running in the background, quietly logging a message to the VS Code terminal every 10 seconds. You can check it out!")

elif selected_page == "👤 Profile & Allergies":
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
        # giriş ekranı gelince oradaki kullanıcı ID'sine göre güncelleyeceğiz.
        st.success(f"Saved! Diet: {diet}, Allergies: {', '.join(allergies) if allergies else 'None'}")

elif selected_page == "📅 Weekly Plan":
    st.title("📅 Weekly Meal Plan")
    st.write("Here is your 7-day meal plan based on your dietary preferences and home inventory.")
    

    weekly_data = {
        "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "Breakfast": ["Oatmeal & Berries", "Scrambled Eggs", "Avocado Toast", "Pancakes", "Smoothie Bowl", "Omelette", "French Toast"],
        "Lunch": ["Chicken Salad", "Lentil Soup", "Quinoa Bowl", "Turkey Wrap", "Pasta Salad", "Grilled Cheese", "Beef Stew"],
        "Dinner": ["Grilled Salmon", "Spaghetti Bolognese", "Vegetable Stir-fry", "Roast Chicken", "Tacos", "Pizza", "Steak & Mash"]
    }
    

    df_plan = pd.DataFrame(weekly_data)
    

    df_plan = pd.DataFrame(weekly_data)
    st.dataframe(df_plan, use_container_width=True, hide_index=True)
    st.divider()
    st.subheader("🌐 Live Backend Connection Test")
    st.write("Let's ask the Spoonacular API for real recipes based on some test ingredients!")
    
    if st.button("Fetch Real Recipes via API", use_container_width=True):
        test_ingredients = ["tomato", "cheese", "garlic"] # Şimdilik test için
        
        with st.spinner("Connecting to Spoonacular API asynchronously..."):
            # Streamlit senkron çalışır, asenkron API'yi çalıştırmak için asyncio.run kullanıyoruz
            recipes = asyncio.run(AsyncRecipeAPI.search_by_ingredients(test_ingredients))
            
            if recipes:
                st.success("✅ Successfully fetched data from API!")
                for recipe in recipes:
                    st.info(f"🍲 **{recipe['title']}** (Missing Ingredients: {recipe['missedIngredientCount']})")
            else:
                st.error("No recipes found. Make sure your .env file has a valid SPOONACULAR_API_KEY!")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate Plan", use_container_width=True):
            st.success("Request sent to AI model! Generating a new plan...")
    with col2:
        if st.button("📥 Export to PDF", use_container_width=True):
            st.info("PDF export feature will be available soon.")
elif selected_page == "🛒 Grocery List":
    st.title("🛒 Automatic Grocery List")
    st.write("Here is your smart shopping list. We've subtracted the items you already have at home!")

    required_items = {"Tomatoes": 6, "Pasta (packs)": 2, "Milk (L)": 2, "Eggs": 12, "Chicken (kg)": 1.5}

    home_items = {"Tomatoes": 2, "Milk (L)": 1, "Eggs": 6, "Apples": 4}

    to_buy = {}
    for item, needed_qty in required_items.items():
        home_qty = home_items.get(item, 0) # Evde yoksa 0 say
        if needed_qty > home_qty:
            to_buy[item] = needed_qty - home_qty

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Currently at Home (AI Detected)")
        for item, qty in home_items.items():
            st.info(f"✅ {item}: {qty}")

    with col2:
        st.subheader("🛒 Missing (To Buy)")
        if not to_buy:
            st.success("You have everything you need for the week! 🎉")
        else:
            for item, qty in to_buy.items():
                st.error(f"➖ {item}: {qty}")

    st.divider()
    
    st.subheader("📝 Your Shopping Checklist")
    for item, qty in to_buy.items():
        st.checkbox(f"Buy {qty}x {item}")

    if st.button("📤 Send to WhatsApp / Mail", use_container_width=True):
        st.success("Message sent! (Integration coming soon)")

elif selected_page == "Smart Inventory":
    st.title("📸 Smart Kitchen Inventory")
    st.write("Manage your ingredients using AI camera or manual entry.")
    st.divider()

    # --- SESSION STATE (HAFIZA) AYARI ---
    # Sayfa yenilense de malzemelerin silinmemesi için bir liste oluşturuyoruz
    if "my_ingredients" not in st.session_state:
        st.session_state.my_ingredients = []

    # Ekranı iki ana sütuna bölüyoruz
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🤖 AI Camera Scanner")
        st.info("Show your ingredients to the camera to detect them automatically.")
        
        # Streamlit'in hazır kamera bileşeni
        picture = st.camera_input("Take a photo of your fridge or counter")

        if picture:
            st.image(picture, caption="Captured Image", use_container_width=True)
            if st.button("🔍 Analyze with AI"):
                with st.spinner("AI is identifying ingredients..."):
                    # BURASI: Dev 1 (AI'cı) arkadaşının YOLO fonksiyonunu çağıracağımız yer.
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