import mysql.connector
import pandas as pd
import streamlit as st

def get_Data():
    # Streamlit inputs
    input_data_type = st.selectbox("Select data type", ["0 (School Data)", "1 (Outdoor Data)"])
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")
    input_device_ID = st.text_input("Enter the device ID")
    data_interval = st.selectbox("Select data interval", ["1min", "15min", "hour"])
    
    # Convert inputs
    if input_data_type == "0 (School Data)":
        table_name = {
            "1min": "reading_db",
            "15min": "reading_15min",
            "hour": "reading_hour"
        }.get(data_interval, None)
    elif input_data_type == "1 (Outdoor Data)":
        table_name = {
            "1min": "cpcb_data",
            "15min": "cpcb_15min",
            "hour": "cpcb_hour"
        }.get(data_interval, None)
    else:
        st.error("Invalid data type. Exiting.")
        return

    if table_name is None:
        st.error("Invalid data interval. Exiting.")
        return

    datetime_column = "datetime"
    query = f"""
        SELECT * FROM {table_name}
        WHERE deviceID = %s 
          AND DATE({datetime_column}) BETWEEN %s AND %s;
    """

    try:
        # Database credentials
        connection = mysql.connector.connect(
            host="139.59.34.149",
            user="neemdb",
            password="(#&pxJ&p7JvhA7<B",
            database="cabh_iaq_db"
        )
        data_frame = pd.read_sql(query, connection, params=(input_device_ID, start_date, end_date))
        
        output_filename = f"{'SchoolData' if input_data_type == '0 (School Data)' else 'OutdoorData'}_{input_device_ID}_{start_date}_to_{end_date}.csv"
        
        # Export the data to CSV
        data_frame.to_csv(output_filename, index=False)
        st.success(f"Data extracted and saved to {output_filename}")
    
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if connection.is_connected():
            connection.close()
