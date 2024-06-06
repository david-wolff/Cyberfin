import requests
import json
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import geocoder
import os

# Load environment variables
load_dotenv()

def fetch_tide_data(lat, lng, api_key):
    """Fetch tide data for today and the next two days."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=2)  # Fetching data for today and the next two days
    params = {
        'lat': lat,
        'lng': lng,
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
        'params': 'waterLevel',
        'source': 'noaa'
    }
    headers = {
        'Authorization': api_key
    }
    try:
        response = requests.get('https://api.stormglass.io/v2/tide/extremes/point', params=params, headers=headers)
        response.raise_for_status()  # Will raise an exception for HTTP error codes
        tide_data = response.json()
        print("Tide data fetched successfully")
        # Filter for high and low tides
        high_low_tides = [entry for entry in tide_data['data'] if entry['type'] in ['high', 'low']]
        return adjust_time_to_brt(high_low_tides)
    except requests.RequestException as e:
        print(f"Failed to fetch tide data: {e}")
        return []  # Return an empty list in case of failure

def save_tide_data(tide_data, file_path):
    """Save tide data to a JSON file, ensuring time is saved in ISO format."""
    with open(file_path, 'w') as file:
        json.dump(tide_data, file, indent=4)
    print(f"Tide data saved to {file_path}")

def get_coordinates(use_rio=False):
    """Get geographic coordinates based on IP address or use Rio de Janeiro's coordinates."""
    if use_rio:
        return (-22.9068, -43.1729)  # Rio de Janeiro coordinates
    location = geocoder.ip('me')
    return location.latlng

def adjust_time_to_brt(tide_entries):
    brt_zone = pytz.timezone('America/Sao_Paulo')
    corrected_tide_entries = []
    for tide in tide_entries:
        utc_time = datetime.strptime(tide['time'], "%Y-%m-%dT%H:%M:%S+00:00")
        utc_time = pytz.utc.localize(utc_time)  # Correctly localize the UTC time
        brt_time = utc_time.astimezone(brt_zone)  # Convert to BRT
        print(f"Original UTC: {tide['time']} -> Converted BRT: {brt_time.isoformat()}")
        tide['time'] = brt_time.isoformat()  # Keep in ISO format for JavaScript
        corrected_tide_entries.append(tide)
    return corrected_tide_entries

if __name__ == "__main__":
    lat, lng = get_coordinates(use_rio=True)  # Change use_rio to False to use actual IP location
    api_key = os.getenv('STORMGLASS_API_KEY_2_2')
    tides = fetch_tide_data(lat, lng, api_key)
    save_tide_data(tides, 'tides.json')
