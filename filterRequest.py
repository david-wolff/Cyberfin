import json
from datetime import datetime, timedelta

def filter_noaa_conditions_to_file(input_file_path, output_file_path):
    current_datetime = datetime.now()
    end_datetime = current_datetime + timedelta(days=10)
    desired_time = "08:00"

    filtered_data = []

    with open(input_file_path, 'r') as file:
        data = json.load(file)

    for hour in data['hours']:
        hour_time = datetime.strptime(hour['time'], "%Y-%m-%dT%H:%M:%S+00:00")
        if current_datetime <= hour_time <= end_datetime:
            if hour_time.strftime("%H:%M") == desired_time:
                formatted_entry = {
                    'time': hour_time.strftime("%d/%m/%Y %H:%M"),
                    'conditions': {
                        'waterTemperature': hour['waterTemperature']['noaa'],
                        'waveDirection': hour['waveDirection']['noaa'],
                        'waveHeight': hour['waveHeight']['noaa'],
                        'wavePeriod': hour['wavePeriod']['noaa'],
                        'windDirection': hour['windDirection']['noaa'],
                        'windSpeed': hour['windSpeed']['noaa']
                    }
                }
                filtered_data.append(formatted_entry)

    filtered_data.sort(key=lambda x: datetime.strptime(x['time'], '%d/%m/%Y %H:%M'))
    
    with open(output_file_path, 'w') as outfile:
        json.dump(filtered_data, outfile, indent=4)

if __name__ == "__main__":
    input_file_path = 'forecast_data.json'  
    output_file_path = 'noaa_filtered.json'  
    
    filter_noaa_conditions_to_file(input_file_path, output_file_path)
