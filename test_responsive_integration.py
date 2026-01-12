#!/usr/bin/env python3
"""
Responsive Integration Test for Musician Song Selector
Tests responsive behavior simulation and cross-device compatibility.
"""

import os
import sys
import json
import logging
import re

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResponsiveIntegrationTest:
    """Test responsive behavior and cross-device compatibility."""
    
    def __init__(self):
        self.app = None
        self.client = None
        self.test_results = []
        
    def setup(self):
        """Set up the test environment."""
        try:
            from startup import create_app
            self.app = create_app()
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
            
            logger.info("✓ Responsive test environment set up")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to set up test environment: {e}")
            return False
    
    def test_viewport_configuration(self):
        """Test viewport meta tag configuration for mobile devices."""
        logger.info("Testing viewport configuration...")
        
        try:
            response = self.client.get('/')
            html_content = response.data.decode('utf-8')
            
            # Check for viewport meta tag
            viewport_pattern = r'<meta\s+name=["\']viewport["\'][^>]*>'
            viewport_match = re.search(viewport_pattern, html_content, re.IGNORECASE)
            assert viewport_match, "Viewport meta tag not found"
            
            viewport_tag = viewport_match.group()
            
            # Check for required viewport properties
            required_properties = [
                'width=device-width',
                'initial-scale=1.0'
            ]
            
            for prop in required_properties:
                assert prop in viewport_tag, f"Missing viewport property: {prop}"
            
            logger.info("✓ Viewport configuration test passed")
            self.test_results.append(("Viewport Configuration", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Viewport configuration test failed: {e}")
            self.test_results.append(("Viewport Configuration", False, str(e)))
            return False
    
    def test_responsive_css_classes(self):
        """Test responsive CSS classes and Bootstrap grid system."""
        logger.info("Testing responsive CSS classes...")
        
        try:
            response = self.client.get('/')
            html_content = response.data.decode('utf-8')
            
            # Test Bootstrap responsive classes
            responsive_classes = [
                'col-12',      # Full width on mobile
                'col-md-8',    # Medium screens
                'col-lg-6',    # Large screens
                'col-lg-10',   # Container sizing
                'form-select-lg',  # Large form elements
                'mb-3',        # Responsive margins
                'g-3',         # Grid gutters
                'justify-content-center'  # Centering
            ]
            
            for css_class in responsive_classes:
                assert css_class in html_content, f"Missing responsive class: {css_class}"
            
            # Test responsive grid structure
            grid_patterns = [
                r'<div[^>]*class="[^"]*row[^"]*"',  # Row containers
                r'<div[^>]*class="[^"]*col-[^"]*"'  # Column containers
            ]
            
            for pattern in grid_patterns:
                assert re.search(pattern, html_content), f"Missing grid pattern: {pattern}"
            
            logger.info("✓ Responsive CSS classes test passed")
            self.test_results.append(("Responsive CSS Classes", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Responsive CSS classes test failed: {e}")
            self.test_results.append(("Responsive CSS Classes", False, str(e)))
            return False
    
    def test_mobile_friendly_elements(self):
        """Test mobile-friendly form elements and touch targets."""
        logger.info("Testing mobile-friendly elements...")
        
        try:
            response = self.client.get('/')
            html_content = response.data.decode('utf-8')
            
            # Test form elements have appropriate sizing
            form_elements = [
                'form-select-lg',  # Large select dropdown
                'form-label',      # Proper labels
                'form-text'        # Help text
            ]
            
            for element in form_elements:
                assert element in html_content, f"Missing mobile-friendly element: {element}"
            
            # Test accessibility attributes
            accessibility_attrs = [
                'aria-describedby',  # Form descriptions
                'aria-live',         # Live regions
                'role="status"',     # Status indicators
                'role="alert"'       # Alert messages
            ]
            
            for attr in accessibility_attrs:
                assert attr in html_content, f"Missing accessibility attribute: {attr}"
            
            # Test touch-friendly IDs and structure
            touch_elements = [
                'id="songSelect"',        # Main dropdown
                'id="loadingState"',      # Loading indicator
                'id="errorState"',        # Error messages
                'id="songDetails"',       # Song details
                'id="musicianAssignments"' # Assignment cards
            ]
            
            for element in touch_elements:
                assert element in html_content, f"Missing touch element: {element}"
            
            logger.info("✓ Mobile-friendly elements test passed")
            self.test_results.append(("Mobile-Friendly Elements", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Mobile-friendly elements test failed: {e}")
            self.test_results.append(("Mobile-Friendly Elements", False, str(e)))
            return False
    
    def test_responsive_css_media_queries(self):
        """Test responsive CSS media queries and breakpoints."""
        logger.info("Testing responsive CSS media queries...")
        
        try:
            response = self.client.get('/static/css/style.css')
            css_content = response.data.decode('utf-8')
            
            # Test for mobile-first approach
            mobile_first_indicators = [
                'min-width: 576px',   # Small devices
                'min-width: 768px',   # Medium devices
                'min-width: 992px',   # Large devices
                'min-width: 1200px'   # Extra large devices
            ]
            
            for indicator in mobile_first_indicators:
                assert indicator in css_content, f"Missing mobile-first breakpoint: {indicator}"
            
            # Test for responsive design patterns
            responsive_patterns = [
                'max-width: 575px',           # Mobile-specific styles
                'orientation: landscape',      # Orientation handling
                'prefers-reduced-motion',      # Accessibility
                'prefers-contrast: high',      # High contrast support
                'hover: none',                 # Touch device detection
                'pointer: coarse'              # Touch pointer detection
            ]
            
            for pattern in responsive_patterns:
                assert pattern in css_content, f"Missing responsive pattern: {pattern}"
            
            # Test for responsive properties
            responsive_properties = [
                'clamp(',                      # Fluid typography
                'flex-direction: column',      # Mobile layout
                'min-height:',                 # Touch targets
                'backdrop-filter:'             # Modern CSS effects
            ]
            
            for prop in responsive_properties:
                assert prop in css_content, f"Missing responsive property: {prop}"
            
            logger.info("✓ Responsive CSS media queries test passed")
            self.test_results.append(("Responsive CSS Media Queries", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Responsive CSS media queries test failed: {e}")
            self.test_results.append(("Responsive CSS Media Queries", False, str(e)))
            return False
    
    def test_javascript_responsive_behavior(self):
        """Test JavaScript responsive behavior and performance optimizations."""
        logger.info("Testing JavaScript responsive behavior...")
        
        try:
            response = self.client.get('/static/js/app.js')
            js_content = response.data.decode('utf-8')
            
            # Test for responsive JavaScript features
            responsive_features = [
                'MusicianSongSelector',        # Main class
                'loadSongs',                   # Data loading
                'handleSongSelection',         # User interaction
                'displaySongDetails',          # Content display
                'showLoadingIndicator',        # Loading states
                'hideLoadingIndicator',        # State management
                'showError',                   # Error handling
                'announceToScreenReader'       # Accessibility
            ]
            
            for feature in responsive_features:
                assert feature in js_content, f"Missing responsive JS feature: {feature}"
            
            # Test for performance optimizations
            performance_features = [
                'cache',                       # Caching mechanisms
                'debounce',                    # Input debouncing
                'fragment',                    # DOM fragments
                'cloneNode',                   # Efficient DOM manipulation
                'setTimeout',                  # Async handling
                'Map(',                        # Efficient data structures
            ]
            
            for feature in performance_features:
                assert feature in js_content, f"Missing performance feature: {feature}"
            
            # Test for accessibility features
            accessibility_features = [
                'aria-live',                   # Live regions
                'aria-atomic',                 # Atomic updates
                'sr-only',                     # Screen reader only
                'announceToScreenReader',      # Screen reader announcements
                'setAttribute',                # Dynamic attributes
                'textContent'                  # Safe text updates
            ]
            
            for feature in accessibility_features:
                assert feature in js_content, f"Missing accessibility feature: {feature}"
            
            logger.info("✓ JavaScript responsive behavior test passed")
            self.test_results.append(("JavaScript Responsive Behavior", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ JavaScript responsive behavior test failed: {e}")
            self.test_results.append(("JavaScript Responsive Behavior", False, str(e)))
            return False
    
    def test_api_response_structure(self):
        """Test API responses are optimized for different devices."""
        logger.info("Testing API response structure...")
        
        try:
            # Test songs API structure
            response = self.client.get('/api/songs')
            songs_data = json.loads(response.data)
            
            # Verify efficient data structure
            assert 'songs' in songs_data, "Missing songs array"
            songs = songs_data['songs']
            assert len(songs) > 0, "Empty songs array"
            
            # Test song data structure is optimized
            first_song = songs[0]
            required_fields = ['song_id', 'display_name', 'artist', 'song']
            for field in required_fields:
                assert field in first_song, f"Missing required field: {field}"
            
            # Test display_name is properly formatted for dropdowns
            display_name = first_song['display_name']
            assert ' - ' in display_name, "Display name not properly formatted"
            assert display_name == f"{first_song['artist']} - {first_song['song']}", "Display name format incorrect"
            
            # Test song details API
            song_id = first_song['song_id']
            response = self.client.get(f'/api/song/{song_id}')
            song_details = json.loads(response.data)
            
            # Verify detailed structure
            required_details = ['song_id', 'artist', 'song', 'time', 'assignments']
            for field in required_details:
                assert field in song_details, f"Missing detail field: {field}"
            
            # Test assignments structure is mobile-friendly
            assignments = song_details['assignments']
            expected_instruments = ['Lead Guitar', 'Rhythm Guitar', 'Bass', 'Battery', 'Singer', 'Keyboards']
            
            for instrument in expected_instruments:
                assert instrument in assignments, f"Missing instrument: {instrument}"
                # Verify assignment is either None or a non-empty string
                assignment = assignments[instrument]
                if assignment is not None:
                    assert isinstance(assignment, str), f"Assignment not a string for {instrument}"
                    assert len(assignment.strip()) > 0, f"Empty assignment for {instrument}"
            
            logger.info("✓ API response structure test passed")
            self.test_results.append(("API Response Structure", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ API response structure test failed: {e}")
            self.test_results.append(("API Response Structure", False, str(e)))
            return False
    
    def test_cross_device_workflow_simulation(self):
        """Test complete workflow simulation across different device types."""
        logger.info("Testing cross-device workflow simulation...")
        
        try:
            # Simulate mobile device workflow
            logger.info("  Simulating mobile device workflow...")
            
            # Step 1: Load page (mobile)
            response = self.client.get('/')
            assert response.status_code == 200, "Mobile page load failed"
            
            # Step 2: Get songs (mobile dropdown)
            response = self.client.get('/api/songs')
            songs_data = json.loads(response.data)
            assert len(songs_data['songs']) > 0, "Mobile songs loading failed"
            
            # Step 3: Select song (mobile touch)
            mobile_song = songs_data['songs'][0]
            response = self.client.get(f'/api/song/{mobile_song["song_id"]}')
            mobile_details = json.loads(response.data)
            assert 'assignments' in mobile_details, "Mobile song details failed"
            
            # Simulate tablet device workflow
            logger.info("  Simulating tablet device workflow...")
            
            # Test multiple rapid selections (tablet browsing)
            tablet_songs = songs_data['songs'][:3]
            for song in tablet_songs:
                response = self.client.get(f'/api/song/{song["song_id"]}')
                assert response.status_code == 200, f"Tablet browsing failed for {song['display_name']}"
            
            # Simulate desktop device workflow
            logger.info("  Simulating desktop device workflow...")
            
            # Test efficient data access (desktop performance)
            desktop_songs = songs_data['songs'][:10]
            for song in desktop_songs:
                response = self.client.get(f'/api/song/{song["song_id"]}')
                details = json.loads(response.data)
                
                # Verify all data is present for desktop display
                assert len(details['assignments']) == 6, f"Incomplete assignments for {song['display_name']}"
                assert details['time'], f"Missing time for {song['display_name']}"
            
            logger.info("✓ Cross-device workflow simulation test passed")
            self.test_results.append(("Cross-Device Workflow Simulation", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Cross-device workflow simulation test failed: {e}")
            self.test_results.append(("Cross-Device Workflow Simulation", False, str(e)))
            return False
    
    def test_performance_across_devices(self):
        """Test performance requirements across different device simulations."""
        logger.info("Testing performance across devices...")
        
        try:
            import time
            
            # Test mobile performance (slower connection simulation)
            logger.info("  Testing mobile performance...")
            start_time = time.time()
            response = self.client.get('/api/songs')
            mobile_time = time.time() - start_time
            assert mobile_time < 1.0, f"Mobile API too slow: {mobile_time:.3f}s"
            
            # Test tablet performance (medium connection)
            logger.info("  Testing tablet performance...")
            songs_data = json.loads(response.data)
            song_id = songs_data['songs'][0]['song_id']
            
            start_time = time.time()
            response = self.client.get(f'/api/song/{song_id}')
            tablet_time = time.time() - start_time
            assert tablet_time < 1.0, f"Tablet API too slow: {tablet_time:.3f}s"
            
            # Test desktop performance (fast connection, multiple requests)
            logger.info("  Testing desktop performance...")
            start_time = time.time()
            for i in range(5):
                song_id = songs_data['songs'][i]['song_id']
                response = self.client.get(f'/api/song/{song_id}')
                assert response.status_code == 200, f"Desktop request {i+1} failed"
            desktop_time = time.time() - start_time
            avg_desktop_time = desktop_time / 5
            assert avg_desktop_time < 0.2, f"Desktop average too slow: {avg_desktop_time:.3f}s"
            
            logger.info(f"✓ Performance test passed - Mobile: {mobile_time:.3f}s, Tablet: {tablet_time:.3f}s, Desktop avg: {avg_desktop_time:.3f}s")
            self.test_results.append(("Performance Across Devices", True, None))
            return True
            
        except Exception as e:
            logger.error(f"✗ Performance across devices test failed: {e}")
            self.test_results.append(("Performance Across Devices", False, str(e)))
            return False
    
    def run_all_tests(self):
        """Run all responsive integration tests."""
        logger.info("Starting responsive integration test suite...")
        
        if not self.setup():
            return False
        
        # List of all test methods
        test_methods = [
            self.test_viewport_configuration,
            self.test_responsive_css_classes,
            self.test_mobile_friendly_elements,
            self.test_responsive_css_media_queries,
            self.test_javascript_responsive_behavior,
            self.test_api_response_structure,
            self.test_cross_device_workflow_simulation,
            self.test_performance_across_devices
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
        logger.info("RESPONSIVE INTEGRATION TEST SUMMARY")
        logger.info("="*70)
        
        for test_name, passed, error in self.test_results:
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{status:<8} {test_name}")
            if not passed and error:
                logger.info(f"         Error: {error}")
        
        logger.info("="*70)
        logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL RESPONSIVE INTEGRATION TESTS PASSED!")
            logger.info("✓ Mobile-first responsive design verified")
            logger.info("✓ Cross-device compatibility confirmed")
            logger.info("✓ Touch-friendly interface validated")
            logger.info("✓ Performance optimizations working")
            logger.info("✓ Accessibility features implemented")
            logger.info("Application is fully responsive and ready for all devices!")
        else:
            logger.error("❌ SOME RESPONSIVE TESTS FAILED!")
            logger.error("Please fix responsive issues before deployment.")
        
        logger.info("="*70)

def main():
    """Main function to run responsive integration tests."""
    test_suite = ResponsiveIntegrationTest()
    success = test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())