import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("data.csv")

# Ensure datetime is parsed
df['published'] = pd.to_datetime(df['published'], errors='coerce')
df = df.dropna(subset=['published'])

# --- Platform Inference ---
def detect_platform(text):
    text = str(text).lower()
    if 'twitter.com' in text or '@' in text:
        return 'Twitter'
    if 'facebook.com' in text:
        return 'Facebook'
    return 'Unknown'

# Create a platform column based on extract or other logic
df['platform'] = df['extract'].apply(detect_platform)

# Extract hour
df['Hour'] = df['published'].dt.hour

# Group by hour and platform
hourly_usage = df.groupby(['Hour', 'platform']).size().reset_index(name='Count')

# UI
st.title("📈 Platform Usage Patterns")
st.subheader("Hourly Complaint Activity by Platform")

# Plot
fig_line = px.line(
    hourly_usage,
    x='Hour',
    y='Count',
    color='platform',
    title="Hourly Distribution of Posts by Platform",
    markers=True,
    template="plotly_white"
)
fig_line.update_layout(xaxis_title="Hour of Day (0-23)", yaxis_title="Number of Posts")

st.plotly_chart(fig_line, use_container_width=True)


#footer
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

