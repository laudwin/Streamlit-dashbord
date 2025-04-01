import streamlit as st

def city_insights():
    st.title("📍 City Insights")

    if "selected_city" not in st.session_state:
        st.warning("No city selected. Please go back and click a city bar.")
        st.stop()

    selected_city = st.session_state["selected_city"]
    st.markdown(f"### Showing insights for **{selected_city}**")

    # Filter your dataframe and show relevant data
    city_df = df_selection[df_selection["city.name"] == selected_city]

    st.write(f"Total Posts: {len(city_df)}")
    st.write(f"Total Engagement: {city_df['engagement'].sum()}")

    # Add more graphs/tables based on city_df
