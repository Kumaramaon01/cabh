import streamlit as st
import json
import os
from monitor_data_points_24_hours.count_device_data_db import process_monitor_list, export_to_csv

st.set_page_config(page_title="24Hr Data Count", layout="wide")

st.title("📊 Monitor Data Points (Last 24 Hours)")

# Load JSON file
json_path = os.path.join("monitor_data_points_24_hours", "monitor_data.json")

if os.path.exists(json_path):
    try:
        with open(json_path, "r") as file:
            monitor_data = json.load(file)

        results = process_monitor_list(monitor_data)

        st.success("Data successfully processed!")

        # Display in Streamlit
        st.dataframe(results, use_container_width=True)

        # Export Button
        if st.button("📁 Export Report to CSV"):
            export_to_csv(results)
            st.success("Report exported successfully!")

    except json.JSONDecodeError:
        st.error("Invalid JSON format in monitor_data.json file.")
    except Exception as e:
        st.error(f"An unexpected error occurred:\n{str(e)}")
else:
    st.error("monitor_data.json file not found.")
