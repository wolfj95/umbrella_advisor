# Umbrella Advisor

An automated daily weather checker that emails you at 7am to let you know if you should bring an umbrella. Runs automatically using GitHub Actions.

## Features

- Fetches 24-hour weather forecast from OpenWeatherMap
- Analyzes precipitation probability and weather conditions
- Sends beautifully formatted HTML email with umbrella recommendation
- Runs automatically every day at 7am using GitHub Actions
- Uses your personal email account (Gmail, Outlook, etc.)

## Setup Instructions

### 1. Get OpenWeatherMap API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key (free tier allows 1,000 calls/day)
4. Save your API key for later

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
| `WEATHER_API_KEY` | Your OpenWeatherMap API key | `abc123def456...` |
| `LOCATION` | Your city/location | `Boston,MA` or `40.7128,-74.0060` |
| `SMTP_SERVER` | Your email provider's SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (usually 587) | `587` |
| `SENDER_EMAIL` | Your email address | `you@gmail.com` |
| `SENDER_PASSWORD` | Your app-specific password | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Email to receive notifications (usually same as sender) | `you@gmail.com` |

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
2. The script fetches weather data from OpenWeatherMap API
3. It analyzes the next 24 hours for:
   - Rain, drizzle, thunderstorms, or snow
   - Probability of precipitation (30% or higher)
4. Sends you an HTML email with:
   - Clear recommendation (bring umbrella or not)
   - Explanation with specific precipitation times
   - Full 24-hour forecast
5. Email includes both plain text and beautiful HTML formatting

## Troubleshooting

### Workflow fails with authentication error
- Verify you're using an **app-specific password**, not your regular email password
- Check that 2-Factor Authentication is enabled for your email account
- Ensure the SMTP server and port are correct for your provider

### No email received
- Check spam/junk folder
- Verify `RECIPIENT_EMAIL` secret is set correctly
- Review workflow logs in GitHub Actions tab

### Weather data not loading
- Verify your `WEATHER_API_KEY` is valid
- Check that `LOCATION` is in correct format: `City,State` or `latitude,longitude`
- Free OpenWeatherMap tier has 1,000 calls/day limit

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
