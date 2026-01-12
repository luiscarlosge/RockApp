"""
Rock and Roll Forum Jam en Español - Flask Web Application
A responsive web application for musicians to view song assignments with Spanish language support.
"""

from flask import Flask, render_template, jsonify, request, session
import os
import logging
import time
from functools import wraps
from csv_data_processor import CSVDataProcessor
from spanish_translations import SPANISH_TRANSLATIONS, get_translation, get_error_message, get_retry_message, get_recovery_message, translate_instrument_name
from live_performance_manager import LivePerformanceManager

# Create Flask application instance
app = Flask(__name__)

# Azure App Service compatibility configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Session configuration for live performance persistence
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days in seconds
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('WEBSITE_SITE_NAME') is not None  # Secure cookies in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configure for Azure App Service environment
if os.environ.get('WEBSITE_SITE_NAME'):  # Running on Azure
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
    # Azure App Service logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Running on Azure App Service")
else:
    # Local development
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Enhanced error handling and retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 0.5
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60  # seconds

# Global error tracking
error_counts = {}
circuit_breaker_state = {}

def circuit_breaker(service_name):
    """
    Circuit breaker decorator to prevent cascading failures.
    
    Args:
        service_name: Name of the service to protect
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_time = time.time()
            
            # Check if circuit is open
            if service_name in circuit_breaker_state:
                last_failure_time, failure_count = circuit_breaker_state[service_name]
                if failure_count >= CIRCUIT_BREAKER_THRESHOLD:
                    if current_time - last_failure_time < CIRCUIT_BREAKER_TIMEOUT:
                        app.logger.warning(f"Circuit breaker open for {service_name}")
                        return jsonify({"error": get_error_message("server_unavailable")}), 503
                    else:
                        # Reset circuit breaker after timeout
                        del circuit_breaker_state[service_name]
                        app.logger.info(f"Circuit breaker reset for {service_name}")
            
            try:
                result = f(*args, **kwargs)
                # Reset error count on success
                if service_name in error_counts:
                    error_counts[service_name] = 0
                return result
            except Exception as e:
                # Increment error count
                error_counts[service_name] = error_counts.get(service_name, 0) + 1
                
                # Update circuit breaker state
                if error_counts[service_name] >= CIRCUIT_BREAKER_THRESHOLD:
                    circuit_breaker_state[service_name] = (current_time, error_counts[service_name])
                    app.logger.error(f"Circuit breaker triggered for {service_name}")
                
                raise e
        return decorated_function
    return decorator

def retry_on_failure(max_attempts=MAX_RETRY_ATTEMPTS, delay=RETRY_DELAY):
    """
    Decorator to retry API operations on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        app.logger.warning(f"Attempt {attempt + 1} failed for {f.__name__}: {str(e)}. Retrying...")
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        app.logger.error(f"All {max_attempts} attempts failed for {f.__name__}: {str(e)}")
            
            raise last_exception
        return decorated_function
    return decorator

def handle_api_error(error, operation_name):
    """
    Centralized API error handling with Spanish error messages.
    
    Args:
        error: The exception that occurred
        operation_name: Name of the operation that failed
        
    Returns:
        Tuple of (JSON response, HTTP status code)
    """
    app.logger.error(f"API error in {operation_name}: {str(error)}")
    
    if isinstance(error, FileNotFoundError):
        return jsonify({"error": get_error_message("file_not_found")}), 404
    elif isinstance(error, ValueError):
        return jsonify({"error": get_error_message("invalid_format", str(error))}), 400
    elif isinstance(error, ConnectionError):
        return jsonify({"error": get_error_message("network")}), 503
    elif isinstance(error, TimeoutError):
        return jsonify({"error": get_error_message("timeout")}), 504
    else:
        return jsonify({"error": get_error_message("500", str(error))}), 500

# Initialize CSV data processor with error handling for Azure
try:
    data_processor = CSVDataProcessor()
    live_performance_manager = LivePerformanceManager(data_processor)
    app.logger.info("CSV data processor and live performance manager initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize data processor or live performance manager: {str(e)}")
    # Create dummy processors to prevent app crash
    data_processor = None
    live_performance_manager = None

# Performance optimization: Simple in-memory cache
_response_cache = {}
_cache_timeout = 300  # 5 minutes cache timeout

def cache_response(timeout=300):
    """
    Simple decorator for caching responses to improve performance.
    
    Args:
        timeout: Cache timeout in seconds (default: 300 seconds / 5 minutes)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{f.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            current_time = time.time()
            
            # Check if we have a valid cached response
            if cache_key in _response_cache:
                cached_data, timestamp = _response_cache[cache_key]
                if current_time - timestamp < timeout:
                    return cached_data
            
            # Generate new response
            result = f(*args, **kwargs)
            
            # Cache the response
            _response_cache[cache_key] = (result, current_time)
            
            # Clean old cache entries (simple cleanup)
            if len(_response_cache) > 100:  # Limit cache size
                old_keys = [k for k, (_, ts) in _response_cache.items() 
                           if current_time - ts > timeout]
                for key in old_keys:
                    _response_cache.pop(key, None)
            
            return result
        return decorated_function
    return decorator

# Configure logging for Azure App Service
if not app.debug:
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    """Main application page with song selector interface and Spanish translations."""
    try:
        # Pass Spanish translations to the template
        translations = SPANISH_TRANSLATIONS
        # Ensure consistent page title
        translations['page_title'] = translations['app_title']
        return render_template('index.html', translations=translations)
    except Exception as e:
        app.logger.error(f"Error rendering index page: {str(e)}")
        return get_error_message("500"), 500

@app.route('/api/songs')
@cache_response(timeout=600)  # Cache for 10 minutes
@circuit_breaker('songs_api')
@retry_on_failure(max_attempts=2)
def get_songs():
    """Return JSON list of all songs for dropdown population with comprehensive error handling."""
    try:
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Validate data processor health
        health_status = data_processor.get_data_health_status()
        if health_status["fallback_active"]:
            app.logger.warning("Using fallback data for songs API")
        
        songs = data_processor.get_songs_for_dropdown()
        
        # Validate response data
        if not songs or not isinstance(songs, list):
            raise ValueError("Invalid songs data returned from processor")
        
        response = jsonify({"songs": songs})
        
        # Performance optimization: Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        response.headers['ETag'] = f'songs-{len(songs)}-{hash(str(songs))}'
        
        return response
        
    except Exception as e:
        return handle_api_error(e, "get_songs")

@app.route('/api/song/<song_id>')
@cache_response(timeout=600)  # Cache for 10 minutes
@circuit_breaker('song_details_api')
@retry_on_failure(max_attempts=2)
def get_song_details(song_id):
    """Return detailed musician assignments for selected song with comprehensive error handling."""
    try:
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Validate input
        if not song_id or not isinstance(song_id, str):
            return jsonify({"error": get_error_message("invalid_format", "Invalid song ID")}), 400
        
        song = data_processor.get_song_by_id(song_id)
        if song is None:
            return jsonify({"error": get_error_message("song_not_found")}), 404
        
        song_details = data_processor.format_song_display(song)
        
        # Validate response data
        if not song_details or not isinstance(song_details, dict):
            raise ValueError("Invalid song details returned from processor")
        
        # Translate instrument names to Spanish
        if 'assignments' in song_details:
            for instrument, musician in song_details['assignments'].items():
                if musician:
                    # Keep the original structure but ensure translation is available
                    pass
        
        response = jsonify(song_details)
        
        # Performance optimization: Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        response.headers['ETag'] = f'song-{song_id}-{hash(str(song_details))}'
        
        return response
        
    except Exception as e:
        return handle_api_error(e, "get_song_details")

@app.route('/api/musicians')
@cache_response(timeout=600)  # Cache for 10 minutes
@circuit_breaker('musicians_api')
@retry_on_failure(max_attempts=2)
def get_musicians():
    """Return JSON list of all musicians for dropdown population with comprehensive error handling."""
    try:
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Validate data processor health
        health_status = data_processor.get_data_health_status()
        if health_status["fallback_active"]:
            app.logger.warning("Using fallback data for musicians API")
        
        musicians = data_processor.get_musicians_for_dropdown()
        
        # Validate response data
        if not isinstance(musicians, list):
            raise ValueError("Invalid musicians data returned from processor")
        
        response = jsonify({"musicians": musicians})
        
        # Performance optimization: Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        response.headers['ETag'] = f'musicians-{len(musicians)}-{hash(str(musicians))}'
        
        return response
        
    except Exception as e:
        return handle_api_error(e, "get_musicians")

@app.route('/api/musician/<musician_id>')
@cache_response(timeout=600)  # Cache for 10 minutes
@circuit_breaker('musician_details_api')
@retry_on_failure(max_attempts=2)
def get_musician_details(musician_id):
    """Return detailed song assignments for selected musician with comprehensive error handling."""
    try:
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Validate input
        if not musician_id or not isinstance(musician_id, str):
            return jsonify({"error": get_error_message("invalid_format", "Invalid musician ID")}), 400
        
        musician = data_processor.get_musician_by_id(musician_id)
        if musician is None:
            return jsonify({"error": get_error_message("musician_not_found")}), 404
        
        # Validate response data
        if not musician or not isinstance(musician, dict):
            raise ValueError("Invalid musician details returned from processor")
        
        response = jsonify(musician)
        
        # Performance optimization: Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        response.headers['ETag'] = f'musician-{musician_id}-{hash(str(musician))}'
        
        return response
        
    except Exception as e:
        return handle_api_error(e, "get_musician_details")

@app.route('/api/live-performance')
@cache_response(timeout=60)  # Cache for 1 minute (shorter due to real-time nature)
@circuit_breaker('live_performance_api')
@retry_on_failure(max_attempts=2)
def get_live_performance():
    """Return current live performance state with comprehensive error handling."""
    try:
        if live_performance_manager is None:
            app.logger.error("Live performance manager not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Validate and clean up state before returning
        validation_result = live_performance_manager.validate_state()
        if validation_result["state_cleaned"]:
            app.logger.info("Cleaned up invalid live performance state")
        
        performance_state = live_performance_manager.get_performance_state()
        
        # Validate response data
        if not isinstance(performance_state, dict):
            raise ValueError("Invalid performance state returned from manager")
        
        response = jsonify(performance_state)
        
        # Performance optimization: Add cache headers (shorter cache for real-time data)
        response.headers['Cache-Control'] = 'public, max-age=60'  # 1 minute
        response.headers['ETag'] = f'live-performance-{hash(str(performance_state))}'
        
        return response
        
    except Exception as e:
        return handle_api_error(e, "get_live_performance")

@app.route('/api/health')
def get_system_health():
    """Return comprehensive system health status for monitoring."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {}
        }
        
        # Check data processor health
        if data_processor is not None:
            try:
                data_health = data_processor.get_data_health_status()
                consistency_check = data_processor.validate_data_consistency()
                health_status["services"]["data_processor"] = {
                    "status": "healthy" if data_health["data_loaded"] else "degraded",
                    "details": data_health,
                    "consistency": consistency_check
                }
            except Exception as e:
                health_status["services"]["data_processor"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        else:
            health_status["services"]["data_processor"] = {
                "status": "not_initialized"
            }
        
        # Check live performance manager health
        if live_performance_manager is not None:
            try:
                validation_result = live_performance_manager.validate_state()
                health_status["services"]["live_performance"] = {
                    "status": "healthy",
                    "validation": validation_result
                }
            except Exception as e:
                health_status["services"]["live_performance"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        else:
            health_status["services"]["live_performance"] = {
                "status": "not_initialized"
            }
        
        # Check circuit breaker states
        health_status["circuit_breakers"] = {
            service: {"failures": count, "state": "open" if service in circuit_breaker_state else "closed"}
            for service, count in error_counts.items()
        }
        
        # Determine overall status
        service_statuses = [service["status"] for service in health_status["services"].values()]
        if "unhealthy" in service_statuses or "not_initialized" in service_statuses:
            health_status["status"] = "degraded"
        
        return jsonify(health_status)
        
    except Exception as e:
        app.logger.error(f"Error getting system health: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/admin/clear-errors', methods=['POST'])
def clear_system_errors():
    """Clear system error states and reset circuit breakers."""
    try:
        # Clear circuit breaker states
        global error_counts, circuit_breaker_state
        error_counts.clear()
        circuit_breaker_state.clear()
        
        # Clear data processor error state
        if data_processor is not None:
            data_processor.clear_error_state()
        
        # Clear cache
        global _response_cache
        _response_cache.clear()
        
        app.logger.info("System error states cleared")
        return jsonify({"success": True, "message": "Error states cleared successfully"})
        
    except Exception as e:
        app.logger.error(f"Error clearing system errors: {str(e)}")
        return jsonify({"error": get_error_message("500", str(e))}), 500

@app.route('/api/data-consistency')
def get_data_consistency():
    """Return comprehensive data consistency report across all sections."""
    try:
        if live_performance_manager is None or data_processor is None:
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Get comprehensive consistency report
        consistency_report = live_performance_manager.get_data_consistency_report()
        
        return jsonify(consistency_report)
        
    except Exception as e:
        app.logger.error(f"Error getting data consistency report: {str(e)}")
        return jsonify({"error": get_error_message("500", str(e))}), 500

@app.route('/api/admin/invalidate-cache', methods=['POST'])
def invalidate_cache():
    """Invalidate all caches to force data refresh across sections."""
    try:
        # Clear response cache
        global _response_cache
        _response_cache.clear()
        
        # Clear data processor cache
        if data_processor is not None:
            data_processor.force_reload()
        
        # Clear live performance cache
        if live_performance_manager is not None:
            live_performance_manager.invalidate_cache()
        
        app.logger.info("All caches invalidated")
        return jsonify({"success": True, "message": "All caches invalidated successfully"})
        
    except Exception as e:
        app.logger.error(f"Error invalidating caches: {str(e)}")
        return jsonify({"error": get_error_message("500", str(e))}), 500

@app.route('/admin/control')
def admin_control():
    """Hidden admin control panel for managing live performance state."""
    try:
        # Pass Spanish translations to the template
        translations = SPANISH_TRANSLATIONS
        # Ensure consistent page title for admin panel
        translations['admin_page_title'] = f"Panel de Control Administrativo - {translations['app_title']}"
        return render_template('admin_control.html', translations=translations)
    except Exception as e:
        app.logger.error(f"Error rendering admin control page: {str(e)}")
        return get_error_message("500"), 500

@app.route('/api/admin/set-current-song', methods=['POST'])
@circuit_breaker('admin_current_song')
@retry_on_failure(max_attempts=2)
def set_current_song():
    """API endpoint to set the current song from admin panel with comprehensive error handling."""
    try:
        if live_performance_manager is None:
            app.logger.error("Live performance manager not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": get_error_message("invalid_format", "No data provided")}), 400
        
        song_id = data.get('song_id')
        
        # Validate input
        if song_id is not None and not isinstance(song_id, (str, type(None))):
            return jsonify({"error": get_error_message("invalid_format", "Invalid song ID format")}), 400
        
        # Allow None/null to clear current song
        if song_id == '' or song_id == 'null':
            song_id = None
        
        # Validate song exists if not None
        if song_id is not None and data_processor is not None:
            song = data_processor.get_song_by_id(song_id)
            if song is None:
                return jsonify({"error": get_error_message("song_not_found")}), 404
        
        success = live_performance_manager.set_current_song(song_id)
        
        if success:
            app.logger.info(f"Current song set to: {song_id}")
            return jsonify({"success": True, "message": "Current song updated successfully"})
        else:
            return jsonify({"error": get_error_message("song_not_found")}), 404
            
    except Exception as e:
        return handle_api_error(e, "set_current_song")

@app.route('/api/admin/set-next-song', methods=['POST'])
@circuit_breaker('admin_next_song')
@retry_on_failure(max_attempts=2)
def set_next_song():
    """API endpoint to set the next song from admin panel with comprehensive error handling."""
    try:
        if live_performance_manager is None:
            app.logger.error("Live performance manager not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": get_error_message("invalid_format", "No data provided")}), 400
        
        song_id = data.get('song_id')
        
        # Validate input
        if song_id is not None and not isinstance(song_id, (str, type(None))):
            return jsonify({"error": get_error_message("invalid_format", "Invalid song ID format")}), 400
        
        # Allow None/null to clear next song
        if song_id == '' or song_id == 'null':
            song_id = None
        
        # Validate song exists if not None
        if song_id is not None and data_processor is not None:
            song = data_processor.get_song_by_id(song_id)
            if song is None:
                return jsonify({"error": get_error_message("song_not_found")}), 404
        
        success = live_performance_manager.set_next_song(song_id)
        
        if success:
            app.logger.info(f"Next song set to: {song_id}")
            return jsonify({"success": True, "message": "Next song updated successfully"})
        else:
            return jsonify({"error": get_error_message("song_not_found")}), 404
            
    except Exception as e:
        return handle_api_error(e, "set_next_song")

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with Spanish messages."""
    return jsonify({"error": get_error_message("404")}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with Spanish messages."""
    return jsonify({"error": get_error_message("500")}), 500

if __name__ == '__main__':
    # Azure App Service compatibility
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)