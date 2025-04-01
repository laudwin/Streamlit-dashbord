import streamlit as st
import pandas as pd
import requests
import json

# --- Load the complaint dataset from uploaded file
DATA_PATH = "data.csv"
df = pd.read_csv(DATA_PATH)

df["engagement"] = pd.to_numeric(df["engagement"], errors='coerce')
df["sentiment"] = pd.to_numeric(df["sentiment"], errors='coerce')
df["published"] = pd.to_datetime(df["published"], errors='coerce')

# --- Gemini API Setup
GEMINI_API_KEY = "AIzaSyAgudPwVzXflapy0tbRg0nGCoffXe_9wgc"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def get_gemini_response(prompt):
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(API_URL, headers=headers, json=data)
    if res.status_code == 200:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return "⚠️ Gemini API error."

# --- Streamlit Interface
st.set_page_config(page_title="💬 Complaint Chatbot", layout="wide")
st.title("💬 Chat with Telkom Complaints")

# --- Chat History
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- Display Chat History
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- User Input
user_query = st.chat_input("Ask a question about customer complaints...")

if user_query:
    st.session_state.chat.append({"role": "user", "content": user_query})

    response = None
    lower_query = user_query.lower().strip()

    # --- Friendly Conversation Responses ---
    greetings = ["hi", "hello", "hey", "howdy"]
    if any(lower_query.startswith(greet) for greet in greetings):
        response = "👋 Hello! I'm your Telkom Complaints Assistant. You can ask me to search, summarize, or analyze Telkom customer feedback."
    elif "how are you" in lower_query:
        response = "😊 I'm just a bunch of code, but I'm always ready to help you explore Telkom complaints!"
    elif "what can you do" in lower_query or "help" in lower_query:
        response = (
            "🤖 I can help you:\n"
            "- 🔍 Search complaints by keyword\n"
            "- 📊 Summarize common themes\n"
            "- 📍 Find top cities or categories\n"
            "- 📈 Analyze engagement trends\n"
            "Just type a question to get started!"
        )

    # --- Keyword Search ---
    elif "search" in lower_query or "find" in lower_query:
        keyword = lower_query.split("search")[-1].strip() or lower_query.split("find")[-1].strip()
        matches = df[df["extract"].str.contains(keyword, case=False, na=False)]
        count = len(matches)
        response = f"🔎 Found **{count}** complaints containing '**{keyword}**' in the extract column."
        st.session_state.chat.append({"role": "assistant", "content": response})
        st.write(response)
        st.dataframe(matches[["published", "extract", "region.name", "city.name", "engagement"]], use_container_width=True)

    # --- Summary of Extracts ---
    elif "summary" in lower_query or "summarize" in lower_query:
        sample_texts = df["extract"].dropna().sample(min(20, len(df))).tolist()
        prompt = "Summarize the themes and concerns in the following Telkom customer complaints:\n" + "\n".join(f"- {t}" for t in sample_texts)
        response = get_gemini_response(prompt)

    # --- Top City ---
    elif "top city" in lower_query or "most complaints" in lower_query:
        top_city = df["city.name"].value_counts().idxmax()
        top_count = df["city.name"].value_counts().max()
        response = f"📍 The city with the most complaints is **{top_city}** with **{top_count}** posts."

    # --- Top Category ---
    elif "top category" in lower_query or "common issue" in lower_query:
        top_cat = df["category.label"].value_counts().idxmax()
        response = f"🏷️ The most common issue category is **{top_cat}**."

    # --- Average Engagement ---
    elif "average engagement" in lower_query:
        avg = df["engagement"].mean()
        response = f"📊 Average engagement per post is **{avg:.2f}**."

    # --- Fallback to Gemini using Extracts ---
    else:
        extract_sample = df.dropna(subset=["extract"]).sample(min(20, len(df)))
        combined = "\n".join(f"- {row}" for row in extract_sample["extract"])
        prompt = f"User asked: '{user_query}'. Answer based only on these Telkom customer complaints:\n{combined}"
        response = get_gemini_response(prompt)

    # --- Show Assistant Response ---
    if response:
        st.session_state.chat.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

# --- Footer ---
st.markdown("---")

footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    height: 5%;
    width: 100%;
    background-color: #243946;
    color: white;
    text-align: center;
    font-size: 14px;
}
.footer a {
    color: white;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>
<div class="footer">
    <p>Developed TISL | WIC | <a href="https://www.heflin.dev/" target="_blank">Visit Site</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
