#!/usr/bin/env python3
"""
Mortgage Alert System - Main Entry Point
Enhanced version with multi-source aggregation, data persistence, and improved reliability
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mortgage_alert.core.alert_system import AlertSystem
from mortgage_alert.core.config import config


def setup_logging():
    """Setup logging configuration"""
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main function to run the mortgage alert system"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Enhanced Mortgage Alert System")
    logger.info(f"Version: 2.0.0")
    
    try:
        # Create alert system
        alert_system = AlertSystem()
        
        # Run alert check
        success = alert_system.run_alert_check()
        
        if success:
            logger.info("Mortgage alert system completed successfully")
            return 0
        else:
            logger.error("Mortgage alert system failed")
            return 1
            
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
