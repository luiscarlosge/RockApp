#!/usr/bin/env python3
"""
Azure Deployment Test Script
Tests the application configuration for Azure App Service compatibility.
"""

import os
import sys
import subprocess
import time
import requests
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_file_exists(filepath, description):
    """Check if a required file exists."""
    if os.path.exists(filepath):
        logger.info(f"✓ {description} found: {filepath}")
        return True
    else:
        logger.error(f"✗ {description} missing: {filepath}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import pandas
        logger.info(f"✓ Flask version: {flask.__version__}")
        logger.info(f"✓ Pandas version: {pandas.__version__}")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        return False

def test_app_import():
    """Test if the application can be imported successfully."""
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Try to import the application
        from startup import application
        logger.info("✓ Application imported successfully")
        
        # Test basic configuration
        if hasattr(application, 'config'):
            logger.info(f"✓ Flask app configured with ENV: {application.config.get('ENV', 'not set')}")
        
        return True, application
    except Exception as e:
        logger.error(f"✗ Failed to import application: {e}")
        return False, None

def test_csv_data():
    """Test if CSV data can be loaded."""
    try:
        from csv_data_processor import CSVDataProcessor
        processor = CSVDataProcessor()
        songs = processor.get_songs_for_dropdown()
        logger.info(f"✓ CSV data loaded successfully: {len(songs)} songs found")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to load CSV data: {e}")
        return False

def run_server_test(app, port=5001):
    """Run the server in a separate thread for testing."""
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Server error: {e}")

def test_endpoints(port=5001):
    """Test API endpoints."""
    base_url = f"http://127.0.0.1:{port}"
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Test main page
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            logger.info("✓ Main page accessible")
        else:
            logger.error(f"✗ Main page returned status: {response.status_code}")
            return False
        
        # Test songs API
        response = requests.get(f"{base_url}/api/songs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'songs' in data:
                logger.info(f"✓ Songs API working: {len(data['songs'])} songs returned")
            else:
                logger.error("✗ Songs API returned invalid format")
                return False
        else:
            logger.error(f"✗ Songs API returned status: {response.status_code}")
            return False
        
        # Test specific song API (if songs exist)
        if data['songs']:
            song_id = data['songs'][0]['song_id']
            response = requests.get(f"{base_url}/api/song/{song_id}", timeout=10)
            if response.status_code == 200:
                song_data = response.json()
                if 'assignments' in song_data:
                    logger.info("✓ Song details API working")
                else:
                    logger.error("✗ Song details API returned invalid format")
                    return False
            else:
                logger.error(f"✗ Song details API returned status: {response.status_code}")
                return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Request failed: {e}")
        return False

def main():
    """Main deployment test function."""
    logger.info("Starting Azure deployment compatibility test...")
    
    all_tests_passed = True
    
    # Check required files
    required_files = [
        ('startup.py', 'Startup script'),
        ('app.py', 'Main application'),
        ('web.config', 'Azure web configuration'),
        ('requirements.txt', 'Python dependencies'),
        ('Data.csv', 'CSV data file'),
        ('templates/index.html', 'Main template'),
        ('static/css/style.css', 'CSS stylesheet'),
        ('static/js/app.js', 'JavaScript file')
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_tests_passed = False
    
    # Check dependencies
    if not check_dependencies():
        all_tests_passed = False
    
    # Test application import
    app_imported, app = test_app_import()
    if not app_imported:
        all_tests_passed = False
    
    # Test CSV data loading
    if not test_csv_data():
        all_tests_passed = False
    
    # Test server functionality (if app was imported successfully)
    if app_imported and app:
        logger.info("Starting server test...")
        
        # Start server in background thread
        server_thread = Thread(target=run_server_test, args=(app, 5001), daemon=True)
        server_thread.start()
        
        # Test endpoints
        if not test_endpoints(5001):
            all_tests_passed = False
    
    # Summary
    if all_tests_passed:
        logger.info("🎉 All deployment tests passed! Application is ready for Azure deployment.")
        return 0
    else:
        logger.error("❌ Some deployment tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())