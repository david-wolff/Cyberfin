# Cyberfin

This is a web-based Surf Forecast application that provides real-time surf conditions such as wave height, wave period, wind direction, and wind speed.

## Features

- **Live Surf Data**: Fetch and display live data on surfing conditions including water temperature, wave direction, and more.
- **Daily Forecasts**: Provides forecasts at different times of the day, highlighting ideal times for surfing.
- **Interactive Chart**: Visualize wave heights and wave periods throughout the day with an interactive chart.

## Technologies Used

- **Flask**: A micro web framework written in Python, used for serving the application.
- **Chart.js**: Simple yet flexible JavaScript charting for designers & developers.
- **JavaScript**: For handling client-side interactions.
- **CSS**: For styling the application with a modern theme.

## Setup and Installation

1. **Clone the repository:**

git clone https://github.com/yourusername/surf-forecast-app.git

cd surf-forecast-app

2. **Install dependencies:**

Ensure you have Python installed, and then set up a virtual environment:

python -m venv venv
source venv/bin/activate # On Windows use venv\Scripts\activate

Install the required Python packages:

pip install -r requirements.txt

3. **Set Environment Variables:**

Create a `.env` file in the project directory and add the necessary environment variables:

STORMGLASS_API_KEY=your_api_key_here

4. **Run the Application:**

python3 app.py

Visit `http://127.0.0.1:5000/` in your web browser to view the application.

## Usage

After launching the application, you will see the current day's surf forecasts presented in a series of cards, each representing different times of the day. The interactive chart at the top of the page displays wave height and period data specifically for the 8 AM forecasts each day.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, or open issues to discuss proposed changes or additions.

## License

This project is open-sourced under the MIT License. See the LICENSE file for more information.
