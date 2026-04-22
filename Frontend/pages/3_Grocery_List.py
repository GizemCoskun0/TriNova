import streamlit as st

st.title("🛒 Automatic Grocery List")
st.write("Here is your smart shopping list. We''ve subtracted the items you already have at home!")

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
