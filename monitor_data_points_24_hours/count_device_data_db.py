import pymysql
import pandas as pd
import json
import time
import streamlit

from .config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Database Connection
def get_db_connection():
    max_retries = 3
    retry_count = 0
    retry_delay = 2  # Initial delay in seconds
    
    while retry_count < max_retries:
        try:
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
            retry_count += 1
            if retry_count == max_retries:
                error_msg = f"Database connection failed after {max_retries} attempts: {str(e)}"
                print(error_msg)
                raise Exception(error_msg)
            print(f"Connection attempt {retry_count} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

# Function to fetch and count data points for all devices in one query
def count_data_points_batch(device_ids):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch latest timestamp
            cursor.execute("SELECT MAX(datetime) FROM reading_db")
            latest_time = cursor.fetchone()["MAX(datetime)"]

            # Get counts and last timestamp for all devices in one query using GROUP BY
            query = """
            SELECT deviceID, COUNT(*) as count, MAX(datetime) as last_timestamp
            FROM reading_db
            WHERE datetime >= DATE_SUB(%s, INTERVAL 24 HOUR)
            AND deviceID IN ({})
            GROUP BY deviceID
            """.format(",".join([str(id) for id in device_ids]))
            
            cursor.execute(query, (latest_time,))
            results = cursor.fetchall()
            
            # Convert results to a dictionary for easy lookup, including last timestamp
            return {str(row["deviceID"]): {"count": row["count"], "last_timestamp": row["last_timestamp"]} for row in results}
    finally:
        connection.close()

def process_monitor_list(monitors_data):
    # Parse the JSON data if it's a string
    if isinstance(monitors_data, str):
        monitors = json.loads(monitors_data)
    else:
        monitors = monitors_data
    
    # Access the Data array from the new JSON structure
    monitors_list = monitors.get('Data', [])
    
    # Get all device IDs
    device_ids = [int(monitor["deviceID"]) for monitor in monitors_list]
    
    # Get counts for all devices in one batch
    data_points_dict = count_data_points_batch(device_ids)
    
    # Create results list using the batch data
    results = []
    for monitor in monitors_list:
        device_id = monitor["deviceID"]
        device_data = data_points_dict.get(device_id, {"count": 0, "last_timestamp": None})
        data_points = device_data["count"]
        data_percentage = round((data_points / 1440) * 100, 2)  # Calculate percentage based on 1440 minutes per day
        result = {
            "deviceID": device_id,
            "deployementID": monitor["deployementID"],
            "typology": monitor["typology"],
            "address": monitor["address"],
            "contact_person": monitor["contact_person"],
            "contact_number": monitor["contact_number"],
            "data_points_24h": data_points,
            "data_percentage": data_percentage,
            "last_timestamp": device_data["last_timestamp"]
        }
        results.append(result)
    
    return results

# Example Usage
def print_monitor_report(results):
    print("\nMonitor Data Points Report (Last 24 Hours):")
    print("-" * 80)
    for result in results:
        print(f"Device ID: {result['deviceID']}")
        print(f"Deployment ID: {result['deployementID']}")
        print(f"Typology: {result['typology']}")
        print(f"Address: {result['address']}")
        print(f"Data Points (24h): {result['data_points_24h']}")
        print(f"Data Percentage: {result['data_percentage']}%")
        print(f"Last Data Timestamp: {result['last_timestamp']}")
        print("-" * 80)

# Function to export results to CSV and display in console
def export_to_csv(results):
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    df = pd.DataFrame(results)
    # Display results in console
    print("\nMonitor Data Points Report:")
    print(df.to_string(index=False))
    print("\n")
    
    # Export to CSV with timestamp
    csv_filename = f'monitor_data_points_report_{timestamp}.csv'
    df.to_csv(csv_filename, index=False)
    print(f"Report exported to {csv_filename}")


# Main execution block
if __name__ == "__main__":
    try:
        # Load monitor data from JSON file
        with open('monitor_data.json', 'r') as file:
            monitor_data = json.load(file)
        
        # Process the monitor list
        results = process_monitor_list(monitor_data)
        
        # Print the report and export to CSV
        print_monitor_report(results)
        export_to_csv(results)
    except FileNotFoundError:
        print("Error: monitor_data.json file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in monitor_data.json file.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
