import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import re
from collections import Counter
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(page_title="Facebook Post Comments Dashboard", page_icon="💬", layout="wide")

# Load datasets
df = pd.read_csv("PostComments.csv")
df_freq = pd.read_csv("PostIdFrequenceClean.csv")
data_df = pd.read_csv("data.csv")

# Clean and prepare main comment data
df.rename(columns={"PostText": "extract", "PublishedDate": "published"}, inplace=True)
df["published"] = pd.to_datetime(df["published"], errors='coerce')
data_df["published"] = pd.to_datetime(data_df["published"], errors='coerce')

def is_customer_comment(text):
    text = str(text).lower()
    promo_keywords = ["deal", "buy", "order", "shop", "save", "promotion", "call me"]
    if len(text.strip()) < 10:
        return False
    if any(promo in text for promo in promo_keywords):
        return False
    return True

df = df[df["extract"].apply(is_customer_comment)]

# Issue classification
def classify_issue(text):
    text = str(text).lower()
    if re.search(r"invoice|charge|billing|refund|cancel|account", text):
        return "Billing"
    elif re.search(r"network|signal|coverage|slow|disconnect|data", text):
        return "Network"
    elif re.search(r"help|support|service|response|ignored|agent", text):
        return "Support"
    elif re.search(r"upgrade|purchase|delivery|order", text):
        return "Purchase"
    else:
        return "Other"

df["issue"] = df["extract"].apply(classify_issue)
data_df["issue"] = data_df["extract"].apply(classify_issue)
df["comment_length"] = df["extract"].apply(lambda x: len(str(x)))
data_df["comment_length"] = data_df["extract"].apply(lambda x: len(str(x)))

# Session state defaults
if "selected_postid" not in st.session_state:
    st.session_state.selected_postid = None
if "selected" not in st.session_state:
    st.session_state.selected = "Overview"

# Sidebar navigation
with st.sidebar:
    selected = st.selectbox("📌 Choose View", [
        "Overview", "Keyword Search", "Word Cloud", "Top Words",
        "Issue Analysis", "Comment Stats", "Post Details", "All Data Insights"
    ], index=[
        "Overview", "Keyword Search", "Word Cloud", "Top Words",
        "Issue Analysis", "Comment Stats", "Post Details", "All Data Insights"
    ].index(st.session_state.selected))
    st.session_state.selected = selected

st.title("💬 Facebook Post Comments Dashboard")

# Overview
if st.session_state.selected == "Overview":
    st.header("🕒 Comments Over Time")
    comments_by_date = df.groupby(df["published"].dt.date).size().reset_index(name="count")
    fig_time = px.line(comments_by_date, x="published", y="count", markers=True, title="Number of Comments per Day")
    st.plotly_chart(fig_time, use_container_width=True)

    st.header("🏷️ Most Active Post IDs")
    top_posts = df["PostId"].value_counts().reset_index()
    top_posts.columns = ["PostId", "Count"]
    for _, row in top_posts.head(10).iterrows():
        if st.button(f"🔗 View Post: {row['PostId']}"):
            st.session_state.selected_postid = row['PostId']
            st.session_state.selected = "Post Details"
            st.rerun()

    st.markdown("### 🔁 Top Posts by Engagement Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig1 = px.bar(df_freq.sort_values("ReplyToCount", ascending=False).head(10), x="PostId", y="ReplyToCount", title="Top Posts by Replies")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(df_freq.sort_values("ReshareCount", ascending=False).head(10), x="PostId", y="ReshareCount", title="Top Posts by Reshares")
        st.plotly_chart(fig2, use_container_width=True)
    with col3:
        fig3 = px.bar(df_freq.sort_values("TotalFKReferences", ascending=False).head(10), x="PostId", y="TotalFKReferences", title="Top Posts by Total Engagement")
        st.plotly_chart(fig3, use_container_width=True)

# Post Details
if st.session_state.selected == "Post Details" and st.session_state.selected_postid:
    post_id = st.session_state.selected_postid
    post_df = df[df["PostId"] == post_id]
    freq_row = df_freq[df_freq["PostId"] == post_id].squeeze()
    st.subheader(f"✍🏻 Post Details: {post_id}")
    st.write(f"Total Comments: {len(post_df)}")

    if not freq_row.empty:
        st.metric("💬 Replies", freq_row["ReplyToCount"])
        st.metric("🔁 Reshares", freq_row["ReshareCount"])
        st.metric("📊 Total Engagements", freq_row["TotalFKReferences"])

    st.markdown("### 📰 Post Summary")
    st.info("""
The discussion regarding the Telkom social media post offering a 120GB Anytime + 120GB Night data deal for R249 per month is quite varied and somewhat contentious. The main themes observed include:

- **Interest in the Deal**: Many users express interest in the deal and request additional information about the specifics, such as whether it includes a router, how the night data works, and whether it's a prepaid or postpaid offer.
- **Application and Delivery Issues**: A number of users mention issues with applying for the deal or not receiving their sim cards. There's a general sentiment of frustration due to lack of communication and follow-up from Telkom.
- **Network Coverage and Quality**: Many users express dissatisfaction with Telkom's network coverage and internet connection quality. Several users mention wanting to switch back to other providers due to these issues.
- **Customer Service**: Negative feedback about Telkom’s customer service is quite prevalent. Users report unresolved issues, delays in responses, and perceived neglect from the company.
- **Contract and Billing Concerns**: Some users express concerns about contract terms, including potential hidden costs, the need for payslips and bank statements, and issues with their current billing.
- **Spam**: There are instances of unrelated promotional messages and spamming within the discussion.

**Overall**, the sentiment is mixed with a slight tilt towards negative due to issues with network coverage, customer service, and application/delivery processes. There are, however, positive sentiments from users who find the deal attractive and express interest in it. A noteworthy observation is that some users confuse the offer as "limitless" data due to the initial post's wording, leading to some confusion and disappointment.
""")

    #st.markdown("### 📏 Comment Length Distribution")
    #fig_len = px.histogram(post_df, x="comment_length", nbins=20, title="Comment Lengths for This Post")
    #st.plotly_chart(fig_len, use_container_width=True)

    #st.markdown("### 📋 Comments")
    #st.dataframe(post_df[["published", "extract"]], use_container_width=True)

    # Additional Visuals for Post Details
    

    st.markdown("### 📝 Post Metadata")
    post_meta = post_df[["PostId", "extract", "published"]].drop_duplicates().rename(columns={
        "extract": "PostText",
        "published": "PublishedDate"
    })
    st.dataframe(post_meta, use_container_width=True)

    # Visual comparison of selected post vs. others
    st.markdown("### 🌐 Interaction Comparison with Top Posts")
    top_compare = df_freq.sort_values("TotalFKReferences", ascending=False).head(10).copy()
    top_compare["Selected"] = top_compare["PostId"].apply(lambda x: "Selected" if x == post_id else "Other")
    fig_compare = px.bar(
        top_compare,
        x="PostId",
        y="TotalFKReferences",
        color="Selected",
        title="Comparison of Total Engagements with Top Posts",
        color_discrete_map={"Selected": "red", "Other": "steelblue"}
    )
    st.plotly_chart(fig_compare, use_container_width=True)


    st.markdown("### 🔁 Top Posts by Engagement Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig1 = px.bar(df_freq.sort_values("ReplyToCount", ascending=False).head(10), x="PostId", y="ReplyToCount", title="Top Posts by Replies")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(df_freq.sort_values("ReshareCount", ascending=False).head(10), x="PostId", y="ReshareCount", title="Top Posts by Reshares")
        st.plotly_chart(fig2, use_container_width=True)
    with col3:
        fig3 = px.bar(df_freq.sort_values("TotalFKReferences", ascending=False).head(10), x="PostId", y="TotalFKReferences", title="Top Posts by Total Engagement")
        st.plotly_chart(fig3, use_container_width=True)






    

# Full Data Analysis
elif st.session_state.selected == "All Data Insights":
    st.header("📊 Telkom Data Insights (Full Dataset)")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📈 Total Engagement", int(data_df["engagement"].sum()))
        st.metric("🧠 Average Sentiment", round(data_df["sentiment"].mean(), 2))
    with col2:
        st.metric("📣 Total OTS", int(data_df["OTS"].sum()))
        st.metric("📝 Total Posts", len(data_df))

    st.subheader("Hourly Complaint Activity")
    data_df["hour"] = pd.to_datetime(data_df["published"], errors='coerce').dt.hour
    hourly_counts = data_df.groupby("hour").size().reset_index(name="count")
    fig_hour = px.bar(hourly_counts, x="hour", y="count", title="Complaints by Hour of Day")
    st.plotly_chart(fig_hour, use_container_width=True)

    st.subheader("Engagement Trend Over Time")
    daily_engage = data_df.groupby(data_df["published"].dt.date)["engagement"].sum().reset_index()
    fig_eng = px.line(daily_engage, x="published", y="engagement", title="Engagement Trend")
    st.plotly_chart(fig_eng, use_container_width=True)

    st.subheader("Sentiment Analysis")
    sentiment_counts = data_df["sentiment"].apply(lambda x: "Positive" if x > 0 else "Negative" if x < 0 else "Neutral")
    sentiment_summary = sentiment_counts.value_counts().reset_index()
    sentiment_summary.columns = ["Sentiment", "Count"]
    fig_sent = px.bar(sentiment_summary, x="Sentiment", y="Count", color="Sentiment", title="Sentiment Distribution")
    st.plotly_chart(fig_sent, use_container_width=True)

    st.subheader("Classified Issues in Comments")
    issue_counts = data_df["issue"].value_counts().reset_index()
    issue_counts.columns = ["Issue Type", "Count"]
    fig_issues = px.bar(issue_counts, x="Issue Type", y="Count", title="Issue Classification", color="Count")
    st.plotly_chart(fig_issues, use_container_width=True)

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