#!/usr/bin/env python3
"""
End-to-End Integration Tests for Musician Song Selector
Tests complete user workflow from song selection to display with responsive behavior.
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from typing import Dict, List, Optional
from unittest.mock import patch, MagicMock

# Add current directory to Python path for imports
sys.path.insert(0, os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationTestSuite:
    """Comprehensive integration test suite for the Musician Song Selector application."""
    
    def __init__(self):
        self.app = None
        self.client = None
        self.test_results = []
        self.server_thread = None
        self.server_port = 5002
        
    def setup(self):
        """Set up the test environment."""
        try:
            # Import and configure the application
            from startup import create_app
            self.app = create_app()
            self.app.config['TESTING'] = True
            self.app.config['DEBUG'] = False
            self.client = self.app.test_client()
            
            logger.info("✓ Test environment set up successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to set up test environment: {e}")
            return False
    
    def test_csv_data_loading(self):
        """Test CSV data loading and processing."""
        logger.info("Testing CSV data loading...")
        
        try:
            from csv_data_processor import CSVDataProcessor
            processor = CSVDataProcessor()
            
            # Test loading songs
            songs = processor.load_songs()
            assert len(songs) > 0, "No songs loaded from CSV"
            
            # Test dropdown data
            dropdown_songs = processor.get_songs_for_dropdown()
            assert len(dropdown_songs) > 0, "No dropdown songs generated"
            assert all('song_id' in song for song in dropdown_songs), "Missing song_id in dropdown data"
            assert all('display_name' in song for song in dropdown_songs), "Missing display_name in dropdown data"
            
            # Test song retrieval by ID
            first_song_id = dropdown_songs[0]['song_id']
            song_details = processor.get_song_by_id(first_song_id)
            assert song_details is not None, f"Could not retrieve song by ID: {first_song_id}"
            
            # Test song formatting
            formatted_song = processor.format_song_display(song_details)
            assert 'assignments' in formatted_song, "Missing assignments in formatted song"
            assert 'song_id' in formatted_song, "Missing song_id in formatted song"
            
            logger.info(f"✓ CSV data loading test passed - {len(songs)} songs loaded")
            self.test_results.append(("CSV Data Loading", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ CSV data loading test failed: {e}")
            self.test_results.append(("CSV Data Loading", False, str(e)))
            return False
    
    def test_flask_routes(self):
        """Test Flask application routes and API endpoints."""
        logger.info("Testing Flask routes...")
        
        try:
            # Test main page
            response = self.client.get('/')
            assert response.status_code == 200, f"Main page returned {response.status_code}"
            assert b'Musician Song Selector' in response.data, "Main page missing title"
            
            # Test songs API
            response = self.client.get('/api/songs')
            assert response.status_code == 200, f"Songs API returned {response.status_code}"
            
            songs_data = json.loads(response.data)
            assert 'songs' in songs_data, "Songs API missing 'songs' key"
            assert len(songs_data['songs']) > 0, "Songs API returned empty list"
            
            # Test song details API
            first_song_id = songs_data['songs'][0]['song_id']
            response = self.client.get(f'/api/song/{first_song_id}')
            assert response.status_code == 200, f"Song details API returned {response.status_code}"
            
            song_details = json.loads(response.data)
            assert 'assignments' in song_details, "Song details missing assignments"
            assert 'song_id' in song_details, "Song details missing song_id"
            
            # Test invalid song ID
            response = self.client.get('/api/song/invalid-song-id')
            assert response.status_code == 404, f"Invalid song ID should return 404, got {response.status_code}"
            
            logger.info("✓ Flask routes test passed")
            self.test_results.append(("Flask Routes", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Flask routes test failed: {e}")
            self.test_results.append(("Flask Routes", False, str(e)))
            return False
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        logger.info("Testing error handling...")
        
        try:
            # Test with missing CSV file
            with patch('csv_data_processor.CSVDataProcessor.__init__') as mock_init:
                mock_init.side_effect = FileNotFoundError("CSV file not found")
                
                response = self.client.get('/api/songs')
                assert response.status_code == 500, f"Missing CSV should return 500, got {response.status_code}"
            
            # Test malformed API requests
            response = self.client.get('/api/song/')  # Empty song ID
            assert response.status_code == 404, f"Empty song ID should return 404, got {response.status_code}"
            
            # Test non-existent endpoints
            response = self.client.get('/api/nonexistent')
            assert response.status_code == 404, f"Non-existent endpoint should return 404, got {response.status_code}"
            
            logger.info("✓ Error handling test passed")
            self.test_results.append(("Error Handling", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Error handling test failed: {e}")
            self.test_results.append(("Error Handling", False, str(e)))
            return False
    
    def test_data_consistency(self):
        """Test data consistency across different access methods."""
        logger.info("Testing data consistency...")
        
        try:
            from csv_data_processor import CSVDataProcessor
            processor = CSVDataProcessor()
            
            # Get songs through different methods
            all_songs = processor.get_all_songs()
            dropdown_songs = processor.get_songs_for_dropdown()
            
            # Verify counts match
            assert len(all_songs) == len(dropdown_songs), "Song count mismatch between methods"
            
            # Test each song's consistency
            for dropdown_song in dropdown_songs:
                song_id = dropdown_song['song_id']
                
                # Get song details
                song_details = processor.get_song_by_id(song_id)
                assert song_details is not None, f"Song not found by ID: {song_id}"
                
                # Verify display name matches
                expected_display = f"{song_details.artist} - {song_details.song}"
                assert dropdown_song['display_name'] == expected_display, f"Display name mismatch for {song_id}"
                
                # Test formatted display
                formatted = processor.format_song_display(song_details)
                assert formatted['song_id'] == song_id, f"Song ID mismatch in formatted data"
                assert formatted['artist'] == song_details.artist, f"Artist mismatch in formatted data"
                assert formatted['song'] == song_details.song, f"Song title mismatch in formatted data"
            
            logger.info("✓ Data consistency test passed")
            self.test_results.append(("Data Consistency", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Data consistency test failed: {e}")
            self.test_results.append(("Data Consistency", False, str(e)))
            return False
    
    def test_performance_requirements(self):
        """Test performance requirements (response time < 1 second)."""
        logger.info("Testing performance requirements...")
        
        try:
            # Test songs API response time
            start_time = time.time()
            response = self.client.get('/api/songs')
            songs_response_time = time.time() - start_time
            
            assert response.status_code == 200, "Songs API failed"
            assert songs_response_time < 1.0, f"Songs API too slow: {songs_response_time:.3f}s"
            
            # Test song details API response time
            songs_data = json.loads(response.data)
            if songs_data['songs']:
                song_id = songs_data['songs'][0]['song_id']
                
                start_time = time.time()
                response = self.client.get(f'/api/song/{song_id}')
                details_response_time = time.time() - start_time
                
                assert response.status_code == 200, "Song details API failed"
                assert details_response_time < 1.0, f"Song details API too slow: {details_response_time:.3f}s"
            
            logger.info(f"✓ Performance test passed - Songs: {songs_response_time:.3f}s, Details: {details_response_time:.3f}s")
            self.test_results.append(("Performance Requirements", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Performance test failed: {e}")
            self.test_results.append(("Performance Requirements", False, str(e)))
            return False
    
    def test_complete_user_workflow(self):
        """Test complete user workflow from song selection to display."""
        logger.info("Testing complete user workflow...")
        
        try:
            # Step 1: Load main page
            response = self.client.get('/')
            assert response.status_code == 200, "Failed to load main page"
            
            # Step 2: Get songs list (simulating dropdown population)
            response = self.client.get('/api/songs')
            assert response.status_code == 200, "Failed to get songs list"
            
            songs_data = json.loads(response.data)
            assert len(songs_data['songs']) > 0, "No songs available"
            
            # Step 3: Select a song (simulating user selection)
            selected_song = songs_data['songs'][0]
            song_id = selected_song['song_id']
            
            # Step 4: Get song details (simulating display update)
            response = self.client.get(f'/api/song/{song_id}')
            assert response.status_code == 200, "Failed to get song details"
            
            song_details = json.loads(response.data)
            
            # Step 5: Verify all required data is present
            required_fields = ['song_id', 'artist', 'song', 'time', 'assignments']
            for field in required_fields:
                assert field in song_details, f"Missing required field: {field}"
            
            # Step 6: Verify assignments structure
            assignments = song_details['assignments']
            expected_instruments = ['Lead Guitar', 'Rhythm Guitar', 'Bass', 'Battery', 'Singer', 'Keyboards']
            for instrument in expected_instruments:
                assert instrument in assignments, f"Missing instrument: {instrument}"
            
            # Step 7: Test multiple song selections (simulating user browsing)
            for i, song in enumerate(songs_data['songs'][:3]):  # Test first 3 songs
                response = self.client.get(f'/api/song/{song["song_id"]}')
                assert response.status_code == 200, f"Failed to get details for song {i+1}"
            
            logger.info("✓ Complete user workflow test passed")
            self.test_results.append(("Complete User Workflow", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Complete user workflow test failed: {e}")
            self.test_results.append(("Complete User Workflow", False, str(e)))
            return False
    
    def test_responsive_behavior_simulation(self):
        """Test responsive behavior simulation (since we can't test actual viewport changes)."""
        logger.info("Testing responsive behavior simulation...")
        
        try:
            # Test that all required CSS classes and structure exist in the HTML
            response = self.client.get('/')
            html_content = response.data.decode('utf-8')
            
            # Check for responsive Bootstrap classes
            responsive_classes = [
                'col-12', 'col-md-8', 'col-lg-6',  # Responsive columns
                'form-select-lg',  # Large form elements
                'card', 'card-header', 'card-body',  # Card structure
                'row', 'g-3'  # Grid system
            ]
            
            for css_class in responsive_classes:
                assert css_class in html_content, f"Missing responsive CSS class: {css_class}"
            
            # Check for viewport meta tag
            assert 'viewport' in html_content, "Missing viewport meta tag"
            assert 'width=device-width' in html_content, "Viewport not configured for mobile"
            
            # Check for Bootstrap CSS
            assert 'bootstrap' in html_content, "Bootstrap CSS not loaded"
            
            # Check for custom CSS
            assert 'style.css' in html_content, "Custom CSS not loaded"
            
            # Verify JavaScript is loaded
            assert 'app.js' in html_content, "Application JavaScript not loaded"
            
            logger.info("✓ Responsive behavior simulation test passed")
            self.test_results.append(("Responsive Behavior Simulation", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Responsive behavior simulation test failed: {e}")
            self.test_results.append(("Responsive Behavior Simulation", False, str(e)))
            return False
    
    def test_azure_deployment_readiness(self):
        """Test Azure deployment readiness."""
        logger.info("Testing Azure deployment readiness...")
        
        try:
            # Check required files exist
            required_files = [
                'startup.py', 'app.py', 'web.config', 'requirements.txt',
                'Data.csv', 'templates/index.html', 'static/css/style.css', 'static/js/app.js'
            ]
            
            for file_path in required_files:
                assert os.path.exists(file_path), f"Required file missing: {file_path}"
            
            # Test startup.py can create application
            from startup import create_app
            test_app = create_app()
            assert test_app is not None, "Failed to create application from startup.py"
            
            # Test environment variable handling
            with patch.dict(os.environ, {'PORT': '8080', 'FLASK_ENV': 'production'}):
                test_app = create_app()
                assert test_app.config['ENV'] == 'production', "Environment configuration not working"
            
            logger.info("✓ Azure deployment readiness test passed")
            self.test_results.append(("Azure Deployment Readiness", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Azure deployment readiness test failed: {e}")
            self.test_results.append(("Azure Deployment Readiness", False, str(e)))
            return False
    
    def test_static_file_serving(self):
        """Test static file serving."""
        logger.info("Testing static file serving...")
        
        try:
            # Test CSS file
            response = self.client.get('/static/css/style.css')
            assert response.status_code == 200, f"CSS file not served, status: {response.status_code}"
            assert b'dark-blue' in response.data or b'primary-blue' in response.data, "CSS content not correct"
            
            # Test JavaScript file
            response = self.client.get('/static/js/app.js')
            assert response.status_code == 200, f"JavaScript file not served, status: {response.status_code}"
            assert b'MusicianSongSelector' in response.data, "JavaScript content not correct"
            
            logger.info("✓ Static file serving test passed")
            self.test_results.append(("Static File Serving", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Static file serving test failed: {e}")
            self.test_results.append(("Static File Serving", False, str(e)))
            return False
    
    def run_all_tests(self):
        """Run all integration tests."""
        logger.info("Starting comprehensive integration test suite...")
        
        if not self.setup():
            return False
        
        # List of all test methods
        test_methods = [
            self.test_csv_data_loading,
            self.test_flask_routes,
            self.test_error_handling,
            self.test_data_consistency,
            self.test_performance_requirements,
            self.test_complete_user_workflow,
            self.test_responsive_behavior_simulation,
            self.test_azure_deployment_readiness,
            self.test_static_file_serving
        ]
        
        # Run all tests
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} crashed: {e}")
        
        # Print summary
        self.print_test_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def print_test_summary(self, passed_tests, total_tests):
        """Print test summary."""
        logger.info("\n" + "="*60)
        logger.info("INTEGRATION TEST SUMMARY")
        logger.info("="*60)
        
        for test_name, passed, error in self.test_results:
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{status:<8} {test_name}")
            if not passed and error:
                logger.info(f"         Error: {error}")
        
        logger.info("="*60)
        logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL INTEGRATION TESTS PASSED!")
            logger.info("Application is ready for production deployment.")
        else:
            logger.error("❌ SOME INTEGRATION TESTS FAILED!")
            logger.error("Please fix the issues before deploying to production.")
        
        logger.info("="*60)

def main():
    """Main function to run integration tests."""
    test_suite = IntegrationTestSuite()
    success = test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())