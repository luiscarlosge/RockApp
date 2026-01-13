"""
Rock and Roll Forum Jam en Español - Flask Web Application
A responsive web application for musicians to view song assignments with Spanish language support.
"""

from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import logging
import time
from functools import wraps
from csv_data_processor import CSVDataProcessor
from spanish_translations import SPANISH_TRANSLATIONS, get_translation, get_error_message, get_retry_message, get_recovery_message, translate_instrument_name, format_order_display
from global_state_manager import GlobalStateManager
from socketio_fallback_config import SocketIOFallbackConfig

# Create Flask application instance
app = Flask(__name__)

# Initialize SocketIO with Azure App Service compatibility and fallback support
# Detect environment and use appropriate configuration
socketio_config = SocketIOFallbackConfig.get_config()
socketio = SocketIO(app, **socketio_config)

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

# Initialize Global State Manager for real-time synchronization
try:
    global_state_manager = GlobalStateManager()
    app.logger.info("Global state manager initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize global state manager: {str(e)}")
    global_state_manager = None

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
        
        # Check global state manager health
        if global_state_manager is not None:
            try:
                global_health = global_state_manager.get_health_status()
                health_status["services"]["global_state_manager"] = global_health
            except Exception as e:
                health_status["services"]["global_state_manager"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        else:
            health_status["services"]["global_state_manager"] = {
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


@app.route('/api/global/current-song')
@cache_response(timeout=30)  # Short cache for real-time data
@circuit_breaker('global_current_song_api')
def get_global_current_song():
    """Get the current global song selection with comprehensive error handling."""
    try:
        if global_state_manager is None:
            app.logger.error("Global state manager not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Get current global state
        current_state = global_state_manager.get_current_state()
        
        if not current_state:
            return jsonify({"error": get_error_message("global_state_error")}), 500
        
        # If we have a current song, get its detailed information
        if current_state.get('current_song_id'):
            song_id = current_state['current_song_id']
            
            # Get detailed song information
            if data_processor is not None:
                try:
                    song = data_processor.get_song_by_id(song_id)
                    if song:
                        song_details = data_processor.format_song_display(song)
                        
                        # Add next song information
                        next_song_info = data_processor.get_next_song_info(song_id)
                        if next_song_info:
                            song_details['next_song'] = next_song_info
                        
                        # Keep instrument names in English for consistent API structure
                        # Translation to Spanish is handled in the frontend for display
                        
                        response_data = {
                            'current_song': song_details,
                            'connected_sessions': current_state.get('connected_sessions', 0),
                            'last_updated': current_state.get('last_update_time', 0),
                            'session_id': current_state.get('last_update_session')
                        }
                        
                        return jsonify(response_data)
                    else:
                        # Song not found, clear the global state
                        app.logger.warning(f"Global song {song_id} not found, clearing state")
                        return jsonify({
                            'current_song': None,
                            'connected_sessions': current_state.get('connected_sessions', 0),
                            'last_updated': current_state.get('last_update_time', 0),
                            'message': get_translation('song_not_found')
                        })
                        
                except Exception as e:
                    app.logger.error(f"Error getting song details for global song {song_id}: {str(e)}")
                    return jsonify({"error": get_error_message("load_song_details")}), 500
            else:
                return jsonify({"error": get_error_message("not_initialized")}), 500
        else:
            # No current song selected
            return jsonify({
                'current_song': None,
                'connected_sessions': current_state.get('connected_sessions', 0),
                'last_updated': current_state.get('last_update_time', 0),
                'message': get_translation('no_current_song')
            })
        
    except Exception as e:
        return handle_api_error(e, "get_global_current_song")

@app.route('/api/global/set-song', methods=['POST'])
@circuit_breaker('global_set_song_api')
@retry_on_failure(max_attempts=2)
def set_global_song():
    """Set the global song selection with proper error handling and Spanish messages."""
    try:
        if global_state_manager is None:
            app.logger.error("Global state manager not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": get_error_message("not_initialized")}), 500
        
        # Validate request data
        if not request.is_json:
            return jsonify({"error": get_error_message("invalid_format", "Request must be JSON")}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": get_error_message("invalid_format", "Empty request body")}), 400
        
        song_id = data.get('song_id')
        if not song_id or not isinstance(song_id, str):
            return jsonify({"error": get_error_message("invalid_format", "Missing or invalid song_id")}), 400
        
        # Validate that the song exists
        song = data_processor.get_song_by_id(song_id)
        if song is None:
            return jsonify({"error": get_error_message("song_not_found")}), 404
        
        # Get detailed song information
        song_details = data_processor.format_song_display(song)
        
        # Add next song information
        next_song_info = data_processor.get_next_song_info(song_id)
        if next_song_info:
            song_details['next_song'] = next_song_info
        
        # Keep instrument names in English for consistent API structure
        # Translation to Spanish is handled in the frontend for display
        
        # Update global state
        session_id = data.get('session_id', 'api_request')
        update_result = global_state_manager.update_global_song(
            song_id, song_details, session_id
        )
        
        if not update_result.get('success'):
            error_msg = update_result.get('error', 'Unknown error')
            app.logger.error(f"Failed to update global song: {error_msg}")
            return jsonify({"error": get_error_message("global_update_error", error_msg)}), 500
        
        # Broadcast the change to all connected sessions
        broadcast_result = global_state_manager.broadcast_song_change(
            song_id, song_details, exclude_session=session_id
        )
        
        # Prepare response
        response_data = {
            'success': True,
            'song_id': song_id,
            'song_details': song_details,
            'update_result': update_result,
            'broadcast_result': broadcast_result,
            'message': get_translation('song_selected')
        }
        
        app.logger.info(f"Global song set to {song_id} by session {session_id}")
        return jsonify(response_data)
        
    except Exception as e:
        return handle_api_error(e, "set_global_song")


# SocketIO Event Handlers for Real-time Communication
@socketio.on('connect')
def handle_connect():
    """Handle client connection to SocketIO."""
    try:
        app.logger.info(f"Client connected: {request.sid}")
        
        # Add session to global state manager
        if global_state_manager:
            metadata = {
                'user_agent': request.headers.get('User-Agent', ''),
                'remote_addr': request.remote_addr
            }
            global_state_manager.add_session(request.sid, metadata)
        
        # Send connection confirmation with current global state
        current_state = global_state_manager.get_current_state() if global_state_manager else {}
        
        emit('connection_status', {
            'status': 'connected',
            'message': get_translation('connected'),
            'session_id': request.sid,
            'current_state': current_state
        })
        
    except Exception as e:
        app.logger.error(f"Error handling connection: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection from SocketIO with comprehensive cleanup and error recovery.
    
    Requirements: 4.2, 4.5, 4.6
    - Removes session from global state tracking
    - Cleans up session resources
    - Logs disconnection for monitoring
    - Handles cleanup errors gracefully
    - Implements recovery mechanisms for failed cleanup
    """
    session_id = request.sid
    cleanup_errors = []
    
    try:
        app.logger.info(f"Client disconnected: {session_id}")
        
        # Leave the global room with error handling
        try:
            leave_room('global_session')
            app.logger.debug(f"Session {session_id} left global_session room")
        except Exception as room_error:
            cleanup_errors.append(f"Room leave error: {str(room_error)}")
            app.logger.warning(f"Error leaving room for {session_id}: {str(room_error)}")
        
        # Remove session from global state manager with detailed error handling
        if global_state_manager:
            try:
                # Get session info before removal for comprehensive logging
                session_info = global_state_manager.get_session_info(session_id)
                
                # Attempt session removal with retry logic
                removal_attempts = 0
                max_removal_attempts = 3
                removal_success = False
                
                while removal_attempts < max_removal_attempts and not removal_success:
                    try:
                        removal_success = global_state_manager.remove_session(session_id)
                        if removal_success:
                            break
                    except Exception as removal_error:
                        removal_attempts += 1
                        cleanup_errors.append(f"Removal attempt {removal_attempts}: {str(removal_error)}")
                        app.logger.warning(f"Session removal attempt {removal_attempts} failed for {session_id}: {str(removal_error)}")
                        
                        if removal_attempts < max_removal_attempts:
                            time.sleep(0.1 * removal_attempts)  # Brief delay with backoff
                
                if removal_success:
                    # Log session statistics
                    if session_info:
                        session_duration = time.time() - session_info.get('connected_at', time.time())
                        cleanup_markers = session_info.get('cleanup_markers', [])
                        app.logger.info(f"Session {session_id} removed after {session_duration:.1f} seconds "
                                      f"({len(cleanup_markers)} cleanup markers)")
                    
                    # Get updated session count with error handling
                    try:
                        current_state = global_state_manager.get_current_state()
                        remaining_sessions = current_state.get('connected_sessions', 0)
                        app.logger.info(f"Remaining connected sessions: {remaining_sessions}")
                        
                        # Broadcast session count update to remaining sessions with error handling
                        try:
                            emit('session_count_updated', {
                                'connected_sessions': remaining_sessions,
                                'disconnected_session': session_id,
                                'timestamp': time.time(),
                                'cleanup_status': 'success' if not cleanup_errors else 'partial'
                            }, room='global_session')
                        except Exception as broadcast_error:
                            cleanup_errors.append(f"Broadcast error: {str(broadcast_error)}")
                            app.logger.warning(f"Error broadcasting session count update: {str(broadcast_error)}")
                            
                    except Exception as state_error:
                        cleanup_errors.append(f"State retrieval error: {str(state_error)}")
                        app.logger.warning(f"Error getting current state during disconnect: {str(state_error)}")
                        
                else:
                    cleanup_errors.append("Failed to remove session after all attempts")
                    app.logger.error(f"Failed to remove session {session_id} from global state manager after {max_removal_attempts} attempts")
                    
                    # Attempt recovery for failed session removal
                    try:
                        recovery_result = global_state_manager.recover_from_error('session_removal_failure', {
                            'session_id': session_id,
                            'attempts': removal_attempts,
                            'errors': cleanup_errors
                        })
                        
                        if recovery_result.get('success'):
                            app.logger.info(f"Recovery successful for failed session removal: {session_id}")
                        else:
                            app.logger.error(f"Recovery failed for session removal: {session_id}")
                            
                    except Exception as recovery_error:
                        cleanup_errors.append(f"Recovery error: {str(recovery_error)}")
                        app.logger.error(f"Error during recovery attempt for {session_id}: {str(recovery_error)}")
                    
            except Exception as state_error:
                cleanup_errors.append(f"Global state error: {str(state_error)}")
                app.logger.error(f"Error removing session {session_id} from global state: {str(state_error)}")
        else:
            cleanup_errors.append("Global state manager not available")
            app.logger.warning("Global state manager not available during disconnect cleanup")
        
        # Perform additional cleanup with error handling
        try:
            # Clean up any session-specific resources
            # This could include temporary files, cached data, etc.
            
            # Clear any session-specific caches
            if hasattr(request, 'session_cache'):
                delattr(request, 'session_cache')
            
            # Additional cleanup operations can be added here
            
        except Exception as additional_cleanup_error:
            cleanup_errors.append(f"Additional cleanup error: {str(additional_cleanup_error)}")
            app.logger.error(f"Error during additional cleanup for {session_id}: {str(additional_cleanup_error)}")
        
        # Log final cleanup status
        if cleanup_errors:
            app.logger.warning(f"Disconnect cleanup completed with {len(cleanup_errors)} errors for session {session_id}: {cleanup_errors}")
        else:
            app.logger.info(f"Disconnect cleanup completed successfully for session {session_id}")
        
        # Trigger periodic cleanup if we've had multiple cleanup errors
        if len(cleanup_errors) >= 2 and global_state_manager:
            try:
                app.logger.info("Triggering periodic cleanup due to multiple disconnect errors")
                cleaned_count = global_state_manager.cleanup_inactive_sessions(timeout_seconds=60)
                app.logger.info(f"Periodic cleanup removed {cleaned_count} additional sessions")
            except Exception as periodic_cleanup_error:
                app.logger.error(f"Error during periodic cleanup: {str(periodic_cleanup_error)}")
        
    except Exception as e:
        app.logger.error(f"Unexpected error handling disconnection for {session_id}: {str(e)}")
        
        # Attempt emergency cleanup
        try:
            if global_state_manager:
                # Force remove session without detailed error handling
                global_state_manager.connected_sessions.discard(session_id)
                global_state_manager.session_metadata.pop(session_id, None)
                app.logger.info(f"Emergency cleanup completed for session {session_id}")
        except Exception as emergency_error:
            app.logger.error(f"Emergency cleanup failed for {session_id}: {str(emergency_error)}")
        
        # Don't emit error on disconnect as client is already gone

@socketio.on('join_global_session')
def handle_join_global_session(data=None):
    """
    Handle client joining the global song selection session.
    
    Requirements: 4.2, 4.5, 4.6
    - Manages session tracking for global synchronization
    - Provides current global state to new sessions
    - Handles errors gracefully with Spanish messages
    """
    try:
        app.logger.info(f"Client joining global session: {request.sid}")
        
        # Validate global state manager availability
        if not global_state_manager:
            app.logger.error("Global state manager not available for join_global_session")
            emit('error', {
                'message': get_error_message('service_unavailable'),
                'code': 'GLOBAL_STATE_UNAVAILABLE',
                'event': 'join_global_session'
            })
            return
        
        # Join the global room for broadcasting
        join_room('global_session')
        app.logger.debug(f"Session {request.sid} joined global_session room")
        
        # Extract client metadata if provided
        client_metadata = {}
        if data and isinstance(data, dict):
            client_metadata = {
                'client_info': data.get('client_info', {}),
                'user_preferences': data.get('user_preferences', {}),
                'connection_type': data.get('connection_type', 'websocket')
            }
        
        # Add session metadata including request headers
        session_metadata = {
            'user_agent': request.headers.get('User-Agent', ''),
            'remote_addr': request.remote_addr,
            'join_time': time.time(),
            **client_metadata
        }
        
        # Add session to global state manager
        session_added = global_state_manager.add_session(request.sid, session_metadata)
        if not session_added:
            app.logger.warning(f"Failed to add session {request.sid} to global state manager")
        
        # Update session activity
        global_state_manager.update_session_activity(request.sid)
        
        # Get current global state with detailed information
        current_state = global_state_manager.get_current_state()
        
        # Prepare response with comprehensive state information
        response_data = {
            'status': 'success',
            'message': get_translation('global_session_joined'),
            'session_id': request.sid,
            'current_state': current_state,
            'server_time': time.time(),
            'connection_info': {
                'transport': request.transport if hasattr(request, 'transport') else 'unknown',
                'room': 'global_session'
            }
        }
        
        # Add current song details if available
        if current_state.get('current_song_id') and data_processor:
            try:
                song = data_processor.get_song_by_id(current_state['current_song_id'])
                if song:
                    song_details = data_processor.format_song_display(song)
                    # Add next song information
                    next_song_info = data_processor.get_next_song_info(current_state['current_song_id'])
                    if next_song_info:
                        song_details['next_song'] = next_song_info
                    
                    # Keep instrument names in English for consistent API structure
                    # Translation to Spanish is handled in the frontend for display
                    
                    response_data['current_song_details'] = song_details
            except Exception as song_error:
                app.logger.warning(f"Could not load current song details: {str(song_error)}")
        
        emit('global_session_joined', response_data)
        app.logger.info(f"Session {request.sid} successfully joined global session. Total sessions: {current_state.get('connected_sessions', 0)}")
        
    except Exception as e:
        app.logger.error(f"Error handling join global session for {request.sid}: {str(e)}")
        emit('error', {
            'message': get_error_message('connection_error'),
            'details': str(e),
            'code': 'JOIN_SESSION_ERROR',
            'event': 'join_global_session'
        })

@socketio.on('select_global_song')
def handle_global_song_selection(data):
    """
    Handle global song selection from a client.
    
    Requirements: 4.2, 4.5, 4.6
    - Updates global song selection state
    - Broadcasts changes to all connected sessions
    - Handles concurrent updates with conflict resolution
    - Provides comprehensive error handling with Spanish messages
    """
    try:
        # Validate input data
        if not data or not isinstance(data, dict):
            app.logger.warning(f"Invalid data received for global song selection from {request.sid}")
            emit('error', {
                'message': get_error_message('invalid_format', 'Request data must be a valid object'),
                'code': 'INVALID_DATA_FORMAT',
                'event': 'select_global_song'
            })
            return
        
        song_id = data.get('song_id')
        if not song_id or not isinstance(song_id, str):
            app.logger.warning(f"Missing or invalid song_id from {request.sid}: {song_id}")
            emit('error', {
                'message': get_error_message('invalid_format', 'Missing or invalid song_id'),
                'code': 'MISSING_SONG_ID',
                'event': 'select_global_song'
            })
            return
        
        app.logger.info(f"Global song selection request: {song_id} by {request.sid}")
        
        # Validate service availability
        if not global_state_manager:
            app.logger.error("Global state manager not available for song selection")
            emit('error', {
                'message': get_error_message('service_unavailable'),
                'code': 'GLOBAL_STATE_UNAVAILABLE',
                'event': 'select_global_song'
            })
            return
        
        if not data_processor:
            app.logger.error("Data processor not available for song selection")
            emit('error', {
                'message': get_error_message('not_initialized'),
                'code': 'DATA_PROCESSOR_UNAVAILABLE',
                'event': 'select_global_song'
            })
            return
        
        # Validate that the song exists
        try:
            song = data_processor.get_song_by_id(song_id)
            if song is None:
                app.logger.warning(f"Song not found: {song_id}")
                emit('error', {
                    'message': get_error_message('song_not_found'),
                    'code': 'SONG_NOT_FOUND',
                    'song_id': song_id,
                    'event': 'select_global_song'
                })
                return
        except Exception as song_error:
            app.logger.error(f"Error validating song {song_id}: {str(song_error)}")
            emit('error', {
                'message': get_error_message('load_song_details'),
                'details': str(song_error),
                'code': 'SONG_VALIDATION_ERROR',
                'song_id': song_id,
                'event': 'select_global_song'
            })
            return
        
        # Get detailed song information
        try:
            song_details = data_processor.format_song_display(song)
            
            # Add next song information
            next_song_info = data_processor.get_next_song_info(song_id)
            if next_song_info:
                song_details['next_song'] = next_song_info
            
            # Keep instrument names in English for consistent API structure
            # Translation to Spanish is handled in the frontend for display
                
        except Exception as format_error:
            app.logger.error(f"Error formatting song details for {song_id}: {str(format_error)}")
            emit('error', {
                'message': get_error_message('load_song_details'),
                'details': str(format_error),
                'code': 'SONG_FORMAT_ERROR',
                'song_id': song_id,
                'event': 'select_global_song'
            })
            return
        
        # Update session activity
        global_state_manager.update_session_activity(request.sid)
        
        # Update global state with conflict resolution
        update_result = global_state_manager.update_global_song(
            song_id, song_details, request.sid
        )
        
        if not update_result.get('success'):
            error_msg = update_result.get('error', 'Unknown error')
            app.logger.error(f"Failed to update global song state: {error_msg}")
            emit('error', {
                'message': get_error_message('update_failed'),
                'details': error_msg,
                'code': 'STATE_UPDATE_ERROR',
                'song_id': song_id,
                'event': 'select_global_song'
            })
            return
        
        # Broadcast to all other sessions in the global room
        try:
            broadcast_data = {
                'song_id': song_id,
                'song_data': song_details,
                'timestamp': time.time(),
                'update_session': request.sid,
                'message': get_translation('song_changed'),
                'conflict_info': {
                    'conflict_detected': update_result.get('conflict_detected', False),
                    'previous_song_id': update_result.get('previous_song_id')
                }
            }
            
            # Broadcast to all sessions except the originating one
            emit('song_changed', broadcast_data, room='global_session', include_self=False)
            
            # Get broadcast statistics from global state manager
            broadcast_result = global_state_manager.broadcast_song_change(
                song_id, song_details, exclude_session=request.sid
            )
            
            app.logger.info(f"Broadcasted song change {song_id} to {broadcast_result.get('successful_broadcasts', 0)} sessions")
            
        except Exception as broadcast_error:
            app.logger.error(f"Error broadcasting song change: {str(broadcast_error)}")
            # Don't fail the entire operation for broadcast errors
            broadcast_result = {'success': False, 'error': str(broadcast_error)}
        
        # Confirm to the originating session
        response_data = {
            'status': 'success',
            'song_id': song_id,
            'song_data': song_details,
            'message': get_translation('song_selected'),
            'update_result': update_result,
            'broadcast_info': broadcast_result,
            'server_time': time.time()
        }
        
        emit('global_song_selected', response_data)
        app.logger.info(f"Global song selection completed: {song_id} by {request.sid}")
        
    except Exception as e:
        app.logger.error(f"Unexpected error handling global song selection from {request.sid}: {str(e)}")
        emit('error', {
            'message': get_error_message('server_error'),
            'details': str(e),
            'code': 'UNEXPECTED_ERROR',
            'event': 'select_global_song'
        })

@socketio.on('request_current_song')
def handle_request_current_song():
    """Handle request for current global song state."""
    try:
        if global_state_manager:
            current_state = global_state_manager.get_current_state()
            emit('current_song_state', current_state)
        else:
            emit('error', {
                'message': get_error_message('service_unavailable'),
                'code': 'GLOBAL_STATE_UNAVAILABLE'
            })
    except Exception as e:
        app.logger.error(f"Error handling current song request: {str(e)}")
        emit('error', {
            'message': get_error_message('server_error'),
            'details': str(e)
        })

@socketio.on('ping')
def handle_ping():
    """Handle ping requests for connection health check."""
    try:
        # Update session activity
        if global_state_manager:
            global_state_manager.update_session_activity(request.sid)
        
        emit('pong', {'timestamp': time.time()})
    except Exception as e:
        app.logger.error(f"Error handling ping: {str(e)}")

# Periodic cleanup task for inactive sessions
@socketio.on('cleanup_sessions')
def handle_cleanup_sessions():
    """Handle manual cleanup of inactive sessions (admin function)."""
    try:
        if global_state_manager:
            cleaned_count = global_state_manager.cleanup_inactive_sessions()
            emit('cleanup_result', {
                'cleaned_sessions': cleaned_count,
                'message': f"Cleaned up {cleaned_count} inactive sessions"
            })
    except Exception as e:
        app.logger.error(f"Error handling session cleanup: {str(e)}")
        emit('error', {
            'message': get_error_message('server_error'),
            'details': str(e)
        })


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
    
    # Use SocketIO run method for proper WebSocket support
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode,
        use_reloader=debug_mode,
        log_output=True
    )