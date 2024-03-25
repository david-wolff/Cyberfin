import json
from datetime import datetime, timedelta

def average_noaa_conditions_to_file(input_file_path, output_file_path):
    #Times when conditions are checked
    key_times = ["02:00", "08:00", "12:00", "18:00"]
    #Forecast Range
    current_datetime = datetime.now()
    end_datetime = current_datetime + timedelta(days=7)

    #Dict for accumulating averages of data
    accumulated_data = {}

    # Read the JSON data from the file
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    for hour in data['hours']:
        hour_time = datetime.strptime(hour['time'], "%Y-%m-%dT%H:%M:%S+00:00")
        if current_datetime <= hour_time <= end_datetime:
            if hour_time.strftime("%H:%M") in key_times:
                formatted_timestamp = hour_time.strftime("%d/%m/%Y - %I:%M %p")
                
                if formatted_timestamp not in accumulated_data:
                    accumulated_data[formatted_timestamp] = {key: 0 for key in ['waterTemperature', 'waveDirection', 'waveHeight', 'wavePeriod', 'windDirection', 'windSpeed']}
                    accumulated_data[formatted_timestamp]['count'] = 0
                
                for key in ['waterTemperature', 'waveDirection', 'waveHeight', 'wavePeriod', 'windDirection', 'windSpeed']:
                    accumulated_data[formatted_timestamp][key] += hour[key]['noaa']
                accumulated_data[formatted_timestamp]['count'] += 1

    # Prepare the average data for output
    average_data = []
    for timestamp, values in accumulated_data.items():
        count = values.pop('count')
        if count > 0:
            formatted_entry = {
                'time': timestamp,
                'conditions': {key: round(value / count, 2) for key, value in values.items()}
            }
            average_data.append(formatted_entry)

    average_data.sort(key=lambda x: datetime.strptime(x['time'], '%d/%m/%Y - %I:%M %p'))
    
    with open(output_file_path, 'w') as outfile:
        json.dump(average_data, outfile, indent=4)

if __name__ == "__main__":

    input_file_path = 'forecast_data.json'  
    output_file_path = 'noaa_filtered.json'  
    
    average_noaa_conditions_to_file(input_file_path, output_file_path)
    