#!/usr/bin/env python3
"""
Functional test for cross-section navigation system
Tests the navigation functionality without requiring a browser
"""

import sys
import unittest
import requests
import json
import time
from unittest.mock import patch, Mock

sys.path.insert(0, '.')


class NavigationFunctionalityTest(unittest.TestCase):
    """Functional tests for cross-section navigation system."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = "http://127.0.0.1:5001"
        self.session = requests.Session()
    
    def test_navigation_state_manager_script_loaded(self):
        """Test that the navigation state manager script is included in the page."""
        try:
            response = self.session.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            
            # Check that navigation-state-manager.js is included
            self.assertIn(
                'navigation-state-manager.js',
                response.text,
                "Navigation state manager script should be included in the page"
            )
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_navigation_state_manager_script_accessible(self):
        """Test that the navigation state manager script is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/static/js/navigation-state-manager.js")
            self.assertEqual(response.status_code, 200)
            
            # Check that the script contains the NavigationStateManager class
            self.assertIn(
                'NavigationStateManager',
                response.text,
                "Navigation state manager script should contain NavigationStateManager class"
            )
            
            # Check for key methods
            self.assertIn(
                'navigateWithPreselection',
                response.text,
                "Script should contain navigateWithPreselection method"
            )
            
            self.assertIn(
                'ensureSectionInitialized',
                response.text,
                "Script should contain ensureSectionInitialized method"
            )
            
            self.assertIn(
                'applyPreselection',
                response.text,
                "Script should contain applyPreselection method"
            )
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_api_endpoints_for_navigation(self):
        """Test that API endpoints needed for navigation are working."""
        try:
            # Test songs API
            response = self.session.get(f"{self.base_url}/api/songs")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('songs', data)
            self.assertIsInstance(data['songs'], list)
            
            # Test musicians API
            response = self.session.get(f"{self.base_url}/api/musicians")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('musicians', data)
            self.assertIsInstance(data['musicians'], list)
            
            # If we have songs, test song details API
            songs_response = self.session.get(f"{self.base_url}/api/songs")
            songs_data = songs_response.json()
            
            if songs_data['songs']:
                first_song = songs_data['songs'][0]
                song_id = first_song['song_id']
                
                response = self.session.get(f"{self.base_url}/api/song/{song_id}")
                self.assertEqual(response.status_code, 200)
                
                song_data = response.json()
                self.assertIn('assignments', song_data)
                self.assertIsInstance(song_data['assignments'], dict)
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_cross_section_navigation_data_structure(self):
        """Test that the data structure supports cross-section navigation."""
        try:
            # Get songs data
            response = self.session.get(f"{self.base_url}/api/songs")
            self.assertEqual(response.status_code, 200)
            
            songs_data = response.json()
            
            if songs_data['songs']:
                # Test first song details
                first_song = songs_data['songs'][0]
                song_id = first_song['song_id']
                
                response = self.session.get(f"{self.base_url}/api/song/{song_id}")
                self.assertEqual(response.status_code, 200)
                
                song_data = response.json()
                
                # Verify song data has assignments (needed for musician links)
                self.assertIn('assignments', song_data)
                assignments = song_data['assignments']
                
                # Check that assignments contain musician names
                musician_names = [name for name in assignments.values() if name and name.strip()]
                
                if musician_names:
                    # Test that we can get musician data for cross-navigation
                    musicians_response = self.session.get(f"{self.base_url}/api/musicians")
                    musicians_data = musicians_response.json()
                    
                    # Find a musician that appears in both song assignments and musician list
                    available_musicians = [m['name'] for m in musicians_data['musicians']]
                    
                    common_musicians = set(musician_names) & set(available_musicians)
                    
                    self.assertGreater(
                        len(common_musicians),
                        0,
                        "There should be musicians that appear in both song assignments and musician list"
                    )
                    
                    # Test musician details for cross-navigation back to songs
                    if musicians_data['musicians']:
                        first_musician = musicians_data['musicians'][0]
                        musician_id = first_musician['id']
                        
                        response = self.session.get(f"{self.base_url}/api/musician/{musician_id}")
                        self.assertEqual(response.status_code, 200)
                        
                        musician_data = response.json()
                        self.assertIn('songs', musician_data)
                        self.assertIsInstance(musician_data['songs'], list)
                        
                        # Verify musician songs have IDs for navigation
                        if musician_data['songs']:
                            first_song = musician_data['songs'][0]
                            self.assertIn('id', first_song)
                            self.assertTrue(first_song['id'])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_menu_sections_present(self):
        """Test that all required menu sections are present in the HTML."""
        try:
            response = self.session.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            
            html_content = response.text
            
            # Check for section elements
            self.assertIn('id="song-selector"', html_content)
            self.assertIn('id="musician-selector"', html_content)
            self.assertIn('id="live-performance"', html_content)
            
            # Check for menu items with data-section attributes
            self.assertIn('data-section="song-selector"', html_content)
            self.assertIn('data-section="musician-selector"', html_content)
            self.assertIn('data-section="live-performance"', html_content)
            
            # Check for cross-section navigation elements
            self.assertIn('id="crossSectionLinks"', html_content)
            self.assertIn('id="musicianSelect"', html_content)
            self.assertIn('id="songSelect"', html_content)
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_javascript_integration_points(self):
        """Test that JavaScript integration points are present."""
        try:
            response = self.session.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            
            html_content = response.text
            
            # Check for JavaScript integration elements
            self.assertIn('window.translations', html_content)
            
            # Check for required script includes
            self.assertIn('app.js', html_content)
            self.assertIn('navigation-state-manager.js', html_content)
            
            # Check for elements that JavaScript will interact with
            self.assertIn('class="menu-toggle"', html_content)
            self.assertIn('class="menu-overlay"', html_content)
            self.assertIn('class="menu-item"', html_content)
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")


if __name__ == '__main__':
    unittest.main()