import streamlit as st
from auth_utils import clear_login_cookie
from user_db import get_dashboard_data
from home_styles import load_home_css


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


def show_home_page():
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            .dashboard-card {
                background: #ffffff;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: 1px solid #f0f2f6;
                margin-bottom: 15px;
            }
            .dashboard-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
                border-color: #ff4b4b;
            }
            .dashboard-icon {
                margin-bottom: 10px;
            }
            .dashboard-title {
                font-size: 18px;
                font-weight: 600;
                color: #31333F;
                margin-bottom: 5px;
            }
            .dashboard-value {
                font-size: 28px;
                font-weight: 700;
                color: #ff4b4b;
                margin-bottom: 5px;
            }
            .step-text {
                font-size: 14px;
                color: #6c757d;
            }
            .smart-box {
                background-color: #e8f4f8;
                border-left: 5px solid #17a2b8;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            }
            .tip-title {
                font-weight: bold;
                color: #0c5460;
                margin-bottom: 5px;
            }
            .tip-text {
                color: #1d6877;
                font-size: 15px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    try:
        load_home_css()
    except Exception:
        pass

    dashboard_data = get_dashboard_data(st.session_state.email)

    if not dashboard_data:
        st.error("Dashboard data could not be loaded.")
        return

    inventory_count = dashboard_data.get("inventory_count", 0)
    shopping_count = dashboard_data.get("shopping_count", 0)
    meal_plan_count = dashboard_data.get("meal_plan_count", 0)
    diet = dashboard_data.get("diet", "Not specified")
    allergy_count = dashboard_data.get("allergy_count", 0)

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #ff4b4b 0%, #ff7676 100%); 
                    border-radius: 15px; 
                    padding: 30px; 
                    color: white; 
                    margin-bottom: 25px;
                    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);">
            <h2 style="margin:0; font-weight:700;">👋 Welcome back, {st.session_state.username}</h2>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                Here is your kitchen overview for today. Let's cook something delicious!
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h3 style="color: #31333F;">🏠 Kitchen Dashboard</h3>', unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="dashboard-icon" style="color: #FF9800; font-size: 28px;">
                    <i class="fa-solid fa-utensils"></i>
                </div>
                <div class="dashboard-title">Meal Plan</div>
                <div class="dashboard-value" style="color: #FF9800;">{meal_plan_count}</div>
                <div class="step-text">saved meal items</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # Envanter için basit bir doluluk barı (örneğin mutfakta ortalama 20 malzeme olsun)
        inventory_percentage = (
            min((inventory_count / 20) * 100, 100) if inventory_count else 0
        )

        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="dashboard-icon" style="color: #4CAF50; font-size: 28px;">
                    <i class="fa-solid fa-kitchen-set"></i>
                </div>
                <div class="dashboard-title">Inventory</div>
                <div class="dashboard-value" style="color: #4CAF50;">{inventory_count}</div>
                <div style="background-color: #e0e0e0; border-radius: 10px; height: 6px; margin-top: 10px; margin-bottom: 5px;">
                    <div style="background-color: #4CAF50; height: 100%; border-radius: 10px; width: {inventory_percentage}%;"></div>
                </div>
                <div class="step-text">ingredients at home</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="dashboard-icon" style="color: #2196F3; font-size: 28px;">
                    <i class="fa-solid fa-cart-shopping"></i>
                </div>
                <div class="dashboard-title">Grocery List</div>
                <div class="dashboard-value" style="color: #2196F3;">{shopping_count}</div>
                <div class="step-text">items to buy</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<h3 style="margin-top: 20px; color: #31333F;">📌 Profile Status</h3>',
        unsafe_allow_html=True,
    )

    col4, col5 = st.columns(2)

    with col4:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="dashboard-icon" style="color: #8BC34A; font-size: 28px;">
                    <i class="fa-solid fa-leaf"></i>
                </div>
                <div class="dashboard-title">Diet Preference</div>
                <div class="dashboard-value" style="font-size:22px; color: #333;">{diet}</div>
                <div class="step-text">used for meal suggestions</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="dashboard-icon" style="color: #E91E63; font-size: 28px;">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                </div>
                <div class="dashboard-title">Allergies</div>
                <div class="dashboard-value" style="color: #E91E63;">{allergy_count}</div>
                <div class="step-text">saved allergy records</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="smart-box">
            <div class="tip-title"><i class="fa-regular fa-lightbulb"></i> Smart Suggestion</div>
            <div class="tip-text">
                Keep your inventory updated before generating a new meal plan.
                This helps the system suggest better recipes and create a more accurate grocery list.
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()
