pip install streamlit langchain-openai
import streamlit as st
import pandas as pd

# survey introduction
st.set_page_config(
    page_title="Marketing Personalization Survey", 
    page_icon="📢"
)
st.title("Marketing Personalization Survey")
st.markdown(
    """
    This study explores how people perceive different types of personalized ads.
    
    **Please note:**
    - In this study, you will be asked to rate 15 advertisements based on their creepiness, personal relevance, click likelihood, and purchase intention.
    - You will be asked for you name, age, city, and gender.
    - All responses are confidential.
    - This survey should take approximately 5 minutes to complete.

    Let's get started!
    """
)

# collecting participant information
st.header("👤 Participant Information")

with st.form("participant_info_form"):
    name = st.text_input("First Name")
    location = st.text_input("City of Residence")
    age = st.number_input("Age", min_value=13, max_value=110)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    purchase_intent = st.text_input("Optional: Are you currently looking to purchase anything online? If so, what?")
    submit_button = st.form_submit_button("Next")

if submit_button:
    if name and location and age and gender:
        st.session_state.participant_info = {
            "Name": name,
            "Location": location,
            "Age": age,
            "Gender": gender,
            "Purchase Intent": purchase_intent
        }
        st.success("Thank you for providing your information! Proceeding to the next section.")
    else:
        st.error("Please fill in all fields to proceed.")
