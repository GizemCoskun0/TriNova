import streamlit as st
import requests
import json  
from auth_utils import require_login

require_login()

USERNAME = st.session_state.username
EMAIL = st.session_state.email

# --- API URL'LERİ ---
API_URL = "http://localhost:8000/api/inventory"
API_ANALYZE_URL = "http://localhost:8000/api/analyze-image"
API_FAVORITES = "http://localhost:8000/api/favorites"              
API_ADD_SINGLE = "http://localhost:8000/api/meal-plan/add-single"  

st.title("📸 Smart Kitchen Inventory")
st.write("Manage your ingredients using AI camera or manual entry. (Connected to Database 🚀)")
st.divider()

st.sidebar.subheader("👤 Active User")

if "username" in st.session_state:
    USERNAME = st.session_state["username"]
    st.sidebar.success(f"Logged in as: {USERNAME}")
else:
    USERNAME = st.sidebar.text_input("Username", value="merve_gunes") 

# --- SESSION STATE TANIMLAMALARI (UI KAYBOLMAMASI İÇİN) ---
if "show_recipes" not in st.session_state:
    st.session_state.show_recipes = False
if "fetched_recipes" not in st.session_state:
    st.session_state.fetched_recipes = []

def get_user_favorite_ids():
    try:
        res = requests.get(f"{API_FAVORITES}/{EMAIL}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                return [f["recipe_id"] for f in data.get("data", [])]
            
    except:
        pass
    return []

user_favorites = get_user_favorite_ids()    

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
        return {"status": "error", "message": "Backend connection error!"}

def update_shopping_list_after_inventory_add():
    pass

def delete_item(item_id):
    try:
        response = requests.delete(f"{API_URL}/{item_id}")
        return response.json()
    except Exception:
        return {"status": "error", "message": "Backend connection error!"}

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

    if 'ai_analyzed' not in st.session_state:
        st.session_state.ai_analyzed = False
    if 'detected_items_list' not in st.session_state:
        st.session_state.detected_items_list = []

    if picture:
        st.image(picture, caption="Selected Image", use_container_width=True)
        if st.button("🔍 Analyze with AI"):
            with st.spinner("AI is analyzing the image..."):
                
                try:
                    files = {"file": ("image.jpg", picture.getvalue(), "image/jpeg")}
                    response = requests.post(API_ANALYZE_URL, files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "success":
                            detected_items = data.get("detected_items", [])
                            
                            st.session_state.detected_items_list = detected_items
                            
                            if not detected_items:
                                st.warning("🤷 AI couldn't detect any ingredients in this image.")
                            else:
                                for item in detected_items:
                                    res = add_item(item.capitalize())
                                    if res.get("status") != "success":
                                        st.error(f"⚠️ Error adding {item}: {res.get('message')}")
                                update_shopping_list_after_inventory_add()
                            
                            st.session_state.ai_analyzed = True
                        else:
                            st.error(f"AI Error: {data.get('message')}")
                    else:
                        st.error("Failed to reach the AI server. Is Uvicorn running?")
                except Exception as e:
                    st.error(f"Connection error: {e}")
                
            st.rerun() 
        
        if st.session_state.ai_analyzed:
             st.success("✨ Analysis complete!")
             
             found_items = st.session_state.detected_items_list
             if found_items:
                 items_str = ", ".join([item.capitalize() for item in found_items])
                 st.info(f"🔍 **Detected:** {items_str}\n\nWould you like to add anything else manually from the right side before generating your meal plan?")
             else:
                 st.info("No items were detected. You can add them manually from the right side.")

with col2:
    st.subheader("✍️ Manual Add & Current Stock")

    if "new_ingredient_name" not in st.session_state:
        st.session_state.new_ingredient_name = ""
    if "new_ingredient_qty" not in st.session_state:
        st.session_state.new_ingredient_qty = 1.0

    def handle_add_item():
        item_name = st.session_state.new_ingredient_name
        item_qty = st.session_state.new_ingredient_qty
        
        if item_name:
            clean_name = item_name.strip().capitalize()
            res = add_item(clean_name, amount=item_qty)
            if res.get("status") == "success":
                st.toast(f"{item_qty} {clean_name} added to database!")
            
                st.session_state.new_ingredient_name = ""
                st.session_state.new_ingredient_qty = 1.0
                
                update_shopping_list_after_inventory_add()
            else:
                st.error(res.get("message"))

    input_col1, input_col2 = st.columns([3, 1])
    with input_col1:
        st.text_input("Ingredient:", placeholder="e.g., Asparagus, Milk", key="new_ingredient_name")
    with input_col2:
        st.number_input("Qty", min_value=0.1, step=1.0, key="new_ingredient_qty")

    st.button("➕ Add to My Kitchen", use_container_width=True, on_click=handle_add_item)
                
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
# --- SADECE API İSTEĞİNİ YAPAN BUTON ---
if st.button("🍳 Get Recipes with These Ingredients", use_container_width=True):
    inventory_items = fetch_inventory()
    
    if not inventory_items:
        st.warning("Your kitchen is empty! Add some ingredients first.")
        st.session_state.show_recipes = False
    else:
        with st.spinner("Finding delicious recipes for you..."):
            ingredients_list = [item['name'] for item in inventory_items]
            ingredients_str = ",".join(ingredients_list)
            
            try:
                RECIPES_API_URL = "http://localhost:8000/api/recipes"
                aktif_kullanici = st.session_state.get("username")

                response = requests.get(RECIPES_API_URL, params={
                "ingredients": ingredients_str, 
                "username": aktif_kullanici,
                "number": 5   # <-- Smart Inventory için tam 5 tarif istiyoruz
                    })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        st.session_state.fetched_recipes = data.get("data", [])
                        st.session_state.show_recipes = True # Tarifleri göstermek için tetikleyiciyi açtık
                    else:
                        st.error(f"API Error: {data.get('message')}")
                else:
                    st.error("Failed to fetch recipes from the backend.")
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- 2. TARİFLERİ SESSION STATE'TEN OKUYUP ÇİZEN KISIM ---
# --- 2. TARİFLERİ SESSION STATE'TEN OKUYUP ÇİZEN KISIM ---
if st.session_state.show_recipes:
    recipes = st.session_state.fetched_recipes
    
    if recipes:
        st.success("✨ Here are some recipes you can make right now!")
        
        for recipe in recipes:
            with st.expander(f"🍲 {recipe['title']}"):
                col_img, col_info = st.columns([1, 2])
                
                with col_img:
                    st.image(recipe['image'], use_container_width=True)

                    # --- SENİN İSTEDİĞİN DİNAMİK FAVORİ BUTONU ---
                    # 1. Kontrol: Bu tarif şu an favorilerde mi? (ID eşleşmesi için int kullanıyoruz)
                    is_fav = int(recipe['id']) in user_favorites
                    
                    # 2. Buton Yazısı: Favorideyse kırmızı, değilse beyaz kalp
                    button_label = "❤️ In Favorite" if is_fav else "🤍 Add to Favorite"

                    # 3. Buton ve İstek
                    if st.button(button_label, key=f"fav_btn_{recipe['id']}", use_container_width=True):
                        all_ingredients = recipe.get("usedIngredients", []) + recipe.get("missedIngredients", [])
                        ingredients_data = {"ingredients": all_ingredients}
                        
                        payload = {
                            "email": EMAIL,
                            "recipe_id": recipe['id'],
                            "recipe_title": recipe['title'],
                            "recipe_image": recipe['image'],
                            "source_url": recipe.get('sourceUrl', ''),
                            "ingredients_json": json.dumps(ingredients_data) 
                        }
                        
                        # Arkadaşının orijinal toggle/add API mantığı
                        res = requests.post(API_FAVORITES, json=payload)
                        if res.status_code == 200:
                            # Sayfayı yenile ki kalp kırmızıya dönsün
                            st.rerun() 
                            
                with col_info:
                    st.write(f"**Used Ingredients:** {recipe['usedIngredientCount']}")
                    st.write(f"**Missing Ingredients:** {recipe['missedIngredientCount']}")
                    
                    if recipe['missedIngredientCount'] > 0:
                        missed = [m['name'] for m in recipe['missedIngredients']]
                        st.warning(f"*(You still need: {', '.join(missed)})*")
                        
                    st.divider()
                    
                
                plan_state_key = f"inv_plan_info_{recipe['id']}"



                if plan_state_key in st.session_state:
                    missing_items = st.session_state[plan_state_key]["missing_items"]
                    meal_plan_id = st.session_state[plan_state_key]["meal_plan_id"]
                    
                    if missing_items:
                        st.warning(f"⚠️ You are missing {len(missing_items)} ingredients:")
                        for m in missing_items:
                            st.write(f"- {m['name']} ({m['amount']} {m['unit']})")
                            
                        API_ADD_MISSING = "http://localhost:8000/api/shopping-list/add-missing"
                        if st.button("🛒 Add Missing Items to Grocery List", key=f"inv_cart_{recipe['id']}", use_container_width=True):
                            missing_payload = {"meal_plan_id": meal_plan_id, "email": EMAIL}
                            m_res = requests.post(API_ADD_MISSING, json=missing_payload)
                            if m_res.status_code == 200:
                                st.success("✅ Items added to Grocery List!")
                                del st.session_state[plan_state_key]
                                st.rerun()
                    else:
                        st.success("🎉 You have all the ingredients at home!")
            # --------------------------------------

    else:
        st.warning("No recipes found with these specific ingredients.")