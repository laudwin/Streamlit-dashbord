import streamlit as st
import pandas as pd
from openai import AzureOpenAI

# --- Azure OpenAI Config
client = AzureOpenAI(
    api_key="db4c85906b5047419a733719992b649e",
    azure_endpoint="https://tisl-openaiservice.openai.azure.com",
    api_version="2025-01-01-preview"
)

DEPLOYMENT_NAME = "gpt-4o"

# --- Load dataset
DATA_PATH = "data.csv"
df_freq = pd.read_csv("PostIdFrequenceClean.csv")
data_df = pd.read_csv("data.csv")
df = pd.read_csv(DATA_PATH)
df["engagement"] = pd.to_numeric(df["engagement"], errors='coerce')
df["sentiment"] = pd.to_numeric(df["sentiment"], errors='coerce')
df["published"] = pd.to_datetime(df["published"], errors='coerce')

# --- Azure GPT Call
def ask_azure_openai(prompt, followup=False):
    try:
        system_message = "You are a Telkom complaints assistant."
        if followup:
            prompt = (
                f"Based on this user query:\n'{prompt}'\n"
                "Generate 3 helpful follow-up questions. "
                "Return only the questions as plain bullet points."
            )
            system_message = "You are a helpful assistant suggesting follow-up questions."

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- Streamlit UI Setup
st.set_page_config(page_title="💬 T-Know Bot", layout="wide")
st.title("💬 AskTelkom Bot")

if "chat" not in st.session_state:
    st.session_state.chat = []

# --- Check for click on a suggested follow-up
clicked_question = st.session_state.get("clicked_question", None)

# --- Display chat history
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Handle main input (typed OR clicked suggestion)
user_query = st.chat_input("Ask about Telkom complaints...")

# Prioritize clicked question
if clicked_question:
    user_query = clicked_question
    st.session_state.clicked_question = None  # reset it

if user_query:
    st.session_state.chat.append({"role": "user", "content": user_query})
    lower_query = user_query.lower().strip()
    response = None

    if any(lower_query.startswith(greet) for greet in ["hi", "hello", "hey"]):
        response = "👋 Hi! I'm your Telkom complaints assistant powered by Azure GPT-4o. How can I help today?"

    elif "summary" in lower_query or "summarize" in lower_query:
        samples = df["extract"].dropna().sample(min(15, len(df))).tolist()
        prompt = "Summarize the themes in these Telkom complaints:\n" + "\n".join(f"- {t}" for t in samples)
        response = ask_azure_openai(prompt)

    elif "search" in lower_query or "find" in lower_query:
        keyword = lower_query.split("search")[-1].strip() or lower_query.split("find")[-1].strip()
        matches = df[df["extract"].str.contains(keyword, case=False, na=False)]
        count = len(matches)
        response = f"🔍 Found **{count}** complaints containing '**{keyword}**'."
        st.session_state.chat.append({"role": "assistant", "content": response})
        st.write(response)
        st.dataframe(matches[["published", "extract", "region.name", "city.name", "engagement"]], use_container_width=True)

    elif "top city" in lower_query:
        top_city = df["city.name"].value_counts().idxmax()
        count = df["city.name"].value_counts().max()
        response = f"📍 Most complaints came from **{top_city}** ({count} posts)."

    elif "top category" in lower_query:
        top_cat = df["category.label"].value_counts().idxmax()
        response = f"🏷️ Most common complaint category is **{top_cat}**."

    elif "average engagement" in lower_query:
        avg = df["engagement"].mean()
        response = f"📊 The average post engagement is **{avg:.2f}**."

    else:
        sample_context = df["extract"].dropna().sample(min(15, len(df))).tolist()
        context = "\n".join(f"- {line}" for line in sample_context)
        prompt = f"User asked: '{user_query}'. Use this data to answer:\n{context}"
        response = ask_azure_openai(prompt)

    if response:
        st.session_state.chat.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

        # --- Generate AI-based suggestions
        followup_raw = ask_azure_openai(user_query, followup=True)
        suggestions = [q.strip("-• ") for q in followup_raw.split("\n") if q.strip()]
        
        if suggestions:
            st.markdown("### 💡 You can also ask:")
            for i, suggestion in enumerate(suggestions):
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state.clicked_question = suggestion
                    st.rerun()

# --- Styling & Footer
st.markdown("---")
st.markdown(
    """
    <style>
    button[kind="secondary"] {
        background-color: #e0f7fa !important;
        color: #007c91 !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem;
        border-radius: 8px;
    }
    </style>
    <div class="footer">
        <p>Powered by TISL WIC | AskTelkom Bot</p>
    </div>
    """,
    unsafe_allow_html=True,
)
