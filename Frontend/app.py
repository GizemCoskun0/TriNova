import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Smart Kitchen Assistant", layout="wide", page_icon="🍳")

@st.cache_resource
def start_scheduler():
    scheduler = BackgroundScheduler()
    

    def auto_generate_plan():
        print(f"⏰ [SCHEDULED TASK WORKED- {datetime.datetime.now()}] Weekly meal plans and shopping lists are generated automatically...")
    

    scheduler.add_job(auto_generate_plan, 'interval', seconds=100)
    scheduler.start()
    return scheduler


scheduler = start_scheduler()

st.title("Welcome to the Smart Kitchen Assistant! 🥗")
st.write("Please select a page from the left menu to proceed.")
st.info("💡 Note: APScheduler is currently running in the background, quietly logging a message to the VS Code terminal every 10 seconds. You can check it out!")        