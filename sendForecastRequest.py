import requests
import os
import geocoder
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from app import store_data

load_dotenv()
logging.basicConfig(level=logging.INFO)

def fetch_forecast():
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
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get forecast data: {e}")
        return None

def filter_and_store_forecast(data):
    current_datetime = datetime.now()
    end_datetime = current_datetime + timedelta(days=10)
    desired_time = "08:00"

    filtered_data = []

    for hour in data['hours']:
        hour_time = datetime.strptime(hour['time'], "%Y-%m-%dT%H:%M:%S+00:00")
        if current_datetime <= hour_time <= end_datetime:
            if hour_time.strftime("%H:%M") == desired_time:
                filtered_entry = {
                    'time': hour_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'water_temperature': hour['waterTemperature']['noaa'],
                    'wave_direction': hour['waveDirection']['noaa'],
                    'wave_height': hour['waveHeight']['noaa'],
                    'wave_period': hour['wavePeriod']['noaa'],
                    'wind_direction': hour['windDirection']['noaa'],
                    'wind_speed': hour['windSpeed']['noaa']
                }
                filtered_data.append(filtered_entry)

    store_data(filtered_data)
    logging.info("Filtered forecast data has been stored in the database")

def update_forecast():
    data = fetch_forecast()
    if data:
        filter_and_store_forecast(data)

def schedule_requests():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_forecast, 'cron', hour=8)
    scheduler.add_job(update_forecast, 'cron', hour=16)
    scheduler.add_job(update_forecast, 'cron', hour=22)
    scheduler.start()

if __name__ == "__main__":
    schedule_requests()
    update_forecast()
