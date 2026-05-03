import streamlit as st

from auth_utils import init_session_state, restore_login_from_cookie
from home_pages import show_landing_page, show_login_page, show_home_page


init_session_state()
restore_login_from_cookie()

if not st.session_state.logged_in:
    if st.session_state.auth_view == "login":
        show_login_page()
    else:
        show_landing_page()

    st.stop()

show_home_page()