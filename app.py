import streamlit as st
from mood_tracker import mood_tracker_page
from cbt_chatbot import cbt_chatbot_page

# Set page config here FIRST
st.set_page_config(page_title="HealHub", layout="centered")

# Sidebar navigation
st.sidebar.title("🧠 HealHub")
page = st.sidebar.radio("Go to", ["Mood Tracker", "CBT Chatbot"])

if page == "Mood Tracker":
    mood_tracker_page()
else:
    cbt_chatbot_page()
