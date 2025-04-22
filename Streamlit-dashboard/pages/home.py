import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# --- Streamlit Config ---
st.set_page_config(page_title="Issue Dashboard", layout="wide")

# --- SQL Server Connection ---
database = 'VerbatimData'
uid = 'someadmin'
pwd = 'Gx9#vTq2Lm'
odbc_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:sqlserverlogical.database.windows.net,1433;"
    f"Database={database};Uid={uid};Pwd={pwd};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)
connect_str = 'mssql+pyodbc:///?odbc_connect=' + quote_plus(odbc_str)
engine = create_engine(connect_str)

# --- Load Data from SQL Server ---
#df = pd.read_sql("SELECT * FROM dbo.Post WHERE PostText IS NOT NULL AND Published IS NOT NULL", con=engine)
df = pd.read_sql("""SELECT PostText, Published
                    FROM dbo.Post
                    WHERE PostText IS NOT NULL
                    AND Published BETWEEN '2025-01-01' AND '2025-02-28'
                    AND Duplicate = 0
                    AND AIclassification = 2
                    AND ContentTypeId > 1;""", con=engine)
df.rename(columns={"PostText": "extract", "Published": "published"}, inplace=True)
df["published"] = pd.to_datetime(df["published"], errors='coerce')

# --- Feature Engineering ---
df = df.dropna(subset=["published"])
df["month"] = df["published"].dt.strftime("%b")
df["day"] = df["published"].dt.strftime("%b %d")

# --- Classification Function ---
def classify_issue(text):
    text = str(text).lower()
    if any(x in text for x in ["billing", "debit", "charge", "refund", "penalty", "contract", "cancel", "account"]):
        return "Billing"
    elif any(x in text for x in ["network", "data", "signal", "coverage", "outage", "disconnect", "speed"]):
        return "Network"
    elif any(x in text for x in ["support", "response", "resolve", "rude", "ignored", "agent"]):
        return "Support"
    elif any(x in text for x in ["delivery", "sim card", "not receive", "delay", "wait"]):
        return "Delivery Issues"
    elif any(x in text for x in ["upgrade", "device", "router", "purchase"]):
        return "Product Upgrade"
    elif any(x in text for x in ["application", "apply", "approval"]):
        return "Application Issues"
    elif any(x in text for x in ["spam", "unrelated", "ads", "promotion"]):
        return "Spam / Promotions"
    elif any(x in text for x in ["login", "access", "portal", "website"]):
        return "Access Issues"
    return "Uncategorized"

df["customer_issue"] = df["extract"].apply(classify_issue)

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("### ⏳ Date Filters")
    start_date = st.date_input("Start date", value=datetime(2022, 1, 1).date())
    end_date = st.date_input("End date", value=datetime.today().date())
    interval = st.selectbox("Interval", ["Day", "Week", "Month", "Quarter"])

if start_date > end_date:
    st.warning("⚠️ Start date must be before end date.")
    st.stop()

# --- Apply Date Filter ---
df = df[df["published"].dt.date.between(start_date, end_date)]

# --- Metrics ---
st.title("📊 Complaint Themes Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("📬 Total Posts", len(df))
col2.metric("💬 Total Comments", "N/A")
col3.metric("📌 Post IDs Tracked", "N/A")

# --- Issue Patterns ---
issue_patterns = {
    "Support": {"No response": r"no response", "Agreeing to resolve": r"resolve", "Rude service": r"rude|ignored"},
    "Network": {"Outage": r"outage", "Unable to use data": r"unable to use data", "Data Expiry": r"expired"},
    "Billing": {"Undue charges": r"undue", "Penalty": r"penalty", "Contract": r"contract", "Cancellation": r"cancel", "Debt collection": r"debit|billing"}
}

# --- CSS Styling ---
st.markdown("""
<style>
.card {background-color: #f9f9f9; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.1); text-align: center; font-size: 0.95rem; margin: 0.2rem;}
.card-title {font-weight: bold; font-size: 0.85rem; color: #444;}
.card-count {font-size: 1.25rem; color: #2c3e50;}
.chart-box {background-color: #fff; border-radius: 0.5rem; box-shadow: 0 4px 10px rgba(0,0,0,0.07); transition: transform 0.2s ease, box-shadow 0.2s ease; padding: 1rem; margin-bottom: 1.5rem;}
.chart-box:hover {transform: translateY(-4px); box-shadow: 0 6px 16px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# --- Summary Cards ---
st.markdown("### 📋 Overall Issue Counts")
issue_counts = df["customer_issue"].value_counts().reset_index()
issue_counts.columns = ["Issue", "Count"]
cols = st.columns(4)
for idx, row in issue_counts.iterrows():
    cols[idx % 4].markdown(f"""
        <div class='card'>
            <div class='card-title'>{row['Issue']}</div>
            <div class='card-count'>{int(row['Count'])}</div>
        </div>""", unsafe_allow_html=True)

# --- Chart Functions ---
def stacked_bar_chart(df, category, patterns, title):
    df_sub = df[df["customer_issue"] == category].copy()
    for label, pattern in patterns.items():
        df_sub[label] = df_sub["extract"].str.contains(pattern, case=False, na=False)
    agg = df_sub.groupby("month")[[*patterns.keys()]].sum().reset_index()
    fig = go.Figure()
    for sub in patterns:
        fig.add_trace(go.Bar(x=agg["month"], y=agg[sub], name=sub, hoverinfo='x+y+name'))
    fig.update_layout(barmode="stack", title=title, template="plotly_white", height=350, hovermode="x unified")
    return fig

def billing_volume_chart(df):
    df_billing = df[df["customer_issue"] == "Billing"].copy()
    df_billing["day"] = df_billing["published"].dt.strftime("%b %d")
    for label, pattern in issue_patterns["Billing"].items():
        df_billing[label] = df_billing["extract"].str.contains(pattern, case=False, na=False)
    agg = df_billing.groupby("day")[[*issue_patterns["Billing"].keys()]].sum().reset_index()
    fig = go.Figure()
    for sub in issue_patterns["Billing"]:
        fig.add_trace(go.Bar(x=agg["day"], y=agg[sub], name=sub, hoverinfo='x+y+name'))
    fig.update_layout(barmode="stack", title="Billing Sub-Issues Over Time", template="plotly_white", height=350, hovermode="x unified")
    return fig

def theme_sunburst(df):
    def get_sub_theme(text):
        text = str(text).lower()
        for keyword, label in {
            "penalty": "Penalty", "contract": "Contract", "cancel": "Cancellation", "refund": "Refund",
            "debit": "Debt collection", "resolve": "Agreeing to resolve", "no response": "No response",
            "data": "Data Expiry", "rude": "Rude service", "ignored": "Rude service"
        }.items():
            if keyword in text: return label
        return "Miscellaneous"

    df["theme"] = df["customer_issue"]
    df["sub_theme"] = df["extract"].apply(get_sub_theme)
    sun_df = df.groupby(["theme", "sub_theme"]).size().reset_index(name="count")
    fig = px.sunburst(sun_df, path=["theme", "sub_theme"], values="count", color="theme", template="plotly_white", height=450)
    return fig

# --- Render Charts ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Customer Support Issues")
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    st.plotly_chart(stacked_bar_chart(df, "Support", issue_patterns["Support"], "Customer Support Issues"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.subheader("Network Issues")
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    st.plotly_chart(stacked_bar_chart(df, "Network", issue_patterns["Network"], "Network Issues"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Billing Issues Breakdown")
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    st.plotly_chart(billing_volume_chart(df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.subheader("Theme and Sub-Themes")
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    st.plotly_chart(theme_sunburst(df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer remains unchanged



# --- Footer ---
footer = """
<style>
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
st.markdown(footer, unsafe_allow_html=True)
