import streamlit as st
import sqlite3
from pathlib import Path

from auth_utils import (
    init_session_state,
    restore_login_from_cookie,
    set_login_cookie,
    clear_login_cookie
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "Backend" / "smartkitchen.db"

def create_connection():
    return sqlite3.connect(DB_PATH)


def register_user(username, email, password):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, password))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        conn.close()
        return False


def check_login(email, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, email
        FROM users
        WHERE email = ? AND password = ?
    """, (email, password))

    user = cursor.fetchone()
    conn.close()

    return user


def hide_sidebar():
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {
                display: none;
            }

            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)


def load_home_css():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
            }

            .hero-box {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                padding: 32px;
                border-radius: 24px;
                color: white;
                margin-bottom: 24px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
            }

            .hero-title {
                font-size: 34px;
                font-weight: 700;
                margin-bottom: 8px;
            }

            .hero-subtitle {
                font-size: 17px;
                color: #d1d5db;
                line-height: 1.6;
            }

            .section-title {
                font-size: 24px;
                font-weight: 700;
                color: #111827;
                margin-top: 10px;
                margin-bottom: 16px;
            }

            .step-card {
                background: white;
                border-radius: 18px;
                padding: 20px;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
                border: 1px solid #e5e7eb;
                height: 170px;
                margin-bottom: 16px;
            }

            .step-number {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: linear-gradient(135deg, #10b981, #22c55e);
                color: white;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 14px;
            }

            .step-title {
                font-size: 18px;
                font-weight: 700;
                color: #111827;
                margin-bottom: 8px;
            }

            .step-text {
                color: #4b5563;
                font-size: 14px;
                line-height: 1.6;
            }

            .tip-box {
                background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
                border-left: 6px solid #f97316;
                padding: 22px;
                border-radius: 18px;
                margin-top: 8px;
                margin-bottom: 24px;
                box-shadow: 0 6px 18px rgba(249, 115, 22, 0.08);
            }

            .tip-title {
                font-size: 18px;
                font-weight: 700;
                color: #9a3412;
                margin-bottom: 8px;
            }

            .tip-text {
                color: #7c2d12;
                font-size: 15px;
                line-height: 1.6;
            }

            div.stButton > button {
                border-radius: 14px;
                height: 48px;
                font-weight: 600;
                font-size: 16px;
                border: none;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
        </style>
    """, unsafe_allow_html=True)


def logout():
    st.session_state.manual_logout = True
    clear_login_cookie()

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.auth_restore_attempts = 0

    st.rerun()


def show_login_page():
    hide_sidebar()

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


init_session_state()
restore_login_from_cookie()

if not st.session_state.logged_in:
    show_login_page()
    st.stop()

show_home_page()