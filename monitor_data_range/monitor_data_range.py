import pandas as pd
import json
from datetime import datetime
import os
from pathlib import Path
import pymysql

def get_db_connection():
    try:
        # Add connection timeout and retry logic
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,  # 5 seconds timeout
            read_timeout=30,    # 30 seconds timeout for read operations
            write_timeout=30    # 30 seconds timeout for write operations
        )
        
        # Test connection by executing a simple query
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        
        return connection
    except pymysql.Error as e:
        error_msg = f"Database connection failed: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

def load_monitor_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def generate_reports(start_date, end_date, monitor_data_file='monitor_data.json'):
    # Convert string dates to datetime objects and format for SQL
    start_datetime = pd.to_datetime(start_date).strftime('%Y-%m-%d 00:00:00')
    end_datetime = pd.to_datetime(end_date).strftime('%Y-%m-%d 23:59:59')
    
    # Load monitor data
    monitor_data = load_monitor_data(monitor_data_file)
    
    # Create DataFrame for active devices from monitor data
    monitor_list = monitor_data.get('Data', [])
    devices_df = pd.DataFrame([{
        'deviceID': device['deviceID'],
        'deployementID': device['deployementID'],
        'typology': device['typology'],
        'address': device['address']
    } for device in monitor_list if device['active'] == '1'])
    
    # Calculate expected data points based on date range (1 point per minute)
    time_diff = (pd.to_datetime(end_datetime) - pd.to_datetime(start_datetime)).total_seconds() / 60
    expected_points = int(time_diff) + 1  # Add 1 to include both start and end points
    
    print(f"Querying data from {start_datetime} to {end_datetime}")
    print(f"Expected points per device: {expected_points}")
    
    # Get data points from database
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Keep deviceID as string
            device_ids = devices_df['deviceID'].tolist()
            # Get counts for all devices in one query using GROUP BY
            query = """
            SELECT deviceID, COUNT(*) as count 
            FROM reading_db 
            WHERE datetime >= %s AND datetime <= %s
            AND deviceID IN ({}) 
            GROUP BY deviceID
            """.format(",".join([f"'{id}'" for id in device_ids]))
            
            print(f"Executing query with {len(device_ids)} devices")
            print(f"Query: {query}")
            cursor.execute(query, (start_datetime, end_datetime))
            results = cursor.fetchall()
            
            print(f"Found data for {len(results)} devices")
            
            # Convert results to a dictionary for easy lookup
            data_points_dict = {str(row["deviceID"]): row["count"] for row in results}
            
            # Print some sample data for verification
            print("\nSample data points:")
            for device_id in list(data_points_dict.keys())[:5]:
                print(f"Device {device_id}: {data_points_dict[device_id]} points")
            
            # Update data points and percentages
            devices_df['data_points'] = devices_df['deviceID'].map(lambda x: data_points_dict.get(x, 0))
            devices_df['data_percentage'] = (devices_df['data_points'] / expected_points * 100).round(2)
            
            # Print summary for verification
            print("\nData summary:")
            print(f"Total devices: {len(devices_df)}")
            print(f"Devices with data: {len(results)}")
            print(f"Average data percentage: {devices_df['data_percentage'].mean():.2f}%")
    finally:
        connection.close()
    
    # Generate timestamp for report files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create output directory if it doesn't exist
    output_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Generate report filenames
    monitor_report_file = output_dir / f'monitor_data_points_report_{timestamp}.csv'
    low_data_report_file = output_dir / f'low_data_sensors_report_{timestamp}.csv'
    
    # Sort devices by data percentage and save reports
    devices_df = devices_df.sort_values('data_percentage', ascending=False)
    devices_df.to_csv(monitor_report_file, index=False)
    
    # Generate low data report (less than 95% data)
    low_data_df = devices_df[devices_df['data_percentage'] < 95].sort_values('data_percentage')
    low_data_df.to_csv(low_data_report_file, index=False)
    
    return monitor_report_file, low_data_report_file

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate monitor data reports for a specific date range')
    parser.add_argument('start_date', help='Start date in YYYY-MM-DD format')
    parser.add_argument('end_date', help='End date in YYYY-MM-DD format')
    parser.add_argument('--monitor-data', default='monitor_data.json',
                        help='Path to monitor_data.json file')
    
    args = parser.parse_args()
    
    try:
        monitor_file, low_data_file = generate_reports(
            args.start_date,
            args.end_date,
            args.monitor_data
        )
        print(f'\nReports generated successfully:')
        print(f'Monitor report: {monitor_file}')
        print(f'Low data report: {low_data_file}')
    except Exception as e:
        print(f'Error generating reports: {str(e)}')