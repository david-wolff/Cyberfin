import json
import requests
import os
import geocoder
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from datetime import datetime, timezone

def update_needed(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            first_forecast_time = datetime.strptime(data['hours'][0]['time'], "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=timezone.utc)
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            return first_forecast_time < today
            
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError):
        return True


def get_and_store_forecast(output_file): 
    try:
        location = geocoder.ip('me')
        lat, lng = location.latlng  
        lat = round(lat, 3) 
        lng = round(lng, 3)  
        params = 'waterTemperature,wavePeriod,waveDirection,windDirection,windSpeed,waveHeight'
        api_url = f"https://api.stormglass.io/v2/weather/point?lat={lat}&lng={lng}&params={params}"
        headers = {'Authorization': os.getenv('STORMGLASS_API_KEY')}
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status() 
        
        data = response.json()
        with open(output_file, 'w') as file: 
            json.dump(data, file, indent=4)
        logging.info(f"Forecast data has been saved to {output_file}") 
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get forecast data: {e}")
def clear_json_files():
    with open('forecast_data.json', 'w') as f:
        f.write('{}')  # Or '[]' if your root JSON structure is a list
    with open('noaa_filtered.json', 'w') as f:
        f.write('[]')
if __name__ == "__main__":
    json_file_path = "forecast_data.json"
    if update_needed(json_file_path):
        get_and_store_forecast(json_file_path)
    else:
        print("No update needed. Forecast data is up-to-date.")
