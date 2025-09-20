"""
Command Line Interface for the Mortgage Alert System
"""

import argparse
import sys
import logging
from typing import Optional

from .core.alert_system import AlertSystem
from .core.config import config


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Hardcoded log file location
    log_file = "alert.log"
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_alert_check() -> int:
    """Run the alert check process"""
    try:
        alert_system = AlertSystem()
        success = alert_system.run_alert_check()
        return 0 if success else 1
    except Exception as e:
        logging.error(f"Error running alert check: {e}")
        return 1


def show_status() -> int:
    """Show current system status"""
    try:
        alert_system = AlertSystem()
        
        print("=== Mortgage Alert System Status ===")
        print(f"Target Rate: {config.target_rate}%")
        print(f"State: {config.state}")
        print(f"Notification Method: {config.notification_method}")
        print(f"Daily Report: {config.daily_report}")
        print(f"Rate Sources: {', '.join(config.preferred_sources)}")
        
        # Get current rate
        rate, source_data = alert_system.get_current_rate()
        if rate:
            print(f"\nCurrent Rate: {rate}%")
            print(f"Confidence: {source_data.get('confidence', 'unknown')}")
            print(f"Sources: {', '.join(source_data.get('successful_sources', []))}")
        else:
            print("\nCould not retrieve current rate")
        
        # Get data summary
        print(f"\n{alert_system.data_manager.get_data_summary()}")
        
        return 0
    except Exception as e:
        logging.error(f"Error showing status: {e}")
        return 1


def show_statistics(days: int = 30) -> int:
    """Show rate statistics"""
    try:
        alert_system = AlertSystem()
        stats = alert_system.get_rate_statistics(days)
        
        print(f"=== Rate Statistics (Last {days} Days) ===")
        if 'error' in stats:
            print(f"Error: {stats['error']}")
            return 1
        
        print(f"Records: {stats.get('record_count', 0)}")
        print(f"Latest Rate: {stats.get('latest_rate', 'N/A')}%")
        print(f"Average Rate: {stats.get('average_rate', 'N/A')}%")
        print(f"Min Rate: {stats.get('min_rate', 'N/A')}%")
        print(f"Max Rate: {stats.get('max_rate', 'N/A')}%")
        print(f"Trend: {stats.get('trend', 'unknown')}")
        print(f"Volatility: {stats.get('volatility', 'N/A')}")
        print(f"Data Size: {stats.get('data_size_kb', 0)} KB")
        
        return 0
    except Exception as e:
        logging.error(f"Error showing statistics: {e}")
        return 1


def validate_config() -> int:
    """Validate configuration"""
    try:
        validation = config.validate()
        
        print("=== Configuration Validation ===")
        for key, value in validation.items():
            status = "✓" if value else "✗"
            print(f"{status} {key}: {value}")
        
        if validation.get('valid'):
            print("\n✓ Configuration is valid")
            return 0
        else:
            print("\n✗ Configuration has issues")
            return 1
    except Exception as e:
        logging.error(f"Error validating configuration: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Mortgage Alert System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mortgage-alert check          # Run alert check
  mortgage-alert status         # Show current status
  mortgage-alert stats --days 7 # Show 7-day statistics
  mortgage-alert validate       # Validate configuration
        """
    )
    
    parser.add_argument(
        'command',
        choices=['check', 'status', 'stats', 'validate'],
        help='Command to run'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for statistics (default: 30)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Log level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Execute command
    if args.command == 'check':
        return run_alert_check()
    elif args.command == 'status':
        return show_status()
    elif args.command == 'stats':
        return show_statistics(args.days)
    elif args.command == 'validate':
        return validate_config()
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
