import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import mysql.connector
from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import threading
import plotly.io as pio
import pymysql
from io import BytesIO
import base64
from PIL import Image
import io
from plotly.subplots import make_subplots
import sqlite3

# Set page layout to wide and title
st.set_page_config(
    page_title="Data Extraction and Visualization of IAQ Monitors",
    page_icon="📊",
    layout='wide',
    menu_items={                          
        'Get Help': 'https://cabh-visualization.streamlit.app/',
        'Report a bug': 'https://www.example.com/bug',
        'About': '# This is an **eQuest Utilities** application!'
    }
)

st.markdown("""
    <h1 style='text-align: center; font-size: 34px; background: linear-gradient(90deg, green, green, green, green, green, green, green);
    -webkit-background-clip: text;
    color: transparent;'>
    Data Extraction and Visualization of IAQ Monitors</h1>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Your updated CSS here */
    .stApp [class*="stIcon"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

button_style = """
    <style>
        .stButton>button {
            box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.8);
        }
    </style>
"""

st.markdown("""
        <style>
        .stButton button {
            height: 30px;
            width: 166px;
        }
        </style>
    """, unsafe_allow_html=True)

if 'script_choice' not in st.session_state:
    st.session_state.script_choice = "people"  # Set default to "about"

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button('People EDS'):
        st.session_state.script_choice = "people"
with col2:
    if st.button('Extract Data'):
        st.session_state.script_choice = "data"
with col3:
    if st.button('Analytics'):
        st.session_state.script_choice = "visual"
with col4:
    if st.button('Device Data Details'):
        st.session_state.script_choice = "abdullah_work"
with col5:
    if st.button('Monthly Trends'):
        st.session_state.script_choice = "monthly_trends"

# Set the default selected date to one day before the current date
default_date = datetime.now() - timedelta(days=1)
#Based on the user selection, display appropriate input fields and run the script
if st.session_state.script_choice == "people":
    host = "139.59.34.149"
    user = "neemdb"
    password = "(#&pxJ&p7JvhA7<B"
    database = "cabh_iaq_db"

    # Input fields for device IDs and date range
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_date = st.date_input("Select Date", value=default_date)
    with col2:
        time_interval = st.selectbox("⏰ Select Time Interval", ['1min', '15min', 'hour'], index=0)
    with col3:
        people = st.selectbox("Select People", ['Gurneet', 'Piyush', 'Sheetal', 'Lakshmi', 'Mariyam', 'Abhishek', 'Surender', 'Robin', 'Hines', 'EDS D Block', 'Nidhi', 'Manpreet', 'TT', 'Hisham'], index=0)
    
    # Initialize device IDs based on the selected person
    if people == 'Gurneet':
        id1 = '1203240077'  # Gurneet Mannat Room
        id2 = '1203240076'  # Gurneet Prabhash Room
        id3 = 'DELDPCC014'
    elif people == 'Piyush':
        id1 = '1201240079'  # Piyush Bedroom
        id2 = '1201240085'  # Piyush Living Room
        id3 = 'DELDPCC014'
    elif people == 'Sheetal':
        id1 = '1203240083'  # Sheetal Living Room
        id2 = '1203240083'  # Add more IDs if necessary
        id3 = 'DELDPCC014'
    elif people == 'Lakshmi':
        id1 = '1201240072'  # Lakshmi Living Room
        id2 = '1201240077'  # Lakshmi Kitchen
        id3 = 'DELDPCC014'
    elif people == 'Mariyam':
        id1 = '1202240027'  # Mariyam Bedroom 1
        id2 = '1202240011'  # Mariyam Living Room
        id3 = 'DELDPCC014'
    elif people == 'Abhishek':
        id1 = '1201240074'  # Abhishek Living Room
        id2 = '1203240080'  # Abhishek Bedroom
        id3 = 'DELDPCC014'
    elif people == 'Surender':
        id1 = '1212230160'  # Surender Bedroom
        id2 = '1201240076'  # Surender Living Room
        id3 = 'DELDPCC014'
    elif people == 'Robin':
        id1 = '1202240009'  # Robin Bedroom
        id2 = '1202240008'  # Robin Living Room
        id3 = 'DELDPCC014'
    elif people == 'Hines':
        id1 = '1201240075'  # Hines Office 1
        id2 = '1201240078'  # Hines Office 2
        id3 = 'DELDPCC014'
    elif people == 'EDS D Block':
        id1 = '1202240025'
        id2 = '1202240026'
        id3 = 'DELDPCC014'
    elif people == 'Hisham':
        id1 = '1203240076'
        id2 = '1203240078'
        id3 = 'DELDPCC014'
    elif people == 'TT':
        id1 = '1201240073'
        id2 = '1201240073'
        id3 = 'DELDPCC014'
    elif people == 'Nidhi': # Bedroom
        id1 = '1203240073'
        id2 = '1203240073'
        id3 = 'DELDPCC014'
    elif people == 'Manpreet': # Drawing
        id1 = '1203240072'
        id2 = '1203240072'
        id3 = 'DELDPCC014'
        
    # Convert Streamlit date input to string format for SQL query
    start_date_str = selected_date.strftime('%Y-%m-%d')  # Correct this to use selected_date
    end_date_str = selected_date.strftime('%Y-%m-%d')  # No change needed if only one day is selected

    connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    engine = create_engine(connection_string)

    # Determine the table name based on the selected interval for Indoor data
    if time_interval == '1min':
        table_name = "reading_db"
        table_name_O = "cpcb_data"
    elif time_interval == '15min':
        table_name = "reading_15min"
        table_name_O = "cpcb_data"
    elif time_interval == 'hour':
        table_name = "reading_hour"

    # SQL query to fetch indoor data for the specified deviceID and date range
    query_indoor = f"""  
        SELECT * FROM {table_name}
        WHERE DATE(datetime) BETWEEN '{start_date_str}' AND '{end_date_str}';
    """

    # SQL query to fetch indoor data for the specified deviceID and date range
    query_outdoor = f"""  
        SELECT * FROM {table_name_O}
        WHERE DATE(datetime) BETWEEN '{start_date_str}' AND '{end_date_str}';
    """

    # Fetch data from the database into DataFrames
    df = pd.read_sql(query_indoor, engine)
    df1 = pd.read_sql(query_outdoor, engine)
    # connection.close()
    engine.dispose()

    if df.empty:
        st.warning("No data available for the selected date and time interval.")
    else:
        # Proceed with visualizing data
        try:    
            if time_interval == "1min" or time_interval == "15min" or time_interval == "hour":
                # Ensure 'deviceID' column is treated as string and remove any leading/trailing spaces
                df['deviceID'] = df['deviceID'].astype(str).str.strip()
                df1['deviceID'] = df1['deviceID'].astype(str).str.strip()
                
                # Defining different rooms' data
                Gurneet_Mannat_Room = df[df['deviceID'] == id1].copy()
                Gurneet_Prabhash_Room = df[df['deviceID'] == id2].copy() if id2 else None
                Gurneet_Outdoor = df1[df1['deviceID'] == id3].copy() if id3 else None

                # Correcting datetime formats
                Gurneet_Mannat_Room['datetime'] = pd.to_datetime(Gurneet_Mannat_Room['datetime'], format='%Y-%m-%d %H:%M')
                Gurneet_Prabhash_Room['datetime'] = pd.to_datetime(Gurneet_Prabhash_Room['datetime'], format='%Y-%m-%d %H:%M')
                Gurneet_Outdoor['datetime'] = pd.to_datetime(Gurneet_Outdoor['datetime'], format='%Y-%m-%d %H:%M')

                # Set 'datetime' as the DataFrame index
                Gurneet_Mannat_Room.set_index('datetime', inplace=True)
                Gurneet_Prabhash_Room.set_index('datetime', inplace=True)
                Gurneet_Outdoor.set_index('datetime', inplace=True)

                # Sort the index for each dataframe
                Gurneet_Mannat_Room = Gurneet_Mannat_Room.sort_index()
                Gurneet_Prabhash_Room = Gurneet_Prabhash_Room.sort_index()
                Gurneet_Outdoor = Gurneet_Outdoor.sort_index()

                # Convert selected date to datetime and define the time range for filtering
                start_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 00:00:00'
                end_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 23:59:00'

                # Filter each dataframe to get the values for the 24-hour period
                gurneet_mannat_pm25 = Gurneet_Mannat_Room.loc[start_time:end_time, 'pm25']
                gurneet_prabhash_pm25 = Gurneet_Prabhash_Room.loc[start_time:end_time, 'pm25']
                gurneet_outdoor_pm25 = Gurneet_Outdoor.loc[start_time:end_time, 'pm25']

                gurneet_mannat_pm10 = Gurneet_Mannat_Room.loc[start_time:end_time, 'pm10']
                gurneet_prabhash_pm10 = Gurneet_Prabhash_Room.loc[start_time:end_time, 'pm10']
                gurneet_outdoor_pm10 = Gurneet_Outdoor.loc[start_time:end_time, 'pm10']

                gurneet_mannat_voc = Gurneet_Mannat_Room.loc[start_time:end_time, 'voc']
                gurneet_prabhash_voc = Gurneet_Prabhash_Room.loc[start_time:end_time, 'voc']
                gurneet_outdoor_voc = Gurneet_Outdoor.loc[start_time:end_time, 'voc']

                gurneet_mannat_co2 = Gurneet_Mannat_Room.loc[start_time:end_time, 'co2']
                gurneet_prabhash_co2 = Gurneet_Prabhash_Room.loc[start_time:end_time, 'co2']
                gurneet_outdoor_co2 = Gurneet_Outdoor.loc[start_time:end_time, 'co2']

                gurneet_mannat_temp = Gurneet_Mannat_Room.loc[start_time:end_time, 'temp']
                gurneet_prabhash_temp = Gurneet_Prabhash_Room.loc[start_time:end_time, 'temp']
                gurneet_outdoor_temp = Gurneet_Outdoor.loc[start_time:end_time, 'temp']

                gurneet_mannat_hum = Gurneet_Mannat_Room.loc[start_time:end_time, 'humidity']
                gurneet_prabhash_hum = Gurneet_Prabhash_Room.loc[start_time:end_time, 'humidity']
                gurneet_outdoor_hum = Gurneet_Outdoor.loc[start_time:end_time, 'humidity']

                fig1, fig2, fig3, fig4, fig5, fig6 = go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

                if people == 'Gurneet':
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Prabhash Room', line=dict(color='violet')))
                    fig1.add_trace(go.Scatter(x=gurneet_outdoor_pm25.index, y=gurneet_outdoor_pm25, mode='lines', name='Outdoor', line=dict(color='green')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Prabhash Room PM10', line=dict(color='violet')))
                    fig2.add_trace(go.Scatter(x=gurneet_outdoor_pm10.index, y=gurneet_outdoor_pm10, mode='lines', name='Outdoor', line=dict(color='green')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Prabhash Room', line=dict(color='violet')))
                    fig3.add_trace(go.Scatter(x=gurneet_outdoor_voc.index, y=gurneet_outdoor_voc, mode='lines', name='Outdoor', line=dict(color='green')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Prabhash Room', line=dict(color='violet')))
                    fig4.add_trace(go.Scatter(x=gurneet_outdoor_co2.index, y=gurneet_outdoor_co2, mode='lines', name='Outdoor', line=dict(color='green')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Prabhash Room', line=dict(color='violet')))
                    fig5.add_trace(go.Scatter(x=gurneet_outdoor_temp.index, y=gurneet_outdoor_temp, mode='lines', name='Outdoor', line=dict(color='green')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Prabhash Room', line=dict(color='violet')))
                    fig6.add_trace(go.Scatter(x=gurneet_outdoor_temp.index, y=gurneet_outdoor_hum, mode='lines', name='outdoor', line=dict(color='green')))
                
                elif people == "Piyush":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Living', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Living', line=dict(color='violet')))
                
                elif people == "Robin":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Living', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Living', line=dict(color='violet')))
                
                elif people == "Surender":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Living', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Living', line=dict(color='violet')))
                
                elif people == "EDS D Block":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Conference', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Conference', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Conference', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Conference', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Conference', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Conference', line=dict(color='violet')))
                
                elif people == "Piyush":
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='red')))
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='red')))
                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='red')))
                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
            
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='red')))
                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Living', line=dict(color='blue')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Bedroom', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Living', line=dict(color='blue')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Bedroom', line=dict(color='violet')))
            
                elif people == "Lakshmi":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Living', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Living', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Living', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Living', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Living', line=dict(color='blue')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Living', line=dict(color='blue')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Kitchen', line=dict(color='violet')))
            
                elif people == "Manpreet":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Bedroom', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Bedroom', line=dict(color='violet')))
            
                elif people == "Nidhi":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Bedroom', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Bedroom', line=dict(color='violet')))
                
                elif people == "TT": # Home
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Home', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Home', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Home', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Home', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Home', line=dict(color='blue')))
                    # fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Bedroom', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Home', line=dict(color='blue')))
                    # fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Bedroom', line=dict(color='violet')))

                elif people == "Sheetal": # Home
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Living', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Living', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Living', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Living', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Living', line=dict(color='blue')))
                    # fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Bedroom', line=dict(color='violet')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Living', line=dict(color='blue')))
                    # fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Bedroom', line=dict(color='violet')))

                elif people == "Hisham":
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='red')))
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='red')))
                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='red')))
                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
            
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='red')))
                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='Living', line=dict(color='red')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='Bedroom', line=dict(color='blue')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='Living', line=dict(color='red')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='Bedroom', line=dict(color='blue')))
            
                elif people == "Mariyam":
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='BR1', line=dict(color='red')))
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='LR1', line=dict(color='blue')))
                    
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='BR1', line=dict(color='red')))
                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='LR1', line=dict(color='blue')))
                    
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='BR1', line=dict(color='red')))
                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='LR1', line=dict(color='blue')))
            
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='BR1', line=dict(color='red')))
                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='LR1', line=dict(color='blue')))

                    fig5.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_temp, mode='lines', name='BR1', line=dict(color='red')))
                    fig5.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_temp, mode='lines', name='LR1', line=dict(color='blue')))

                    fig6.add_trace(go.Scatter(x=gurneet_mannat_temp.index, y=gurneet_mannat_hum, mode='lines', name='BR1', line=dict(color='red')))
                    fig6.add_trace(go.Scatter(x=gurneet_prabhash_temp.index, y=gurneet_prabhash_hum, mode='lines', name='LR1', line=dict(color='blue')))

                # Define threshold lines
                threshold_lines = [(25, 'PM2.5', fig1), (50, 'PM10', fig2), (500, 'VOC', fig3), (1000, 'CO2', fig4), (24, 'Temp', fig5), (60, 'Humidity', fig6)]
                
                # Loop through threshold lines and create plots
                for threshold, name, fig in threshold_lines:
                    fig.add_trace(go.Scatter(
                        x=[start_time, end_time], y=[threshold, threshold],
                        mode="lines", line=dict(color="black", width=2, dash="dot"),
                        name=f"Threshold {name}"
                    ))
            
                for fig, title in zip([fig1, fig2, fig3, fig4, fig5, fig6], ['PM2.5', 'PM10', 'VOC', 'CO2', 'Temp', 'Humidity']):
                    yaxis_title = (
                        f'{title} Concentration (ppm)' if title == 'CO2' 
                        else f'{title} Temperature (°C)' if title == 'Temp' 
                        else f'{title} Concentration (%)' if title == 'Humidity'
                        else f'{title} Concentration (µg/m³)'
                    )
                    fig.update_layout(
                        title=f'🔴 {title} Levels in Various Locations',
                        xaxis_title='Date & Time',
                        yaxis_title=yaxis_title,
                        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5),
                        hovermode='x unified',
                        # xaxis=dict(domain=[0, 0.8])
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
                threshold_lines = [(25, 'PM2.5', fig1), (50, 'PM10', fig2), (500, 'VOC', fig3), (1000, 'CO2', fig4), (24, 'Temp', fig5), (60, 'Humidity', fig6)]
                conn = sqlite3.connect('remarks.db')
                c = conn.cursor()
                try:
                    c.execute('ALTER TABLE remarks ADD COLUMN date TEXT')
                except sqlite3.OperationalError:
                    pass

                c.execute('''
                    CREATE TABLE IF NOT EXISTS remarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user TEXT,
                        remark TEXT,
                        date TEXT
                    )
                ''')
                def add_remark(user, remark, date):
                    c.execute('INSERT INTO remarks (user, remark, date) VALUES (?, ?, ?)', (user, remark, date))
                    conn.commit()

                def update_remark(user, new_remark, date):
                    c.execute('UPDATE remarks SET remark = ?, date = ? WHERE user = ? AND date = ?', (new_remark, date, user, date))
                    conn.commit()

                def get_user_remarks(user, date):
                    c.execute('SELECT remark, date FROM remarks WHERE user = ? AND date = ?', (user, date))
                    return c.fetchall()  

                date_str = selected_date.strftime("%Y-%m-%d") 
                existing_remarks = get_user_remarks(people, date_str)
                if existing_remarks:
                    st.write(f"Existing remarks for {people} on {date_str}:")
                    for remark, date in existing_remarks:
                        st.write(f"- {remark}")
                else:
                    st.write(f"No remarks found for {people} on {date_str}. You can add a new one.")
            
                # Expander for adding or updating remarks
                with st.expander("Add or View Remark"):
                    # Define the placeholder text
                    placeholder_text = "PM2.5 - \n\npm10 - \n\nVOC - \n\nCO2 - \n\nTemperature - \n\nHumidity - "
                    remark_input = st.text_area(
                        "Enter your remark",
                        value=existing_remarks[-1][0] if existing_remarks else placeholder_text,
                        height = 300
                    )
                
                    # Save Remark button
                    if st.button("Save Remark"):
                        if existing_remarks:
                            update_remark(people, remark_input, date_str)
                            st.success(f"Remark updated for {people} on {date_str}!")
                        else:
                            add_remark(people, remark_input, date_str)
                            st.success(f"Remark added for {people} on {date_str}!")
            
                # Close the database connection
                conn.close()
        
        except Exception as e:
            st.info(f"🚨 Please upload right file for choosen Time Interval!")

if st.session_state.script_choice == "data":
    # Database credentials
    host = "139.59.34.149"
    user = "neemdb"
    password = "(#&pxJ&p7JvhA7<B"
    database = "cabh_iaq_db"

    # Input data type selection using a select_slider
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        input_data_type = st.select_slider(
            "Select Data Type",
            options=['Indoor Data', 'Outdoor Data'])
    with col2:
        input_device_ID = st.text_input("Enter the Device ID")
    with col3:
        start_date = st.date_input("Select Start Date", datetime.now())
    with col4:
        end_date = st.date_input("Select End Date", datetime.now())
    with col5:
        table_name = st.selectbox("Select Data Interval", ['1min', '15min', 'hour'])
    # Convert Streamlit date input to string format for SQL query
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    from monitor_data_range.device_data_analysis import calculate_data_metrics
    if input_device_ID:
        installation_date, expected, actual, percent = calculate_data_metrics(input_device_ID)

        if installation_date:
            st.markdown("#### 📊 Data Availability Analysis")
            
            # Display in 2 columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🛠️ Installation Date:**")
                st.write(installation_date.strftime('%Y-%m-%d %H:%M:%S'))

                st.markdown("**📈 Expected Data Points:**")
                st.write(f"{expected:,}")  # comma-separated

            with col2:
                st.markdown("**📉 Actual Data Points:**")
                st.write(f"{actual:,}")  # comma-separated

                st.markdown("**✅ Data Collection %:**")
                st.write(f"{percent:.2f}%")
        else:
            st.warning("⚠️ No valid installation date found for this device.")
    else:
        st.warning("⚠️ Please enter a valid **Device ID** to view records.")

    # Validate inputs and execute on button click
    if st.button('Fetch Data'):
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
    
        # Determine the table name based on the data type and interval
        if input_data_type == 'Indoor Data':
            if table_name == '1min':
                table_name = "reading_db"
            elif table_name == '15min':
                table_name = "reading_15min"
            elif table_name == 'hour':
                table_name = "reading_hour"
        elif input_data_type == 'Outdoor Data':
            if table_name == '1min':
                table_name = "cpcb_data"
            elif table_name == '15min':
                table_name = "cpcb_15min"
            elif table_name == 'hour':
                table_name = "cpcb_hour"
    
        # SQL query to fetch data for the specified deviceID and date range
        query = f"""
            SELECT * FROM {table_name}
            WHERE deviceID = '{input_device_ID}' 
              AND DATE(datetime) BETWEEN '{start_date}' AND '{end_date}';
        """
    
        # Fetch data from the database
        data_frame = pd.read_sql(query, connection)
    
        # Define output filename based on the input type and dates
        if input_data_type == 'School Data':
            output_filename = f"SchoolData_{input_device_ID}_{start_date}_to_{end_date}.csv"
        else:
            output_filename = f"OutdoorData_{input_device_ID}_{start_date}_to_{end_date}.csv"
    
        # Display success message and allow the user to download the CSV
        if not data_frame.empty:
            st.write(f"Data extracted for Device ID: {input_device_ID} from {start_date} to {end_date}")
            st.write(f"Saving as {output_filename}")
            st.dataframe(data_frame)
    
            # Streamlit download button
            csv = data_frame.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=output_filename,
                mime='text/csv',
            )
        else:
            st.write("No data found for the specified inputs.")
    
        # Close the connection
        connection.close()

if st.session_state.script_choice == "abdullah_work":
    from app import main  # assuming app.py has a `main()` function
    try:
        main()
    except Exception as e:
        print(f"Failed to run script!!")
    
#Based on the user selection, display appropriate input fields and run the script
if st.session_state.script_choice == "visual":

    start_date = datetime(datetime.now().year, 7, 1).date()
    end_date = datetime.now().date()
    col1, col2 = st.columns(2)
    with col1:
        time_interval = st.selectbox("⏰ Select Time Interval", ['1min', '15min', 'hour'], index=0)
    with col2:
        selected_date = st.date_input("📅 Select Date", value=datetime(2024, 9, 17).date())
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file1 = st.file_uploader("Upload Indoor File", type=["csv"])
    with col2:
        uploaded_file2 = st.file_uploader("Upload Outdoor File", type=["csv"])

    # Convert Streamlit date input to string format for SQL query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Determine the table name based on the selected interval for Indoor data
    if uploaded_file1 and uploaded_file2:
        if time_interval == '1min':
            df = pd.read_csv(uploaded_file1)
            df1 = pd.read_csv(uploaded_file2)
        elif time_interval == '15min':
            df = pd.read_csv(uploaded_file1)
            df1 = pd.read_csv(uploaded_file2)
        elif time_interval == 'hour':
            df = pd.read_csv(uploaded_file1)
            df1 = pd.read_csv(uploaded_file2)

        # Proceed with visualizing data without re-reading it from CSV
        try:   
            if time_interval == "1min" and not df.empty and not df1.empty:
                # Ensure 'deviceID' column is treated as string and remove any leading/trailing spaces
                df['deviceID'] = df['deviceID'].astype(str).str.strip()
                df1['deviceID'] = df1['deviceID'].astype(str).str.strip()
                
                # Create individual dataframes based on deviceID
                SepClassroom = df[df['deviceID'] == '1202240029'].copy()
                SepCompLab = df[df['deviceID'] == '1202240010'].copy()
                SepLibrary = df[df['deviceID'] == '1202240028'].copy()
                SepChemLab = df[df['deviceID'] == '1202240012'].copy()
                Sepcpcb = df1[df1['deviceID'] == 'DELDPCC016'].copy()
                
                # Convert 'datetime' to proper datetime format
                SepClassroom['datetime'] = pd.to_datetime(SepClassroom['datetime'], format='%d-%m-%Y %H:%M')
                SepLibrary['datetime'] = pd.to_datetime(SepLibrary['datetime'], format='%d-%m-%Y %H:%M')
                SepChemLab['datetime'] = pd.to_datetime(SepChemLab['datetime'], format='%d-%m-%Y %H:%M')
                SepCompLab['datetime'] = pd.to_datetime(SepCompLab['datetime'], format='%d-%m-%Y %H:%M')
                Sepcpcb['datetime'] = pd.to_datetime(Sepcpcb['datetime'], format='%d-%m-%Y %H:%M')
                
                # Set 'datetime' as the DataFrame index
                SepClassroom.set_index('datetime', inplace=True)
                SepLibrary.set_index('datetime', inplace=True)
                SepChemLab.set_index('datetime', inplace=True)
                SepCompLab.set_index('datetime', inplace=True)
                Sepcpcb.set_index('datetime', inplace=True)
                
                # Sort the index for each dataframe
                SepClassroom = SepClassroom.sort_index()
                SepLibrary = SepLibrary.sort_index()
                SepChemLab = SepChemLab.sort_index()
                SepCompLab = SepCompLab.sort_index()
                Sepcpcb = Sepcpcb.sort_index()
            
                # Convert selected date to datetime and define the time range for filtering
                start_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 00:00:00'
                end_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 23:59:00'
                
                # Filter each dataframe to get the values for the 24-hour period
                classroom_pm25 = SepClassroom.loc[start_time:end_time, 'pm25']
                library_pm25 = SepLibrary.loc[start_time:end_time, 'pm25']
                chemlab_pm25 = SepChemLab.loc[start_time:end_time, 'pm25']
                complab_pm25 = SepCompLab.loc[start_time:end_time, 'pm25']
                cpcb_pm25 = Sepcpcb.loc[start_time:end_time, 'pm25']
                
                classroom_pm10 = SepClassroom.loc[start_time:end_time, 'pm10']
                library_pm10 = SepLibrary.loc[start_time:end_time, 'pm10']
                chemlab_pm10 = SepChemLab.loc[start_time:end_time, 'pm10']
                complab_pm10 = SepCompLab.loc[start_time:end_time, 'pm10']
                cpcb_pm10 = Sepcpcb.loc[start_time:end_time, 'pm10']
                
                classroom_voc = SepClassroom.loc[start_time:end_time, 'voc']
                library_voc = SepLibrary.loc[start_time:end_time, 'voc']
                chemlab_voc = SepChemLab.loc[start_time:end_time, 'voc']
                complab_voc = SepCompLab.loc[start_time:end_time, 'voc']
                cpcb_voc = Sepcpcb.loc[start_time:end_time, 'voc']
                
                classroom_co2 = SepClassroom.loc[start_time:end_time, 'co2']
                library_co2 = SepLibrary.loc[start_time:end_time, 'co2']
                chemlab_co2 = SepChemLab.loc[start_time:end_time, 'co2']
                complab_co2 = SepCompLab.loc[start_time:end_time, 'co2']
                cpcb_co2 = Sepcpcb.loc[start_time:end_time, 'co2']
            
                # Create a new figure
                fig1 = go.Figure()
                fig2 = go.Figure()
                fig3 = go.Figure()
                fig4 = go.Figure()
                
                # Add traces for each dataframe with specified colors
                fig1.add_trace(go.Scatter(x=classroom_pm25.index, y=classroom_pm25, mode='lines', name='Classroom', line=dict(color='blue')))
                fig1.add_trace(go.Scatter(x=library_pm25.index, y=library_pm25, mode='lines', name='Library', line=dict(color='violet')))
                fig1.add_trace(go.Scatter(x=chemlab_pm25.index, y=chemlab_pm25, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig1.add_trace(go.Scatter(x=complab_pm25.index, y=complab_pm25, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig1.add_trace(go.Scatter(x=cpcb_pm25.index, y=cpcb_pm25, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig2.add_trace(go.Scatter(x=classroom_pm10.index, y=classroom_pm10, mode='lines', name='Classroom', line=dict(color='blue')))
                fig2.add_trace(go.Scatter(x=library_pm10.index, y=library_pm10, mode='lines', name='Library', line=dict(color='violet')))
                fig2.add_trace(go.Scatter(x=chemlab_pm10.index, y=chemlab_pm10, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig2.add_trace(go.Scatter(x=complab_pm10.index, y=complab_pm10, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig2.add_trace(go.Scatter(x=cpcb_pm10.index, y=cpcb_pm10, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig3.add_trace(go.Scatter(x=classroom_voc.index, y=classroom_voc, mode='lines', name='Classroom', line=dict(color='blue')))
                fig3.add_trace(go.Scatter(x=library_voc.index, y=library_voc, mode='lines', name='Library', line=dict(color='violet')))
                fig3.add_trace(go.Scatter(x=chemlab_voc.index, y=chemlab_voc, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig3.add_trace(go.Scatter(x=complab_voc.index, y=complab_voc, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig3.add_trace(go.Scatter(x=cpcb_voc.index, y=cpcb_voc, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig4.add_trace(go.Scatter(x=classroom_co2.index, y=classroom_co2, mode='lines', name='Classroom', line=dict(color='blue')))
                fig4.add_trace(go.Scatter(x=library_co2.index, y=library_co2, mode='lines', name='Library', line=dict(color='violet')))
                fig4.add_trace(go.Scatter(x=chemlab_co2.index, y=chemlab_co2, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig4.add_trace(go.Scatter(x=complab_co2.index, y=complab_co2, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig4.add_trace(go.Scatter(x=cpcb_co2.index, y=cpcb_co2, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                # Add a horizontal dotted line at PM2.5 threshold of 25 (with black color)
                fig1.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[25, 25],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 25"
                ))
                
                fig2.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[50, 50],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 50"
                ))
                
                fig3.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[500, 500],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 500"
                ))
                
                fig4.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[1000, 1000],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 1000"
                ))
                
                # Update layout for all figures with titles
                fig1.update_layout(
                    title='🔴 PM2.5 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='PM2.5 Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig2.update_layout(
                    title='🔴 PM10 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='PM10 Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig3.update_layout(
                    title='🔴 VOC Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='VOC Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig4.update_layout(
                    title='🔴 CO2 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='CO2 Concentration  (ppm)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                # Display figures
                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.plotly_chart(fig3, use_container_width=True)
                st.plotly_chart(fig4, use_container_width=True)
            
            # 15 MIN
            elif time_interval == "15min" and not df.empty and not df1.empty:
                df['deviceID'] = df['deviceID'].astype(str).str.strip()
                df1['deviceID'] = df1['deviceID'].astype(str).str.strip()
            
                # Create individual dataframes based on deviceID
                SepClassroom = df[df['deviceID'] == '1202240029']
                SepCompLab = df[df['deviceID'] == '1202240010']
                SepLibrary = df[df['deviceID'] == '1202240028']
                SepChemLab = df[df['deviceID'] == '1202240012']
                Sepcpcb = df1[df1['deviceID'] == 'DELDPCC016']
                
                # Convert 'datetime' to proper datetime format
                SepClassroom['datetime'] = pd.to_datetime(SepClassroom['datetime'], format='%d-%m-%Y %H:%M')
                SepLibrary['datetime'] = pd.to_datetime(SepLibrary['datetime'], format='%d-%m-%Y %H:%M')
                SepChemLab['datetime'] = pd.to_datetime(SepChemLab['datetime'], format='%d-%m-%Y %H:%M')
                SepCompLab['datetime'] = pd.to_datetime(SepCompLab['datetime'], format='%d-%m-%Y %H:%M')
                Sepcpcb['datetime'] = pd.to_datetime(Sepcpcb['datetime'], format='%d-%m-%Y %H:%M')
                
                # Set 'datetime' as the DataFrame index
                SepClassroom.set_index('datetime', inplace=True)
                SepLibrary.set_index('datetime', inplace=True)
                SepChemLab.set_index('datetime', inplace=True)
                SepCompLab.set_index('datetime', inplace=True)
                Sepcpcb.set_index('datetime', inplace=True)
                
                # Sort the index for each dataframe
                SepClassroom = SepClassroom.sort_index()
                SepLibrary = SepLibrary.sort_index()
                SepChemLab = SepChemLab.sort_index()
                SepCompLab = SepCompLab.sort_index()
                Sepcpcb = Sepcpcb.sort_index()
            
                # Convert selected date to datetime and define the time range for filtering
                start_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 00:00:00'
                end_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 23:59:00'
                
                # Filter each dataframe to get the values for the 24-hour period
                classroom_pm25 = SepClassroom.loc[start_time:end_time, 'avg_pm25']
                library_pm25 = SepLibrary.loc[start_time:end_time, 'avg_pm25']
                chemlab_pm25 = SepChemLab.loc[start_time:end_time, 'avg_pm25']
                complab_pm25 = SepCompLab.loc[start_time:end_time, 'avg_pm25']
                cpcb_pm25 = Sepcpcb.loc[start_time:end_time, 'pm25']
                
                classroom_pm10 = SepClassroom.loc[start_time:end_time, 'avg_pm10']
                library_pm10 = SepLibrary.loc[start_time:end_time, 'avg_pm10']
                chemlab_pm10 = SepChemLab.loc[start_time:end_time, 'avg_pm10']
                complab_pm10 = SepCompLab.loc[start_time:end_time, 'avg_pm10']
                cpcb_pm10 = Sepcpcb.loc[start_time:end_time, 'pm10']
                
                classroom_voc = SepClassroom.loc[start_time:end_time, 'avg_voc']
                library_voc = SepLibrary.loc[start_time:end_time, 'avg_voc']
                chemlab_voc = SepChemLab.loc[start_time:end_time, 'avg_voc']
                complab_voc = SepCompLab.loc[start_time:end_time, 'avg_voc']
                cpcb_voc = Sepcpcb.loc[start_time:end_time, 'voc']
                
                classroom_co2 = SepClassroom.loc[start_time:end_time, 'avg_co2']
                library_co2 = SepLibrary.loc[start_time:end_time, 'avg_co2']
                chemlab_co2 = SepChemLab.loc[start_time:end_time, 'avg_co2']
                complab_co2 = SepCompLab.loc[start_time:end_time, 'avg_co2']
                cpcb_co2 = Sepcpcb.loc[start_time:end_time, 'co2']
            
                # Create a new figure
                fig1 = go.Figure()
                fig2 = go.Figure()
                fig3 = go.Figure()
                fig4 = go.Figure()
                
                # Add traces for each dataframe with specified colors
                fig1.add_trace(go.Scatter(x=classroom_pm25.index, y=classroom_pm25, mode='lines', name='Classroom', line=dict(color='blue')))
                fig1.add_trace(go.Scatter(x=library_pm25.index, y=library_pm25, mode='lines', name='Library', line=dict(color='violet')))
                fig1.add_trace(go.Scatter(x=chemlab_pm25.index, y=chemlab_pm25, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig1.add_trace(go.Scatter(x=complab_pm25.index, y=complab_pm25, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig1.add_trace(go.Scatter(x=cpcb_pm25.index, y=cpcb_pm25, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig2.add_trace(go.Scatter(x=classroom_pm10.index, y=classroom_pm10, mode='lines', name='Classroom', line=dict(color='blue')))
                fig2.add_trace(go.Scatter(x=library_pm10.index, y=library_pm10, mode='lines', name='Library', line=dict(color='violet')))
                fig2.add_trace(go.Scatter(x=chemlab_pm10.index, y=chemlab_pm10, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig2.add_trace(go.Scatter(x=complab_pm10.index, y=complab_pm10, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig2.add_trace(go.Scatter(x=cpcb_pm10.index, y=cpcb_pm10, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig3.add_trace(go.Scatter(x=classroom_voc.index, y=classroom_voc, mode='lines', name='Classroom', line=dict(color='blue')))
                fig3.add_trace(go.Scatter(x=library_voc.index, y=library_voc, mode='lines', name='Library', line=dict(color='violet')))
                fig3.add_trace(go.Scatter(x=chemlab_voc.index, y=chemlab_voc, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig3.add_trace(go.Scatter(x=complab_voc.index, y=complab_voc, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig3.add_trace(go.Scatter(x=cpcb_voc.index, y=cpcb_voc, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig4.add_trace(go.Scatter(x=classroom_co2.index, y=classroom_co2, mode='lines', name='Classroom', line=dict(color='blue')))
                fig4.add_trace(go.Scatter(x=library_co2.index, y=library_co2, mode='lines', name='Library', line=dict(color='violet')))
                fig4.add_trace(go.Scatter(x=chemlab_co2.index, y=chemlab_co2, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig4.add_trace(go.Scatter(x=complab_co2.index, y=complab_co2, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig4.add_trace(go.Scatter(x=cpcb_co2.index, y=cpcb_co2, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                # Add a horizontal dotted line at PM2.5 threshold of 25 (with black color)
                fig1.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[25, 25],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 25"
                ))
                
                fig2.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[50, 50],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 50"
                ))
                
                fig3.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[500, 500],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 500"
                ))
                
                fig4.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[1000, 1000],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 1000"
                ))
                
                # Update layout for all figures with titles
                fig1.update_layout(
                    title='🔴 PM2.5 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='PM2.5 Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig2.update_layout(
                    title='🔴 PM10 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='PM10 Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig3.update_layout(
                    title='🔴 VOC Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='VOC Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig4.update_layout(
                    title='🔴 CO2 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='CO2 Concentration (ppm)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                # Display figures
                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.plotly_chart(fig3, use_container_width=True)
                st.plotly_chart(fig4, use_container_width=True)
            
            elif time_interval == "hour" and not df.empty and not df1.empty:
                df['deviceID'] = df['deviceID'].astype(str).str.strip()
                df1['deviceID'] = df1['deviceID'].astype(str).str.strip()
            
                # Create individual dataframes based on deviceID
                SepClassroom = df[df['deviceID'] == '1202240029']
                SepCompLab = df[df['deviceID'] == '1202240010']
                SepLibrary = df[df['deviceID'] == '1202240028']
                SepChemLab = df[df['deviceID'] == '1202240012']
                Sepcpcb = df1[df1['deviceID'] == 'DELDPCC016']
                
                # Convert 'datetime' to proper datetime format
                SepClassroom['datetime'] = pd.to_datetime(SepClassroom['datetime'], format='%d-%m-%Y %H:%M')
                SepLibrary['datetime'] = pd.to_datetime(SepLibrary['datetime'], format='%d-%m-%Y %H:%M')
                SepChemLab['datetime'] = pd.to_datetime(SepChemLab['datetime'], format='%d-%m-%Y %H:%M')
                SepCompLab['datetime'] = pd.to_datetime(SepCompLab['datetime'], format='%d-%m-%Y %H:%M')
                Sepcpcb['datetime'] = pd.to_datetime(Sepcpcb['datetime'], format='%d-%m-%Y %H:%M')
                
                # Set 'datetime' as the DataFrame index
                SepClassroom.set_index('datetime', inplace=True)
                SepLibrary.set_index('datetime', inplace=True)
                SepChemLab.set_index('datetime', inplace=True)
                SepCompLab.set_index('datetime', inplace=True)
                Sepcpcb.set_index('datetime', inplace=True)
                
                # Sort the index for each dataframe
                SepClassroom = SepClassroom.sort_index()
                SepLibrary = SepLibrary.sort_index()
                SepChemLab = SepChemLab.sort_index()
                SepCompLab = SepCompLab.sort_index()
                Sepcpcb = Sepcpcb.sort_index()
            
                # Convert selected date to datetime and define the time range for filtering
                start_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 00:00:00'
                end_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 23:59:00'
                
                # Filter each dataframe to get the values for the 24-hour period
                classroom_pm25 = SepClassroom.loc[start_time:end_time, 'avg_pm25']
                library_pm25 = SepLibrary.loc[start_time:end_time, 'avg_pm25']
                chemlab_pm25 = SepChemLab.loc[start_time:end_time, 'avg_pm25']
                complab_pm25 = SepCompLab.loc[start_time:end_time, 'avg_pm25']
                cpcb_pm25 = Sepcpcb.loc[start_time:end_time, 'avg_pm25']
                
                classroom_pm10 = SepClassroom.loc[start_time:end_time, 'avg_pm10']
                library_pm10 = SepLibrary.loc[start_time:end_time, 'avg_pm10']
                chemlab_pm10 = SepChemLab.loc[start_time:end_time, 'avg_pm10']
                complab_pm10 = SepCompLab.loc[start_time:end_time, 'avg_pm10']
                cpcb_pm10 = Sepcpcb.loc[start_time:end_time, 'avg_pm10']
                
                classroom_voc = SepClassroom.loc[start_time:end_time, 'avg_voc']
                library_voc = SepLibrary.loc[start_time:end_time, 'avg_voc']
                chemlab_voc = SepChemLab.loc[start_time:end_time, 'avg_voc']
                complab_voc = SepCompLab.loc[start_time:end_time, 'avg_voc']
                if 'avg_voc' in Sepcpcb.columns:
                        cpcb_voc = Sepcpcb.loc[start_time:end_time, 'avg_voc']
                else:
                    cpcb_voc = None  # or handle it in some other way
                
                classroom_co2 = SepClassroom.loc[start_time:end_time, 'avg_co2']
                library_co2 = SepLibrary.loc[start_time:end_time, 'avg_co2']
                chemlab_co2 = SepChemLab.loc[start_time:end_time, 'avg_co2']
                complab_co2 = SepCompLab.loc[start_time:end_time, 'avg_co2']
                if 'avg_co2' in Sepcpcb.columns:
                    cpcb_co2 = Sepcpcb.loc[start_time:end_time, 'avg_co2']
                else:
                    cpcb_co2 = None
        
                # Create a new figure
                fig1 = go.Figure()
                fig2 = go.Figure()
                fig3 = go.Figure()
                fig4 = go.Figure()
                
                # Add traces for each dataframe with specified colors
                fig1.add_trace(go.Scatter(x=classroom_pm25.index, y=classroom_pm25, mode='lines', name='Classroom', line=dict(color='blue')))
                fig1.add_trace(go.Scatter(x=library_pm25.index, y=library_pm25, mode='lines', name='Library', line=dict(color='violet')))
                fig1.add_trace(go.Scatter(x=chemlab_pm25.index, y=chemlab_pm25, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig1.add_trace(go.Scatter(x=complab_pm25.index, y=complab_pm25, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig1.add_trace(go.Scatter(x=cpcb_pm25.index, y=cpcb_pm25, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig2.add_trace(go.Scatter(x=classroom_pm10.index, y=classroom_pm10, mode='lines', name='Classroom', line=dict(color='blue')))
                fig2.add_trace(go.Scatter(x=library_pm10.index, y=library_pm10, mode='lines', name='Library', line=dict(color='violet')))
                fig2.add_trace(go.Scatter(x=chemlab_pm10.index, y=chemlab_pm10, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig2.add_trace(go.Scatter(x=complab_pm10.index, y=complab_pm10, mode='lines', name='Comp Lab', line=dict(color='orange')))
                fig2.add_trace(go.Scatter(x=cpcb_pm10.index, y=cpcb_pm10, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                
                fig3.add_trace(go.Scatter(x=classroom_voc.index, y=classroom_voc, mode='lines', name='Classroom', line=dict(color='blue')))
                fig3.add_trace(go.Scatter(x=library_voc.index, y=library_voc, mode='lines', name='Library', line=dict(color='violet')))
                fig3.add_trace(go.Scatter(x=chemlab_voc.index, y=chemlab_voc, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig3.add_trace(go.Scatter(x=complab_voc.index, y=complab_voc, mode='lines', name='Comp Lab', line=dict(color='orange')))
                if cpcb_voc is not None and not cpcb_voc.empty:
                    fig3.add_trace(go.Scatter(x=cpcb_voc.index, y=cpcb_voc, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                else:
                    st.warning("CPCB Outdoor Data is not available for VOC.")
                    
                fig4.add_trace(go.Scatter(x=classroom_co2.index, y=classroom_co2, mode='lines', name='Classroom', line=dict(color='blue')))
                fig4.add_trace(go.Scatter(x=library_co2.index, y=library_co2, mode='lines', name='Library', line=dict(color='violet')))
                fig4.add_trace(go.Scatter(x=chemlab_co2.index, y=chemlab_co2, mode='lines', name='Chem Lab', line=dict(color='green')))
                fig4.add_trace(go.Scatter(x=complab_co2.index, y=complab_co2, mode='lines', name='Comp Lab', line=dict(color='orange')))
                if cpcb_co2 is not None and not cpcb_co2.empty:
                    fig4.add_trace(go.Scatter(x=cpcb_co2.index, y=cpcb_co2, mode='lines', name='CPCB Outdoor Data', line=dict(color='red', width=2.5)))
                else:
                    st.warning("CPCB Outdoor Data is not available for CO2.")
                
                # Add a horizontal dotted line at PM2.5 threshold of 25 (with black color)
                fig1.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[25, 25],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 25"
                ))
                
                fig2.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[50, 50],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 50"
                ))
                
                fig3.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[500, 500],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 500"
                ))
                
                fig4.add_trace(go.Scatter(
                    x=[start_time, end_time], y=[1000, 1000],
                    mode="lines",
                    line=dict(color="black", width=2, dash="dot"),
                    name="Threshold 1000"
                ))
                
                # Update layout for all figures with titles
                fig1.update_layout(
                    title='🔴 PM2.5 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='PM2.5 Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig2.update_layout(
                    title='🔴 PM10 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='PM10 Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig3.update_layout(
                    title='🔴 VOC Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='VOC Concentration (µg/m³)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                fig4.update_layout(
                    title='🔴 CO2 Levels in Various Locations',
                    xaxis_title='Date & Time',
                    yaxis_title='CO2 Concentration (ppm)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='x unified'  # Ensures that hover information is clear
                )
                
                # Display figures
                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                st.plotly_chart(fig3, use_container_width=True)
                st.plotly_chart(fig4, use_container_width=True)
        except Exception as e:
            st.info(f"🚨 Please upload right file for choosen Time Interval!")
        
if st.session_state.script_choice == "login":
    # Custom CSS for beautiful styling
    st.markdown("""
        <style>
        body {
            background-color: #f0f2f6;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .login-box {
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        .title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .input-box input {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .input-box input:focus {
            border-color: #4CAF50;
            outline: none;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<div class='title'>🔑 Login</div>", unsafe_allow_html=True)
    
    # Create the login form
    with st.form("login_form"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        login_button = st.form_submit_button("Login")
        if login_button:
            if username == "admin" and password == "password":  # Sample check for demo
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password")
    st.markdown("</div>", unsafe_allow_html=True)



# Wrap chart rendering in the monthly trends section with the new CSS class
if st.session_state.script_choice == "monthly_trends":
    # Import necessary libraries
    import streamlit as st
    import pandas as pd
    import mysql.connector
    from datetime import datetime
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np
    import calendar
    from matplotlib.colors import ListedColormap, BoundaryNorm
    from matplotlib.backends.backend_pdf import PdfPages
    from io import BytesIO


    def create_pdf_from_figs(fig_dict):
        pdf_buffer = BytesIO()
        with PdfPages(pdf_buffer) as pdf:
            for fig in fig_dict.values():
                pdf.savefig(fig, bbox_inches='tight')
        pdf_buffer.seek(0)
        return pdf_buffer

    # Database connection details
    host = "139.59.34.149"
    user = "neemdb"
    password = "(#&pxJ&p7JvhA7<B"
    database = "cabh_iaq_db"

    # Device Data Dictionary (deviceID, address, typology)
    device_data = {
        "1201240075": ("Hines Office, 12th Floor, One Horizon Centre, Sec-43, Gurugram", "Office"),
        "1201240078": ("Hines Office, 12th Floor, One Horizon Centre, Sec-43, Gurugram", "Office"),
        "1202240026": ("D-1/25 Vasant Vihar, New Delhi-110057(EDS Delhi)", "Office"),
        "1202240025": ("D-1/25 Vasant Vihar, New Delhi-110057(EDS Delhi)", "Office"),
        "1203240081": ("26A Poorvi Marg, Vasant Vihar, New Delhi-110057 (EDS, E-Block, Delhi)", "Office"),
        "1202240011": ("D-188, Abul Fazal Enclave-I, Jamia Nagar, New Delhi-110025", "Apartment"),
        "1202240027": ("D-188, Abul Fazal Enclave-I, Jamia Nagar, New Delhi-110025", "Apartment"),
        "1203240076": ("D 184 ABUL FAZAL ENCLAVE, JAMIA NAGAR, OKHLA, NEW DELHI 25", "Midrise Apartment (G+5)"),
        "1203240078": ("D 184 ABUL FAZAL ENCLAVE, JAMIA NAGAR, OKHLA, NEW DELHI 25", "Midrise Apartment (G+5)"),
        "1203240075": ("A 48/B, Third Floor, Abul Fazal Enclave Part II, New Delhi", "Residential"),
        "1201240077": ("448, Sector-9, Pocket-1 DDA Flats Dwarka, New Delhi-110075", "Residential"),
        "1201240072": ("448, Sector-9, Pocket-1 DDA Flats Dwarka, New Delhi-110075", "Residential"),
        "1203240079": ("C-403, Prince Apartments, Plot 54, I.P. Extension, Patparganj, Delhi - 110092", "Residential, Multi-family"),
        "1201240079": ("B-3/527, Ekta Gardens Apts, Patparganj, Delhi - 110092", "Residential"),
        "1201240085": ("B-3/527, Ekta Gardens Apts, Patparganj, Delhi - 110092", "Residential"),
        "1203240083": ("Flat No. 25, Tower E2, Sector E1, Vasant Kunj, New Delhi", "Residential"),
        "1203240073": ("Flat no. 495, Block 14, Kaveri Apartments, D6, Vasant Kunj, Delhi - 110070", "Residential"),
        "1203240074": ("569 sector A pocket C Vasant Kunj, Delhi - 110070", "Residential"),
        "1201240076": ("H No.-296 Near Durga Ashram, Chhatarpur, Delhi-110074", "Residential"),
        "1212230160": ("H No.-296 Near Durga Ashram, Chhatarpur, Delhi-110074", "Residential"),
        "1202240009": ("D-13A 2nd Floor Left side, Paryavaran Complex, Delhi 1100030", "Office"),
        "1202240008": ("D-13A 2nd Floor Left side, Paryavaran Complex, Delhi 1100030", "Office"),
        "1201240073": ("569 sector A pocket C Vasant Kunj, Delhi - 110070", "Residential"),
        "1203240080": ("F-5, 318-N, Chirag Delhi, Delhi-110017", "Residential"),
        "1201240074": ("F-5, 318-N, Chirag Delhi, Delhi-110017", "Residential"),
        "1203240077": ("B-2/51-A, Keshav Puram", "Apartment"),
        "1203240082": ("B-2/51-A, Keshav Puram", "Apartment"),
        "1202240029": ("St. Mary's School, Dwarka Sec-19", "Office"),
        "1202240028": ("St. Mary's School, Dwarka Sec-19", "Office"),
        "1202240010": ("St. Mary's School, Dwarka Sec-19", "Office"),
        "1202240012": ("St. Mary's School, Dwarka Sec-19", "School"),
    }

    residential_ids = [
        "1203240075", "1201240077", "1201240072", "1203240079", "1201240079",
        "1201240085", "1203240083", "1203240073", "1203240074", "1201240076",
        "1212230160", "1201240073", "1203240080", "1201240074"
    ]

    # Mapping of indoor device IDs to outdoor device IDs
    indoor_to_outdoor_mapping = {
        "1202240026": "THIRD_DPCC_SCR_RKPURAM",
        "1202240025": "THIRD_DPCC_SCR_RKPURAM",
        "1203240081": "THIRD_DPCC_SCR_RKPURAM",
        "1202240011": "DELCPCB010",
        "1202240027": "DELCPCB010",
        "1203240076": "DELCPCB010",
        "1203240078": "DELCPCB010",
        "1203240075": "DELCPCB010",
        "1201240077": "DELDPCC016",
        "1201240072": "DELDPCC016",
        "1203240079": "DELDPCC006",
        "1201240079": "DELDPCC006",
        "1201240085": "DELDPCC006",
        "1203240083": "THIRD_DPCC_SCR_RKPURAM",
        "1203240073": "DELDPCC018",
        "1203240074": "DELDPCC011",
        "1201240076": "DELDPCC018",
        "1212230160": "DELDPCC018",
        "1202240009": "DELDPCC018",
        "1202240008": "DELDPCC018",
        "1201240073": "DELDPCC018",
        "1203240080": "DELCPCB005",
        "1201240074": "DELCPCB005",
        "1203240077": "DELDPCC014",
        "1203240082": "DELDPCC014",
        "1202240029": "DELDPCC016",
        "1202240028": "DELDPCC016",
        "1202240010": "DELDPCC016",
        "1202240012": "DELDPCC016",
    }

    pollutant_display_names = {
        'aqi': 'AQI',
        'pm25': 'PM 2.5',
        'pm10': 'PM 10',
        'co2': 'CO₂',
        'voc': 'VOC',
        'temp': 'Temp.',
        'humidity': 'Humidity'
    }

    # Function to plot and display line charts for pollutants
    def plot_and_display_line_charts(indoor_df, outdoor_df, pollutant_display_names, all_figs):
        thresholds = {
        'aqi': 300,
        'pm25': 250,
        'pm10': 350,
        'co2': 900,
        'voc': 500,
        'temp': 28,
        'humidity': 70
      }

        combined_df = pd.concat(
            [indoor_df.add_suffix('_indoor'), outdoor_df.add_suffix('_outdoor')],
            axis=1
        )

        for pollutant in pollutant_display_names.keys():
            indoor_col = f"{pollutant}_indoor"
            outdoor_col = f"{pollutant}_outdoor"

            # Skip plotting if indoor data doesn't exist
            if indoor_col not in combined_df.columns:
                continue

            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot indoor data
            combined_df[indoor_col].plot(ax=ax, label=f"{pollutant_display_names[pollutant]} (Indoor)", color='blue')

            # Plot outdoor data only if:
            # - the pollutant is NOT CO2 or VOC
            # - the column exists
            if pollutant.lower() not in ['co2', 'voc'] and outdoor_col in combined_df.columns:
                combined_df[outdoor_col].plot(ax=ax, label=f"{pollutant_display_names[pollutant]} (Outdoor)", color='orange')

        # Add a horizontal red line for the threshold if it exists
            if pollutant in thresholds:
                ax.axhline(y=thresholds[pollutant], color='red', linestyle='--', linewidth=1.5, label=f"Threshold ({thresholds[pollutant]})")

                ax.set_title(f"{pollutant_display_names[pollutant]} - Indoor vs Outdoor", fontsize=14)
                ax.set_xlabel("Date", fontsize=12)
                ax.set_ylabel(pollutant_display_names[pollutant], fontsize=12)
                ax.legend()
                ax.grid(True)

                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
                buf.seek(0)
                img = Image.open(buf)
                img = img.resize((int(img.width * 0.7), int(img.height * 0.7)))  # Scale to 70%
                
                st.image(img)
                all_figs[f"{pollutant}_line_chart"] = fig

    # Function to plot and display heatmaps for each feature (pollutant)
    def plot_and_display_feature_heatmaps(indoor_df, features, year, month, all_figs):
        feature_boundaries = {
            'aqi': [0, 50, 100, 150, 200, 300, 500],
            'pm25': [0, 12, 35, 55, 150, 250, 500],
            'pm10': [0, 20, 50, 100, 250, 350, 500],
            'co2': [0, 900, 10000],
            'voc': [0, 500, 1000],
            'temp': [0, 18, 28, 50],
            'humidity': [0, 50, 70, 100]
        }

        feature_labels = {
            'aqi': ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe'],
            'pm25': ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe'],
            'pm10': ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe'],
            'co2': ['Good', 'Poor'],
            'voc': ['Good', 'Poor'],
            'temp': ['Low', 'Normal', 'High'],
            'humidity': ['Low', 'Normal', 'High']
        }

        num_days = calendar.monthrange(year, month)[1]
        first_day_of_month = calendar.monthrange(year, month)[0]
        calendar_data = np.full((5, 7), np.nan)
        daily_averages = indoor_df.resample('D').mean()

        for feature in features:
            if feature not in daily_averages.columns:
                continue
            calendar_data.fill(np.nan)
            for day in range(1, num_days + 1):
                if day in daily_averages.index.day:
                    daily_avg = daily_averages.loc[daily_averages.index.day == day, feature].mean()
                    week_row = (day + first_day_of_month - 1) // 7
                    week_col = (day + first_day_of_month - 1) % 7
                    if week_row < 5:
                        calendar_data[week_row, week_col] = daily_avg

            fig, ax = plt.subplots(figsize=(10, 6))
            color_list = ['#006400', '#228B22', '#FFFF00', '#FF7F00', '#FF0000', '#8B0000']
            cmap = ListedColormap(color_list)
            boundaries = feature_boundaries[feature]
            labels = feature_labels[feature]
            norm = BoundaryNorm(boundaries, cmap.N)

            sns.heatmap(calendar_data, annot=True, fmt=".0f", cmap=cmap, norm=norm,
                        cbar=False, xticklabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        yticklabels=False, ax=ax, linewidths=1, linecolor='black', annot_kws={"size": 14})
            ax.xaxis.tick_top()
            ax.set_title(f"Daily Average - {pollutant_display_names.get(feature, feature)}", fontsize=14, pad=35)
            ax.set_xlabel(f"{calendar.month_name[month]} {year}", fontsize=12)
            ax.set_ylabel("Week", fontsize=12)
            ax.set_yticks([])

            fig.subplots_adjust(right=0.85)
            cbar_ax = fig.add_axes([0.87, 0.1, 0.03, 0.8])
            cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbar_ax, orientation='vertical')
            cbar.set_ticks([(b + b_next) / 2 for b, b_next in zip(boundaries[:-1], boundaries[1:])])
            cbar.set_ticklabels(labels)
            cbar.ax.tick_params(labelsize=12)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            img = img.resize((int(img.width * 0.7), int(img.height * 0.7)))  # Scale to 70%
            
            st.image(img)
            all_figs[f"{feature}_heatmap"] = fig

    def plot_indoor_vs_outdoor_scatter(indoor_df, outdoor_df, pollutants, all_figs):
        # Resample to hourly averages
        indoor_df_hourly = indoor_df.resample('H').mean()
        outdoor_df_hourly = outdoor_df.resample('H').mean()

        for pollutant in pollutants:
            if pollutant in indoor_df_hourly.columns and pollutant in outdoor_df_hourly.columns:
                data = pd.merge(indoor_df_hourly[[pollutant]], outdoor_df_hourly[[pollutant]], left_index=True, right_index=True, how='inner')
                if data.empty:
                    continue

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(data[pollutant + '_x'], data[pollutant + '_y'], color='purple', alpha=0.7)
                ax.set_title(f"Hourly Avg: Indoor vs Outdoor - {pollutant.upper()}", fontsize=14)
                ax.set_xlabel(f"{pollutant.upper()} (Indoor)", fontsize=12)
                ax.set_ylabel(f"{pollutant.upper()} (Outdoor)", fontsize=12)
                ax.grid(True)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
                buf.seek(0)
                img = Image.open(buf)
                img = img.resize((int(img.width * 0.7), int(img.height * 0.7)))  # Scale to 70%
                
                st.image(img)
                all_figs[f"{pollutant}_scatter"] = fig

    def plot_residential_seasonal_line_chart(indoor_df, pollutants, year, all_figs):
        seasons = {
            "Spring": [2, 3, 4],
            "Summer": [5, 6, 7],
            "Autumn": [8, 9, 10],
            "Winter": [11, 12, 1]
        }
    
        yearly_df = indoor_df[(indoor_df.index.year == year) | ((indoor_df.index.year == year - 1) & (indoor_df.index.month == 12))]
        
        for pollutant in pollutants:
            fig, ax = plt.subplots(figsize=(10, 6))
            for season, months in seasons.items():
                seasonal_data = indoor_df[indoor_df.index.month.isin(months)]
                if not seasonal_data.empty:
                    seasonal_data = seasonal_data.resample('D').mean()
                    ax.plot(seasonal_data.index, seasonal_data[pollutant], label=season)
                else:
                    ax.plot([], [], label=f"{season} (No Data)")
    
            ax.set_title(f"Yearly {pollutant.upper()} Trends for Residential Buildings ({year})", fontsize=14)
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel(f"{pollutant.upper()}", fontsize=12)
            ax.legend(title="Season")
            ax.grid(True)
            ax.set_xlim(indoor_df.index.min(), indoor_df.index.max())
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            img = img.resize((int(img.width * 0.7), int(img.height * 0.7)))  # Scale to 70%
                
            st.image(img)
            all_figs[f"{pollutant}_seasonal_line_chart"] = fig


    st.markdown("""
        <style>
            .title {
                font-size: 18px;
                text-align: left;
                padding: 20px;
            }
            .black-line {
                border-top: 3px solid black;
                margin-top: 30px;
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h3 class="title">Indoor & Outdoor Air Quality Trends</h3>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Create columns for user inputs (deviceID, year, month)
    col1, col2, col3 = st.columns(3)    
    with col1:
        device_id_list = list(device_data.keys())
        device_id = st.selectbox("Select Device ID:", options=sorted(device_id_list), index=0)

    with col2:
        year = st.number_input("Select Year:", min_value=2024, max_value=2025, value=2024)

    with col3:
        month = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        month_name = st.selectbox("Select Month:", list(month.keys()), index=0)
        selected_month = month[month_name]

    st.markdown('<div class="black-line"></div>', unsafe_allow_html=True)

    # Get the address and typology for the entered device ID
    device_info = device_data.get(device_id, ("Not Available", "Not Available"))

    # Display address and typology
    st.write(f"Address: {device_info[0]}")
    st.write(f"Typology: {device_info[1]}")

    st.markdown('<div class="black-line"></div>', unsafe_allow_html=True)

    # Button to generate line charts
    if st.button("Generate Charts"):
        all_figs = {}
        with st.spinner("Generating Charts...please wait"):
            if not device_id.strip():
                st.error("Device ID cannot be empty.")
                st.stop()
            try:
                # Connect to the MySQL database
                conn = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database
                )
                cursor = conn.cursor()

                # Get the corresponding outdoor device ID
                outdoor_device_id = indoor_to_outdoor_mapping.get(device_id)
                if not outdoor_device_id:
                    st.error(f"No outdoor device mapping found for indoor device ID {device_id}.")
                    st.stop()

                # Query to fetch indoor data for selected month
                indoor_query_month = """
                SELECT datetime, pm25, pm10, aqi, co2, voc, temp, humidity
                FROM reading_db
                WHERE deviceID = %s AND YEAR(datetime) = %s AND MONTH(datetime) = %s;
                """
                cursor.execute(indoor_query_month, (device_id, year, selected_month))
                indoor_rows = cursor.fetchall()

                # Query to fetch all indoor data for the year (for seasonal trends)
                indoor_query_year = """
                SELECT datetime, pm25, pm10, aqi, co2, voc, temp, humidity
                FROM reading_db
                WHERE deviceID = %s AND YEAR(datetime) = %s;
                """
                cursor.execute(indoor_query_year, (device_id, year))
                indoor_rows_year = cursor.fetchall()

                # Query to fetch outdoor data for selected month
                outdoor_query = """
                SELECT datetime, pm25, pm10, aqi, co2, voc, temp, humidity
                FROM cpcb_data
                WHERE deviceID = %s AND YEAR(datetime) = %s AND MONTH(datetime) = %s;
                """
                cursor.execute(outdoor_query, (outdoor_device_id, year, selected_month))
                outdoor_rows = cursor.fetchall()

                if indoor_rows and outdoor_rows:
                # Process indoor data for the selected month
                    indoor_df = pd.DataFrame(indoor_rows, columns=["datetime", "pm25", "pm10", "aqi", "co2", "voc", "temp", "humidity"])
                    indoor_df['datetime'] = pd.to_datetime(indoor_df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    indoor_df.set_index('datetime', inplace=True)

                    # Filter indoor data: Remove rows with zero in specific columns before resampling
                    columns_to_check_indoor = ['pm25', 'pm10', 'aqi', 'temp']  # Modify as needed
                    indoor_df = indoor_df[(indoor_df[columns_to_check_indoor] != 0).all(axis=1)]

                    # Resample to daily averages after filtering out zero values
                    indoor_df = indoor_df.resample('D').mean()

                    indoor_df_hourly = pd.DataFrame(indoor_rows, columns=["datetime", "pm25", "pm10", "aqi", "co2", "voc", "temp", "humidity"])
                    indoor_df_hourly['datetime'] = pd.to_datetime(indoor_df_hourly['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    indoor_df_hourly.set_index('datetime', inplace=True)

                    columns_to_check_indoor = ['pm25', 'pm10', 'aqi', 'temp']  # Modify as needed
                    indoor_df_hourly = indoor_df_hourly[(indoor_df_hourly[columns_to_check_indoor] != 0).all(axis=1)]

                    indoor_df_hourly = indoor_df_hourly.resample('H').mean()
                    
                    # Process outdoor data
                    outdoor_df = pd.DataFrame(outdoor_rows, columns=["datetime", "pm25", "pm10", "aqi", "co2", "voc", "temp", "humidity"])
                    outdoor_df['datetime'] = pd.to_datetime(outdoor_df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    outdoor_df.set_index('datetime', inplace=True)

                    # Filter outdoor data: Remove rows with zero in specific columns before resampling
                    columns_to_check_outdoor = ['pm25', 'pm10', 'aqi']  # Modify as needed
                    outdoor_df = outdoor_df[(outdoor_df[columns_to_check_outdoor] != 0).all(axis=1)]

                    # Resample to daily averages after filtering out zero values
                    outdoor_df = outdoor_df.resample('D').mean()

                    outdoor_df_hourly = pd.DataFrame(outdoor_rows, columns=["datetime", "pm25", "pm10", "aqi", "co2", "voc", "temp", "humidity"])
                    outdoor_df_hourly['datetime'] = pd.to_datetime(outdoor_df_hourly['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    outdoor_df_hourly.set_index('datetime', inplace=True)

                    # Filter outdoor data: Remove rows with zero in specific columns before resampling
                    columns_to_check_outdoor = ['pm25', 'pm10', 'aqi']  
                    outdoor_df_hourly = outdoor_df_hourly[(outdoor_df_hourly[columns_to_check_outdoor] != 0).all(axis=1)]

                    # Resample to hourly averages after filtering out zero values
                    outdoor_df_hourly = outdoor_df_hourly.resample('H').mean()

                    # Generate heatmaps and other plots using one-month data
                    features = ['pm25', 'pm10', 'aqi', 'co2', 'voc', 'temp', 'humidity']
                    plot_and_display_feature_heatmaps(indoor_df, features, year, selected_month, all_figs)


                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<h3 style='font-size:30px; text-align:left; font-weight:bold;'>Line Charts of Indoor & Outdoor</h3>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    plot_and_display_line_charts(indoor_df, outdoor_df, pollutant_display_names, all_figs)


                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<h3 style='font-size:30px; text-align:left; font-weight:bold;'>Indoor vs Outdoor Scatter Plots</h3>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    plot_indoor_vs_outdoor_scatter(indoor_df_hourly, outdoor_df_hourly, ['aqi', 'pm10', 'pm25'], all_figs)


                else:
                    st.warning("No data found for the given Device ID and selected month.")

                # Generate seasonal line chart using all-year data
                if indoor_rows_year:
                    indoor_df_year = pd.DataFrame(indoor_rows_year, columns=["datetime", "pm25", "pm10", "aqi", "co2", "voc", "temp", "humidity"])
                    indoor_df_year['datetime'] = pd.to_datetime(indoor_df_year['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    indoor_df_year.set_index('datetime', inplace=True)

                    # Check if the device ID belongs to residential buildings
                    if device_id in residential_ids:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("<h3 style='font-size:30px; text-align:left; font-weight:bold;'>Seasonal Line Chart for Residential Buildings</h3>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        plot_residential_seasonal_line_chart(indoor_df_year, ['aqi', 'pm10', 'pm25'], year, all_figs)
                    else:
                        st.info("Seasonal line charts are only available for residential buildings.")
                else:
                    st.warning("No yearly data found for the selected Device ID.")
                
                if all_figs:
                    pdf_data = create_pdf_from_figs(all_figs)
                    st.download_button(
                        label="📄 Download All Charts as PDF",
                        data=pdf_data,
                        file_name="AirQualityCharts.pdf",
                        mime="application/pdf"
                    )


            except mysql.connector.Error as e:
                st.error(f"Database error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                # Ensure the database connection is closed
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

st.markdown('<hr style="border:1px solid black">', unsafe_allow_html=True)
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .footer {
            background-color: #f8f9fa;
            padding: 20px 0;
            color: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
            text-align: center;
        }
        .footer .logo {
            flex: 1;
        }
        .footer .logo img {
            max-width: 150px;
            height: auto;
        }
        .footer .social-media {
            flex: 2;
        }
        .footer .social-media p {
            margin: 0;
            font-size: 16px;
        }
        .footer .icons {
            margin-top: 10px;
        }
        .footer .icons a {
            margin: 0 10px;
            color: #666;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        .footer .icons a:hover {
            color: #0077b5; /* LinkedIn color as default */
        }
        .footer .icons a .fab {
            font-size: 28px;
        }
        .footer .additional-content {
            margin-top: 10px;
        }
        .footer .additional-content h4 {
            margin: 0;
            font-size: 18px;
            color: #007bff;
        }
        .footer .additional-content p {
            margin: 5px 0;
            font-size: 16px;
        }
    </style>
   <div class="footer">
        <div class="social-media" style="flex: 2;">
            <p>&copy; 2024. All Rights Reserved</p>
            <div class="icons">
                <a href="https://twitter.com/edsglobal?lang=en" target="_blank"><i class="fab fa-twitter" style="color: #1DA1F2;"></i></a>
                <a href="https://www.facebook.com/Environmental.Design.Solutions/" target="_blank"><i class="fab fa-facebook" style="color: #4267B2;"></i></a>
                <a href="https://www.instagram.com/eds_global/?hl=en" target="_blank"><i class="fab fa-instagram" style="color: #E1306C;"></i></a>
                <a href="https://www.linkedin.com/company/environmental-design-solutions/" target="_blank"><i class="fab fa-linkedin" style="color: #0077b5;"></i></a>
            </div>
            <div class="additional-content">
                <h4>Contact Us</h4>
                <p>Email: info@edsglobal.com | Phone: +123 456 7890</p>
                <p>Follow us on social media for the latest updates and news.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)
