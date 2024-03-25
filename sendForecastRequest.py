import json
import requests 
import os
import geocoder
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

load_dotenv()

def get_and_store_forecast(output_file): 
    
    location = geocoder.ip('me')
    lat, lng = location.latlng  # Get the latitude and longitude
    lat = round(lat, 3) 
    lng = round(lng, 3)  # Round the longitude to 3 decimal places
    #geolocator = Nominatim(user_agent = "geoapiExercises")
    #location = geolocator.geocode(location_name)
    #lat, lon = round(location.latitude, 3), round(location.longitude, 3)
    params = 'waterTemperature,wavePeriod,waveDirection,windDirection,windSpeed,waveHeight'
    api_url = f"https://api.stormglass.io/v2/weather/point?lat={lat}&lng={lng}&params={params}"
    headers = {
        
        'Authorization' : os.getenv('STORMGLASS_API_KEY')
    
    }
    
    response = requests.get(api_url, headers=headers)
       
    if response.status_code == 200:
        data = response.json()
        
        with open(output_file, 'w') as file: 
            json.dump(data, file, indent=4)
        print(f"Forecast data for {location} has been saved to {output_file}") 
    else:
        print(f"Failed to get forecast data: {response.status_code}")
if __name__ == "__main__":
    get_and_store_forecast("forecast_data.json")