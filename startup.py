"""
Azure App Service startup configuration
This file ensures proper Flask application startup on Azure App Service
with enhanced error handling and logging, including SocketIO support.
"""

import os
import sys
import logging
from app import app, socketio

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
    Returns the configured Flask application instance with SocketIO.
    """
    try:
        # Log startup information
        logger.info("Starting Musician Song Selector application with SocketIO")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Verify CSV data file exists
        csv_path = os.path.join(os.getcwd(), 'Data.csv')
        if os.path.exists(csv_path):
            logger.info(f"CSV data file found at: {csv_path}")
        else:
            logger.error(f"CSV data file not found at: {csv_path}")
            logger.info(f"Files in current directory: {os.listdir(os.getcwd())}")
        
        # Configure Flask app for Azure with WebSocket support
        app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
        app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        # Azure App Service WebSocket configuration
        if os.environ.get('WEBSITE_SITE_NAME'):  # Running on Azure
            logger.info("Configuring for Azure App Service with WebSocket support")
            app.config['WEBSOCKET_ENABLED'] = True
            app.config['SOCKETIO_ASYNC_MODE'] = 'threading'
            app.config['SOCKETIO_PING_TIMEOUT'] = 60
            app.config['SOCKETIO_PING_INTERVAL'] = 25
            
            # Azure-specific SocketIO configuration
            socketio.init_app(
                app,
                cors_allowed_origins="*",
                async_mode='threading',
                logger=True,
                engineio_logger=True,
                ping_timeout=60,
                ping_interval=25,
                transports=['websocket', 'polling'],
                allow_upgrades=True,
                http_compression=True
            )
        else:
            # Local development configuration
            logger.info("Configuring for local development")
            app.config['WEBSOCKET_ENABLED'] = True
            
        logger.info("Application with SocketIO configured successfully")
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
        
        logger.info(f"Starting SocketIO server on {host}:{port}")
        
        # Check if running on Azure App Service
        is_azure = os.environ.get('WEBSITE_SITE_NAME') is not None
        
        if is_azure:
            logger.info("Running on Azure App Service with WebSocket support")
            # Azure App Service configuration
            socketio.run(
                application,
                host=host, 
                port=port, 
                debug=False,  # Always False in production
                use_reloader=False,  # Disable reloader for production
                log_output=True,
                # Azure-specific settings
                allow_unsafe_werkzeug=True,  # Required for Azure
                transports=['websocket', 'polling'],
                # WebSocket configuration
                ping_timeout=60,
                ping_interval=25,
                max_http_buffer_size=1000000,  # 1MB
                cors_allowed_origins="*"
            )
        else:
            logger.info("Running in local development mode")
            # Local development configuration
            socketio.run(
                application,
                host=host, 
                port=port, 
                debug=application.config.get('DEBUG', False),
                use_reloader=False,  # Disable reloader to prevent issues
                log_output=True
            )
        
    except Exception as e:
        logger.error(f"Failed to start SocketIO application: {str(e)}")
        sys.exit(1)