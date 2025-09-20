# Project Structure Documentation

This document describes the organization and structure of the Enhanced Mortgage Alert System.

## 📁 Directory Structure

```
mortgage_alert/
├── src/                           # Source code directory
│   └── mortgage_alert/            # Main package
│       ├── __init__.py           # Package initialization
│       ├── cli.py                # Command-line interface
│       ├── core/                 # Core system components
│       │   ├── __init__.py
│       │   ├── alert_system.py   # Main orchestration class
│       │   └── config.py         # Configuration management
│       ├── scrapers/             # Rate scraping modules
│       │   ├── __init__.py
│       │   └── rate_scraper.py   # Multi-source rate scraper
│       ├── notifications/        # Notification services
│       │   ├── __init__.py
│       │   ├── notification_service.py  # Base notification class
│       │   ├── email_service.py         # Email notifications
│       │   └── telegram_service.py      # Telegram notifications
│       ├── data/                 # Data management
│       │   ├── __init__.py
│       │   └── data_manager.py   # Rate data persistence
│       └── utils/                # Utility functions
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_alert_system.py      # Tests for AlertSystem
│   ├── test_config.py            # Tests for Config
│   ├── test_data_manager.py      # Tests for RateDataManager
│   └── test_rate_scraper.py      # Tests for EnhancedRateScraper
├── docs/                         # Documentation
│   └── PROJECT_STRUCTURE.md      # This file
├── data/                         # Runtime data storage
│   ├── rates.csv                 # Rate history data
│   └── metadata.json             # System metadata
├── .github/                      # GitHub configuration
│   └── workflows/                # GitHub Actions workflows
│       └── enhanced-rate-alert.yml
├── main.py                       # Main entry point
├── setup.py                      # Package setup
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── env_example.txt               # Environment variables template
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

## 🏗️ Architecture Overview

### Core Components

1. **AlertSystem** (`core/alert_system.py`)
   - Main orchestration class
   - Coordinates all system components
   - Handles the complete alert workflow

2. **Config** (`core/config.py`)
   - Configuration management
   - Environment variable handling
   - Validation and error checking

### Data Layer

3. **RateDataManager** (`data/data_manager.py`)
   - Rate data persistence
   - Historical tracking
   - Statistical analysis
   - CSV-based storage

### Scraping Layer

4. **EnhancedRateScraper** (`scrapers/rate_scraper.py`)
   - Multi-source rate aggregation
   - Rate validation and outlier detection
   - Confidence scoring
   - Fallback mechanisms

### Notification Layer

5. **NotificationService** (Base class)
   - Abstract base for notification services
   - Common functionality and interfaces

6. **EmailNotificationService** (`notifications/email_service.py`)
   - SMTP email notifications
   - HTML formatting
   - Multiple recipients support

7. **TelegramNotificationService** (`notifications/telegram_service.py`)
   - Telegram bot API integration
   - Markdown formatting
   - Real-time delivery

### Interface Layer

8. **CLI** (`cli.py`)
   - Command-line interface
   - Status checking
   - Configuration validation
   - Statistics viewing

## 🔄 Data Flow

```
1. Configuration Loading
   ├── Environment variables
   ├── Validation
   └── Error handling

2. Rate Fetching
   ├── Multiple sources (FRED, Bankrate, MND, Freddie Mac)
   ├── Rate validation
   ├── Aggregation (median)
   └── Confidence scoring

3. Alert Logic
   ├── Threshold comparison
   ├── Daily report check
   └── Notification decision

4. Data Persistence
   ├── Rate storage
   ├── Metadata update
   └── Historical tracking

5. Notification
   ├── Message formatting
   ├── Delivery (Email/Telegram)
   └── Error handling
```

## 📦 Package Organization

### Import Structure

```python
# Main package imports
from mortgage_alert import AlertSystem, Config
from mortgage_alert.core import AlertSystem, Config
from mortgage_alert.scrapers import EnhancedRateScraper
from mortgage_alert.data import RateDataManager
from mortgage_alert.notifications import EmailNotificationService

# CLI usage
python -m mortgage_alert check
python -m mortgage_alert status
python -m mortgage_alert validate
```

### Entry Points

1. **main.py** - Direct script execution
2. **mortgage_alert.cli** - Command-line interface
3. **mortgage_alert.core.AlertSystem** - Programmatic usage

## 🧪 Testing Structure

```
tests/
├── test_alert_system.py      # Integration tests
├── test_config.py            # Configuration tests
├── test_data_manager.py      # Data persistence tests
└── test_rate_scraper.py      # Scraping tests
```

### Test Categories

1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Component interaction testing
3. **Mock Tests** - External service simulation
4. **Validation Tests** - Configuration and data validation

## 🚀 Deployment

### Local Development
```bash
pip install -e .
python main.py
```

### GitHub Actions
- Automated daily execution
- Data persistence via artifacts
- Log upload and monitoring

### Configuration
- Environment variables
- `.env` file support
- GitHub Secrets integration

## 📋 Maintenance

### Regular Tasks
1. Update rate source selectors
2. Monitor source reliability
3. Review and rotate API keys
4. Clean up old data files
5. Update dependencies

### Monitoring
1. Check GitHub Actions logs
2. Review rate data quality
3. Monitor notification delivery
4. Validate configuration

## 🔧 Development

### Adding New Features
1. Create feature branch
2. Add tests for new functionality
3. Update documentation
4. Submit pull request

### Code Standards
- Type hints for all functions
- Comprehensive error handling
- Detailed logging
- Unit test coverage
- Documentation strings

## 📊 Data Management

### Storage
- CSV format for rate data
- JSON format for metadata
- GitHub Artifacts for persistence
- 90-day retention policy

### Backup
- Git repository backup
- GitHub Actions artifacts
- Local data directory
- Configuration templates
