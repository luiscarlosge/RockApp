"""
Azure App Service startup configuration
This file ensures proper Flask application startup on Azure App Service
with enhanced error handling and logging.
"""

import os
import sys
import logging
from app import app

# Configure logging for Azure App Service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """
    Application factory for Azure App Service deployment.
    Returns the configured Flask application instance.
    """
    try:
        # Log startup information
        logger.info("Starting Musician Song Selector application")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Verify CSV data file exists
        csv_path = os.path.join(os.getcwd(), 'Data.csv')
        if os.path.exists(csv_path):
            logger.info(f"CSV data file found at: {csv_path}")
        else:
            logger.error(f"CSV data file not found at: {csv_path}")
            logger.info(f"Files in current directory: {os.listdir(os.getcwd())}")
        
        # Configure Flask app for Azure
        app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
        app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info("Application configured successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

# Create the application instance
application = create_app()

if __name__ == "__main__":
    try:
        # Get port from environment variable for Azure App Service
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Run the application
        application.run(
            host=host, 
            port=port, 
            debug=application.config.get('DEBUG', False)
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)