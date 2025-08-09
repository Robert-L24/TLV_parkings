import streamlit as st
import pandas as pd
from utils import plot_avg_weekly

df = pd.read_csv("parkings_statuses.csv", parse_dates=["datetime"])
df.dropna(inplace=True)
status_map = {'available': 1, 'full': 0}
df['Probability to be available'] = df['parking_status'].map(status_map)

st.set_page_config(layout="wide")
st.title("TLV Parkings Availability vs Time")

# Multiselect for parking names
selected_names = st.multiselect("Plot Parkings:", list(df['parking_name'].unique()), default=['חניון שרתון'])

# Filter df by selected names
if selected_names:
    filtered_df = df[df['parking_name'].isin(selected_names)]
    # Loop over unique parking_ids in filtered df
    for parking_id in filtered_df['parking_id'].unique():
        parking = filtered_df[filtered_df['parking_id'] == parking_id]
        latest_prob = parking.sort_values('datetime')['Probability to be available'].iloc[-1]
        st.markdown(
            f"### {parking['parking_name'].iloc[0]} <span style='color:green; font-style: italic; font-size: 0.8em;'>(Probability now: {latest_prob:.2f})</span>",
            unsafe_allow_html=True)

        fig = plot_avg_weekly(parking, time_col='datetime', value_col='Probability to be available', time_interval=10)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please select at least one parking to display the plot.")
