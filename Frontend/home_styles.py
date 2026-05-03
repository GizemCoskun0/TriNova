from networkx import display
import streamlit as st
import base64
from pathlib import Path


def get_base64_image(image_path):
    image_path = Path(image_path)

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    return encoded

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

            .dashboard-card {
                background: white;
                border-radius: 20px;
                padding: 22px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
                min-height: 145px;
                margin-bottom: 18px;
            }

            .dashboard-icon {
                font-size: 28px;
                margin-bottom: 10px;
            }

            .dashboard-title {
                font-size: 15px;
                color: #6b7280;
                font-weight: 600;
                margin-bottom: 6px;
            }

            .dashboard-value {
                font-size: 28px;
                color: #111827;
                font-weight: 800;
            }

            .step-text {
                color: #4b5563;
                font-size: 14px;
                line-height: 1.6;
            }

            .status-box {
                background: #ffffff;
                border-radius: 20px;
                padding: 24px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
                margin-top: 18px;
            }

            .smart-box {
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border-left: 6px solid #10b981;
                padding: 22px;
                border-radius: 18px;
                margin-top: 20px;
                margin-bottom: 24px;
                box-shadow: 0 8px 22px rgba(16, 185, 129, 0.08);
            }

            .tip-title {
                font-size: 18px;
                font-weight: 700;
                color: #065f46;
                margin-bottom: 8px;
            }

            .tip-text {
                color: #065f46;
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
    image_path = Path(__file__).resolve().parent / "assets" / "kitchen_bg.jpg"
    bg_image = get_base64_image(image_path)

    st.markdown(f"""
        <style>
            [data-testid="stToolbar"] {{
                display: none !important;
            }}

            [data-testid="stDecoration"] {{
                display: none !important;
            }}

            #MainMenu {{
                visibility: hidden;
            }}

            header {{
                visibility: hidden;
            }}

            .stApp {{
                background-image:
                    linear-gradient(
                        rgba(255, 255, 255, 0.10),
                        rgba(255, 255, 255, 0.10)
                    ),
                    url("data:image/jpg;base64,{bg_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}

            .landing-hero {{
                background: rgba(17, 24, 39, 0.88);
                color: white;
                padding: 42px;
                border-radius: 26px;
                box-shadow: 0 14px 34px rgba(0, 0, 0, 0.22);
                margin-bottom: 28px;
                border: 1px solid rgba(255, 255, 255, 0.18);
            }}

            .landing-title {{
                font-size: 42px;
                font-weight: 800;
                margin-bottom: 12px;
                color: #ffffff;
            }}

            .landing-subtitle {{
                font-size: 18px;
                color: #f3f4f6;
                line-height: 1.7;
            }}

            .feature-card {{
                background: rgba(255, 255, 255, 0.94);
                padding: 22px;
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.65);
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
                height: 150px;
                margin-bottom: 18px;
            }}

            .feature-title {{
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 8px;
                color: #111827;
            }}

            .feature-text {{
                color: #374151;
                font-size: 14px;
                line-height: 1.5;
            }}

            div.stButton > button {{
                border-radius: 14px;
                height: 48px;
                font-weight: 600;
                font-size: 16px;
                border: none;
                background: rgba(255, 255, 255, 0.96);
                color: #111827;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
            }}

            div.stButton > button:hover {{
                background: white;
                color: #111827;
                border: none;
            }}
        </style>
    """, unsafe_allow_html=True)