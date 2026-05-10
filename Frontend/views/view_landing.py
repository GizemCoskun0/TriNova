import streamlit as st
import time
from home_styles import load_landing_css

def show_landing_page():
    # CSS Tasarımı - Yüksek Kontrastlı ve Keskin Okunabilirlik
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .top-brand {
                font-size: 26px; font-weight: 900; color: #FFFFFF; /* En koyu lacivert */
                display: flex; align-items: center; gap: 10px;
            }

            /* DEV BAŞLIK ALANI */
            .giant-hero {
                text-align: center; padding: 40px 20px 10px 20px;
                animation: fadeInUp 0.8s ease-out;
            }
            .giant-title {
                font-size: 70px; font-weight: 900; color: #d32f2f; /* Daha doygun, net bir kırmızı */
                margin-bottom: 15px; line-height: 1.1;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }
            /* YENİ: Alt başlık çok daha koyu ve net */
            .hero-subtitle { 
                font-size: 26px; color: #1a1a1a; font-weight: 700; margin-bottom: 30px;
            }
            /* YENİ: Ana metin tam siyah ve tok */
            .about-text-clean {
                text-align: center; font-size: 20px; line-height: 1.7; color: #000000; 
                font-weight: 600; max-width: 1000px; margin: 0 auto 50px auto;
                animation: fadeInUp 0.8s ease-out 0.2s backwards;
            }

            /* SOL TARAF İÇİN YÜKSEK KONTRASTLI KARTLAR */
            .compact-card {
                background: #ffffff; border-radius: 14px; padding: 22px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #cccccc; border-left: 6px solid #002b5c; 
                transition: all 0.3s ease; 
                display: flex; align-items: flex-start; text-align: left;
                margin-bottom: 18px;
            }
            .compact-card:hover { transform: translateX(8px); border-color: #002b5c; }
            
            .c-icon { font-size: 32px; margin-right: 20px; min-width: 45px; text-align: center; margin-top: 5px;}
            .c-content { flex-grow: 1; }
            /* YENİ: Kart başlıkları ve açıklamaları artık çok daha belirgin */
            .c-title { font-size: 22px; font-weight: 900; color: #002b5c; margin-bottom: 6px; }
            .c-desc { font-size: 17px; color: #111111; line-height: 1.5; font-weight: 600; margin: 0;}

            /* SAĞ TARAF DEMO KUTUSU */
            .demo-box-clean {
                background: white; border: 2px solid #002b5c; border-radius: 20px;
                padding: 25px; text-align: center; box-shadow: 0 15px 45px rgba(0,0,0,0.12);
                position: sticky; top: 20px;
            }

            /* FOOTER */
            .footer-box {
                text-align: center; margin-top: 60px; padding-top: 25px;
                border-top: 3px solid #002b5c; padding-bottom: 15px;
            }
            .footer-text { font-size: 20px; font-weight: 900; color: #002b5c; letter-spacing: 3px; }
            
            /* ST-TABS KONTRASTI */
            .stTabs [data-baseweb="tab-list"] { gap: 15px; border-bottom: 2px solid #ddd; }
            .stTabs [data-baseweb="tab"] { font-size: 20px; font-weight: 800; color: #002b5c; }
            .section-header { font-size: 30px; font-weight: 900; color: #002b5c; margin-bottom: 25px; text-decoration: underline;}
        </style>
    """, unsafe_allow_html=True)

    try:
        load_landing_css()
    except Exception:
        pass

    # 1. ÜST BAR
    top_col1, top_col2 = st.columns([6, 1])
    with top_col1:
        st.markdown("""
            <div class="top-brand">
                <i class="fa-solid fa-leaf" style="color: #2e7d32;"></i> 
                Smart Kitchen Assistant
            </div>
        """, unsafe_allow_html=True)
    with top_col2:
        if st.button("Login / Register", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.rerun()

    # 2. DEV BAŞLIK VE KESKİN AÇIKLAMA 
    st.markdown("""
        <div class="giant-hero">
            <div class="giant-title">WHAT TO COOK TODAY?</div>
            <div class="hero-subtitle">Stop the waste. Start the flavor. Meet your AI chef.</div>
        </div>
        <div class="about-text-clean">
            Our YOLO-powered AI camera recognizes your ingredients in real-time. 
            Get personalized recipes based on your stock, manage your pantry effortlessly, 
            and create smart grocery lists instantly.
        </div>
    """, unsafe_allow_html=True)


    # === 3. SPLIT-SCREEN TASARIM ===
    left_col, right_col = st.columns([1.2, 1], gap="large")

    # --- SOL KOLON ---
    with left_col:
        st.markdown('<div class="section-header">CORE FEATURES</div>', unsafe_allow_html=True)
        
        tab_steps, tab_lifestyle = st.tabs(["⚙️ HOW IT WORKS", "🎯 FOR YOU"])
        
        with tab_steps:
            st.markdown("""
                <div class="compact-card">
                    <div class="c-icon" style="color: #d32f2f;"><i class="fa-solid fa-camera"></i></div>
                    <div class="c-content">
                        <div class="c-title">1. Scan Ingredients</div>
                        <p class="c-desc">Snap a photo. Our AI identifies your stock with high precision using YOLO models.</p>
                    </div>
                </div>
                <div class="compact-card">
                    <div class="c-icon" style="color: #d32f2f;"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
                    <div class="c-content">
                        <div class="c-title">2. AI Recipe Matching</div>
                        <p class="c-desc">The system filters thousands of recipes to find what you can cook right now.</p>
                    </div>
                </div>
                <div class="compact-card">
                    <div class="c-icon" style="color: #d32f2f;"><i class="fa-solid fa-cart-shopping"></i></div>
                    <div class="c-content">
                        <div class="c-title">3. Smart Grocery Lists</div>
                        <p class="c-desc">Automatically identify missing ingredients and add them to your list with one click.</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with tab_lifestyle:
            st.markdown("""
                <div class="compact-card" style="border-left-color: #FF9800;">
                    <div class="c-icon" style="color: #FF9800;"><i class="fa-solid fa-graduation-cap"></i></div>
                    <div class="c-content">
                        <div class="c-title">For Students</div>
                        <p class="c-desc">Save money and eat healthy. Perfect for dorm life and tight budgets.</p>
                    </div>
                </div>
                <div class="compact-card" style="border-left-color: #E91E63;">
                    <div class="c-icon" style="color: #E91E63;"><i class="fa-solid fa-dumbbell"></i></div>
                    <div class="c-content">
                        <div class="c-title">For Athletes</div>
                        <p class="c-desc">Track your macros and find high-protein recipes tailored to your pantry.</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)


    # --- SAĞ KOLON ---
    with right_col:
        st.markdown('<div class="section-header">LIVE AI DEMO</div>', unsafe_allow_html=True)
        st.markdown('<div class="demo-box-clean">', unsafe_allow_html=True)
        
        st.image("https://images.unsplash.com/photo-1588964895597-cfccd6e2dbf9?w=800&q=80", 
                 caption="AI Visual Recognition Test", 
                 use_container_width=True)
        
        if st.button("🔍 START YOLO VISION SCAN", use_container_width=True, type="primary"):
            with st.spinner("Analyzing ingredients..."):
                time.sleep(1.5)
            st.success("SCAN COMPLETE!")
            st.markdown("<b style='color:black; font-size:18px;'>Detected: 3x Tomatoes, 1x Milk, 6x Eggs</b>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 6. G & M & B FOOTER
    st.markdown("""
        <div class="footer-box">
            <div class="footer-text">G & M & B</div>
            <div style="color: #000; font-weight: 700; font-size: 15px; margin-top: 5px;">© 2026 Smart Kitchen Assistant</div>
        </div>
    """, unsafe_allow_html=True)