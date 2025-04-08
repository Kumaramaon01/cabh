import os
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, RECIPIENT_EMAILS

def send_monitoring_report(monitor_report_path, low_data_report_path):
    """Send monitoring reports via email."""
    try:
        print(f"Preparing to send email using SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"From: {SMTP_USERNAME}")
        print(f"To: {', '.join(RECIPIENT_EMAILS)}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = ", ".join(RECIPIENT_EMAILS)
        msg['Subject'] = f"breathe-in Data Monitoring Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Get summary statistics from the reports
        monitor_df = pd.read_csv(monitor_report_path)
        low_data_df = pd.read_csv(low_data_report_path)
        
        # Calculate statistics
        total_sensors = len(monitor_df)
        low_data_sensors = len(low_data_df)
        avg_data_percentage = monitor_df['data_percentage'].mean()

        # Email body with statistics
        body = f"""Hello Ashish,

Please find attached the latest breathe-in data monitoring reports.

Summary Statistics:
- Total sensors analyzed: {total_sensors}
- Sensors with low data (<95%): {low_data_sensors}
- Average data percentage: {avg_data_percentage:.2f}%

Low Data Sensors (Top 5 most critical):
"""

        # Add top 5 most critical sensors if any exist
        if not low_data_df.empty:
            low_data_summary = low_data_df.sort_values('data_percentage').head(5)[
                ['deviceID', 'deployementID', 'data_percentage', 'contact_person', 'contact_number']
            ].to_string(index=False)
            body += f"\n{low_data_summary}\n"
        else:
            body += "\nNo sensors with low data detected.\n"

        body += """

Attached Reports:
1. Complete Monitor Data Points Report
2. Low Data Sensors Report (devices with <95% data)

This is an automated email. Please do not reply.

Best regards,
Abdullah Kidwai"""

        msg.attach(MIMEText(body, 'plain'))

        # Verify files exist before attaching
        for file_path in [monitor_report_path, low_data_report_path]:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Report file not found: {file_path}")

        # Attach monitor report
        print(f"Attaching monitor report: {monitor_report_path}")
        with open(monitor_report_path, 'rb') as f:
            monitor_attachment = MIMEApplication(f.read(), _subtype='csv')
            monitor_attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=os.path.basename(monitor_report_path))
            msg.attach(monitor_attachment)

        # Attach low data report
        print(f"Attaching low data report: {low_data_report_path}")
        with open(low_data_report_path, 'rb') as f:
            low_data_attachment = MIMEApplication(f.read(), _subtype='csv')
            low_data_attachment.add_header('Content-Disposition', 'attachment', 
                                         filename=os.path.basename(low_data_report_path))
            msg.attach(low_data_attachment)

        # Send email
        print("Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("Starting TLS...")
            server.starttls()
            print("Logging in...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("Sending message...")
            server.send_message(msg)
            print("Email sent successfully!")
            return True

        print("\nMonitoring reports sent successfully via email.")
        print(f"Reports sent to: {', '.join(RECIPIENT_EMAILS)}")

    except Exception as e:
        print(f"\nError sending email: {str(e)}")