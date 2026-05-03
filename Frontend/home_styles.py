import streamlit as st


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


def load_landing_css():
    st.markdown("""
        <style>
            .landing-hero {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                color: white;
                padding: 42px;
                border-radius: 26px;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.14);
                margin-bottom: 28px;
            }

            .landing-title {
                font-size: 42px;
                font-weight: 800;
                margin-bottom: 12px;
            }

            .landing-subtitle {
                font-size: 18px;
                color: #d1d5db;
                line-height: 1.7;
            }

            .feature-card {
                background: white;
                padding: 22px;
                border-radius: 18px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
                height: 150px;
            }

            .feature-title {
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 8px;
                color: #111827;
            }

            .feature-text {
                color: #4b5563;
                font-size: 14px;
                line-height: 1.5;
            }
        </style>
    """, unsafe_allow_html=True)