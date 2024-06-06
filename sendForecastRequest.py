import json
import requests
import os
import geocoder
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def update_needed(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            last_request_time = datetime.strptime(data['meta']['end'], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return now - last_request_time > timedelta(hours=8)  # Allow updates every 8 hours
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
        headers = {'Authorization': os.getenv('STORMGLASS_API_KEY_2')}
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status() 
        
        data = response.json()
        with open(output_file, 'w') as file: 
            json.dump(data, file, indent=4)
        logging.info(f"Forecast data has been saved to {output_file}") 
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get forecast data: {e}")

def schedule_requests():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: request_forecast_if_needed('forecast_data.json'), 'cron', hour=8)
    scheduler.add_job(lambda: request_forecast_if_needed('forecast_data.json'), 'cron', hour=16)
    scheduler.add_job(lambda: request_forecast_if_needed('forecast_data.json'), 'cron', hour=22)
    scheduler.start()

def request_forecast_if_needed(json_file_path):
    if update_needed(json_file_path):
        get_and_store_forecast(json_file_path)
    else:
        logging.info("No update needed. Forecast data is up-to-date.")

if __name__ == "__main__":
    schedule_requests()
    json_file_path = "forecast_data.json"
    if update_needed(json_file_path):
        get_and_store_forecast(json_file_path)
    else:
        print("No update needed. Forecast data is up-to-date.")
