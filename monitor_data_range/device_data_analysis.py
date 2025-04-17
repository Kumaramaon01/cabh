import json
import os
from datetime import datetime
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# # Database connection parameters
# DB_HOST = os.getenv('DB_HOST')
# DB_NAME = os.getenv('DB_NAME')
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_PORT = os.getenv('DB_PORT')

# def get_device_installation_date(device_id):
#     """Get installation date for a specific device from monitor_data.json"""
#     try:
#         # Convert input device_id to string for comparison
#         device_id_str = str(device_id)
#         with open('monitor_data.json', 'r') as file:
#             data = json.load(file)
#             for device in data['Data']:
#                 if str(device['deviceID']) == device_id_str:
#                     if device.get('installation_date'):
#                         try:
#                             return datetime.strptime(device['installation_date'], '%Y-%m-%d %H:%M:%S')
#                         except ValueError as e:
#                             print(f"Error parsing installation date for device {device_id}: {e}")
#                             return None
#                     else:
#                         print(f"No installation date found for device {device_id}")
#                         return None
#             print(f"Device ID {device_id} not found in monitor_data.json")
#             return None
#     except Exception as e:
#         print(f"Error reading monitor_data.json: {e}")
#         return None

# def calculate_data_metrics(device_id):
#     """Calculate data count and percentage since installation date"""
#     installation_date = get_device_installation_date(device_id)
#     if not installation_date:
#         print(f"\nCannot calculate metrics: No valid installation date found for device {device_id}")
#         return

#     try:
#         # Ensure device_id is a string
#         device_id_str = str(device_id)
        
#         # Connect to the database
#         conn = pymysql.connect(
#             host=DB_HOST,
#             database=DB_NAME,
#             user=DB_USER,
#             password=DB_PASSWORD,
#             port=int(DB_PORT) if DB_PORT else 3306,
#             cursorclass=pymysql.cursors.DictCursor
#         )
#         cursor = conn.cursor()

#         # Calculate total expected data points (1-minute intervals)
#         current_time = datetime.now()
#         time_diff = current_time - installation_date
#         expected_count = time_diff.total_seconds() / 60  # 1-minute intervals

#         # Query actual data points
#         query = """
#         SELECT COUNT(*) as count
#         FROM reading_db 
#         WHERE deviceID = %s 
#         AND datetime >= %s
#         """
#         try:
#             cursor.execute(query, (device_id_str, installation_date))
#             result = cursor.fetchone()
#             if result is None:
#                 print(f"No data found for device {device_id}")
#                 return
#             actual_count = result['count']

#             # Calculate percentage
#             percentage = (actual_count / expected_count) * 100 if expected_count > 0 else 0

#             print(f"\nData Analysis for Device {device_id}:")
#             print(f"Installation Date: {installation_date}")
#             print(f"Expected Data Points: {int(expected_count)}")
#             print(f"Actual Data Points: {actual_count}")
#             print(f"Data Collection Percentage: {percentage:.2f}%")
#         except Exception as e:
#             print(f"Error executing database query: {e}")
#             return

#     except Exception as e:
#         print(f"Database error: {e}")
#     finally:
#         if 'conn' in locals():
#             conn.close()

# def main():
#     device_id = input("Enter the device ID: ")
#     calculate_data_metrics(device_id)

# if __name__ == "__main__":
#     main()

# Database connection parameters
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

def get_device_installation_date(device_id):
    """Get installation date for a specific device from monitor_data.json"""
    try:
        device_id_str = str(device_id)
        with open(r'monitor_data_range\monitor_data.json', 'r') as file:
            data = json.load(file)
            for device in data['Data']:
                if str(device['deviceID']) == device_id_str:
                    if device.get('installation_date'):
                        try:
                            return datetime.strptime(device['installation_date'], '%Y-%m-%d %H:%M:%S')
                        except ValueError as e:
                            print(f"Error parsing installation date for device {device_id}: {e}")
                            return None
                    else:
                        print(f"No installation date found for device {device_id}")
                        return None
            print(f"Device ID {device_id} not found in monitor_data.json")
            return None
    except Exception as e:
        print(f"Error reading monitor_data.json: {e}")
        return None

def calculate_data_metrics(device_id):
    """Return installation date, expected count, actual count, and data percentage"""
    installation_date = get_device_installation_date(device_id)
    if not installation_date:
        return None, None, None, None

    try:
        device_id_str = str(device_id)
        conn = pymysql.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=int(DB_PORT) if DB_PORT else 3306,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        current_time = datetime.now()
        time_diff = current_time - installation_date
        expected_count = time_diff.total_seconds() / 60

        query = """
        SELECT COUNT(*) as count
        FROM reading_db 
        WHERE deviceID = %s 
        AND datetime >= %s
        """
        cursor.execute(query, (device_id_str, installation_date))
        result = cursor.fetchone()
        actual_count = result['count'] if result else 0
        percentage = (actual_count / expected_count) * 100 if expected_count > 0 else 0

        return installation_date, int(expected_count), actual_count, round(percentage, 2)

    except Exception as e:
        print(f"Database error: {e}")
        return None, None, None, None
    finally:
        if 'conn' in locals():
            conn.close()
