"""
Run with: streamlit run visualize.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import time, timedelta


def plot_avg_weekly(
        df,
        time_col,
        value_col,
        start_day="Sunday",
        time_interval=10
):
    """
    Plot weekly average values in custom time intervals.

    Parameters:
    - df: pandas DataFrame
    - time_col: column name with datetime values
    - value_col: numeric column to average
    - start_day: first day of week ("Sunday", "Monday", etc.)
    - time_interval: interval in minutes (e.g., 10, 15, 30)
    """
    colors = {1: 'green', 0: 'red', 'other': 'orange'}
    # --- Step 1: Prepare input data ---
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    df["weekday"] = df[time_col].dt.dayofweek  # Monday=0, Sunday=6
    df["weekday_name"] = df[time_col].dt.day_name()
    df["time_of_day"] = df[time_col].dt.floor(f"{time_interval}min").dt.time

    # --- Step 2: Aggregate averages ---
    avg_df = (
        df.groupby(["weekday", "weekday_name", "time_of_day"])[value_col]
        .mean()
        .reset_index()
    )

    # --- Step 3: Determine day order ---
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_index = day_names.index(start_day)
    day_names = day_names[start_index:] + day_names[:start_index]
    day_order = [(i + start_index) % 7 for i in range(7)]

    # --- Step 4: Generate full weekly grid ---
    def generate_time_slots(minutes):
        slots = []
        t = timedelta(minutes=0)
        while t < timedelta(days=1):
            slots.append(time(hour=t.seconds // 3600, minute=(t.seconds // 60) % 60))
            t += timedelta(minutes=minutes)
        return slots

    all_times = generate_time_slots(time_interval)

    full_grid = pd.DataFrame(
        [(day, day_names[day_order.index(day)], tod) for day in day_order for tod in all_times],
        columns=["weekday", "weekday_name", "time_of_day"]
    )
    full_grid["weekday"] = pd.Categorical(full_grid["weekday"], categories=day_order, ordered=True)

    # --- Step 5: Merge with actual averages ---
    merged = full_grid.merge(avg_df, on=["weekday", "weekday_name", "time_of_day"], how="left")
    merged["x_index"] = range(len(merged))

    # Hover text
    merged["hover"] = (
            "Day: " + merged["weekday_name"] +
            "<br>Time: " + merged["time_of_day"].astype(str) +
            "<br>Average: " + merged[value_col].round(3).astype(str)
    )

    # --- Step 6: Create Plotly figure ---
    fig = go.Figure()

    # Background shading per day
    day_length = len(all_times)
    for i, day in enumerate(day_names):
        fig.add_vrect(
            x0=i * day_length - 0.5,
            x1=(i + 1) * day_length - 0.5,
            fillcolor="lightgrey" if i % 2 == 0 else "white",
            opacity=0.08,
            layer="below",
            line_width=0
        )

    # Average line
    fig.add_trace(go.Scatter(
        x=merged["x_index"],
        y=merged[value_col],
        mode="lines",
        name="Average",
        line=dict(color="blue", width=2),
        text=merged["hover"],
        hoverinfo="text"
    ))

    # Day labels on x-axis
    tick_positions = [i * day_length + day_length / 2 for i in range(len(day_names))]
    fig.update_xaxes(
        tickvals=tick_positions,
        ticktext=day_names,
        tickangle=0
    )

    # Layout styling
    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title=value_col,
        template="plotly_white",
        margin=dict(l=40, r=20, t=60, b=60)
    )

    # --- Step 7: Show in Streamlit ---
    st.plotly_chart(fig, use_container_width=True)


df = pd.read_csv("parkings_statuses.csv", parse_dates=["datetime"])
df.dropna(inplace=True)
status_map = {'available': 1, 'full': 0}
df['availability'] = df['parking_status'].map(status_map)

st.set_page_config(layout="wide")
st.title("TLV Parkings Availability vs Time")
for parking_id in df['parking_id'].unique():
    parking = df[df['parking_id'] == parking_id]
    st.subheader(parking['parking_name'].iloc[0])

    plot_avg_weekly(parking, time_col='datetime', value_col='availability', time_interval=10)
