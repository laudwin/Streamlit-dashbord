import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("data.csv")

df["engagement"] = pd.to_numeric(df["engagement"], errors='coerce')
df["sentiment"] = pd.to_numeric(df["sentiment"], errors='coerce')

st.title("📊 Overview: Telkom Complaint Demographics")

# === Filters
st.subheader("Filter by Region & Gender")
selected_regions = st.multiselect("Select Region", options=df['region.name'].dropna().unique(), default=df['region.name'].dropna().unique())
selected_genders = st.multiselect("Select Gender", options=df['gender.label'].dropna().unique(), default=df['gender.label'].dropna().unique())

filtered_df = df[
    df['region.name'].isin(selected_regions) &
    df['gender.label'].isin(selected_genders)
]

# === Gender Breakdown
st.subheader("👤 Gender Distribution")
gender_counts = filtered_df['gender.label'].value_counts()
fig_gender = px.pie(gender_counts, names=gender_counts.index, values=gender_counts.values, title="Complaints by Gender")
st.plotly_chart(fig_gender, use_container_width=True)

# === Region Breakdown
st.subheader("📍 Complaints by Region")
region_counts = filtered_df['region.name'].value_counts()
fig_region = px.bar(region_counts, x=region_counts.index, y=region_counts.values, title="Complaints by Region")
st.plotly_chart(fig_region, use_container_width=True)

# === City Breakdown
st.subheader("🏙️ Complaints by City")
city_counts = filtered_df['city.name'].value_counts().nlargest(10)
fig_city = px.bar(city_counts, x=city_counts.index, y=city_counts.values, title="Top 10 Cities by Complaint Volume")
st.plotly_chart(fig_city, use_container_width=True)

# === Sentiment Distribution
st.subheader("🧠 Sentiment")
sentiment_bins = pd.cut(filtered_df["sentiment"], [-10, -0.1, 0.1, 10], labels=["Negative", "Neutral", "Positive"])
sentiment_counts = sentiment_bins.value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Count"]
fig_sentiment = px.pie(sentiment_counts, names="Sentiment", values="Count", title="Customer Sentiment")
st.plotly_chart(fig_sentiment, use_container_width=True)

# === Footer
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
<p>Developed TISL | WIC <a style='display: block; text-align: center;' href="https://www.heflin.dev/" target="_blank"></a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
