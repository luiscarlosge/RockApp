#!/usr/bin/env python3
"""
Azure App Service Linux startup configuration
This file ensures proper Flask application startup on Azure App Service Linux
with enhanced error handling and logging.
"""

import os
import sys
import logging
import signal
from app import app

# Configure logging for Azure App Service Linux
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def create_app():
    """
    Application factory for Azure App Service Linux deployment.
    Returns the configured Flask application instance.
    """
    try:
        # Log startup information
        logger.info("Starting Musician Song Selector application on Linux")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Verify CSV data file exists
        csv_path = os.path.join(os.getcwd(), 'Data.csv')
        if os.path.exists(csv_path):
            logger.info(f"CSV data file found at: {csv_path}")
        else:
            logger.error(f"CSV data file not found at: {csv_path}")
            logger.info(f"Files in current directory: {os.listdir(os.getcwd())}")
        
        # Configure Flask app for Azure Linux
        app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
        app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        # Azure App Service Linux configuration
        if os.environ.get('WEBSITE_SITE_NAME'):  # Running on Azure
            logger.info("Configuring for Azure App Service Linux")
        else:
            # Local development configuration
            logger.info("Configuring for local development")
            
        logger.info("Application configured successfully for Linux")
        return app
        
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

# Create the application instance
application = create_app()

if __name__ == "__main__":
    try:
        # Get port from environment variable for Azure App Service
        port = int(os.environ.get('PORT', 8000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info(f"Starting Flask server on {host}:{port}")
        
        # Check if running on Azure App Service Linux
        is_azure = os.environ.get('WEBSITE_SITE_NAME') is not None
        
        if is_azure:
            logger.info("Running on Azure App Service Linux")
            # Azure App Service Linux configuration
            application.run(
                host=host, 
                port=port, 
                debug=False,  # Always False in production
                use_reloader=False,  # Disable reloader for production
                threaded=True
            )
        else:
            logger.info("Running in local development mode")
            # Local development configuration
            application.run(
                host=host, 
                port=port, 
                debug=application.config.get('DEBUG', False),
                use_reloader=False,  # Disable reloader to prevent issues
                threaded=True
            )
        
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        sys.exit(1)