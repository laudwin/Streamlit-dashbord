import streamlit as st
import pandas as pd
import plotly.express as px

# Load your data
df = pd.read_csv("data.csv")

df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce")
df["engagement"] = pd.to_numeric(df["engagement"], errors="coerce")

st.title("📊 Telkom Social Media Complaint Insights")
st.markdown("""
Welcome to the executive dashboard. Get an overview of Telkom's social media engagement, complaint trends, and sentiment breakdown.
""")

# === Key Metrics
st.header("Key Insights at a Glance")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Complaints", df.shape[0])
with col2:
    avg_engagement = df["engagement"].mean()
    st.metric("Avg. Engagement", f"{avg_engagement:.2f}")
with col3:
    avg_sentiment = df["sentiment"].mean()
    st.metric("Avg. Sentiment", f"{avg_sentiment:.2f}")
with col4:
    top_category = df["category.label"].mode()[0]
    st.metric("Top Issue Category", top_category)

# === Breakdown by Region
if "region.name" in df.columns:
    st.header("📍 Complaints by Region")
    region_counts = df["region.name"].value_counts().reset_index()
    region_counts.columns = ["Region", "Count"]
    fig_region = px.bar(region_counts, x="Region", y="Count", title="Complaints per Region")
    st.plotly_chart(fig_region, use_container_width=True)

# === Sentiment Distribution
st.header("🧠 Sentiment Distribution")
sent_bins = pd.cut(df["sentiment"], bins=[-10, -0.1, 0.1, 10], labels=["Negative", "Neutral", "Positive"])
sent_counts = sent_bins.value_counts().reset_index()
sent_counts.columns = ["Sentiment", "Count"]
fig_sent = px.pie(sent_counts, names="Sentiment", values="Count", title="Overall Sentiment")
st.plotly_chart(fig_sent, use_container_width=True)

# === Footer


footer="""<style>
 

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
height:5%;
bottom: 0;
width: 100%;
background-color: #243946;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed TISL | WIC <a style='display: block; text-align: center;' href="https://www.heflin.dev/" target="_blank"></a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

