import streamlit as st

# 1. Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# 2. If NOT logged in, show login page and HIDE sidebar
if not st.session_state.logged_in:
    # CSS trick to completely hide the sidebar and its toggle button
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {display: none;}
            [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    st.title("🔐 Login to Smart Kitchen Assistant")
    
    input_username = st.text_input("Username") 
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        # We will connect this to the real database later!
        if input_username == "admin" and password == "1234": 
            st.session_state.logged_in = True
            st.session_state.username = input_username 
            st.success("Login successful! Loading...")
            st.rerun() 
        else:
            st.error("Invalid username or password!")
            
    # Stop reading the rest of the code if not logged in
    st.stop() 

# --- THE CODE BELOW ONLY RUNS AFTER A SUCCESSFUL LOGIN ---

# Since the user is logged in, the CSS above won't run, and the sidebar will magically appear!
st.title("👋 Welcome, " + st.session_state.username)
st.write("You can access the Smart Inventory and other menus from the left-hand sidebar.")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()