import streamlit as st
import json
import os
from io import BytesIO
import pandas as pd
from monitor_data_points_24_hours.count_device_data_db import process_monitor_list, export_to_csv

def main():
    st.markdown("<h4>📊 Monitor Data Points (Last 24 Hours)</h4>", unsafe_allow_html=True)
    json_path = os.path.join("monitor_data_points_24_hours", "monitor_data.json")

    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as file:
                monitor_data = json.load(file)

            results = process_monitor_list(monitor_data)

            # ✅ Ensure it's a DataFrame
            if isinstance(results, list):
                results = pd.DataFrame(results)

            st.success("Data successfully processed!")
            st.dataframe(results, use_container_width=True)

            # ✅ Convert to CSV for download
            csv = results.to_csv(index=False).encode('utf-8')

            # 📥 Download button
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="results.csv",
                mime="text/csv"
            )
        except json.JSONDecodeError:
            st.error("Invalid JSON format in monitor_data.json file.")
        except Exception as e:
            st.error(f"An unexpected error occurred:\n{str(e)}")
    else:
        st.error("monitor_data.json file not found.")

