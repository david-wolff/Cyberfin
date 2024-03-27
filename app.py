from flask import Flask, render_template
import json
from datetime import datetime, timedelta

app = Flask(__name__)

def retrieve_forecast_for_next_day(json_file_path):
    current_datetime = datetime.now()
    end_datetime = (current_datetime + timedelta(days=4)).replace(hour=23, minute=59, second=59)  # Plus four days
    relevant_forecasts = []
    with open(json_file_path, 'r') as file:
        forecasts = json.load(file)

    for forecast in forecasts:
        forecast_time = datetime.strptime(forecast['time'], '%d/%m/%Y - %I:%M %p')
        if current_datetime <= forecast_time <= end_datetime:
            relevant_forecasts.append(forecast)
            if len(relevant_forecasts) >= 8:  # Limit to 8 forecasts
                break

    return relevant_forecasts


def degrees_to_direction(degrees):
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(degrees / (360. / len(directions)))
    return directions[index % len(directions)]

@app.route('/')
def home():
    json_file_path = 'noaa_filtered.json' 
    forecast_data = retrieve_forecast_for_next_day(json_file_path)
    return render_template('forecast.html', forecasts=forecast_data)

if __name__ == "__main__":
    app.run(debug=True)
