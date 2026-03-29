import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import pandas as pd


st.set_page_config(page_title="Smart Kitchen Assistant", layout="wide", page_icon="🍳")

@st.cache_resource
def start_scheduler():
    scheduler = BackgroundScheduler()
    

    def auto_generate_plan():
        print(f"⏰ [SCHEDULED TASK WORKED- {datetime.datetime.now()}] Weekly meal plans and shopping lists are generated automatically...")
    

    scheduler.add_job(auto_generate_plan, 'interval', seconds=10)
    scheduler.start()
    return scheduler


scheduler = start_scheduler()


st.sidebar.title("🍳 Smart Kitchen")
st.sidebar.write("Menu")
selected_page = st.sidebar.radio(
    "Select the page you want to visit:", 
    ["Home", "👤 Profile & Allergies", "📅 Weekly Plan", "🛒 Grocery List"]
)

if selected_page == "Home":
    st.title("Welcome to the Smart Kitchen Assistant! 🥗")
    st.write("Please select a page from the left menu to proceed.")
    st.info("💡 Note: APScheduler is currently running in the background, quietly logging a message to the VS Code terminal every 10 seconds. You can check it out!")

elif selected_page == "👤 Profile & Allergies":
    st.title("User Profile")
    st.write("User dietary preferences and allergies will be collected here.")
    st.write("*(The Smart Filtering Strategy Pattern will be integrated here later)*")

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
    

    st.dataframe(df_plan, use_container_width=True, hide_index=True)
    
    st.divider() 
    

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate Plan", use_container_width=True):
            st.success("Request sent to AI model! Generating a new plan...")
            # İleride burası yapay zeka modelini (Dev 1'in yazdığı kodu) tetikleyecek
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
    
    # Kullanıcı için etkileşimli kontrol listesi (Checklist)
    st.subheader("📝 Your Shopping Checklist")
    for item, qty in to_buy.items():
        st.checkbox(f"Buy {qty}x {item}")

    if st.button("📤 Send to WhatsApp / Mail", use_container_width=True):
        st.success("Message sent! (Integration coming soon)")