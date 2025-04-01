import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
data = pd.read_csv("data.csv")
#df = pd.read_csv("data.csv", encoding="utf-8", errors="replace")


# Page config
st.set_page_config(page_title="Social Media Addiction Insights", page_icon="📊", layout="wide")

# Title
st.title("📊 Social Media Addiction Insights")
st.markdown("""
Welcome to the Social Media Insights! Explore trends, addiction levels, and usage patterns across platforms like TikTok, Instagram, Facebook, and YouTube.
""")

# Key Metrics Section
st.header("Key Insights at a Glance")
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_users = data.shape[0]
    st.metric("Total Users", total_users)
with col2:
    avg_income = data["Income"].mean()
    st.metric("Average Income ($)", f"{avg_income:,.2f}")
with col3:
    avg_addiction = data["Addiction Level"].mean()
    st.metric("Average Addiction Level", f"{avg_addiction:.2f}")
with col4:
    most_used_platform = data["Platform"].mode()[0]
    st.metric("Most Used Platform", most_used_platform)

# Optional: Watch Reasons by Platform
watch_reason_counts = data.groupby(["Platform", "Watch Reason"]).size().reset_index(name="Count")
fig_watch_reason = px.bar(
    watch_reason_counts,
    x="Platform",
    y="Count",
    color="Watch Reason",
    title="Watch Reasons by Platform",
    barmode="stack",
    template="plotly_white"
)
st.plotly_chart(fig_watch_reason, use_container_width=True)

# User Engagement Section
st.header("🔍 Dive Deeper")
st.markdown("Use the chatbot to get personalized insights!")

# Footer
st.markdown("---")

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
<p>Developed by Laudwin <a style='display: block; text-align: center;' href="https://www.heflin.dev/" target="_blank"></a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

