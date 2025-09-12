import streamlit as st
from openai import OpenAI
import json

if "participant_info" not in st.session_state:
    st.session_state.participant_info = {}
if "ads" not in st.session_state:
    st.session_state.ads = []
if "current_ad" not in st.session_state:
    st.session_state.current_ad = 0
if "responses" not in st.session_state:
    st.session_state.responses = []

st.header("👤 Participant Information")

with st.form("participant_info_form"):
        name = st.text_input("First Name")
        location = st.text_input("City of Residence")
        age = st.number_input("Age", min_value=18, max_value=110)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        purchase_intent = st.text_input(
            "Optional: Are you currently looking to purchase anything online? If so, what? (Examples: camera, plant, furniture, etc.)"
        )
        submit_button = st.form_submit_button("Next")
   # stores answers in participant_info 
if submit_button:
    if name and location and age and gender:
        st.session_state.participant_info = {
            "Name": name,
            "Location": location,
            "Age": age,
            "Gender": gender,
            "Purchase Intent": purchase_intent
        }
        st.success("✅ Info saved! You can now go to **Ad Rating**.")
    else:
        st.error("⚠️ Please fill in all required fields.")