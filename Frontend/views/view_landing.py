import streamlit as st
from home_styles import load_landing_css, hide_sidebar


def show_landing_page():
    try:
        load_landing_css()
        hide_sidebar()
    except Exception:
        pass

    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

        <style>
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .top-brand {
                font-size: 26px;
                font-weight: 900;
                color: #FFFFFF;
                display: flex;
                align-items: center;
                gap: 10px;
                text-shadow: 0 3px 12px rgba(0,0,0,0.55);
            }

            .giant-hero {
                text-align: center;
                padding: 60px 20px 20px 20px;
                animation: fadeInUp 0.8s ease-out;
            }

            .giant-title {
                font-size: 64px;
                font-weight: 900;
                color: #E427F5;
                margin-bottom: 15px;
                line-height: 1.1;
                text-shadow: 0 3px 14px rgba(255,255,255,0.95);
            }

            .hero-subtitle { 
                font-size: 25px;
                color: #b291c9;
                font-weight: 900;
                margin-bottom: 30px;
                text-shadow: 0 3px 14px rgba(255,255,255,0.95);
            }

            .about-text-clean {
                text-align: center;
                font-size: 20px;
                line-height: 1.7;
                color: #1c4223;
                font-weight: 0;
                max-width: 700px;
                margin: 0 auto 45px auto;
                animation: fadeInUp 0.8s ease-out 0.2s backwards;
                text-shadow: 0 3px 14px rgba(255,255,255,0.95);
            }

            .section-header {
                font-size: 30px;
                font-weight: 900;
                color: #111827;
                margin-bottom: 25px;
                text-align: center;
                letter-spacing: 2px;
                text-shadow: 0 3px 14px rgba(255,255,255,0.95);
            }

            .compact-card {
                background: rgba(255, 255, 255, 0.94);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 8px 28px rgba(0,0,0,0.18);
                border: 1px solid rgba(255,255,255,0.65);
                border-left: 6px solid #002b5c; 
                transition: all 0.3s ease; 
                display: flex;
                align-items: flex-start;
                text-align: left;
                margin-bottom: 18px;
                min-height: 170px;
            }

            .compact-card:hover {
                transform: translateY(-6px);
                box-shadow: 0 12px 34px rgba(0,0,0,0.24);
            }
            
            .c-icon {
                font-size: 34px;
                margin-right: 18px;
                min-width: 45px;
                text-align: center;
                margin-top: 5px;
            }

            .c-content {
                flex-grow: 1;
            }

            .c-title {
                font-size: 22px;
                font-weight: 900;
                color: #002b5c;
                margin-bottom: 8px;
            }

            .c-desc {
                font-size: 16px;
                color: #111111;
                line-height: 1.5;
                font-weight: 600;
                margin: 0;
            }

            .footer-box {
                text-align: center;
                margin-top: 55px;
                padding-top: 24px;
                padding-bottom: 15px;
            }

            .footer-text {
                font-size: 18px;
                font-weight: 900;
                color: #fff1d0;
                letter-spacing: 2px;
                text-shadow: 0 3px 12px rgba(0,0,0,0.55);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    top_col1, top_col2 = st.columns([5, 1.4])

    with top_col1:
        st.markdown(
            """
            <div class="top-brand">
                <i class="fa-solid fa-leaf" style="color: #4ade80;"></i> 
                Smart Kitchen Assistant
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_col2:
        if st.button("Login / Register", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.rerun()

    st.markdown(
        """
        <div class="giant-hero">
            <div class="giant-title">What Should I Cook Today?</div>
            <div class="hero-subtitle">Plan meals, track ingredients, and shop easier.</div>
        </div>

        <div class="about-text-clean">
            Turn the ingredients you already have into smart meal ideas.
            Smart Kitchen Assistant helps you organize your kitchen inventory,
            create personalized meal plans, and prepare grocery lists based on
            your diet preferences, allergies, and available ingredients.
            It makes cooking easier by helping you decide what to cook today,
            what you already have at home, and what you need to buy before shopping.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-header">CORE FEATURES</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="compact-card">
                <div class="c-icon" style="color: #d32f2f;">
                    <i class="fa-solid fa-camera"></i>
                </div>
                <div class="c-content">
                    <div class="c-title">Ingredient Detection</div>
                    <p class="c-desc">
                        Detect ingredients from images and use them for smarter kitchen management.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="compact-card">
                <div class="c-icon" style="color: #2e7d32;">
                    <i class="fa-solid fa-utensils"></i>
                </div>
                <div class="c-content">
                    <div class="c-title">Meal Planning</div>
                    <p class="c-desc">
                        Create personalized meal plans based on inventory, diet, and allergies.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="compact-card">
                <div class="c-icon" style="color: #f57c00;">
                    <i class="fa-solid fa-cart-shopping"></i>
                </div>
                <div class="c-content">
                    <div class="c-title">Grocery List</div>
                    <p class="c-desc">
                        Add missing ingredients to your shopping list and manage what you need to buy.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="footer-box">
            <div class="footer-text">Developed by G & M & B </div>
            <div class="footer-text">2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
