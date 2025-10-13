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


def get_weather_forecast(api_key, location):
    """
    Fetch weather forecast from OpenWeatherMap API

    Args:
        api_key: OpenWeatherMap API key
        location: City name or "lat,lon" coordinates

    Returns:
        dict: Weather data including precipitation probability
    """
    base_url = "http://api.openweathermap.org/data/2.5/forecast"

    # Check if location is coordinates or city name
    if ',' in location:
        lat, lon = location.split(',')
        params = {
            'lat': lat.strip(),
            'lon': lon.strip(),
            'appid': api_key,
            'units': 'imperial'
        }
    else:
        params = {
            'q': location,
            'appid': api_key,
            'units': 'imperial'
        }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    return response.json()


def analyze_weather(weather_data):
    """
    Analyze weather data to determine if umbrella is needed

    Args:
        weather_data: JSON response from OpenWeatherMap

    Returns:
        tuple: (needs_umbrella: bool, reason: str, forecast_details: str)
    """
    # Check next 24 hours (8 3-hour forecasts)
    forecasts = weather_data['list'][:8]

    rain_forecasts = []
    conditions = []

    for forecast in forecasts:
        time = datetime.fromtimestamp(forecast['dt']).strftime('%I:%M %p')
        weather = forecast['weather'][0]
        description = weather['description']
        main_weather = weather['main']

        # Check for precipitation
        pop = forecast.get('pop', 0) * 100  # Probability of precipitation

        conditions.append(f"  • {time}: {description.title()} (Temp: {forecast['main']['temp']:.0f}°F)")

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
    weather_data = get_weather_forecast(weather_api_key, location)

    print("Analyzing weather conditions...")
    needs_umbrella, reason, forecast_details = analyze_weather(weather_data)

    print(f"Sending email to {recipient_email}...")
    send_email(
        smtp_server, smtp_port, sender_email, sender_password, recipient_email,
        needs_umbrella, reason, forecast_details, location
    )

    print("✓ Email sent successfully!")
    print(f"Recommendation: {'BRING UMBRELLA' if needs_umbrella else 'NO UMBRELLA NEEDED'}")


if __name__ == '__main__':
    main()
