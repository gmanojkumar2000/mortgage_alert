# Enhanced Mortgage Alert System

A robust Python-based alert system that monitors refinance mortgage rates from multiple sources and sends notifications when rates drop below your target threshold.

## 🚀 New Features (v2.0.0)

### ✅ **Multi-Source Rate Aggregation**
- Fetches rates from multiple sources simultaneously
- Uses median calculation for more reliable aggregated rates
- Includes confidence scoring based on source consistency
- Fallback mechanisms for when sources fail

### ✅ **Data Persistence & Historical Tracking**
- Stores rate data using GitHub Artifacts (100% FREE)
- Tracks rate trends and volatility
- Provides statistical analysis and insights
- 90-day data retention with automatic cleanup

### ✅ **Enhanced Reliability**
- Improved rate validation and outlier detection
- Better error handling and retry logic
- Updated scraping selectors and fallback URLs
- Comprehensive logging and monitoring

## 📁 Project Structure

```
mortgage_alert/
├── src/mortgage_alert/           # Main package
│   ├── core/                     # Core system components
│   │   ├── alert_system.py       # Main orchestration class
│   │   └── config.py            # Configuration management
│   ├── scrapers/                 # Rate scraping modules
│   │   └── rate_scraper.py      # Multi-source rate scraper
│   ├── notifications/            # Notification services
│   │   ├── notification_service.py
│   │   ├── email_service.py
│   │   └── telegram_service.py
│   ├── data/                     # Data management
│   │   └── data_manager.py      # Rate data persistence
│   └── utils/                    # Utility functions
├── tests/                        # Test suite
├── docs/                         # Documentation
├── data/                         # Rate data storage
├── main.py                       # Main entry point
├── setup.py                      # Package setup
└── requirements.txt              # Dependencies
```

## 🛠️ Installation & Setup

### 1. Clone and Install
```bash
git clone <your-repo-url>
cd mortgage_alert

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### 2. Configuration
Copy the example environment file:
```bash
cp env_example.txt .env
```

Edit `.env` with your settings:
```env
# Email Configuration
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com

# Telegram Configuration (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Alert Settings
TARGET_RATE=6.0
NOTIFICATION_METHOD=email  # or telegram
STATE=Oregon
DAILY_REPORT=true

# Rate Sources
RATE_SOURCE=fred
FRED_API_KEY=your_fred_api_key  # Optional but recommended

# Logging
LOG_LEVEL=INFO
```

### 3. Test the System
```bash
# Run the main alert system
python main.py

# Or use the CLI
python -m mortgage_alert check

# Check system status
python -m mortgage_alert status

# Validate configuration
python -m mortgage_alert validate
```

## 🔧 GitHub Actions Setup

### 1. Add Repository Secrets
Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret. Add:
- `SENDER_EMAIL`
- `SENDER_PASSWORD`
- `RECIPIENT_EMAIL` (comma-separated for multiple recipients)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TARGET_RATE` (e.g. `6`)
- `NOTIFICATION_METHOD` (`email` or `telegram`)
- `STATE` (e.g. `Oregon`)
- `FRED_API_KEY` (optional but recommended)

### 2. Workflow Configuration
The system uses `.github/workflows/enhanced-rate-alert.yml` which:
- Runs daily at 7:30 AM PST (15:30 UTC)
- Downloads previous rate data from artifacts
- Runs the enhanced rate check
- Uploads updated data and logs as artifacts
- Optionally commits data to repository

## 📊 Rate Sources

The system aggregates rates from multiple sources:

1. **FRED (Federal Reserve)** - Most reliable, official data
2. **Bankrate** - Consumer-focused rates
3. **Mortgage News Daily** - Industry rates
4. **Freddie Mac PMMS** - Primary market survey

### Confidence Levels
- **High**: 3+ sources with low variance (< 5%)
- **Medium**: 2+ sources with moderate variance (< 10%)
- **Low**: Few sources or high variance

## 💾 Data Persistence

### GitHub Artifacts (Recommended)
- **Cost**: 100% FREE
- **Storage**: 500MB free quota
- **Retention**: 90 days
- **Reliability**: High (GitHub infrastructure)

### Data Structure
```csv
date,timestamp,rate,source,target_rate,state,alert_sent,daily_report_sent,notes
2024-01-15,2024-01-15T10:30:00,5.25,fred;bankrate,6.0,Oregon,false,true,"Sources: fred, bankrate, Confidence: high"
```

## 🔔 Notifications

### Email Notifications
- HTML formatted emails
- Multiple recipients support
- Rich rate information and trends
- Action items and next steps

### Telegram Notifications
- Markdown formatted messages
- Inline rate information
- Quick action suggestions
- Real-time delivery

## 🧪 Testing

Run the test suite:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_alert_system.py

# Run with coverage
python -m pytest tests/ --cov=src/mortgage_alert

# Run tests with verbose output
python -m pytest tests/ -v

# Run tests and generate HTML coverage report
python -m pytest tests/ --cov=src/mortgage_alert --cov-report=html
```

## 📈 Monitoring & Analytics

The system provides:
- Rate trend analysis
- Volatility tracking
- Historical comparisons
- Source reliability metrics
- Alert frequency statistics

## 🔒 Security

- Environment variables for sensitive data
- GitHub Secrets for CI/CD
- No hardcoded credentials
- Secure API key handling

## 🚀 Advanced Usage

### Custom Rate Sources
Add new rate sources by extending the `EnhancedRateScraper` class:

```python
class CustomRateScraper(RateScraper):
    def get_rate(self) -> Optional[float]:
        # Your custom scraping logic
        pass
```

### Custom Notifications
Create custom notification services:

```python
class CustomNotificationService(NotificationService):
    def send_alert(self, current_rate: float, target_rate: float, 
                   state: str, **kwargs) -> bool:
        # Your custom notification logic
        pass
```

## 📝 Logging

Comprehensive logging includes:
- Rate fetching attempts and results
- Source reliability metrics
- Notification delivery status
- Data persistence operations
- Error handling and recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Rate scraping fails**: Check internet connectivity and source availability
2. **Email not sending**: Verify Gmail app password and SMTP settings
3. **Telegram not working**: Check bot token and chat ID
4. **Data not persisting**: Verify GitHub Actions permissions

### Debug Mode
Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

### Manual Testing
```bash
# Test rate scraping only
python -c "import sys; sys.path.insert(0, 'src'); from mortgage_alert.scrapers import get_enhanced_rate_scraper; scraper = get_enhanced_rate_scraper(); print(scraper.get_aggregated_rate())"

# Test data persistence only
python -c "import sys; sys.path.insert(0, 'src'); from mortgage_alert.data import data_manager; print(data_manager.get_data_summary())"

# Test configuration
python -c "import sys; sys.path.insert(0, 'src'); from mortgage_alert.core.config import config; print(config.get_summary())"

# Test CLI
python -m mortgage_alert status
python -m mortgage_alert validate
```

## 📞 Support

For issues and questions:
- Check the logs in `alert.log`
- Review GitHub Actions workflow runs
- Open an issue on GitHub
- Check the troubleshooting section above

---

**Version**: 2.0.0  
**Last Updated**: September 2024  
**Python**: 3.8+