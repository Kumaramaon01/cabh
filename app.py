# app.py

import streamlit as st
import json
import os
from monitor_data_points_24_hours.count_device_data_db import process_monitor_list, export_to_csv

def main():
    st.title("📊 Monitor Data Points (Last 24 Hours)")
    json_path = os.path.join("monitor_data_points_24_hours", "monitor_data.json")

    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as file:
                monitor_data = json.load(file)
            results = process_monitor_list(monitor_data)
            st.success("Data successfully processed!")
            st.dataframe(results, use_container_width=True)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in monitor_data.json file.")
        except Exception as e:
            st.error(f"An unexpected error occurred:\n{str(e)}")
    else:
        st.error("monitor_data.json file not found.")
