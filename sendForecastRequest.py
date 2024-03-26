import json
import requests
import os
import geocoder
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def update_needed(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            latest_date = max(datetime.strptime(entry['time'], "%Y-%m-%dT%H:%M:%S+00:00") for entry in data['hours'])
            return datetime.now() > latest_date
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError):
        return True

def get_and_store_forecast(output_file): 
    location = geocoder.ip('me')
    lat, lng = location.latlng  
    lat = round(lat, 3) 
    lng = round(lng, 3)  
    params = 'waterTemperature,wavePeriod,waveDirection,windDirection,windSpeed,waveHeight'
    api_url = f"https://api.stormglass.io/v2/weather/point?lat={lat}&lng={lng}&params={params}"
    headers = {
        'Authorization': os.getenv('STORMGLASS_API_KEY')
    }
    
    response = requests.get(api_url, headers=headers)
       
    if response.status_code == 200:
        data = response.json()
        
        with open(output_file, 'w') as file: 
            json.dump(data, file, indent=4)
        print(f"Forecast data has been saved to {output_file}") 
    else:
        print(f"Failed to get forecast data: {response.status_code}")

if __name__ == "__main__":
    json_file_path = "forecast_data.json"
    if update_needed(json_file_path):
        get_and_store_forecast(json_file_path)
    else:
        print("No update needed. Forecast data is up-to-date.")
