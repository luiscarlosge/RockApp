#!/usr/bin/env python3
"""
End-to-End Integration Test for Musician Song Selector
Tests complete application functionality without external dependencies.
"""

import os
import sys
import json
import time
import logging
from unittest.mock import patch

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EndToEndTestSuite:
    """End-to-end test suite for the complete application."""
    
    def __init__(self):
        self.app = None
        self.client = None
        self.test_results = []
        
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
    
    def test_application_startup(self):
        """Test application startup and initialization."""
        logger.info("Testing application startup...")
        
        try:
            # Test that the application starts without errors
            assert self.app is not None, "Application failed to initialize"
            assert self.client is not None, "Test client failed to initialize"
            
            # Test configuration
            assert 'TESTING' in self.app.config, "Testing configuration not set"
            assert self.app.config['TESTING'] is True, "Testing mode not enabled"
            
            logger.info("✓ Application startup test passed")
            self.test_results.append(("Application Startup", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Application startup test failed: {e}")
            self.test_results.append(("Application Startup", False, str(e)))
            return False
    
    def test_csv_data_processing(self):
        """Test CSV data processing without pandas dependency."""
        logger.info("Testing CSV data processing...")
        
        try:
            from csv_data_processor import CSVDataProcessor
            
            # Test processor initialization
            processor = CSVDataProcessor()
            assert processor is not None, "CSV processor failed to initialize"
            
            # Test data loading
            songs = processor.load_songs()
            assert len(songs) > 0, "No songs loaded from CSV"
            assert len(songs) == 39, f"Expected 39 songs, got {len(songs)}"
            
            # Test first song structure
            first_song = songs[0]
            required_fields = ['artist', 'song', 'song_id', 'time']
            for field in required_fields:
                assert hasattr(first_song, field), f"Missing field: {field}"
            
            # Test song ID generation
            assert first_song.song_id is not None, "Song ID not generated"
            assert isinstance(first_song.song_id, str), "Song ID not a string"
            assert len(first_song.song_id) > 0, "Song ID is empty"
            
            logger.info(f"✓ CSV data processing test passed - {len(songs)} songs loaded")
            self.test_results.append(("CSV Data Processing", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ CSV data processing test failed: {e}")
            self.test_results.append(("CSV Data Processing", False, str(e)))
            return False
    
    def test_web_interface(self):
        """Test web interface and HTML rendering."""
        logger.info("Testing web interface...")
        
        try:
            # Test main page
            response = self.client.get('/')
            assert response.status_code == 200, f"Main page returned {response.status_code}"
            
            html_content = response.data.decode('utf-8')
            
            # Test essential HTML elements
            essential_elements = [
                'Musician Song Selector',  # Title
                'songSelect',  # Dropdown ID
                'Choose a Song',  # Label
                'musicianAssignments',  # Assignments container
                'loadingState',  # Loading state
                'errorState',  # Error state
                'emptyState'  # Empty state
            ]
            
            for element in essential_elements:
                assert element in html_content, f"Missing essential element: {element}"
            
            # Test responsive design elements
            responsive_elements = [
                'viewport',  # Viewport meta tag
                'bootstrap',  # Bootstrap CSS
                'col-12',  # Responsive columns
                'form-select'  # Form styling
            ]
            
            for element in responsive_elements:
                assert element in html_content, f"Missing responsive element: {element}"
            
            logger.info("✓ Web interface test passed")
            self.test_results.append(("Web Interface", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Web interface test failed: {e}")
            self.test_results.append(("Web Interface", False, str(e)))
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints functionality."""
        logger.info("Testing API endpoints...")
        
        try:
            # Test songs list API
            response = self.client.get('/api/songs')
            assert response.status_code == 200, f"Songs API returned {response.status_code}"
            
            songs_data = json.loads(response.data)
            assert 'songs' in songs_data, "Songs API missing 'songs' key"
            assert len(songs_data['songs']) > 0, "Songs API returned empty list"
            assert len(songs_data['songs']) == 39, f"Expected 39 songs, got {len(songs_data['songs'])}"
            
            # Test song structure
            first_song = songs_data['songs'][0]
            required_fields = ['song_id', 'display_name', 'artist', 'song']
            for field in required_fields:
                assert field in first_song, f"Missing field in song data: {field}"
            
            # Test song details API
            song_id = first_song['song_id']
            response = self.client.get(f'/api/song/{song_id}')
            assert response.status_code == 200, f"Song details API returned {response.status_code}"
            
            song_details = json.loads(response.data)
            required_details = ['song_id', 'artist', 'song', 'time', 'assignments']
            for field in required_details:
                assert field in song_details, f"Missing field in song details: {field}"
            
            # Test assignments structure
            assignments = song_details['assignments']
            expected_instruments = ['Lead Guitar', 'Rhythm Guitar', 'Bass', 'Battery', 'Singer', 'Keyboards']
            for instrument in expected_instruments:
                assert instrument in assignments, f"Missing instrument: {instrument}"
            
            # Test invalid song ID
            response = self.client.get('/api/song/invalid-song-id')
            assert response.status_code == 404, f"Invalid song ID should return 404, got {response.status_code}"
            
            logger.info("✓ API endpoints test passed")
            self.test_results.append(("API Endpoints", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ API endpoints test failed: {e}")
            self.test_results.append(("API Endpoints", False, str(e)))
            return False
    
    def test_static_assets(self):
        """Test static asset serving."""
        logger.info("Testing static assets...")
        
        try:
            # Test CSS file
            response = self.client.get('/static/css/style.css')
            assert response.status_code == 200, f"CSS file not served, status: {response.status_code}"
            
            css_content = response.data.decode('utf-8')
            css_elements = ['dark-blue', 'primary-blue', 'responsive', 'instrument-card']
            for element in css_elements:
                assert element in css_content, f"Missing CSS element: {element}"
            
            # Test JavaScript file
            response = self.client.get('/static/js/app.js')
            assert response.status_code == 200, f"JavaScript file not served, status: {response.status_code}"
            
            js_content = response.data.decode('utf-8')
            js_elements = ['MusicianSongSelector', 'loadSongs', 'handleSongSelection', 'displaySongDetails']
            for element in js_elements:
                assert element in js_content, f"Missing JavaScript element: {element}"
            
            logger.info("✓ Static assets test passed")
            self.test_results.append(("Static Assets", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Static assets test failed: {e}")
            self.test_results.append(("Static Assets", False, str(e)))
            return False
    
    def test_complete_user_workflow(self):
        """Test complete user workflow simulation."""
        logger.info("Testing complete user workflow...")
        
        try:
            # Step 1: User loads the page
            response = self.client.get('/')
            assert response.status_code == 200, "Failed to load main page"
            
            # Step 2: User gets songs list (dropdown population)
            response = self.client.get('/api/songs')
            assert response.status_code == 200, "Failed to get songs list"
            songs_data = json.loads(response.data)
            
            # Step 3: User selects multiple songs (simulate browsing)
            test_songs = songs_data['songs'][:5]  # Test first 5 songs
            
            for i, song in enumerate(test_songs):
                song_id = song['song_id']
                
                # Get song details
                response = self.client.get(f'/api/song/{song_id}')
                assert response.status_code == 200, f"Failed to get details for song {i+1}: {song['display_name']}"
                
                song_details = json.loads(response.data)
                
                # Verify song details match dropdown info
                assert song_details['song_id'] == song_id, f"Song ID mismatch for song {i+1}"
                assert song_details['artist'] == song['artist'], f"Artist mismatch for song {i+1}"
                assert song_details['song'] == song['song'], f"Song title mismatch for song {i+1}"
                
                # Verify assignments are present
                assignments = song_details['assignments']
                assert isinstance(assignments, dict), f"Assignments not a dict for song {i+1}"
                
                # Check that at least some instruments are assigned
                assigned_count = sum(1 for v in assignments.values() if v is not None and v.strip())
                assert assigned_count > 0, f"No instruments assigned for song {i+1}"
            
            logger.info(f"✓ Complete user workflow test passed - tested {len(test_songs)} songs")
            self.test_results.append(("Complete User Workflow", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Complete user workflow test failed: {e}")
            self.test_results.append(("Complete User Workflow", False, str(e)))
            return False
    
    def test_performance_requirements(self):
        """Test performance requirements."""
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
            song_id = songs_data['songs'][0]['song_id']
            
            start_time = time.time()
            response = self.client.get(f'/api/song/{song_id}')
            details_response_time = time.time() - start_time
            
            assert response.status_code == 200, "Song details API failed"
            assert details_response_time < 1.0, f"Song details API too slow: {details_response_time:.3f}s"
            
            # Test multiple rapid requests (caching performance)
            start_time = time.time()
            for _ in range(5):
                response = self.client.get('/api/songs')
                assert response.status_code == 200, "Rapid request failed"
            total_time = time.time() - start_time
            avg_time = total_time / 5
            
            assert avg_time < 0.1, f"Cached requests too slow: {avg_time:.3f}s average"
            
            logger.info(f"✓ Performance test passed - Songs: {songs_response_time:.3f}s, Details: {details_response_time:.3f}s, Cached: {avg_time:.3f}s")
            self.test_results.append(("Performance Requirements", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Performance test failed: {e}")
            self.test_results.append(("Performance Requirements", False, str(e)))
            return False
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        logger.info("Testing error handling...")
        
        try:
            # Test invalid endpoints
            response = self.client.get('/api/invalid')
            assert response.status_code == 404, f"Invalid endpoint should return 404, got {response.status_code}"
            
            # Test invalid song ID
            response = self.client.get('/api/song/nonexistent-song')
            assert response.status_code == 404, f"Invalid song ID should return 404, got {response.status_code}"
            
            # Test empty song ID
            response = self.client.get('/api/song/')
            assert response.status_code == 404, f"Empty song ID should return 404, got {response.status_code}"
            
            # Test malformed requests
            response = self.client.post('/api/songs')  # POST instead of GET
            assert response.status_code == 405, f"Wrong method should return 405, got {response.status_code}"
            
            logger.info("✓ Error handling test passed")
            self.test_results.append(("Error Handling", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Error handling test failed: {e}")
            self.test_results.append(("Error Handling", False, str(e)))
            return False
    
    def test_data_integrity(self):
        """Test data integrity and consistency."""
        logger.info("Testing data integrity...")
        
        try:
            # Get all songs through API
            response = self.client.get('/api/songs')
            songs_data = json.loads(response.data)
            songs = songs_data['songs']
            
            # Test each song for data integrity
            for song in songs:
                song_id = song['song_id']
                
                # Get detailed song data
                response = self.client.get(f'/api/song/{song_id}')
                assert response.status_code == 200, f"Failed to get details for {song_id}"
                
                song_details = json.loads(response.data)
                
                # Verify consistency between list and details
                assert song_details['song_id'] == song['song_id'], f"Song ID mismatch for {song_id}"
                assert song_details['artist'] == song['artist'], f"Artist mismatch for {song_id}"
                assert song_details['song'] == song['song'], f"Song title mismatch for {song_id}"
                
                # Verify display name format
                expected_display = f"{song['artist']} - {song['song']}"
                assert song['display_name'] == expected_display, f"Display name format incorrect for {song_id}"
                
                # Verify assignments structure
                assignments = song_details['assignments']
                expected_instruments = ['Lead Guitar', 'Rhythm Guitar', 'Bass', 'Battery', 'Singer', 'Keyboards']
                
                for instrument in expected_instruments:
                    assert instrument in assignments, f"Missing instrument {instrument} in {song_id}"
                    # Assignment can be None or a string, but not other types
                    assignment = assignments[instrument]
                    assert assignment is None or isinstance(assignment, str), f"Invalid assignment type for {instrument} in {song_id}"
                
                # Verify time format
                time_str = song_details['time']
                assert isinstance(time_str, str), f"Time not a string for {song_id}"
                assert ':' in time_str, f"Time format invalid for {song_id}"
            
            logger.info(f"✓ Data integrity test passed - verified {len(songs)} songs")
            self.test_results.append(("Data Integrity", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Data integrity test failed: {e}")
            self.test_results.append(("Data Integrity", False, str(e)))
            return False
    
    def test_azure_deployment_compatibility(self):
        """Test Azure deployment compatibility."""
        logger.info("Testing Azure deployment compatibility...")
        
        try:
            # Test required files exist
            required_files = [
                'startup.py', 'app.py', 'web.config', 'requirements.txt',
                'Data.csv', '.deployment', 'deploy.cmd', 'runtime.txt'
            ]
            
            for file_path in required_files:
                assert os.path.exists(file_path), f"Required file missing: {file_path}"
            
            # Test startup.py functionality
            from startup import create_app
            test_app = create_app()
            assert test_app is not None, "Failed to create application from startup.py"
            
            # Test environment variable handling
            with patch.dict(os.environ, {'PORT': '8080', 'FLASK_ENV': 'production'}):
                test_app = create_app()
                assert test_app.config['ENV'] == 'production', "Environment configuration not working"
            
            # Test web.config content
            with open('web.config', 'r') as f:
                web_config = f.read()
                assert 'httpPlatformHandler' in web_config, "web.config missing httpPlatformHandler"
                assert 'startup.py' in web_config, "web.config not referencing startup.py"
            
            # Test requirements.txt content
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
                assert 'Flask' in requirements, "requirements.txt missing Flask"
            
            logger.info("✓ Azure deployment compatibility test passed")
            self.test_results.append(("Azure Deployment Compatibility", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Azure deployment compatibility test failed: {e}")
            self.test_results.append(("Azure Deployment Compatibility", False, str(e)))
            return False
    
    def run_all_tests(self):
        """Run all end-to-end tests."""
        logger.info("Starting comprehensive end-to-end test suite...")
        
        if not self.setup():
            return False
        
        # List of all test methods
        test_methods = [
            self.test_application_startup,
            self.test_csv_data_processing,
            self.test_web_interface,
            self.test_api_endpoints,
            self.test_static_assets,
            self.test_complete_user_workflow,
            self.test_performance_requirements,
            self.test_error_handling,
            self.test_data_integrity,
            self.test_azure_deployment_compatibility
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
        logger.info("\n" + "="*70)
        logger.info("END-TO-END INTEGRATION TEST SUMMARY")
        logger.info("="*70)
        
        for test_name, passed, error in self.test_results:
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{status:<8} {test_name}")
            if not passed and error:
                logger.info(f"         Error: {error}")
        
        logger.info("="*70)
        logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL END-TO-END TESTS PASSED!")
            logger.info("✓ Complete user workflow verified")
            logger.info("✓ Responsive behavior confirmed")
            logger.info("✓ Error handling validated")
            logger.info("✓ Performance requirements met")
            logger.info("✓ Azure deployment ready")
            logger.info("Application is fully integrated and ready for production!")
        else:
            logger.error("❌ SOME END-TO-END TESTS FAILED!")
            logger.error("Please fix the issues before deploying to production.")
        
        logger.info("="*70)

def main():
    """Main function to run end-to-end tests."""
    test_suite = EndToEndTestSuite()
    success = test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())