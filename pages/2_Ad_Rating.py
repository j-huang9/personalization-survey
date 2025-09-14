import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI
import json

st.set_page_config(page_title="Ad Rating", page_icon="📢")
st.sidebar.header("Ad Rating")

if "participant_info" not in st.session_state or not st.session_state.participant_info:
    st.error("⚠️ Please complete the **Participant Information** page first.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
mongo_client = MongoClient(
    st.secrets["MONGODB_URI"],
    server_api=ServerApi('1')
)

# select database and collection
db = mongo_client["personalized_marketing_survey"]
collection = db["responses"]

if not st.session_state.ads:
    purchase_intent = st.session_state.participant_info.get("Purchase Intent", "").strip()
    # if item is mentioned in purchase intent question, it will be occasionally included in product advertisements
    if purchase_intent:
        product_list = f"t-shirts, shoes, hats, skincare, watches, phones, jacket, backpack, headphones, drinks, and occasionally the product they are currently interested in purchasing: {purchase_intent}."
    else:
        product_list = "t-shirts, shoes, hats, skincare, watches, phones, jacket, backpack, headphones, drinks."    
    prompt = f"""
    Generate 15 one-sentence personalized advertisements for these products: {product_list}
    Pick a random product for each advertisement you generate. 
    Personalize each ad using these features from the survey: {st.session_state.participant_info}
        
    Make the ads sophisticated, playful, and appealing.
    If including the name, feel free to use wordplay or puns.
    If including location, you can imply the location cleverly
    Tailor ads to match participant characteristics (age, gender) in either a subtle or stereotypical way.

        
    You don't have to strictly use all the details as-is; make the advertisement catchy and attractive (use emojis commonly found in advertisements, including 🔥 👀 ⚡️ ✨). The age doesn't have to be included if not relevant, but use it for creating relevant context. Change the structure/phrasing of each advertisement so the personalized features are not obvious. The features should not be right at the beginning of every advertisement. The creepiness should get higher as more features are included, and the ads will be concerningly more personalized

    Output 15 different advertisements in a JSON format. 4 of those will only use one personalised feature - Name, Age, Location, gender. 6 will use two features - (Name, Age), (Age, Location), (Name, Location) (Name, gender), (Age, gender), (Location, gender). 4 will use three features - (Name, Age, Gender), (Age, Location, Gender), (Name, Location, Gender), (Name, Age, Location). The last one will use all 4 features - (Name, Age, Location, Gender).

    Output as a JSON dictionary where the key is a comma-separated string of the features used (e.g. "Name,Location") and the value is the advertisement string. Strictly output valid JSON, no extra text.
    """
    with st.spinner("Generating personalized ads… this may take up to a minute… "):
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                    "role": "system", "content": "You are an expert marketing copywriter. Follow instructions carefully."},
                    {
                    "role": "user", "content": prompt, "instructions": "Use creativity, wordplay, and context from the participant info. Follow the constraints exactly. Output only valid JSON."}
                ],
            )
            ad_text = response.choices[0].message.content
            ads_json = json.loads(ad_text)
            st.session_state.ads = list(ads_json.values())
        except Exception as e:
            st.error(f"Ad generation failed: {e}")
            st.stop()

if "responses" not in st.session_state or isinstance(st.session_state.responses, list):
    st.session_state.responses = {}


# show ads
for i, ad_text in enumerate(st.session_state.ads):
    st.markdown(f"<h4 style='text-align:center'>{ad_text}</h4>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("Please rate this advertisement based on the following criteria:")

    # creepiness + personal relevance
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
           **How creepy is this ad?**   
                     
           1 = Not creepy at all → “This ad feels normal and not creepy.”  
           2 = Slightly creepy → “This ad feels mostly okay, with only mild creepiness.”  
           3 = Somewhat creepy → “This ad feels a little off, but not too bad.”  
           4 = Quite creepy → “This ad feels uncomfortably personal or intrusive.”  
           5 = Extremely creepy → “This ad feels very unsettling, invasive, or stalker-like.”  
           """)
        creepiness = st.slider("", 1, 5, 3, key=f"creepiness_{i}")

    with col2:
        st.markdown("""
           **How tailored is this ad to you?**   
                    
           1 = Not tailored at all → “This ad doesn’t feel related to me in any way.”  
           2 = Slightly tailored → “This ad seems vaguely related to me.”  
           3 = Somewhat tailored → “This ad has some clear connection to me.”  
           4 = Quite tailored → “This ad feels well-matched to me personally.”  
           5 = Extremely tailored → “This ad feels directly designed for me.”  
           """)
        personal_relevance = st.slider("", 1, 5, 3, key=f"personal_relevance_{i}")

    # click intention + purchase intention
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
           **How likely would you be to engage with this ad? (Clicking, taking a photo, talking with others, etc)**   
                    
           1 = Very unlikely → “Would definitely not engage.”   
           2 = Unlikely → “Probably wouldn’t engage.”   
           3 = Neutral / Maybe → “Might or might not engage.”   
           4 = Likely → “Would probably engage.”   
           5 = Very likely → “Would definitely engage.”  
           """)
        click_intention = st.slider("", 1, 5, 3, key=f"click_intention_{i}")

    with col4:
        st.markdown("""
           **Based on this advertisement, how likely are you to purchase this item?**   
           
           1 = Very unlikely → “I would definitely not buy this.”    
           2 = Unlikely → “I probably wouldn’t buy this.”   
           3 = Neutral → “I might or might not buy this.”   
           4 = Likely → “I would probably buy this.”   
           5 = Very likely → “I would definitely buy this.”  
           """)
        purchase_intention = st.slider("", 1, 5, 3, key=f"purchase_intention_{i}")

    # save to session state
    st.session_state.responses[str(i)] = {
        "ad": ad_text,
        "creepiness": creepiness,
        "personal_relevance": personal_relevance,
        "click_intention": click_intention,
        "purchase_intention": purchase_intention,
    }

# save all responses
try:
        collection.update_one(
            {"participant_info.Name": st.session_state.participant_info["Name"]},
            {"$set": {
                "participant_info": st.session_state.participant_info,
                "responses": list(st.session_state.responses.values())
            }},
            upsert=True
        )
except Exception as e:
        st.warning(f"MongoDB update failed: {e}")

st.success("You’ve completed the survey! 🎉 Thank you for your participation.")