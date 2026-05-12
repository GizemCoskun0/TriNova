import streamlit as st
import requests
import json
import re
from auth_utils import require_login

require_login()

USERNAME = st.session_state.username
EMAIL = st.session_state.email

if "ingredient_checks" not in st.session_state:
    st.session_state.ingredient_checks = {}

API_GET_PLAN = f"http://localhost:8000/api/meal-plan/{EMAIL}"
API_GENERATE_PLAN = "http://localhost:8000/api/meal-plan/generate"
API_CHECK_INGREDIENTS = "http://localhost:8000/api/meal-plan/check-ingredients"
API_ADD_MISSING = "http://localhost:8000/api/shopping-list/add-missing"
API_PROFILE = f"http://localhost:8000/api/profile/{USERNAME}"
API_INVENTORY = f"http://localhost:8000/api/inventory/{USERNAME}"
API_FAVORITES = "http://localhost:8000/api/favorites" # <--- EKSİK OLAN LİNK EKLENDİ

# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------

def get_user_favorite_ids():
    try:
        res = requests.get(f"{API_FAVORITES}/{EMAIL}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                # recipe_id'leri garanti olsun diye integer'a çeviriyoruz
                return [int(f["recipe_id"]) for f in data.get("data", [])]
    except:
        pass
    return []

# Her rerun olduğunda listeyi tazeler
user_favorites = get_user_favorite_ids()

def clean_html(text):
    if not text:
        return ""

    clean_text = re.sub("<.*?>", "", text)
    return clean_text.strip()


def parse_ingredients(ingredients_text):
    if not ingredients_text:
        return []

    try:
        data = json.loads(ingredients_text)

        if "ingredients" in data:
            return data.get("ingredients", [])

        used = data.get("usedIngredients", [])
        missed = data.get("missedIngredients", [])

        return used + missed

    except:
        return []


def get_meal_emoji(meal_type):
    if meal_type == "Breakfast":
        return "🍳"
    elif meal_type == "Lunch":
        return "🥗"
    elif meal_type == "Dinner":
        return "🍽️"
    return "🍴"


def fetch_meal_plan():
    try:
        response = requests.get(API_GET_PLAN)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success":
                return data.get("meal_plan", [])

    except requests.exceptions.ConnectionError:
        st.error("🚨 CONNECTION ERROR: Backend is not running.")

    return []


def fetch_profile_summary():
    diet = "None"
    allergies = []

    try:
        response = requests.get(API_PROFILE)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success":
                diet = data.get("diet", "None")
                allergies = data.get("allergies", [])

    except:
        pass

    return diet, allergies


def fetch_inventory_count():
    try:
        response = requests.get(API_INVENTORY)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success":
                return len(data.get("data", []))

    except:
        pass

    return 0


meal_plan = fetch_meal_plan()
if meal_plan:
    meal_plan.sort(key=lambda x: int(x['plan_day'].split()[-1]) if x['plan_day'] and x['plan_day'].split()[-1].isdigit() else 0)
current_diet, current_allergies = fetch_profile_summary()
inventory_count = fetch_inventory_count()

st.title("🍽️ My Meal Plan")
st.write("Create and manage your personalized meal plan based on your diet, allergies, and home inventory.")

st.divider()


st.subheader("📌 Plan Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("User", USERNAME)

with col2:
    st.metric("Diet", current_diet)

with col3:
    allergy_text = str(len(current_allergies))
    st.metric("Allergies", allergy_text)

with col4:
    st.metric("Inventory Items", inventory_count)

if current_allergies:
    st.caption("Allergies: " + ", ".join(current_allergies))
else:
    st.caption("Allergies: None")

st.divider()
# --- Bölüm: Tarif Önerileri ---
st.subheader("⚙️ Meal Plan Actions")

if st.button("🔄 Suggest 10 New Recipes", use_container_width=True):
    with st.spinner("Fetching personalized suggestions..."):
        # Backend'deki generate endpoint'ine istek atıyoruz
        response = requests.post(API_GENERATE_PLAN, json={"username": USERNAME, "email": EMAIL, "days": 3})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                # Gelen 10 tarifi session_state'e kaydediyoruz ki sayfada kalsınlar
                st.session_state.candidate_recipes = data.get("data")
                st.success("✅ 10 new suggestions loaded below!")
            else:
                st.error(data.get("message", "Failed to fetch suggestions."))

st.divider()

# --- Aday Tariflerin Listelenmesi ---
if "candidate_recipes" in st.session_state:
    st.subheader("💡 Suggested Recipes (Add to Your Plan)")
    
    # Döngü burada başlıyor
    for recipe in st.session_state.candidate_recipes:
        with st.expander(f"🍲 {recipe['title']}"):
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                st.image(recipe['image'], use_container_width=True)
                
            with col_info:
                # Seçim kutuları
                target_day = st.selectbox("Select Day", ["Day 1", "Day 2", "Day 3"], key=f"day_{recipe['id']}")
                target_meal = st.selectbox("Select Meal", ["Breakfast", "Lunch", "Dinner"], key=f"meal_{recipe['id']}")
                
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    if st.button(f"➕ Add to Plan", key=f"add_{recipe['id']}", use_container_width=True):
                        raw_instr = recipe.get("instructions")
        
                        # Eğer talimat yoksa veya boş metinse, analyzedInstructions kısmına bakıyoruz
                        if not raw_instr or raw_instr == "":
                            analyzed = recipe.get("analyzedInstructions", [])
                            if analyzed and len(analyzed) > 0:
                                steps = analyzed[0].get("steps", [])
                                # Adımları 1. Step, 2. Step gibi alt alta birleştiriyoruz
                                raw_instr = "\n".join([f"{s['number']}. {s['step']}" for s in steps])
                        
                        # Eğer hala boşsa senin orijinal "No instructions..." yazını yazıyoruz
                        final_instr = raw_instr if raw_instr else "No instructions available."
                        # --- 🚀 ENTEGRE EDİLEN KISIM BİTTİ ---
                        add_payload = {
                            "email": EMAIL,
                            "day": target_day,
                            "meal_type": target_meal,
                            "recipe_id": recipe['id'],
                            "recipe_title": recipe['title'],
                            "recipe_image": recipe['image'],
                            "ready_in_minutes": recipe.get("readyInMinutes") or recipe.get("ready_in_minutes") or 45,
                            "servings": recipe.get("servings") or 4,
                            "instructions": final_instr, # 🚀 BUNU YENİ EKLEDİK
                            "ingredients_json": json.dumps({
                                "ingredients": recipe.get("usedIngredients", []) + recipe.get("missedIngredients", [])
                            })
                        }
                        
              
                        res = requests.post("http://localhost:8000/api/meal-plan/add-single", json=add_payload)
                        if res.status_code == 200:
                            st.toast("✅ Added to Plan!")
                            st.rerun()
 
                
                with btn_col2:
                # 1. Kontrol: Bu tarif şu an favorilerde mi? 
                    is_fav = recipe['id'] in user_favorites
                    
                    # 2. Senin istediğin dinamik metin ve ikon:
                    # Başta "🤍 Add to Favorite", eklenince "❤️ In Favorite"
                    button_label = "❤️ In Favorite" if is_fav else "🤍 Add to Favorite"
                    
                    # 3. Arkadaşının orijinal butonu (Sadece ismi 'button_label' yaptık)
                    if st.button(button_label, key=f"fav_suggest_{recipe['id']}", use_container_width=True):
                        fav_payload = {
                            "email": EMAIL,
                            "recipe_id": recipe['id'],
                            "recipe_title": recipe['title'],
                            "recipe_image": recipe['image']
                        }
                        
                        # Arkadaşının orijinal API adresi ve isteği (Hiçbir şey değişmedi)
                        res = requests.post(API_FAVORITES, json=fav_payload)
                        
                        if res.status_code == 200:
                            st.toast("⭐ Favorites updated!")
                            # Kalbin kırmızıya dönmesi ve yazının değişmesi için sayfayı tazeler
                            st.rerun()


# Döngü bitti, sayfanın geri kalanı
st.divider()
st.subheader("⚙️ Meal Plan Actions")
if meal_plan:
    st.warning("You already have a meal plan. Regenerating will replace the current plan.")
    button_label = "🔄 Regenerate Meal Plan"
else:
    button_label = "✨ Generate Meal Plan"

    payload = {
        "username": USERNAME,
        "email": EMAIL,
        "days": 3
    }

    with st.spinner("Generating your personalized meal plan..."):
        try:
            response = requests.post(API_GENERATE_PLAN, json=payload)

            if response.status_code == 200:
                data = response.json()

                if data.get("status") == "success":
                    st.session_state.ingredient_checks = {}
                    st.success("✅ Your meal plan has been generated successfully!")
                    st.rerun()

                else:
                    st.error(data.get("message", "Failed to generate meal plan."))

            else:
                st.error("Backend Error: Failed to generate meal plan.")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error("🚨 CONNECTION ERROR: Backend is not running.")

st.divider()

st.subheader("📅 Your Current Plan")

if not meal_plan:
    st.info("No meal plan found yet. Click the button above to generate your personalized meal plan.")
    st.stop()

meal_order = ["Breakfast", "Lunch", "Dinner"]

days = []
for item in meal_plan:
    if item.get("plan_day") not in days:
        days.append(item.get("plan_day"))

for day in days:
    st.markdown(f"## {day}")

    day_items = [
        item for item in meal_plan
        if item.get("plan_day") == day
    ]

    day_items = sorted(
        day_items,
        key=lambda x: meal_order.index(x.get("meal_type"))
        if x.get("meal_type") in meal_order else 99
    )

    cols = st.columns(3)

    for index, item in enumerate(day_items):
        meal_plan_id = item.get("id")
        meal_type = item.get("meal_type", "")
        recipe_title = item.get("recipe_title", "")
        meal_emoji = get_meal_emoji(meal_type)

        with cols[index % 3]:

            with st.container(border=True):
                st.markdown(f"### {meal_emoji} {meal_type}")
                st.markdown(f"**{recipe_title}**")

                if item.get("recipe_image"):
                    st.image(item.get("recipe_image"), use_container_width=True)

                recipe_id = item.get("recipe_id")
                is_fav = recipe_id in user_favorites
                heart_icon = "❤️ In Favorites" if is_fav else "🤍 Add to Favorites"

                if st.button(heart_icon, key=f"fav_meal_{meal_plan_id}"):
                    fav_payload = {
                        "email": EMAIL,
                        "recipe_id": recipe_id,
                        "recipe_title": recipe_title,
                        "recipe_image": item.get("recipe_image"),
                        "source_url": item.get("source_url", ""),
                        "ingredients_json": item.get("ingredients", '{"ingredients": []}')
                    }
                    try:
                        res = requests.post(API_FAVORITES, json=fav_payload)
                        if res.status_code == 200:
                            st.rerun()
                    except Exception:
                        st.toast("Error: Backend could not be reached..")
                # -----------------------------

                # --- DÜZELTİLEN KISIM: Dakika ve Porsiyon ---
                # Hem veritabanı formatını (ready_in_minutes) hem de Spoonacular formatını (readyInMinutes) yakalar.
                # Eğer Backend'den boş (None) gelirse, ekranda çirkin bir "None" yazması yerine "N/A" veya varsayılan değer yazar.
                
                ready_time = item.get("ready_in_minutes") or item.get("readyInMinutes") or "45"
                servings = item.get("servings") or "4"

                st.caption(f"⏱️ {ready_time} min | 🍽️ {servings} servings")
                # ---------------------------------------------
 

                with st.expander("View Details"):
                    st.markdown("#### 🧂 Ingredients")

                    ingredients = parse_ingredients(item.get("ingredients"))

                    if ingredients:
                        for ingredient in ingredients:
                            name = ingredient.get("name", "Unknown ingredient")
                            amount = ingredient.get("amount", "")
                            unit = ingredient.get("unit", "")

                            st.write(f"- {name} {amount} {unit}")
                    else:
                        st.info("Ingredients are not available for this recipe.")

                    st.markdown("#### 👩‍🍳 Instructions")

                    instructions = item.get("instructions")

                    if instructions:
                        st.write(clean_html(instructions))
                    else:
                        st.info("Instructions will be available soon.")

                    if item.get("source_url"):
                        st.link_button("View Full Recipe", item.get("source_url"))

                    st.divider()

                    if st.button(
                        "🔍 Check Ingredients",
                        key=f"check_{meal_plan_id}",
                        use_container_width=True
                    ):
                        payload = {
                            "meal_plan_id": meal_plan_id,
                            "email": EMAIL
                        }

                        with st.spinner("Checking your inventory..."):
                            try:
                                check_response = requests.post(
                                    API_CHECK_INGREDIENTS,
                                    json=payload
                                )

                                if check_response.status_code == 200:
                                    check_data = check_response.json()

                                    if check_data.get("status") == "success":
                                        st.session_state.ingredient_checks[str(meal_plan_id)] = check_data
                                        st.success("✅ Ingredient check completed!")
                                        st.rerun()

                                    else:
                                        st.error(check_data.get("message", "Ingredient check failed."))

                                else:
                                    st.error("Backend Error: Failed to check ingredients.")
                                    st.write(check_response.text)

                            except requests.exceptions.ConnectionError:
                                st.error("🚨 CONNECTION ERROR: Backend is not running.")


                    check_result = st.session_state.ingredient_checks.get(str(meal_plan_id))

                    if check_result:
                        st.divider()
                        st.markdown("#### 🧾 Ingredient Check Result")

                        available_items = check_result.get("available_items", [])
                        missing_items = check_result.get("missing_items", [])

                        if available_items:
                            st.markdown("**🏠 Available at Home**")
                            for available in available_items:
                                name = available.get("name", "")
                                required_amount = available.get("required_amount", "")
                                home_amount = available.get("home_amount", "")
                                unit = available.get("unit", "")

                                st.success(
                                    f"{name} - Required: {required_amount} {unit}, "
                                    f"At home: {home_amount} {unit}"
                                )
                        else:
                            st.info("No matching ingredients found at home.")

                        if missing_items:
                            st.markdown("**🛒 Missing Ingredients**")
                            for missing in missing_items:
                                name = missing.get("name", "")
                                amount = missing.get("amount", "")
                                unit = missing.get("unit", "")

                                st.error(f"{name}: {amount} {unit}")

                            if st.button(
                                "➕ Add Missing Items to Shopping List",
                                key=f"add_missing_{meal_plan_id}",
                                use_container_width=True
                            ):
                                payload = {
                                    "meal_plan_id": meal_plan_id,
                                    "email": EMAIL
                                }

                                with st.spinner("Adding missing items to shopping list..."):
                                    try:
                                        add_response = requests.post(
                                            API_ADD_MISSING,
                                            json=payload
                                        )

                                        if add_response.status_code == 200:
                                            add_data = add_response.json()

                                            if add_data.get("status") == "success":
                                                st.success("✅ Missing items added to your shopping list.")
                                                st.info("You can view them on the Grocery List page.")
                                            else:
                                                st.error(add_data.get("message", "Failed to add missing items."))

                                        else:
                                            st.error("Backend Error: Failed to add missing items.")
                                            st.write(add_response.text)

                                    except requests.exceptions.ConnectionError:
                                        st.error("🚨 CONNECTION ERROR: Backend is not running.")
                        else:
                            st.success("You have all ingredients for this recipe!")

    st.divider()

if st.button("📥 Export to PDF", use_container_width=True):
    st.info("PDF export feature will be available soon.")