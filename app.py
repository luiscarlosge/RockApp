"""
Musician Song Selector - Flask Web Application
A responsive web application for musicians to view song assignments.
"""

from flask import Flask, render_template, jsonify, request
import os
import logging
import time
from functools import wraps
from csv_data_processor import CSVDataProcessor

# Create Flask application instance
app = Flask(__name__)

# Azure App Service compatibility configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

# Initialize CSV data processor with error handling for Azure
try:
    data_processor = CSVDataProcessor()
    app.logger.info("CSV data processor initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize CSV data processor: {str(e)}")
    # Create a dummy processor to prevent app crash
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
    """Main application page with song selector interface."""
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error rendering index page: {str(e)}")
        return "Application error occurred", 500

@app.route('/api/songs')
@cache_response(timeout=600)  # Cache for 10 minutes
def get_songs():
    """Return JSON list of all songs for dropdown population with caching."""
    try:
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": "Application not properly initialized"}), 500
            
        songs = data_processor.get_songs_for_dropdown()
        response = jsonify({"songs": songs})
        
        # Performance optimization: Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        response.headers['ETag'] = f'songs-{len(songs)}-{hash(str(songs))}'
        
        return response
    except FileNotFoundError:
        app.logger.error("CSV data file not found")
        return jsonify({"error": "Song data file not found"}), 404
    except ValueError as e:
        app.logger.error(f"Invalid CSV data: {str(e)}")
        return jsonify({"error": "Invalid song data format"}), 400
    except Exception as e:
        app.logger.error(f"Error fetching songs: {str(e)}")
        return jsonify({"error": "Failed to load songs"}), 500

@app.route('/api/song/<song_id>')
@cache_response(timeout=600)  # Cache for 10 minutes
def get_song_details(song_id):
    """Return detailed musician assignments for selected song with caching."""
    try:
        if data_processor is None:
            app.logger.error("Data processor not initialized")
            return jsonify({"error": "Application not properly initialized"}), 500
            
        song = data_processor.get_song_by_id(song_id)
        if song is None:
            return jsonify({"error": "Song not found"}), 404
        
        song_details = data_processor.format_song_display(song)
        response = jsonify(song_details)
        
        # Performance optimization: Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=600'  # 10 minutes
        response.headers['ETag'] = f'song-{song_id}-{hash(str(song_details))}'
        
        return response
    except FileNotFoundError:
        app.logger.error("CSV data file not found")
        return jsonify({"error": "Song data file not found"}), 404
    except ValueError as e:
        app.logger.error(f"Invalid CSV data: {str(e)}")
        return jsonify({"error": "Invalid song data format"}), 400
    except Exception as e:
        app.logger.error(f"Error fetching song details for {song_id}: {str(e)}")
        return jsonify({"error": "Failed to load song details"}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Azure App Service compatibility
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)