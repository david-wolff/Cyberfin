from flask import Flask, render_template
import json
import pytz
import os
from datetime import datetime, timedelta
from sendForecastRequest import get_and_store_forecast
from filterRequest import filter_noaa_conditions_to_file
from tide_data import fetch_tide_data, save_tide_data, get_coordinates

app = Flask(__name__)

def degrees_to_cardinal(d):
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((d + 11.25) / 22.5) % 16
    return f"{d}° {dirs[ix]}"

def initialize():
    raw_data_file = "forecast_data.json"
    processed_data_file = "noaa_filtered.json"
    
    get_and_store_forecast(raw_data_file)
    filter_noaa_conditions_to_file(raw_data_file, processed_data_file)
    
    lat, lng = get_coordinates(use_rio=True)  # Change use_rio to False to use actual IP location
    api_key = os.getenv('STORMGLASS_API_KEY_2')
    tides = fetch_tide_data(lat, lng, api_key)
    save_tide_data(tides, 'tides.json')
    print("Initialization complete")

def filter_tides(tides):
    today = datetime.now().astimezone(pytz.timezone('America/Sao_Paulo'))
    end_time = today + timedelta(days=2)  # End of the next two days
    filtered_tides = []
    for tide in tides:
        local_time = datetime.fromisoformat(tide['time']).astimezone(pytz.timezone('America/Sao_Paulo'))
        if today <= local_time < end_time:
            tide['time'] = local_time.strftime('%d/%m/%y %H:%M')
            filtered_tides.append(tide)
    return filtered_tides

@app.route('/')
def home():
    try:
        with open('noaa_filtered.json', 'r') as file:
            forecasts = json.load(file)
            for forecast in forecasts:
                forecast['conditions']['waveDirection'] = degrees_to_cardinal(forecast['conditions']['waveDirection'])
                forecast['conditions']['windDirection'] = degrees_to_cardinal(forecast['conditions']['windDirection'])
        
        with open('tides.json', 'r') as file:
            raw_tides = json.load(file)
            tides = filter_tides(raw_tides)
            print(f"Tides data loaded and filtered: {tides}")
    except Exception as e:
        print(f"Failed to load forecast or tide data: {e}")
        forecasts = []
        tides = []

    return render_template('forecast.html', forecasts=forecasts, tides=tides)

initialize()

if __name__ == "__main__":
    app.run(debug=True)
