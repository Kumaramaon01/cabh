import pandas as pd
from count_device_data_db import process_monitor_list
import json
from email_utils import send_monitoring_report
import os
from datetime import datetime

def generate_low_data_report():
    try:
        # First, run the monitor data points report
        monitor_data_path = os.path.join(os.path.dirname(__file__), 'monitor_data.json')
        if not os.path.exists(monitor_data_path):
            raise FileNotFoundError(f"monitor_data.json not found at {monitor_data_path}")
            
        print(f"Reading monitor data from {monitor_data_path}")
        with open(monitor_data_path, 'r') as file:
            monitor_data = json.load(file)
        
        # Process the monitor list and get results
        results = process_monitor_list(monitor_data)
        
        # Get current timestamp for filenames
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create DataFrame and export to CSV with timestamp
        df = pd.DataFrame(results)
        output_filename = f'monitor_data_points_report_{timestamp}.csv'
        df.to_csv(output_filename, index=False)
        
        # Filter for low data sensors
        low_data_df = df[df['data_percentage'] < 95.0].sort_values('data_percentage')
        
        # Export low data sensors to a separate CSV file with timestamp
        low_data_output = f'low_data_sensors_report_{timestamp}.csv'
        low_data_df.to_csv(low_data_output, index=False)
        
        # Print summary
        print("\nMonitor Data Points Report Summary")
        print("-" * 80)
        print(f"Total sensors analyzed: {len(df)}")
        print(f"Sensors with low data (<95%): {len(low_data_df)}")
        print(f"Full report exported to {output_filename}")
        print(f"Low data sensors report exported to {low_data_output}")
        
        # Send reports via email
        send_monitoring_report(output_filename, low_data_output)
        
        if not low_data_df.empty:
            print("\nLow Data Sensors:")
            print(low_data_df[['deviceID', 'deployementID', 'data_percentage']].to_string(index=False))
        
    except FileNotFoundError:
        print("Error: monitor_data.json file not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    generate_low_data_report()