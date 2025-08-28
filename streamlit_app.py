import streamlit as st
import openai
import pandas as pd

openai.api_key = st.secrets["OPENAI_API_KEY"]

# initialize page state
if "page" not in st.session_state:
    st.session_state.page = 1

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
            st.session_state.page = 3
        else:
            st.error("Please fill in all required fields.")

# page 3: advertisements
elif st.session_state.page == 3:
    st.title("Next Section: Personalized Ads")
    st.markdown("""
        This is where you can display AI-generated personalized advertisements
        and collect ratings.
    """)
    
    st.write("Participant info collected:")
    st.json(st.session_state.participant_info)
    
    if st.button("Generate Example Ad"):
        prompt = f"""Generate a one-sentence advertisement for a watch that is personalised to include the following details: {st.session_state.participant_info} List of products to advertise: t-shirts, shoes, hats, skincare, watches, phones, jacket, backpack, headphones, drinks.
Pick a random product for each advertisement you generate.
You don't have to strictly use all the details as-is; make the advertisement catchy and attractive (use emojis commonly found in advertisements, including 🔥 👀 ⚡️ ✨). The age doesn't have to be included if not relevant, but use it for creating relevant context. Change the structure/phrasing of each advertisement so the personalized features are not obvious. The features should not be right at the beginning of every advertisement. The creepiness should get higher as more features are included, and the ads will be concerningly more personalized.
Output 15 different advertisements in a JSON format. 4 of those will only use one personalised feature - Name, Age, Location, gender. 6 will use two features - (Name, Age), (Age, Location), (Name, Location), (Name, gender), (Age, gender), (Location, gender). 4 will use three features - (Name, Age, Gender), (Age, Location, Gender), (Name, Location, Gender), (Name, Age, Location). The last one will use all 4 features - (Name, Age, Location, Gender).
In the Json format, indicate as a key the features used in that specific advertisement."""

        with st.spinner("Generating ad..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8
                )
                ad_text = response.choices[0].message["content"].strip()
                st.markdown(f"**Example Ad:** {ad_text}")
            except Exception as e:
                st.error(f"OpenAI request failed: {e}")
