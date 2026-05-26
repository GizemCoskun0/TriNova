import time
import sqlite3
from pathlib import Path

import streamlit as st
from streamlit_cookies_controller import CookieController

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "Backend" / "smartkitchen.db"

AUTH_COOKIE = "smartkitchen_user_email"

cookie_controller = CookieController(key="auth_cookie_manager")


def create_connection():
    return sqlite3.connect(DB_PATH)


def get_user_by_email(email):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email
        FROM users
        WHERE email = ?
    """,
        (email,),
    )

    user = cursor.fetchone()
    conn.close()

    return user


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "username" not in st.session_state:
        st.session_state.username = ""

    if "email" not in st.session_state:
        st.session_state.email = ""

    if "auth_restore_attempts" not in st.session_state:
        st.session_state.auth_restore_attempts = 0

    if "manual_logout" not in st.session_state:
        st.session_state.manual_logout = False
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "landing"


def set_login_cookie(email):
    cookie_controller.set(
        AUTH_COOKIE, email, path="/", max_age=60 * 60 * 24 * 7, same_site="lax"
    )

    time.sleep(0.7)


def clear_login_cookie():
    cookie_controller.set(AUTH_COOKIE, "", path="/", max_age=0, same_site="lax")

    time.sleep(0.3)

    cookie_controller.remove(AUTH_COOKIE, path="/", same_site="lax")

    time.sleep(0.7)


def restore_login_from_cookie(max_attempts=3):
    init_session_state()

    if st.session_state.manual_logout:
        return False

    if st.session_state.logged_in:
        return True

    try:
        cookie_controller.refresh()
    except Exception:
        pass

    saved_email = cookie_controller.get(AUTH_COOKIE)

    if saved_email:
        user = get_user_by_email(saved_email)

        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.username = user[1]
            st.session_state.email = user[2]
            st.session_state.auth_restore_attempts = 0
            return True

        clear_login_cookie()
        return False

    if st.session_state.auth_restore_attempts < max_attempts:
        st.session_state.auth_restore_attempts += 1
        time.sleep(0.4)
        st.rerun()

    return False


def require_login():
    is_logged_in = restore_login_from_cookie()

    if not is_logged_in:
        st.warning("🚨 Please login from the main page first!")
        st.stop()

    st.markdown(
        """
        <style>
            /* 1. Menünün ana çerçevesini ekranın altına kadar zorla uzatır */
            [data-testid="stSidebarNav"] {
                min-height: 85vh !important; 
                display: flex !important;
                flex-direction: column !important;
            }
            
            /* 2. İçindeki listeyi tüm boşluğu kaplayacak şekilde esnetir */
            [data-testid="stSidebarNavItems"] {
                display: flex !important;
                flex-direction: column !important;
                flex-grow: 1 !important; 
            }
            
            /* 3. En sondaki sayfayı (Settings) zorla en dibe fırlatır */
            [data-testid="stSidebarNavItems"] > li:last-child {
                margin-top: auto !important;
                padding-top: 15px !important;
                margin-bottom: 15px !important;
                border-top: 1px solid rgba(128, 128, 128, 0.3) !important;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
