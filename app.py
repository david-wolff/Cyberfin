from flask import Flask, render_template
import json
import os
from sendForecastRequest import get_and_store_forecast
from filterRequest import average_noaa_conditions_to_file

app = Flask(__name__)

def filter_for_8am(data):
    """Filters data to include only entries at 8 AM."""
    filtered = []
    for entry in data:
        if '08:00 AM' in entry['time']:
            filtered.append(entry)
    return filtered

def can_make_api_request(raw_data_file):
    try:
        with open(raw_data_file, 'r') as file:
            data = json.load(file)
            request_count = data['meta']['requestCount']
            daily_quota = data['meta']['dailyQuota']
            return request_count < (daily_quota - 1)  # Ensuring we don't hit the quota
    except FileNotFoundError:
        return True  # If the file doesn't exist, consider that no requests have been made
    except KeyError:
        return False  # If the file is corrupted or improperly formatted

def initialize():
    raw_data_file = "forecast_data.json"
    processed_data_file = "noaa_filtered.json"
    
    if can_make_api_request(raw_data_file):
        get_and_store_forecast(raw_data_file)
        print("API request made and data updated.")
    else:
        print("API request limit reached. Using existing data.")   
    average_noaa_conditions_to_file(raw_data_file, processed_data_file)

def filter_for_8am(data):
    """Filters data to include only entries at 8 AM."""
    filtered = []
    for entry in data:
        if '08:00 AM' in entry['time']:
            filtered.append(entry)
    return filtered

@app.route('/')
def home():
    try:
        with open('noaa_filtered.json', 'r') as file:
            forecasts = json.load(file)
            chart_forecasts = filter_for_8am(forecasts)  # Filter data for chart
    except Exception as e:
        print(f"Failed to load forecast data: {e}")
        forecasts = []  # Provide an empty list if there's an error
        chart_forecasts = []  # Ensure chart data is also empty on failure
    return render_template('forecast.html', forecasts=forecasts, chart_forecasts=chart_forecasts)

initialize()

if __name__ == "__main__":
    app.run(debug=True)



