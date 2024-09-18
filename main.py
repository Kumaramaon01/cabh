import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pages
import mysql.connector
from datetime import datetime

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


# Initialize session state for script_choice if it does not exist
if 'script_choice' not in st.session_state:
    st.session_state.script_choice = "about"  # Set default to "about"

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('About'):
        st.session_state.script_choice = "about"
with col2:
    if st.button('Extract Data'):
        st.session_state.script_choice = "data"
with col3:
    if st.button('Analytics'):
        st.session_state.script_choice = "visual"

#Based on the user selection, display appropriate input fields and run the script
if st.session_state.script_choice == "about":
    # Location
    st.markdown("#### 📍 Location: Dwarka, New Delhi")
    # Introduction
    st.write("We’ve deployed IAQ monitors in key locations to ensure a healthy learning environment. Below are the monitoring points across the school:")
    # Monitoring Locations with icons
    st.markdown("""
    - **📚 Library:** Ensuring a peaceful, clean environment for reading.
    - **🏫 Classroom:** Fresh air for students' well-being and focus.
    - **🌳 CPCB Outdoor Monitor:** Collecting outdoor air data for comparison.
    - **💻 Computer Lab:** Monitoring air quality in tech-heavy spaces.
    - **🔬 Chemistry Lab:** Maintaining a safe atmosphere for experiments.
    """)

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

        
    # reading_db = pd.read_csv("database/Sep_1min.csv")
    # cpcb_data = pd.read_csv("database/cpcb_data.csv")
    # reading_15min = pd.read_csv("database/reading_15min.csv")
    # cpcb_data = pd.read_csv("database/cpcb_data.csv")
    # reading_hour = pd.read_csv("database/reading_hr.csv")
    # cpcb_hour = pd.read_csv("database/cpcb_hour.csv")

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
