#!/usr/bin/env python3
"""
Test musician selector functionality after feature removal
Tests that musician loading, details display, and cross-section navigation work correctly
Requirements: 4.2
"""

import sys
import unittest
import requests
import json
import time
from unittest.mock import patch, Mock

sys.path.insert(0, '.')


class MusicianSelectorFunctionalityTest(unittest.TestCase):
    """Test musician selector functionality after feature removal."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = "http://127.0.0.1:5001"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def test_musician_loading_works_correctly(self):
        """Test that musician loading works correctly."""
        try:
            # Test musicians API endpoint
            response = self.session.get(f"{self.base_url}/api/musicians")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('musicians', data)
            self.assertIsInstance(data['musicians'], list)
            self.assertGreater(len(data['musicians']), 0, "Should have at least one musician")
            
            # Verify musician structure
            first_musician = data['musicians'][0]
            required_fields = ['id', 'name']
            for field in required_fields:
                self.assertIn(field, first_musician, f"Musician should have {field} field")
                self.assertIsNotNone(first_musician[field], f"Musician {field} should not be None")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_musician_details_display_works_correctly(self):
        """Test that musician details display works correctly."""
        try:
            # First get list of musicians
            musicians_response = self.session.get(f"{self.base_url}/api/musicians")
            self.assertEqual(musicians_response.status_code, 200)
            
            musicians_data = musicians_response.json()
            self.assertGreater(len(musicians_data['musicians']), 0, "Should have musicians to test")
            
            # Test musician details for first musician
            first_musician = musicians_data['musicians'][0]
            musician_id = first_musician['id']
            
            details_response = self.session.get(f"{self.base_url}/api/musician/{musician_id}")
            self.assertEqual(details_response.status_code, 200)
            
            details_data = details_response.json()
            
            # Verify musician details structure
            required_fields = ['id', 'name', 'songs']
            for field in required_fields:
                self.assertIn(field, details_data, f"Musician details should have {field} field")
            
            # Verify songs structure
            songs = details_data['songs']
            self.assertIsInstance(songs, list, "Songs should be a list")
            
            # If there are songs, check their structure
            if songs:
                first_song = songs[0]
                song_required_fields = ['id', 'song', 'artist', 'duration', 'instruments']
                for field in song_required_fields:
                    self.assertIn(field, first_song, f"Song should have {field} field")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_cross_section_navigation_to_song_selector_works(self):
        """Test that cross-section navigation to song selector works."""
        try:
            # Get a musician with song assignments
            musicians_response = self.session.get(f"{self.base_url}/api/musicians")
            self.assertEqual(musicians_response.status_code, 200)
            
            musicians_data = musicians_response.json()
            self.assertGreater(len(musicians_data['musicians']), 0, "Should have musicians to test")
            
            # Find a musician with song assignments
            musician_with_songs = None
            for musician in musicians_data['musicians']:
                details_response = self.session.get(f"{self.base_url}/api/musician/{musician['id']}")
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    songs = details_data['songs']
                    
                    # Check if musician has songs assigned
                    if songs and len(songs) > 0:
                        musician_with_songs = details_data
                        break
            
            self.assertIsNotNone(musician_with_songs, "Should find at least one musician with song assignments")
            
            # Verify that we can get song data for cross-navigation
            songs_response = self.session.get(f"{self.base_url}/api/songs")
            self.assertEqual(songs_response.status_code, 200)
            
            songs_data = songs_response.json()
            self.assertIn('songs', songs_data)
            self.assertIsInstance(songs_data['songs'], list)
            self.assertGreater(len(songs_data['songs']), 0, "Should have songs for navigation")
            
            # Verify that assigned songs exist in the songs list
            musician_songs = musician_with_songs['songs']
            available_song_ids = [s['song_id'] for s in songs_data['songs']]
            
            for song in musician_songs:
                self.assertIn(
                    song['id'], 
                    available_song_ids,
                    f"Assigned song '{song['id']}' should exist in songs list"
                )
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_musician_selector_ui_elements_present(self):
        """Test that musician selector UI elements are present in the HTML."""
        try:
            response = self.session.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            
            html_content = response.text
            
            # Check for musician selector section
            self.assertIn('id="musician-selector"', html_content, "Should have musician selector section")
            
            # Check for musician selection dropdown
            self.assertIn('id="musicianSelect"', html_content, "Should have musician selection dropdown")
            
            # Check for musician details display elements
            self.assertIn('id="musicianDetails"', html_content, "Should have musician details display")
            self.assertIn('id="musicianName"', html_content, "Should have musician name element")
            self.assertIn('id="musicianSongCount"', html_content, "Should have musician song count element")
            self.assertIn('id="musicianSongs"', html_content, "Should have musician songs element")
            
            # Check for loading and error states
            self.assertIn('id="musicianLoadingState"', html_content, "Should have musician loading state element")
            self.assertIn('id="musicianErrorState"', html_content, "Should have musician error state element")
            self.assertIn('id="musicianEmptyState"', html_content, "Should have musician empty state element")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_musician_selector_javascript_functionality(self):
        """Test that musician selector JavaScript functionality is loaded."""
        try:
            # Check main JavaScript file
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            self.assertEqual(response.status_code, 200)
            
            js_content = response.text
            
            # Check for MusicianSelector class
            self.assertIn('class MusicianSelector', js_content, "Should have MusicianSelector class")
            
            # Check for key methods
            self.assertIn('loadMusicians()', js_content, "Should have loadMusicians method")
            self.assertIn('handleMusicianSelection', js_content, "Should have handleMusicianSelection method")
            self.assertIn('displayMusicianDetails', js_content, "Should have displayMusicianDetails method")
            self.assertIn('navigateToSongSelector', js_content, "Should have navigateToSongSelector method")
            
            # Verify that live performance functionality is removed
            self.assertNotIn('LivePerformanceManager', js_content, "Should not have LivePerformanceManager class")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")


if __name__ == '__main__':
    unittest.main()