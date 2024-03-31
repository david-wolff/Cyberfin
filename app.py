from flask import Flask, render_template
import json
import os
from sendForecastRequest import get_and_store_forecast
from filterRequest import average_noaa_conditions_to_file

app = Flask(__name__)

def can_make_api_request(raw_data_file):
    """
    Checks if the application can make an API request without exceeding the quota.
    """
    if os.path.exists(raw_data_file):
        with open(raw_data_file, 'r') as file:
            data = json.load(file)
            request_count = data['meta']['requestCount']
            daily_quota = data['meta']['dailyQuota']
            
            if request_count < (daily_quota - 1):  # Ensuring we don't hit the quota
                return True
    # If the file doesn't exist or we've reached the quota, don't make a new request.
    return False

def initialize():
    raw_data_file = "forecast_data.json"
    processed_data_file = "noaa_filtered.json"
    
    if can_make_api_request(raw_data_file):
        get_and_store_forecast(raw_data_file)
        print("API request made and data updated.")
    else:
        print("API request limit reached. Using existing data.")
    
    average_noaa_conditions_to_file(raw_data_file, processed_data_file)

@app.route('/')
def home():
    with open("noaa_filtered.json", 'r') as file:
        forecasts = json.load(file)
    return render_template('forecast.html', forecasts=forecasts)

initialize()

if __name__ == "__main__":
    app.run(debug=True)
