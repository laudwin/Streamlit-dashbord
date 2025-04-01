import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(page_title="📍 Activity & Engagement", layout="wide")
st.title("📍 Engagement Overview")

# Load dataset safely
df = pd.read_csv("data.csv")

# Convert numeric columns
df["engagement"] = pd.to_numeric(df["engagement"], errors="coerce")
df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce")
df["OTS"] = pd.to_numeric(df["OTS"], errors="coerce")

# ========================
# 1. Engagement by City
# ========================
st.subheader("🏙️ Engagement by City")
engagement_by_city = (
    df.groupby("city.name")["engagement"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .dropna()
)

fig_city = px.bar(
    engagement_by_city.head(10),
    x="city.name",
    y="engagement",
    title="Top 10 Cities by Engagement",
    labels={"city.name": "City", "engagement": "Engagement"},
    color="engagement",
    template="plotly_white"
)
st.plotly_chart(fig_city, use_container_width=True)

# ========================
# 2. Activity by Category
# ========================
st.subheader("📂 Activity by Category")
category_counts = df["category.label"].value_counts(dropna=True).reset_index()
category_counts.columns = ["Category", "Count"]

fig_cat = px.pie(
    category_counts,
    names="Category",
    values="Count",
    title="Distribution of Activity by Category",
    template="plotly_white"
)
st.plotly_chart(fig_cat, use_container_width=True)

# ========================
# 3. Sentiment Distribution
# ========================
st.subheader("🧠 Sentiment Distribution")
sentiment_counts = df["sentiment"].dropna().round(1).value_counts().reset_index()
sentiment_counts.columns = ["Sentiment Score", "Count"]
sentiment_counts = sentiment_counts.sort_values("Sentiment Score")

fig_sent = px.bar(
    sentiment_counts,
    x="Sentiment Score",
    y="Count",
    title="Sentiment Score Distribution",
    template="plotly_white"
)
st.plotly_chart(fig_sent, use_container_width=True)

# ========================
# 4. OTS by Region
# ========================
st.subheader("📡 OTS (Opportunity To See) by Region")
ots_by_region = (
    df.groupby("region.name")["OTS"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .dropna()
)

fig_ots = px.bar(
    ots_by_region.head(10),
    x="region.name",
    y="OTS",
    title="Top Regions by OTS",
    labels={"region.name": "Region", "OTS": "OTS"},
    color="OTS",
    template="plotly_white"
)
st.plotly_chart(fig_ots, use_container_width=True)


# Footer
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
