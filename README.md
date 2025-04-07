# Breathe-in Data Monitoring System

This project implements an automated system for monitoring and reporting data points from breathe-in sensors over 24-hour periods. It analyzes sensor data, generates detailed reports, and sends automated email notifications about sensor performance.

## Features

- 24-hour data point monitoring for multiple sensors
- Automated email reporting system
- Data percentage calculation and analysis
- Low data detection (<95% data points)
- CSV report generation
- Robust database connection handling with retry mechanism

## System Requirements

- Python 3.x
- MySQL/MariaDB Database
- SMTP server access for email notifications

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd cabh_last_24hr_datacount
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp monitor_data_points_24_hours/.env.example monitor_data_points_24_hours/.env
   ```

2. Configure the environment variables in `.env`:

   ```env
   # Database Configuration
   DB_HOST=your_database_host
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_NAME=your_database_name

   # Email Configuration
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=your_smtp_port
   SMTP_USERNAME=your_email
   SMTP_PASSWORD=your_email_password
   RECIPIENT_EMAILS=email1@example.com, email2@example.com
   ```

## Project Structure

```
cabh_last_24hr_datacount/
├── monitor_data_points_24_hours/
│   ├── config.py                  # Configuration management
│   ├── count_device_data_db.py    # Database operations and data counting
│   ├── email_utils.py             # Email notification functionality
│   ├── generate_low_data_report.py# Low data report generation
│   └── monitor_data.json          # Sample monitor data
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```

## Usage

1. Prepare your monitor data JSON file with the required format:
   ```json
   {
     "Data": [
       {
         "deviceID": "123",
         "deployementID": "DEP123",
         "typology": "Type1",
         "address": "Location1",
         "contact_person": "John Doe",
         "contact_number": "+1234567890"
       }
     ]
   }
   ```

2. Run the monitoring script:
   ```bash
   python monitor_data_points_24_hours/count_device_data_db.py
   ```

## Output

The system generates two types of reports:

1. **Monitor Data Points Report**: Contains data for all sensors
   - Device ID
   - Deployment ID
   - Typology
   - Address
   - Data points in last 24 hours
   - Data percentage
   - Last timestamp

2. **Low Data Sensors Report**: Lists sensors with <95% data points
   - Includes contact information for follow-up
   - Prioritizes critical cases

## Email Notifications

The system sends automated email reports containing:
- Summary statistics
- List of sensors with low data
- Attached CSV reports
- Contact information for follow-up

## Error Handling

- Database connection retries with exponential backoff
- File existence verification
- Email sending error handling
- JSON parsing error handling

## Contributing

Please follow these steps to contribute:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For support and questions, please contact:
- Email: abdullah@edsglobal.com

## License

This project is proprietary and confidential. All rights reserved.