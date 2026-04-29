import streamlit as st
import sqlite3
from pathlib import Path


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


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if not st.session_state.logged_in:

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

    st.title("🔐 Smart Kitchen Assistant")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Registered User Login")

        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True):
            if login_email == "" or login_password == "":
                st.warning("Please enter your email and password.")

            else:
                user = check_login(login_email, login_password)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.email = user[2]

                    st.success("Login successful! Loading...")
                    st.rerun()

                else:
                    st.error("Invalid email or password!")

    with tab2:
        st.subheader("Create New Account")

        register_username = st.text_input("Username", key="register_username")
        register_email = st.text_input("Email", key="register_email")
        register_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Register", use_container_width=True):
            if register_username == "" or register_email == "" or register_password == "" or confirm_password == "":
                st.warning("Please fill in all fields.")

            elif "@" not in register_email:
                st.warning("Please enter a valid email address.")

            elif register_password != confirm_password:
                st.error("Passwords do not match!")

            else:
                result = register_user(register_username, register_email, register_password)

                if result:
                    st.success("Registration successful! You can now login.")

                else:
                    st.error("This email or username may already be registered.")

    st.stop()

st.title("👋 Welcome, " + st.session_state.username)

st.write("You can access the Smart Inventory and other menus from the left-hand sidebar.")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.email = ""
    st.rerun()