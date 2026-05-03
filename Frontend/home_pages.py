import streamlit as st

from auth_utils import set_login_cookie, clear_login_cookie
from user_db import register_user, check_login
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

    top_col1, top_col2 = st.columns([3, 1])

    with top_col1:
        st.markdown("## 🍽️ Smart Kitchen Assistant")

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

    st.markdown(f"""
        <div class="hero-box">
            <div class="hero-title">👋 Welcome back, {st.session_state.username}</div>
            <div class="hero-subtitle">
                Ready to make your kitchen smarter today?<br>
                Smart Kitchen Assistant helps you organize your kitchen,
                plan your meals, and manage your grocery needs more easily.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">How it works?</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class="step-card">
                <div class="step-number">1</div>
                <div class="step-title">Save your preferences</div>
                <div class="step-text">
                    Add your diet type and allergy information from the Profile & Allergies page.
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="step-card">
                <div class="step-number">2</div>
                <div class="step-title">Add your inventory</div>
                <div class="step-text">
                    Enter the ingredients you currently have at home to help the system make better suggestions.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-title">Generate your meal plan</div>
                <div class="step-text">
                    Create a personalized meal plan based on your preferences and available ingredients.
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="step-card">
                <div class="step-number">4</div>
                <div class="step-title">Check your grocery list</div>
                <div class="step-text">
                    See which ingredients you need to buy before shopping and stay organized.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="tip-box">
            <div class="tip-title">💡 Tip of the day</div>
            <div class="tip-text">
                Keeping your inventory updated helps the system suggest better recipes
                and create a more accurate grocery list.
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        logout()