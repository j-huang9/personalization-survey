import streamlit as st
from openai import OpenAI
import pandas as pd
import random 

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# initialize page state
if "page" not in st.session_state:
    st.session_state.page = 1
if "participant_info" not in st.session_state:
    st.session_state.participant_info = {}
if "ads" not in st.session_state:
    st.session_state.ads = []
if "current_ad" not in st.session_state:
    st.session_state.current_ad = 0
if "responses" not in st.session_state:
    st.session_state.responses = []

# survey introduction
if st.session_state.page == 1:
    st.set_page_config(
        page_title="Marketing Personalization Survey",
        page_icon="📢"
    )
    st.title("Marketing Personalization Survey")
    st.markdown("""
        This study explores how people perceive different types of personalized ads.
        
        **Please note:**
        - You will be asked to rate 15 advertisements based on creepiness, personal relevance, click likelihood, and purchase intention.
        - You will be asked for your name, age, city, and gender.
        - All responses are confidential.
        - This survey should take approximately 5 minutes.
    """)
    
    if st.button("Let's get started"):
        st.session_state.page = 2

# page 2: participant info
elif st.session_state.page == 2:
    st.header("👤 Participant Information")
    
    with st.form("participant_info_form"):
        name = st.text_input("First Name")
        location = st.text_input("City of Residence")
        age = st.number_input("Age", min_value=13, max_value=110)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        purchase_intent = st.text_input(
            "Optional: Are you currently looking to purchase anything online? If so, what?"
        )
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
        if not st.session_state.ads:
            prompt = f"""
        Generate 15 one-sentence personalized advertisements for these products: t-shirts, shoes, hats, skincare, watches, phones, jacket, backpack, headphones, drinks.
        Personalize each ad using these features from the survey: {st.session_state.participant_info}
        Use the following mapping for features:
          - 4 ads: Only one feature (Name, Age, Location, or Gender)
          - 6 ads: Two features (combinations like Name+Age)
          - 4 ads: Three features
          - 1 ad: All four features
        Output as a JSON dictionary where the key is a comma-separated string of the features used (e.g. "Name,Location") and the value is the advertisement string. Strictly output valid JSON, no extra text.
        Use lots of emoji (🔥 👀 ⚡️ ✨) and make the ads catchy.
        """
            try:
                response = client.chat.completions.create(
                    model="gpt-5-mini", 
                    messages=[{"role": "user", "content": prompt}],
                )
                ad_text = response.choices[0].message.content
                import json
                ads_json = json.loads(ad_text)
                ads_list = list(ads_json.values()) if isinstance(ads_json, dict) else ads_json
                st.session_state.ads = ads_list
            except Exception as e:
                st.error(f"OpenAI request failed: {e}")
                st.stop()
        st.session_state.page = 3  # Go straight to ad rating
    else:
        st.error("Please fill in all required fields.")
        

# page 3: rating advertisements
elif st.session_state.page == 3:
    st.title("Rate the Ads")

    if st.session_state.current_ad < len(st.session_state.ads):
        ad_text = st.session_state.ads[st.session_state.current_ad]
        
        st.subheader(f"Advertisement {st.session_state.current_ad + 1} of {len(st.session_state.ads)}")
        st.markdown(f"**{ad_text}**")

        # Creepiness
        st.markdown("""
        **How creepy is this ad?**  
        1 = Not creepy at all → “This ad feels normal and not creepy.”  
        2 = Slightly creepy → “This ad feels mostly okay, with only mild creepiness.”  
        3 = Somewhat creepy → “This ad feels a little off, but not too bad.”  
        4 = Quite creepy → “This ad feels uncomfortably personal or intrusive.”  
        5 = Extremely creepy → “This ad feels very unsettling, invasive, or stalker-like.”
        """)
        creepiness = st.slider("", 1, 5, 3)

        # Perceived personal relevance
        st.markdown("""
        **How tailored is this ad to you?**  
        1 = Not tailored at all → “This ad doesn’t feel related to me in any way.”  
        2 = Slightly tailored → “This ad seems vaguely related to me.”  
        3 = Somewhat tailored → “This ad has some clear connection to me.”  
        4 = Quite tailored → “This ad feels well-matched to me personally.”  
        5 = Extremely tailored → “This ad feels directly designed for me.”
        """)
        personal_relevance = st.slider("", 1, 5, 3)

        # Click intention
        st.markdown("""
        **How likely are you to click this ad?**  
        1 = Very unlikely → “I would definitely not click this.”  
        2 = Unlikely → “I probably wouldn’t click this.”  
        3 = Neutral / Maybe → “I might or might not click this.”  
        4 = Likely → “I would probably click this.”  
        5 = Very likely → “I would definitely click this.”
        """)
        click_intention = st.slider("", 1, 5, 3)

        # Purchase intention
        st.markdown("""
        **How likely are you to purchase this item?**  
        1 = Very unlikely → “I would definitely not buy this.”  
        2 = Unlikely → “I probably wouldn’t buy this.”  
        3 = Neutral → “I might or might not buy this.”  
        4 = Likely → “I would probably buy this.”  
        5 = Very likely → “I would definitely buy this.”
        """)
        purchase_intention = st.slider("", 1, 5, 3)

        # Next button
        if st.button("Next"):
            st.session_state.responses.append({
                "ad": ad_text,
                "creepiness": creepiness,
                "personal_relevance": personal_relevance,
                "click_intention": click_intention,
                "purchase_intention": purchase_intention
            })
            st.session_state.current_ad += 1

    else:
        st.success("You’ve completed the survey! 🎉 Thank you for your participation.")

