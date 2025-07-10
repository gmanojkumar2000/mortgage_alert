# Refinance Rate Alert System

A Python-based alert system that notifies you via email or Telegram when refinance mortgage rates for Oregon drop below your target threshold.

---

## Features
- Scrapes refinance rates from public sources (Bankrate, Mortgage News Daily, Freddie Mac)
- Sends alerts via Gmail (using app password) or Telegram
- **Supports multiple email recipients** (comma-separated)
- **Daily rate reports** - send daily updates regardless of threshold
- All configuration and credentials are loaded from a `.env` file
- Logs every run to `alert.log`
- Runs daily at 7:30 AM PST via GitHub Actions

---

## 1. Local Setup

### 1.1. Clone the Repository
```bash
git clone <your-repo-url>
cd mortgage_alert
```

### 1.2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.3. Create Your `.env` File
Copy the template and fill in your values:
```bash
cp env_example.txt .env
```
Edit `.env`:
```
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com,recipient3@example.com
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TARGET_RATE=6
NOTIFICATION_METHOD=email  # or telegram
STATE=Oregon
DAILY_REPORT=true  # Send daily rate report regardless of threshold
LOG_FILE=alert.log
LOG_LEVEL=INFO
RATE_SOURCE=freddiemac  # bankrate, mortgage_news_daily, or freddiemac
```

**Multiple Email Recipients:**
- Add multiple email addresses separated by commas: `recipient1@example.com,recipient2@example.com`
- No spaces around commas (spaces will be automatically trimmed)
- All recipients will receive the same alert email

**Daily Reports:**
- Set `DAILY_REPORT=true` to receive daily rate updates regardless of threshold
- Set `DAILY_REPORT=false` to only receive alerts when rates drop below target

- **Gmail:** Use an [App Password](https://support.google.com/accounts/answer/185833) (not your regular password)
- **Telegram:** [Create a bot and get your chat ID](https://core.telegram.org/bots#6-botfather)

### 1.4. Test the Script Manually
```bash
python rate_alert.py
```
- Check `alert.log` for results and errors.

---

## 2. GitHub Actions Setup

### 2.1. Add Repository Secrets
Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret. Add:
- `SENDER_EMAIL`
- `SENDER_PASSWORD`
- `RECIPIENT_EMAIL` (comma-separated for multiple recipients)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TARGET_RATE` (e.g. `6`)
- `NOTIFICATION_METHOD` (`email` or `telegram`)
- `STATE` (e.g. `Oregon`)

### 2.2. How the Scheduler Works
- The workflow in `.github/workflows/rate-alert.yml` runs **every day at 7:30 AM PST** (15:30 UTC)
- It loads secrets into a `.env` file
- Installs dependencies
- Runs `python rate_alert.py`
- Uploads `alert.log` as an artifact for review

---

## 3. Customization
- **Change rate source:** Set `RATE_SOURCE` in `.env` to `bankrate`, `mortgage_news_daily`, or `freddiemac`
- **Change notification:** Set `NOTIFICATION_METHOD` to `email` or `telegram`
- **Add/remove recipients:** Update `RECIPIENT_EMAIL` with comma-separated addresses
- **Daily reports:** Set `DAILY_REPORT=true` to get daily updates, `false` for threshold-only alerts
- **Change logging:** Set `LOG_LEVEL` in `.env` to `DEBUG`, `INFO`, `WARNING`, or `ERROR`

---

## 4. Troubleshooting
- Check `alert.log` for errors
- Make sure your Gmail uses an App Password
- For Telegram, ensure your bot and chat ID are correct
- If running on GitHub Actions, check the Actions tab for logs and artifacts
- **Multiple recipients:** Ensure email addresses are comma-separated without spaces

---

## 5. Security
- **Never commit your `.env` file** with real credentials
- Use GitHub Secrets for CI/CD
- Rotate your app passwords and tokens regularly

---

## 6. Manual Test Script
You can also run:
```bash
python test_rate_alert.py
```
To check scraping, notification, and config loading.

---

## 7. License
MIT 