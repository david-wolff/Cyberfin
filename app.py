from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import os
import geocoder
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///surf_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SurfData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    water_temperature = db.Column(db.Float, nullable=False)
    wave_direction = db.Column(db.Float, nullable=False)
    wave_direction_cardinal = db.Column(db.String(3), nullable=False)
    wave_height = db.Column(db.Float, nullable=False)
    wave_period = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.Float, nullable=False)
    wind_direction_cardinal = db.Column(db.String(3), nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)

def degrees_to_cardinal(d):
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    ix = round(d / (360. / len(dirs)))
    return dirs[ix % len(dirs)]

@app.context_processor
def context_processor():
    return dict(degrees_to_cardinal=degrees_to_cardinal)

def store_data(data):
    for record in data:
        date_time = datetime.strptime(record['time'], "%Y-%m-%d %H:%M:%S")
        date = date_time.date()
        time = date_time.time()
        existing_data = SurfData.query.filter_by(date=date, time=time).first()

        if existing_data:
            db.session.delete(existing_data)

        new_data = SurfData(
            date=date,
            time=time,
            water_temperature=record['water_temperature'],
            wave_direction=record['wave_direction'],
            wave_direction_cardinal=degrees_to_cardinal(record['wave_direction']),
            wave_height=record['wave_height'],
            wave_period=record['wave_period'],
            wind_direction=record['wind_direction'],
            wind_direction_cardinal=degrees_to_cardinal(record['wind_direction']),
            wind_speed=record['wind_speed']
        )
        db.session.add(new_data)
    db.session.commit()

@app.route('/api/data', methods=['POST'])
def api_store_data():
    data = request.get_json()
    store_data(data.get('data', []))
    return jsonify({"message": "Data stored successfully"}), 200

@app.route('/fetch_and_store', methods=['GET'])
def fetch_and_store():
    data = fetch_forecast()
    if data:
        filter_and_store_forecast(data)
        return jsonify({"message": "Data fetched and stored successfully"}), 200
    else:
        return jsonify({"message": "Failed to fetch data"}), 500

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

@app.route('/')
def index():
    today = datetime.now().date()
    forecasts = SurfData.query.filter(SurfData.date >= today).order_by(SurfData.date, SurfData.time).all()
    
    # Debugging: Print retrieved forecasts
    print("Retrieved Forecasts:")
    for forecast in forecasts:
        print(forecast.date, forecast.time, forecast.wave_height)
    
    # Prepare data for the chart
    daily_data = {}
    for forecast in forecasts:
        key = forecast.date.strftime('%Y-%m-%d')
        if key not in daily_data:
            daily_data[key] = {'wave_heights': [], 'wave_periods': [], 'directions': []}
        
        daily_data[key]['wave_heights'].append(forecast.wave_height)
        daily_data[key]['wave_periods'].append(forecast.wave_period)
        daily_data[key]['directions'].append(degrees_to_cardinal(forecast.wind_direction))
    
    # Debugging: Print daily_data for chart
    print("Daily Data for Chart:")
    for key, data in daily_data.items():
        print(f"Date: {key}, Wave Heights: {data['wave_heights']}, Wave Periods: {data['wave_periods']}")
    
    chart_data = {
        'labels': list(daily_data.keys()),
        'wave_heights': [sum(d['wave_heights'])/len(d['wave_heights']) for d in daily_data.values()],
        'wave_periods': [sum(d['wave_periods'])/len(d['wave_periods']) for d in daily_data.values()]
    }
    
    # Debugging: Print chart_data
    print("Chart Data:")
    print(chart_data)
    
    return render_template('forecast.html', forecasts=forecasts, chart_data=chart_data)

@app.route('/check_db')
def check_db():
    data = SurfData.query.all()
    return jsonify([{
        'date': entry.date.strftime('%Y-%m-%d'),
        'time': entry.time.strftime('%H:%M:%S'),
        'water_temperature': entry.water_temperature,
        'wave_direction': entry.wave_direction,
        'wave_direction_cardinal': entry.wave_direction_cardinal,
        'wave_height': entry.wave_height,
        'wave_period': entry.wave_period,
        'wind_direction': entry.wind_direction,
        'wind_direction_cardinal': entry.wind_direction_cardinal,
        'wind_speed': entry.wind_speed
    } for entry in data])

def schedule_requests():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store, 'interval', hours=8)  # Fetch and store data every 8 hours
    scheduler.start()

if __name__ == '__main__':
    load_dotenv()  # Ensure environment variables are loaded
    logging.basicConfig(level=logging.INFO)
    try:
        with app.app_context():
            print("Creating all tables if they don't exist...")
            db.create_all()  # Create tables if they don't exist
            print("Tables created or verified.")
    except Exception as e:
        print("Error during database initialization:", str(e))
    
    schedule_requests()  # Start the scheduler
    app.run(debug=True)
