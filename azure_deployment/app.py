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
from spanish_translations import SPANISH_TRANSLATIONS, get_translation, get_error_message, get_retry_message, get_recovery_message, translate_instrument_name, format_order_display

# Create Flask application instance
app = Flask(__name__)

# Azure App Service compatibility configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Session configuration
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
    app.logger.info("CSV data processor initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize data processor: {str(e)}")
    # Create dummy processor to prevent app crash
    data_processor = None

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
    """Return JSON list of all songs for dropdown population sorted by order with comprehensive error handling."""
    try:
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Validate data processor health
        health_status = data_processor.get_data_health_status()
        if health_status["fallback_active"]:
            app.logger.warning("Using fallback data for songs API")
        
        # Get songs sorted by order (the get_songs_for_dropdown method already sorts by order)
        songs = data_processor.get_songs_for_dropdown()
        
        # Validate response data
        if not songs or not isinstance(songs, list):
            raise ValueError("Invalid songs data returned from processor")
        
        # Ensure all songs have order information and handle missing order values gracefully
        for song in songs:
            if 'order' not in song or song['order'] is None:
                app.logger.warning(f"Song {song.get('song_id', 'unknown')} missing order information")
                # Assign a high order number for songs without order
                song['order'] = 9999
        
        # Double-check sorting by order (already done in processor, but ensure consistency)
        songs.sort(key=lambda x: (x.get('order', 9999), x.get('artist', ''), x.get('song', '')))
        
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
    """Return detailed musician assignments for selected song with order and next song information."""
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
        
        # Add next song information
        next_song_info = data_processor.get_next_song_info(song_id)
        if next_song_info:
            song_details['next_song'] = next_song_info
        else:
            song_details['next_song'] = None
        
        # Ensure order number is included (should already be in format_song_display)
        if 'order' not in song_details:
            song_details['order'] = song.order if hasattr(song, 'order') else None
        
        # Keep instrument names in English for consistent API structure
        # Translation to Spanish is handled in the frontend for display
        
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
    """Return detailed song assignments for selected musician sorted by order with Spanish formatting."""
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
        
        # The get_musician_by_id method already calls get_musician_songs which sorts by order
        # But let's ensure the songs are properly formatted with Spanish order display
        if 'songs' in musician:
            for song in musician['songs']:
                # Add Spanish order formatting to song descriptions
                if 'order' in song and song['order'] is not None:
                    # Format order display in Spanish
                    order_display = format_order_display(song['order'])
                    
                    # Update the title to include order information
                    original_title = song.get('title', f"{song.get('artist', '')} - {song.get('song', '')}")
                    song['title_with_order'] = f"{order_display} - {original_title}"
                    
                    # Add order display as separate field for flexibility
                    song['order_display'] = order_display
                
                # Ensure instruments are translated to Spanish (already done in get_musician_songs)
                if 'instruments' in song:
                    translated_instruments = []
                    for instrument in song['instruments']:
                        translated_instruments.append(translate_instrument_name(instrument))
                    song['instruments_spanish'] = translated_instruments
        
        response = jsonify(musician)
        
        # Performance optimization: Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        response.headers['ETag'] = f'musician-{musician_id}-{hash(str(musician))}'
        
        return response
        
    except Exception as e:
        return handle_api_error(e, "get_musician_details")

@app.route('/global-selector')
def global_selector():
    """Global song selection interface with Spanish language support."""
    try:
        # Pass Spanish translations to the template
        translations = SPANISH_TRANSLATIONS
        # Ensure consistent page title
        translations['page_title'] = translations['global_selector_title']
        return render_template('global-selector.html', translations=translations)
    except Exception as e:
        app.logger.error(f"Error rendering global selector page: {str(e)}")
        return get_error_message("500"), 500

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
    
    # Use standard Flask run method
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode,
        use_reloader=debug_mode,
        threaded=True
    )