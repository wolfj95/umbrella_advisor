# Umbrella Advisor

An automated daily weather checker that emails you at 7am to let you know if you should bring an umbrella. Runs automatically using GitHub Actions. test 4

## Features

- Fetches 24-hour hourly weather forecast from OpenWeatherMap One Call API 3.0
- Analyzes precipitation probability and weather conditions
- Sends beautifully formatted HTML email with umbrella recommendation
- Runs automatically every day at 7am using GitHub Actions
- Uses your personal email account (Gmail, Outlook, etc.)
- Supports both city names and GPS coordinates

## Setup Instructions

### 1. Get OpenWeatherMap API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to [API Keys](https://home.openweathermap.org/api_keys) and copy your API key
4. **Important**: This script uses the **One Call API 3.0**, which requires a subscription
   - Go to [One Call API 3.0](https://openweathermap.org/api/one-call-3)
   - Subscribe to "One Call by Call" (includes 1,000 free calls/day)
   - No credit card required for the free tier
5. Wait 1-2 hours for your API key to activate (new keys take time to activate)

### 2. Set Up Email App Password

Since you're using your own email account, you'll need an app-specific password:

#### For Gmail:
1. Enable 2-Factor Authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Select "Mail" and "Other (Custom name)"
4. Name it "Umbrella Advisor"
5. Copy the generated 16-character password

#### For Outlook/Hotmail:
1. Go to [Microsoft Account Security](https://account.microsoft.com/security)
2. Enable 2-Step Verification
3. Create an app password
4. Copy the generated password

#### For Other Email Providers:
Look for "app passwords" or "application-specific passwords" in your email provider's security settings.

### 3. Push Code to GitHub

1. Create a new repository on GitHub
2. Initialize git and push this code:

```bash
git init
git add .
git commit -m "Initial commit: Umbrella advisor"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/umbrella-advisor.git
git push -u origin main
```

### 4. Configure GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** and add each of the following:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `WEATHER_API_KEY` | Your OpenWeatherMap API key (with One Call 3.0 subscription) | `abc123def456...` |
| `LOCATION` | Your city/location with country code | `Somerville,MA,US` or `Boston,MA,US` |
| `SMTP_SERVER` | Your email provider's SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (usually 587) | `587` |
| `SENDER_EMAIL` | Your email address | `you@gmail.com` |
| `SENDER_PASSWORD` | Your app-specific password | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Email to receive notifications (usually same as sender) | `you@gmail.com` |

**Location Format Options:**
- City with state and country: `Somerville,MA,US` (recommended for US cities)
- City with country: `London,GB` or `Paris,FR`
- GPS coordinates: `42.3875,-71.0995` (latitude,longitude)

#### Common SMTP Servers:
- **Gmail**: `smtp.gmail.com` (port 587)
- **Outlook/Hotmail**: `smtp-mail.outlook.com` (port 587)
- **Yahoo**: `smtp.mail.yahoo.com` (port 587)
- **iCloud**: `smtp.mail.me.com` (port 587)

### 5. Adjust Schedule (Optional)

The workflow runs at 7am EST by default. To change this:

1. Open [.github/workflows/daily-umbrella-check.yml](.github/workflows/daily-umbrella-check.yml)
2. Find the cron schedule: `- cron: '0 12 * * *'`
3. Adjust the time (uses UTC, so 12:00 UTC = 7:00 AM EST)
4. Use [crontab.guru](https://crontab.guru/) to help with cron syntax

**Common timezone conversions:**
- 7am EST = 12:00 UTC → `0 12 * * *`
- 7am PST = 15:00 UTC → `0 15 * * *`
- 7am CST = 13:00 UTC → `0 13 * * *`

### 6. Test the Workflow

1. Go to **Actions** tab in your GitHub repository
2. Click on "Daily Umbrella Check" workflow
3. Click **Run workflow** > **Run workflow**
4. Check your email within a few minutes

## How It Works

1. **GitHub Actions** triggers the workflow daily at 7am (or manually)
2. The script uses the **Geocoding API** to convert your city name to coordinates
3. It fetches weather data from **One Call API 3.0** with hourly forecasts
4. It analyzes the next 24 hours for:
   - Rain, drizzle, thunderstorms, or snow
   - Probability of precipitation (30% or higher)
5. Sends you an HTML email with:
   - Clear recommendation (bring umbrella or not)
   - Explanation with specific precipitation times and probabilities
   - Full 24-hour hourly forecast with temperature and precipitation chance
6. Email includes both plain text and beautiful HTML formatting

## Troubleshooting

### Workflow fails with 401 or 403 error
- Your API key may not be activated yet (wait 1-2 hours after creation)
- Verify you've subscribed to **One Call API 3.0** ("One Call by Call" subscription)
- Check that your API key is correctly set in GitHub Secrets

### Workflow fails with "Location not found"
- Add country code to your location: `Somerville,MA,US` instead of `Somerville,MA`
- Use the format: `City,State,CountryCode` for US cities
- Or use GPS coordinates: `42.3875,-71.0995`

### Workflow fails with authentication error (email)
- Verify you're using an **app-specific password**, not your regular email password
- Check that 2-Factor Authentication is enabled for your email account
- Ensure the SMTP server and port are correct for your provider

### No email received
- Check spam/junk folder
- Verify `RECIPIENT_EMAIL` secret is set correctly
- Review workflow logs in GitHub Actions tab

### Weather data not loading
- Verify your `WEATHER_API_KEY` is valid and activated
- Check that you've subscribed to One Call API 3.0 (required, but free tier available)
- Verify `LOCATION` format includes country code: `Boston,MA,US`
- Free tier has 1,000 calls/day limit

### Wrong timezone
- GitHub Actions runs in UTC
- Adjust the cron schedule in the workflow file
- Remember to account for daylight saving time changes

## File Structure

```
umbrella-advisor/
├── umbrella_advisor.py          # Main script
├── requirements.txt             # Python dependencies
├── .github/
│   └── workflows/
│       └── daily-umbrella-check.yml  # GitHub Actions workflow
└── README.md                    # This file
```

## Customization

### Change precipitation threshold
Edit line 77 in [umbrella_advisor.py](umbrella_advisor.py):
```python
elif pop >= 30:  # Change 30 to your preferred percentage
```

### Modify email styling
Edit the HTML template in the `send_email()` function (lines 120-160)

### Add more weather details
Modify the `analyze_weather()` function to include wind, humidity, etc.

## Privacy & Security

- All sensitive data is stored in GitHub Secrets (encrypted)
- Secrets are never exposed in logs or code
- The script only runs when triggered by GitHub Actions
- No data is stored or shared with third parties

## License

MIT License - Feel free to modify and use as you wish!

## Support

If you encounter issues:
1. Check the GitHub Actions logs for error messages
2. Verify all secrets are set correctly
3. Test your API keys and credentials manually
4. Open an issue in this repository

---

Stay dry! ☂️
