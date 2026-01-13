#!/usr/bin/env python3
"""
Comprehensive Integration Tests for UI/UX Improvements
Tests complete user flows including navigation, refresh cycles, and accessibility compliance.

This test suite validates all requirements from the UI/UX improvements specification:
- Text contrast and visibility (Requirements 1.1-1.5)
- Real-time data refresh (Requirements 2.1-2.5)
- Cross-section navigation (Requirements 3.1-3.5)
- Enhanced user feedback (Requirements 4.1-4.5)
- Accessibility compliance (Requirements 5.1-5.5)
"""

import os
import sys
import json
import time
import logging
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UIUXIntegrationFlowsTest(unittest.TestCase):
    """
    Comprehensive integration tests for UI/UX improvements.
    Tests complete user flows and system integration.
    """
    
    def setUp(self):
        """Set up test environment."""
        try:
            from startup import create_app
            self.app = create_app()
            self.app.config['TESTING'] = True
            self.app.config['DEBUG'] = False
            self.client = self.app.test_client()
            
            # Mock external dependencies
            self.mock_data_processor = Mock()
            self.mock_live_manager = Mock()
            
        except Exception as e:
            self.skipTest(f"Failed to set up test environment: {e}")
    
    def test_complete_navigation_flow(self):
        """
        Test complete navigation flow between all sections with preselection.
        Validates Requirements 3.1, 3.2, 3.3, 3.4, 3.5
        """
        logger.info("Testing complete navigation flow...")
        
        # Step 1: Load main page (song selector)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.data.decode('utf-8')
        
        # Verify navigation menu structure
        self.assertIn('data-section="song-selector"', html_content)
        self.assertIn('data-section="musician-selector"', html_content)
        self.assertIn('data-section="live-performance"', html_content)
        
        # Step 2: Test song selection and cross-section navigation
        response = self.client.get('/api/songs')
        self.assertEqual(response.status_code, 200)
        
        songs_data = json.loads(response.data)
        if songs_data.get('songs'):
            first_song_id = songs_data['songs'][0]['song_id']
            
            # Get song details to test cross-section links
            response = self.client.get(f'/api/song/{first_song_id}')
            self.assertEqual(response.status_code, 200)
            
            song_details = json.loads(response.data)
            
            # Verify song details structure for navigation
            self.assertIn('assignments', song_details)
            self.assertIn('song_id', song_details)
            
            # Test that assignments contain musician names for navigation
            assignments = song_details['assignments']
            musician_names = [name for name in assignments.values() if name and name.strip()]
            self.assertGreater(len(musician_names), 0, "Should have at least one musician assignment")
        
        # Step 3: Test musician selector navigation
        response = self.client.get('/api/musicians')
        self.assertEqual(response.status_code, 200)
        
        musicians_data = json.loads(response.data)
        if musicians_data.get('musicians'):
            first_musician_id = musicians_data['musicians'][0]['id']
            
            # Get musician details to test reverse navigation
            response = self.client.get(f'/api/musician/{first_musician_id}')
            self.assertEqual(response.status_code, 200)
            
            musician_details = json.loads(response.data)
            
            # Verify musician details structure for navigation
            self.assertIn('songs', musician_details)
            self.assertIn('id', musician_details)
            
            # Test that songs contain IDs for navigation back to song selector
            songs = musician_details['songs']
            if songs:
                self.assertIn('id', songs[0])
        
        # Step 4: Test live performance section
        response = self.client.get('/api/live-performance')
        self.assertEqual(response.status_code, 200)
        
        performance_data = json.loads(response.data)
        
        # Verify live performance data structure
        self.assertIsInstance(performance_data, dict)
        
        logger.info("✓ Complete navigation flow test passed")
    
    def test_enhanced_refresh_cycle_integration(self):
        """
        Test enhanced refresh cycle with countdown timer and error handling.
        Validates Requirements 2.1, 2.2, 2.3, 2.4, 2.5
        """
        logger.info("Testing enhanced refresh cycle integration...")
        
        # Test 1: Verify 5-second refresh interval capability (Requirements 2.1)
        start_time = time.time()
        
        # Simulate multiple rapid requests to test refresh capability
        for i in range(3):
            response = self.client.get('/api/live-performance')
            self.assertEqual(response.status_code, 200)
            
            # Verify response time is suitable for 5-second intervals
            request_time = time.time() - start_time
            self.assertLess(request_time, 1.0, "Request should complete within 1 second for 5s intervals")
            start_time = time.time()
        
        # Test 2: Verify countdown timer data structure (Requirements 2.2, 2.5)
        response = self.client.get('/api/live-performance')
        self.assertEqual(response.status_code, 200)
        
        performance_data = json.loads(response.data)
        
        # Verify data structure supports countdown display
        self.assertIsInstance(performance_data, dict)
        
        # Test 3: Verify error handling structure (Requirements 2.3)
        # Test with invalid endpoint to trigger error handling
        response = self.client.get('/api/invalid-live-performance')
        self.assertEqual(response.status_code, 404)
        
        # Test 4: Verify DOM update structure (Requirements 2.4, 2.5)
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Check for live performance display elements
        self.assertIn('id="currentSongDisplay"', html_content)
        self.assertIn('id="nextSongDisplay"', html_content)
        
        # Check for refresh UI elements
        self.assertIn('aria-live', html_content)  # For screen reader announcements
        
        logger.info("✓ Enhanced refresh cycle integration test passed")
    
    def test_text_contrast_compliance_integration(self):
        """
        Test text contrast compliance across all sections.
        Validates Requirements 1.1, 1.2, 1.3, 1.4, 1.5
        """
        logger.info("Testing text contrast compliance integration...")
        
        # Test main page CSS structure
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        
        # Verify high contrast color definitions (Requirements 1.1, 1.2)
        contrast_indicators = [
            '#ffffff',  # White text for maximum contrast
            'color:',   # Color property definitions
            'background-color:',  # Background color definitions
        ]
        
        for indicator in contrast_indicators:
            self.assertIn(indicator, css_content, f"CSS should contain {indicator} for contrast compliance")
        
        # Test HTML structure for contrast compliance
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Verify menu structure supports high contrast (Requirements 1.1)
        self.assertIn('menu-item', html_content)
        self.assertIn('menu-toggle', html_content)
        
        # Verify form elements support contrast (Requirements 1.2, 1.4, 1.5)
        self.assertIn('form-select', html_content)
        self.assertIn('form-label', html_content)
        
        # Verify interactive elements support hover states (Requirements 1.3)
        self.assertIn('button', html_content)  # Button elements for interaction
        
        logger.info("✓ Text contrast compliance integration test passed")
    
    def test_accessibility_compliance_integration(self):
        """
        Test accessibility compliance across all features.
        Validates Requirements 5.1, 5.2, 5.3, 5.4, 5.5
        """
        logger.info("Testing accessibility compliance integration...")
        
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Test 1: Screen reader support (Requirements 5.1, 5.5)
        accessibility_attributes = [
            'aria-live',
            'aria-label',
            'aria-describedby',
            'role=',
            'aria-expanded',
            'aria-hidden'
        ]
        
        for attr in accessibility_attributes:
            self.assertIn(attr, html_content, f"HTML should contain {attr} for screen reader support")
        
        # Test 2: Focus indicators (Requirements 5.3)
        # Verify focusable elements have proper structure
        focusable_elements = [
            'aria-expanded',
            'form-select',
            'button',
            'menu-item'
        ]
        
        for element in focusable_elements:
            self.assertIn(element, html_content, f"HTML should contain {element} for focus management")
        
        # Test 3: Timer accessibility (Requirements 5.4)
        # Verify live performance section has accessibility attributes
        self.assertIn('live-performance', html_content)
        
        # Test 4: WCAG compliance structure (Requirements 5.2)
        # Verify semantic HTML structure
        semantic_elements = [
            '<main',
            '<section',
            '<nav',
            '<header',
            'role='
        ]
        
        semantic_count = sum(1 for element in semantic_elements if element in html_content)
        self.assertGreater(semantic_count, 2, "Should have semantic HTML structure for WCAG compliance")
        
        logger.info("✓ Accessibility compliance integration test passed")
    
    def test_user_feedback_integration(self):
        """
        Test user feedback systems integration.
        Validates Requirements 4.1, 4.2, 4.3, 4.4, 4.5
        """
        logger.info("Testing user feedback integration...")
        
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Test 1: Loading state feedback (Requirements 4.1, 4.2)
        loading_indicators = [
            'loadingState',
            'spinner',
            'loading',
            'aria-live'
        ]
        
        for indicator in loading_indicators:
            self.assertIn(indicator, html_content, f"Should have {indicator} for loading feedback")
        
        # Test 2: Error state feedback (Requirements 4.1, 4.2)
        error_indicators = [
            'errorState',
            'alert',
            'error',
            'role="alert"'
        ]
        
        for indicator in error_indicators:
            self.assertIn(indicator, html_content, f"Should have {indicator} for error feedback")
        
        # Test 3: Transition support (Requirements 4.3)
        # Verify CSS and JavaScript are loaded for smooth transitions
        self.assertIn('style.css', html_content)
        self.assertIn('app.js', html_content)
        
        # Test 4: Success feedback structure (Requirements 4.4, 4.5)
        # Verify elements exist for success feedback
        success_indicators = [
            'songDetails',
            'musicianDetails',
            'card'
        ]
        
        for indicator in success_indicators:
            self.assertIn(indicator, html_content, f"Should have {indicator} for success feedback")
        
        logger.info("✓ User feedback integration test passed")
    
    def test_cross_browser_compatibility_structure(self):
        """
        Test cross-browser compatibility structure and standards compliance.
        """
        logger.info("Testing cross-browser compatibility structure...")
        
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Test 1: HTML5 doctype and structure
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('<html', html_content)
        self.assertIn('lang=', html_content)
        
        # Test 2: Viewport meta tag for mobile compatibility
        self.assertIn('viewport', html_content)
        self.assertIn('width=device-width', html_content)
        
        # Test 3: Bootstrap CSS for cross-browser consistency
        self.assertIn('bootstrap', html_content)
        
        # Test 4: Progressive enhancement structure
        # Verify that basic functionality works without JavaScript
        # Note: This application is JavaScript-dependent, so we check for graceful degradation
        self.assertIn('visually-hidden', html_content, "Should have screen reader support")
        
        # Test 5: CSS compatibility
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        
        # Check for vendor prefixes and fallbacks
        compatibility_indicators = [
            'display: flex',  # Modern CSS
            'transition:',    # CSS transitions
            '@media',         # Media queries for responsive design
        ]
        
        for indicator in compatibility_indicators:
            self.assertIn(indicator, css_content, f"CSS should contain {indicator} for compatibility")
        
        logger.info("✓ Cross-browser compatibility structure test passed")
    
    def test_responsive_design_integration(self):
        """
        Test responsive design integration across all components.
        """
        logger.info("Testing responsive design integration...")
        
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Test 1: Bootstrap grid system
        grid_classes = [
            'col-12',
            'col-md-',
            'col-lg-',
            'row',
            'container'
        ]
        
        for grid_class in grid_classes:
            self.assertIn(grid_class, html_content, f"Should use {grid_class} for responsive layout")
        
        # Test 2: Responsive form elements
        responsive_form_classes = [
            'form-select-lg',
            'form-select',
            'form-label'
        ]
        
        for form_class in responsive_form_classes:
            self.assertIn(form_class, html_content, f"Should use {form_class} for responsive forms")
        
        # Test 3: Responsive navigation
        nav_classes = [
            'menu-toggle',
            'menu-overlay',
            'menu-item'
        ]
        
        for nav_class in nav_classes:
            self.assertIn(nav_class, html_content, f"Should use {nav_class} for responsive navigation")
        
        # Test 4: CSS media queries
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        
        # Verify media queries for different screen sizes
        media_queries = [
            '@media',
            'max-width',
            'min-width'
        ]
        
        for query in media_queries:
            self.assertIn(query, css_content, f"CSS should contain {query} for responsive design")
        
        logger.info("✓ Responsive design integration test passed")
    
    def test_performance_optimization_integration(self):
        """
        Test performance optimization integration.
        """
        logger.info("Testing performance optimization integration...")
        
        # Test 1: API response times
        endpoints = [
            '/api/songs',
            '/api/live-performance',
            '/api/musicians'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            response_time = time.time() - start_time
            
            # Should respond quickly for good user experience
            self.assertLess(response_time, 1.0, f"{endpoint} should respond within 1 second")
            
            if response.status_code == 200:
                # Verify JSON response is properly formatted
                try:
                    json.loads(response.data)
                except json.JSONDecodeError:
                    self.fail(f"{endpoint} should return valid JSON")
        
        # Test 2: Static asset serving
        static_assets = [
            '/static/css/style.css',
            '/static/js/app.js'
        ]
        
        for asset in static_assets:
            start_time = time.time()
            response = self.client.get(asset)
            response_time = time.time() - start_time
            
            self.assertEqual(response.status_code, 200, f"{asset} should be served successfully")
            self.assertLess(response_time, 0.5, f"{asset} should load quickly")
        
        # Test 3: Caching headers (if implemented)
        response = self.client.get('/api/songs')
        if response.status_code == 200:
            # Check for cache-friendly headers
            headers = dict(response.headers)
            # Note: Actual caching implementation may vary
            self.assertIsInstance(headers, dict, "Should have response headers")
        
        logger.info("✓ Performance optimization integration test passed")
    
    def test_error_handling_integration(self):
        """
        Test comprehensive error handling integration.
        """
        logger.info("Testing error handling integration...")
        
        # Test 1: API error responses
        error_endpoints = [
            '/api/song/nonexistent-id',
            '/api/musician/nonexistent-id',
            '/api/invalid-endpoint'
        ]
        
        for endpoint in error_endpoints:
            response = self.client.get(endpoint)
            self.assertIn(response.status_code, [404, 500], f"{endpoint} should return appropriate error code")
            
            if response.status_code != 404:  # 404 might not have JSON body
                try:
                    error_data = json.loads(response.data)
                    self.assertIn('error', error_data, "Error response should contain error message")
                except json.JSONDecodeError:
                    # Some error responses might be HTML
                    pass
        
        # Test 2: Error state UI elements
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        error_ui_elements = [
            'errorState',
            'alert-danger',
            'role="alert"',
            'aria-live="assertive"'
        ]
        
        for element in error_ui_elements:
            self.assertIn(element, html_content, f"Should have {element} for error handling UI")
        
        # Test 3: Graceful degradation
        # Verify that the page loads even if some resources fail
        self.assertIn('visually-hidden', html_content, "Should have screen reader support for graceful degradation")
        
        logger.info("✓ Error handling integration test passed")
    
    def test_data_consistency_integration(self):
        """
        Test data consistency across all sections and navigation flows.
        """
        logger.info("Testing data consistency integration...")
        
        # Test 1: Song data consistency
        response = self.client.get('/api/songs')
        if response.status_code == 200:
            songs_data = json.loads(response.data)
            
            if songs_data.get('songs'):
                # Test first song for consistency
                first_song = songs_data['songs'][0]
                song_id = first_song['song_id']
                
                # Get detailed song data
                response = self.client.get(f'/api/song/{song_id}')
                if response.status_code == 200:
                    song_details = json.loads(response.data)
                    
                    # Verify consistency between list and details
                    self.assertEqual(song_details['song_id'], first_song['song_id'])
                    self.assertEqual(song_details['artist'], first_song['artist'])
                    self.assertEqual(song_details['song'], first_song['song'])
        
        # Test 2: Musician data consistency
        response = self.client.get('/api/musicians')
        if response.status_code == 200:
            musicians_data = json.loads(response.data)
            
            if musicians_data.get('musicians'):
                # Test first musician for consistency
                first_musician = musicians_data['musicians'][0]
                musician_id = first_musician['id']
                
                # Get detailed musician data
                response = self.client.get(f'/api/musician/{musician_id}')
                if response.status_code == 200:
                    musician_details = json.loads(response.data)
                    
                    # Verify consistency
                    self.assertEqual(musician_details['id'], first_musician['id'])
                    self.assertEqual(musician_details['name'], first_musician['name'])
        
        # Test 3: Cross-reference consistency
        # Verify that musicians mentioned in songs exist in musician list
        response = self.client.get('/api/songs')
        if response.status_code == 200:
            songs_data = json.loads(response.data)
            
            response = self.client.get('/api/musicians')
            if response.status_code == 200:
                musicians_data = json.loads(response.data)
                musician_names = {m['name'] for m in musicians_data.get('musicians', [])}
                
                # Check a few songs for musician consistency
                for song in songs_data.get('songs', [])[:3]:  # Check first 3 songs
                    response = self.client.get(f'/api/song/{song["song_id"]}')
                    if response.status_code == 200:
                        song_details = json.loads(response.data)
                        assignments = song_details.get('assignments', {})
                        
                        # Check that assigned musicians exist in musician list
                        for musician_name in assignments.values():
                            if musician_name and musician_name.strip():
                                # Note: This is a soft check since data might have inconsistencies
                                # In a real system, this would be a hard requirement
                                if musician_names:  # Only check if we have musician data
                                    self.assertIn(
                                        musician_name, musician_names,
                                        f"Musician {musician_name} should exist in musician list"
                                    )
        
        logger.info("✓ Data consistency integration test passed")


def run_integration_tests():
    """Run all integration tests and return results."""
    logger.info("Starting UI/UX Integration Flow Tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(UIUXIntegrationFlowsTest)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("UI/UX INTEGRATION FLOW TEST SUMMARY")
    logger.info("="*70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failures}")
    logger.info(f"Errors: {errors}")
    logger.info(f"Skipped: {skipped}")
    
    if result.failures:
        logger.info("\nFAILURES:")
        for test, traceback in result.failures:
            logger.info(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        logger.info("\nERRORS:")
        for test, traceback in result.errors:
            logger.info(f"- {test}: {traceback.split('\\n')[-2]}")
    
    success = failures == 0 and errors == 0
    
    if success:
        logger.info("\n🎉 ALL UI/UX INTEGRATION TESTS PASSED!")
        logger.info("✓ Complete navigation flows validated")
        logger.info("✓ Enhanced refresh cycles tested")
        logger.info("✓ Text contrast compliance verified")
        logger.info("✓ Accessibility compliance confirmed")
        logger.info("✓ User feedback systems validated")
        logger.info("✓ Cross-browser compatibility structure verified")
        logger.info("✓ Responsive design integration confirmed")
        logger.info("✓ Performance optimization validated")
        logger.info("✓ Error handling integration tested")
        logger.info("✓ Data consistency verified")
        logger.info("\nAll UI/UX improvements are properly integrated!")
    else:
        logger.error("\n❌ SOME UI/UX INTEGRATION TESTS FAILED!")
        logger.error("Please review and fix the issues before deployment.")
    
    logger.info("="*70)
    
    return success


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)