import streamlit as st

from auth_utils import set_login_cookie, clear_login_cookie
from user_db import register_user, check_login, get_dashboard_data
from home_styles import hide_sidebar, load_home_css, load_landing_css


def logout():
    st.session_state.manual_logout = True
    st.session_state.auth_view = "landing"

    clear_login_cookie()

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.auth_restore_attempts = 0

    st.rerun()


def show_landing_page():
    hide_sidebar()
    load_landing_css()

    top_col1, top_col2 = st.columns([4, 1])

    with top_col1:
        st.markdown("""
        <div style="
            font-size: 26px;
            font-weight: 800;
            color: white;
            text-shadow: 0 2px 8px rgba(0,0,0,0.35);
            margin-bottom: 20px;
        ">
            🍽️ Smart Kitchen Assistant
        </div>
    """, unsafe_allow_html=True)

    with top_col2:
        if st.button("Login / Register", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()

    st.markdown("""
        <div class="landing-hero">
            <div class="landing-title">Plan smarter. Shop easier.</div>
            <div class="landing-subtitle">
                Smart Kitchen Assistant helps you organize your kitchen,
                create personalized meal plans, and prepare grocery lists based on your ingredients.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-title">🥗 Personalized Meal Plans</div>
                <div class="feature-text">
                    Generate meal plans based on your diet, allergies, and available ingredients.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-title">🏠 Inventory Tracking</div>
                <div class="feature-text">
                    Keep track of the ingredients you already have at home.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-title">🛒 Smart Grocery List</div>
                <div class="feature-text">
                    See what you need to buy based on your meal plan and inventory.
                </div>
            </div>
        """, unsafe_allow_html=True)


def show_login_page():
    hide_sidebar()

    if st.button("← Back to Home"):
        st.session_state.auth_view = "landing"
        st.rerun()

    st.title("🔐 Smart Kitchen Assistant")
    st.write("Login or create an account to continue.")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Registered User Login")

        with st.form("login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            remember_me = st.checkbox("Remember me", value=True)

            login_submitted = st.form_submit_button("Login", use_container_width=True)

        if login_submitted:
            if login_email == "" or login_password == "":
                st.warning("Please enter your email and password.")
            else:
                user = check_login(login_email, login_password)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.email = user[2]
                    st.session_state.manual_logout = False

                    if remember_me:
                        set_login_cookie(user[2])
                    else:
                        clear_login_cookie()

                    st.success("Login successful! Loading...")
                    st.rerun()
                else:
                    st.error("Invalid email or password!")

    with tab2:
        st.subheader("Create New Account")

        with st.form("register_form"):
            register_username = st.text_input("Username", key="register_username")
            register_email = st.text_input("Email", key="register_email")
            register_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

            register_submitted = st.form_submit_button("Register", use_container_width=True)

        if register_submitted:
            if register_username == "" or register_email == "" or register_password == "" or confirm_password == "":
                st.warning("Please fill in all fields.")
            elif "@" not in register_email:
                st.warning("Please enter a valid email address.")
            elif register_password != confirm_password:
                st.error("Passwords do not match!")
            elif len(register_password) < 4:
                st.warning("Password must be at least 4 characters.")
            else:
                result = register_user(register_username, register_email, register_password)

                if result:
                    st.success("Registration successful! You can now login.")
                else:
                    st.error("This username or email is already registered.")

def show_home_page():
    load_home_css()

    dashboard_data = get_dashboard_data(st.session_state.email)

    if not dashboard_data:
        st.error("Dashboard data could not be loaded.")
        return

    inventory_count = dashboard_data["inventory_count"]
    shopping_count = dashboard_data["shopping_count"]
    meal_plan_count = dashboard_data["meal_plan_count"]
    diet = dashboard_data["diet"]
    allergy_count = dashboard_data["allergy_count"]

    st.markdown(f"""
        <div class="hero-box">
            <div class="hero-title">👋 Welcome back, {st.session_state.username}</div>
            <div class="hero-subtitle">
                Here is your kitchen overview for today.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🏠 Kitchen Dashboard</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-icon">🍽️</div>
                <div class="dashboard-title">Meal Plan</div>
                <div class="dashboard-value">{meal_plan_count}</div>
                <div class="step-text">saved meal items</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-icon">🏠</div>
                <div class="dashboard-title">Inventory</div>
                <div class="dashboard-value">{inventory_count}</div>
                <div class="step-text">ingredients at home</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-icon">🛒</div>
                <div class="dashboard-title">Grocery List</div>
                <div class="dashboard-value">{shopping_count}</div>
                <div class="step-text">items to buy</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">📌 Profile Status</div>',
        unsafe_allow_html=True
    )

    col4, col5 = st.columns(2)

    with col4:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-icon">🥗</div>
                <div class="dashboard-title">Diet Preference</div>
                <div class="dashboard-value" style="font-size:24px;">{diet}</div>
                <div class="step-text">used for meal suggestions</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
            <div class="dashboard-card">
                <div class="dashboard-icon">⚠️</div>
                <div class="dashboard-title">Allergies</div>
                <div class="dashboard-value">{allergy_count}</div>
                <div class="step-text">saved allergy records</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="smart-box">
            <div class="tip-title">💡 Smart Suggestion</div>
            <div class="tip-text">
                Keep your inventory updated before generating a new meal plan.
                This helps the system suggest better recipes and create a more accurate grocery list.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
