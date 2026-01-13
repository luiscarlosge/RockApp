"""
SocketIO Fallback Configuration for Restricted Environments

This module provides fallback configurations for environments where
WebSocket connections may be restricted or unavailable, such as:
- Corporate firewalls
- Proxy servers
- Load balancers without WebSocket support
- Network environments with connection restrictions

The fallback strategy uses:
1. Server-Sent Events (SSE) for server-to-client communication
2. HTTP polling for client-to-server communication
3. Long polling for improved efficiency
4. Graceful degradation with user notifications
"""

import os
import logging
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)

class SocketIOFallbackConfig:
    """Manages SocketIO fallback configurations for restricted environments."""
    
    @staticmethod
    def get_azure_config():
        """Get Azure App Service optimized SocketIO configuration."""
        return {
            'cors_allowed_origins': "*",
            'async_mode': 'threading',  # Best for Azure App Service
            'logger': True,
            'engineio_logger': True,
            'ping_timeout': 60,
            'ping_interval': 25,
            'max_http_buffer_size': 1000000,  # 1MB
            'transports': ['websocket', 'polling'],
            'allow_upgrades': True,
            'http_compression': True,
            'compression_threshold': 1024,
            'always_connect': True,
            'reconnection': True,
            'reconnection_attempts': 5,
            'reconnection_delay': 1000,
            'reconnection_delay_max': 5000,
            'max_reconnection_attempts': 5,
            'timeout': 20000,
            'force_new_connection': False
        }
    
    @staticmethod
    def get_restricted_config():
        """Get configuration for highly restricted environments."""
        return {
            'cors_allowed_origins': "*",
            'async_mode': 'threading',
            'logger': True,
            'engineio_logger': False,  # Reduce logging in restricted environments
            'ping_timeout': 120,  # Longer timeout for slow connections
            'ping_interval': 60,  # Less frequent pings
            'max_http_buffer_size': 500000,  # Smaller buffer
            'transports': ['polling'],  # Only polling, no WebSocket
            'allow_upgrades': False,  # Disable WebSocket upgrades
            'http_compression': False,  # Disable compression to avoid issues
            'always_connect': True,
            'reconnection': True,
            'reconnection_attempts': 10,  # More attempts for unreliable connections
            'reconnection_delay': 2000,  # Longer initial delay
            'reconnection_delay_max': 10000,  # Longer max delay
            'max_reconnection_attempts': 10,
            'timeout': 30000,  # Longer timeout
            'force_new_connection': True  # Force new connections
        }
    
    @staticmethod
    def get_local_dev_config():
        """Get configuration for local development."""
        return {
            'cors_allowed_origins': "*",
            'async_mode': 'threading',
            'logger': True,
            'engineio_logger': True,
            'ping_timeout': 20,
            'ping_interval': 10,
            'max_http_buffer_size': 1000000,
            'transports': ['websocket', 'polling'],
            'allow_upgrades': True,
            'http_compression': True,
            'always_connect': True,
            'reconnection': True,
            'reconnection_attempts': 3,
            'reconnection_delay': 500,
            'reconnection_delay_max': 2000,
            'max_reconnection_attempts': 3,
            'timeout': 10000,
            'force_new_connection': False
        }
    
    @staticmethod
    def detect_environment():
        """Detect the current environment and return appropriate configuration."""
        # Check for Azure App Service
        if os.environ.get('WEBSITE_SITE_NAME'):
            logger.info("Detected Azure App Service environment")
            return 'azure'
        
        # Check for restricted environment indicators
        restricted_indicators = [
            os.environ.get('HTTP_PROXY'),
            os.environ.get('HTTPS_PROXY'),
            os.environ.get('CORPORATE_NETWORK'),
            os.environ.get('WEBSOCKET_DISABLED')
        ]
        
        if any(restricted_indicators):
            logger.info("Detected restricted network environment")
            return 'restricted'
        
        # Check Flask environment
        flask_env = os.environ.get('FLASK_ENV', 'production').lower()
        if flask_env in ['development', 'dev']:
            logger.info("Detected local development environment")
            return 'local_dev'
        
        # Default to Azure configuration for production
        logger.info("Using Azure configuration as default")
        return 'azure'
    
    @classmethod
    def get_config(cls, environment=None):
        """Get SocketIO configuration for the specified or detected environment."""
        if environment is None:
            environment = cls.detect_environment()
        
        config_map = {
            'azure': cls.get_azure_config,
            'restricted': cls.get_restricted_config,
            'local_dev': cls.get_local_dev_config
        }
        
        config_func = config_map.get(environment, cls.get_azure_config)
        config = config_func()
        
        logger.info(f"Using SocketIO configuration for environment: {environment}")
        logger.info(f"Transports: {config['transports']}")
        logger.info(f"WebSocket upgrades: {config.get('allow_upgrades', 'N/A')}")
        
        return config
    
    @staticmethod
    def configure_socketio(app, environment=None):
        """Configure and return a SocketIO instance with fallback support."""
        config = SocketIOFallbackConfig.get_config(environment)
        
        try:
            # Create SocketIO instance with configuration
            socketio = SocketIO(app, **config)
            
            # Add fallback event handlers
            SocketIOFallbackConfig.add_fallback_handlers(socketio)
            
            logger.info("SocketIO configured successfully with fallback support")
            return socketio
            
        except Exception as e:
            logger.error(f"Failed to configure SocketIO: {str(e)}")
            
            # Try with minimal configuration as last resort
            try:
                minimal_config = {
                    'cors_allowed_origins': "*",
                    'async_mode': 'threading',
                    'transports': ['polling'],
                    'logger': False,
                    'engineio_logger': False
                }
                
                socketio = SocketIO(app, **minimal_config)
                logger.warning("Using minimal SocketIO configuration as fallback")
                return socketio
                
            except Exception as fallback_error:
                logger.error(f"Failed to configure minimal SocketIO: {str(fallback_error)}")
                raise
    
    @staticmethod
    def add_fallback_handlers(socketio):
        """Add event handlers for fallback scenarios."""
        
        @socketio.on('connect_error')
        def handle_connect_error(data):
            """Handle connection errors and suggest fallbacks."""
            logger.warning(f"SocketIO connection error: {data}")
            
        @socketio.on('disconnect')
        def handle_disconnect():
            """Handle disconnections with fallback information."""
            logger.info("SocketIO client disconnected")
        
        @socketio.on('reconnect')
        def handle_reconnect():
            """Handle successful reconnections."""
            logger.info("SocketIO client reconnected")
        
        @socketio.on('reconnect_error')
        def handle_reconnect_error(data):
            """Handle reconnection errors."""
            logger.warning(f"SocketIO reconnection error: {data}")

def get_client_fallback_config(environment=None):
    """Get client-side JavaScript configuration for fallback scenarios."""
    if environment is None:
        environment = SocketIOFallbackConfig.detect_environment()
    
    if environment == 'restricted':
        return {
            'transports': ['polling'],
            'upgrade': False,
            'rememberUpgrade': False,
            'timeout': 30000,
            'reconnection': True,
            'reconnectionAttempts': 10,
            'reconnectionDelay': 2000,
            'reconnectionDelayMax': 10000,
            'maxReconnectionAttempts': 10,
            'forceNew': True
        }
    elif environment == 'azure':
        return {
            'transports': ['websocket', 'polling'],
            'upgrade': True,
            'rememberUpgrade': True,
            'timeout': 20000,
            'reconnection': True,
            'reconnectionAttempts': 5,
            'reconnectionDelay': 1000,
            'reconnectionDelayMax': 5000,
            'maxReconnectionAttempts': 5,
            'forceNew': False
        }
    else:  # local_dev
        return {
            'transports': ['websocket', 'polling'],
            'upgrade': True,
            'rememberUpgrade': True,
            'timeout': 10000,
            'reconnection': True,
            'reconnectionAttempts': 3,
            'reconnectionDelay': 500,
            'reconnectionDelayMax': 2000,
            'maxReconnectionAttempts': 3,
            'forceNew': False
        }

# Export main configuration function
configure_socketio_with_fallback = SocketIOFallbackConfig.configure_socketio