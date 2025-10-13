#!/usr/bin/env python3
"""
Umbrella Advisor - Daily weather check and email notification
Checks weather forecast and emails whether you should bring an umbrella
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def geocode_location(api_key, location):
    """
    Convert city name to latitude/longitude coordinates

    Args:
        api_key: OpenWeatherMap API key
        location: City name (e.g., "Boston,MA,US" or "London,GB")

    Returns:
        tuple: (latitude, longitude, location_name)
    """
    geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': location,
        'limit': 1,
        'appid': api_key
    }

    print(f"Geocoding location: {location}")
    response = requests.get(geocode_url, params=params)
    response.raise_for_status()

    data = response.json()
    if not data:
        raise ValueError(f"Location '{location}' not found. Try adding country code (e.g., 'Boston,MA,US')")

    result = data[0]
    lat = result['lat']
    lon = result['lon']
    name = result['name']
    state = result.get('state', '')
    country = result.get('country', '')

    location_name = f"{name}"
    if state:
        location_name += f", {state}"
    if country:
        location_name += f", {country}"

    print(f"Found coordinates: {lat}, {lon} ({location_name})")
    return lat, lon, location_name


def get_weather_forecast(api_key, location):
    """
    Fetch weather forecast from OpenWeatherMap One Call API 3.0

    Args:
        api_key: OpenWeatherMap API key
        location: City name (e.g., "Boston,MA,US") or "lat,lon" coordinates

    Returns:
        tuple: (weather_data dict, location_name string)
    """
    # Check if location is coordinates (numeric) or city name
    if ',' in location:
        parts = location.split(',')
        # Check if both parts are numeric (coordinates)
        try:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            location_name = f"Coordinates: {lat}, {lon}"
        except ValueError:
            # Not numeric, geocode the city name
            lat, lon, location_name = geocode_location(api_key, location)
    else:
        # Single city name, geocode it
        lat, lon, location_name = geocode_location(api_key, location)

    # Use One Call API 3.0
    base_url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'imperial',
        'exclude': 'minutely,alerts'  # We only need hourly and daily forecasts
    }

    print(f"Fetching weather from One Call API 3.0...")
    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(f"Error Response: {response.status_code}")
        print(f"Response Body: {response.text}")

    response.raise_for_status()

    return response.json(), location_name


def analyze_weather(weather_data):
    """
    Analyze weather data to determine if umbrella is needed
    Uses One Call API 3.0 response format

    Args:
        weather_data: JSON response from OpenWeatherMap One Call API 3.0

    Returns:
        tuple: (needs_umbrella: bool, reason: str, forecast_details: str)
    """
    # Check next 24 hours from hourly forecast
    hourly_forecasts = weather_data['hourly'][:24]

    rain_forecasts = []
    conditions = []

    for forecast in hourly_forecasts:
        time = datetime.fromtimestamp(forecast['dt']).strftime('%I:%M %p')
        weather = forecast['weather'][0]
        description = weather['description']
        main_weather = weather['main']

        # Check for precipitation
        pop = forecast.get('pop', 0) * 100  # Probability of precipitation

        conditions.append(f"  • {time}: {description.title()} (Temp: {forecast['temp']:.0f}°F, {pop:.0f}% precip)")

        # Check if rain/snow is likely
        if main_weather in ['Rain', 'Drizzle', 'Thunderstorm', 'Snow']:
            rain_forecasts.append((time, description, pop))
        elif pop >= 30:  # 30% or higher chance of rain
            rain_forecasts.append((time, f"possible precipitation", pop))

    forecast_summary = "\n".join(conditions)

    if rain_forecasts:
        needs_umbrella = True
        rain_times = [f"{time} ({desc}, {pop:.0f}% chance)" for time, desc, pop in rain_forecasts]
        reason = f"Precipitation expected:\n  " + "\n  ".join(rain_times)
    else:
        needs_umbrella = False
        reason = "Clear skies ahead - no precipitation expected in the next 24 hours."

    return needs_umbrella, reason, forecast_summary


def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email,
               needs_umbrella, reason, forecast_details, location):
    """
    Send email notification about umbrella recommendation

    Args:
        smtp_server: SMTP server address (e.g., smtp.gmail.com)
        smtp_port: SMTP port (usually 587 for TLS)
        sender_email: Email address sending the notification
        sender_password: App-specific password for sender email
        recipient_email: Email address to receive notification
        needs_umbrella: Boolean indicating if umbrella is needed
        reason: Explanation of the recommendation
        forecast_details: Detailed forecast information
        location: Location being monitored
    """
    # Create message
    msg = MIMEMultipart('alternative')

    if needs_umbrella:
        subject = f"☂️ BRING AN UMBRELLA - {location}"
        emoji = "☂️"
        recommendation = "YES, bring an umbrella today!"
    else:
        subject = f"☀️ No umbrella needed - {location}"
        emoji = "☀️"
        recommendation = "No umbrella needed today!"

    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Create plain text and HTML versions
    text_body = f"""
Umbrella Advisor - Daily Weather Report
{'=' * 50}

{emoji} {recommendation}

{reason}

Today's Forecast for {location}:
{forecast_details}

{'=' * 50}
Report generated at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
"""

    html_body = f"""
<html>
<head>
<style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
    .header {{ background-color: {'#4a90e2' if needs_umbrella else '#f39c12'}; color: white; padding: 20px; text-align: center; }}
    .content {{ padding: 20px; }}
    .recommendation {{ font-size: 24px; font-weight: bold; color: {'#e74c3c' if needs_umbrella else '#27ae60'}; }}
    .reason {{ background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-left: 4px solid {'#e74c3c' if needs_umbrella else '#27ae60'}; }}
    .forecast {{ background-color: #f9f9f9; padding: 15px; margin: 15px 0; }}
    .footer {{ font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; }}
</style>
</head>
<body>
    <div class="header">
        <h1>{emoji} Umbrella Advisor</h1>
        <p>Daily Weather Report for {location}</p>
    </div>
    <div class="content">
        <p class="recommendation">{recommendation}</p>
        <div class="reason">
            <strong>Why?</strong><br>
            {reason.replace(chr(10), '<br>')}
        </div>
        <div class="forecast">
            <strong>Today's Forecast:</strong><br>
            {forecast_details.replace(chr(10), '<br>')}
        </div>
    </div>
    <div class="footer">
        Report generated at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
    </div>
</body>
</html>
"""

    # Attach both versions
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)


def main():
    """Main function to orchestrate weather check and email notification"""

    # Get configuration from environment variables
    weather_api_key = os.environ.get('WEATHER_API_KEY')
    location = os.environ.get('LOCATION', 'Boston,MA')

    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipient_email = os.environ.get('RECIPIENT_EMAIL', sender_email)

    # Validate required environment variables
    required_vars = {
        'WEATHER_API_KEY': weather_api_key,
        'SENDER_EMAIL': sender_email,
        'SENDER_PASSWORD': sender_password
    }

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    print(f"Fetching weather for {location}...")
    weather_data, location_name = get_weather_forecast(weather_api_key, location)

    print("Analyzing weather conditions...")
    needs_umbrella, reason, forecast_details = analyze_weather(weather_data)

    print(f"Sending email to {recipient_email}...")
    send_email(
        smtp_server, smtp_port, sender_email, sender_password, recipient_email,
        needs_umbrella, reason, forecast_details, location_name
    )

    print("✓ Email sent successfully!")
    print(f"Recommendation: {'BRING UMBRELLA' if needs_umbrella else 'NO UMBRELLA NEEDED'}")


if __name__ == '__main__':
    main()
