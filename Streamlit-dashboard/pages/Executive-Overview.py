import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load dataset
df = pd.read_csv("data.csv")
df["engagement"] = pd.to_numeric(df["engagement"], errors='coerce')
df["sentiment"] = pd.to_numeric(df["sentiment"], errors='coerce')
df["published"] = pd.to_datetime(df["published"], errors='coerce')

st.set_page_config(page_title="📊 Executive Overview", layout="wide")
st.title("📊 Executive Overview")

# ===============================
with st.expander("💬 Voice of the Customer", expanded=True):
    st.subheader("Sentiment Distribution")
    sentiment_bins = pd.cut(df["sentiment"], bins=[-10, -0.1, 0.1, 10], labels=["Negative", "Neutral", "Positive"])
    sentiment_counts = sentiment_bins.value_counts().reset_index()
    sentiment_counts.columns = ["Sentiment", "Count"]

    fig_sentiment = px.pie(
        sentiment_counts,
        names="Sentiment",
        values="Count",
        title="Overall Sentiment Split",
        color="Sentiment",
        template="plotly_white"
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

# ===============================
with st.expander("📈 CX & Complaint Trends", expanded=True):
    st.subheader("Weekly Engagement Trend")
    df_valid = df.dropna(subset=["published", "engagement"])
    df_valid["Week"] = df_valid["published"].dt.to_period("W").astype(str)
    weekly = df_valid.groupby("Week")["engagement"].sum().reset_index()

    fig_trend = px.line(
        weekly,
        x="Week",
        y="engagement",
        title="Weekly Engagement Trend",
        markers=True,
        template="plotly_white"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ===============================
with st.expander("🏙️ Customer Pulse Tracker", expanded=True):
    st.subheader("Top Complaint Cities")
    top_cities = df["city.name"].value_counts().head(10).reset_index()
    top_cities.columns = ["City", "Count"]
    fig_cities = px.bar(
        top_cities,
        x="City",
        y="Count",
        title="Top 10 Cities with Highest Complaint Activity",
        color="Count",
        template="plotly_white"
    )
    st.plotly_chart(fig_cities, use_container_width=True)

# ===============================
with st.expander("📂 Engagement & Sentiment Insights", expanded=True):
    st.subheader("Average Sentiment by Complaint Category")
    sentiment_by_category = (
        df.groupby("category.label")["sentiment"]
        .mean()
        .reset_index()
        .sort_values(by="sentiment")
    )

    fig_category_sentiment = px.bar(
        sentiment_by_category,
        x="category.label",
        y="sentiment",
        title="Average Sentiment Score by Complaint Category",
        labels={"category.label": "Category", "sentiment": "Avg Sentiment"},
        template="plotly_white",
        color="sentiment"
    )
    fig_category_sentiment.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_category_sentiment, use_container_width=True)

# ===============================
with st.expander("📶 Brand Health Monitor", expanded=True):
    st.subheader("Customer Experience Index (CX Score)")

    avg_sentiment = df["sentiment"].mean(skipna=True)
    avg_engagement = df["engagement"].mean(skipna=True)
    avg_OTS = df["OTS"].mean(skipna=True) if "OTS" in df.columns else 0
    cx_score = round((avg_sentiment * 0.4 + avg_engagement * 0.4 + avg_OTS * 0.2), 2)

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cx_score,
        title={'text': "Overall CX Index"},
        gauge={
            'axis': {'range': [None, 4000]},
            'steps': [
                {'range': [0, 1000], 'color': "tomato"},
                {'range': [1000, 2000], 'color': "orange"},
                {'range': [2000, 3000], 'color': "lightgreen"},
                {'range': [3000, 4000], 'color': "seagreen"},
            ],
            'bar': {'color': "royalblue"}
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)

# ===============================
with st.expander("🧠 Customer Insights Dashboard", expanded=True):
    st.subheader("Engagement by Category and Region")

    # Engagement by category
    cat_avg = df.groupby("category.label")["engagement"].mean().reset_index()
    fig_cat = px.bar(
        cat_avg.sort_values(by="engagement", ascending=False),
        x="category.label",
        y="engagement",
        title="Avg Engagement by Category",
        template="plotly_white",
        color="engagement"
    )
    fig_cat.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_cat, use_container_width=True)

    # Engagement by region
    if "region.name" in df.columns:
        region_avg = df.groupby("region.name")["engagement"].mean().reset_index()
        fig_reg = px.bar(
            region_avg.sort_values(by="engagement", ascending=False),
            x="region.name",
            y="engagement",
            title="Avg Engagement by Region",
            template="plotly_white",
            color="engagement"
        )
        fig_reg.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_reg, use_container_width=True)

# ===============================
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
