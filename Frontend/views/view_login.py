import streamlit as st
from auth_utils import set_login_cookie, clear_login_cookie
from user_db import register_user, check_login
from home_styles import hide_sidebar

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