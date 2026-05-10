import streamlit as st

st.set_page_config(
    page_title="Smart Kitchen Assistant", 
    page_icon="🍳", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

from auth_utils import init_session_state, restore_login_from_cookie

from views.view_landing import show_landing_page
from views.view_login import show_login_page
from views.view_dashboard import show_home_page

init_session_state()
restore_login_from_cookie()

if not st.session_state.logged_in:
    if st.session_state.auth_view == "login":
        show_login_page()
    else:
        show_landing_page()
        
    st.stop() 

show_home_page()