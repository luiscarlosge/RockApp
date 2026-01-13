#!/usr/bin/env python3
"""
Test song selector functionality after feature removal
Tests that song loading, details display, and cross-section navigation work correctly
Requirements: 4.1
"""

import sys
import unittest
import requests
import json
import time
from unittest.mock import patch, Mock

sys.path.insert(0, '.')


class SongSelectorFunctionalityTest(unittest.TestCase):
    """Test song selector functionality after feature removal."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = "http://127.0.0.1:5001"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def test_song_loading_works_correctly(self):
        """Test that song loading works correctly."""
        try:
            # Test songs API endpoint
            response = self.session.get(f"{self.base_url}/api/songs")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('songs', data)
            self.assertIsInstance(data['songs'], list)
            self.assertGreater(len(data['songs']), 0, "Should have at least one song")
            
            # Verify song structure
            first_song = data['songs'][0]
            required_fields = ['song_id', 'display_name', 'artist', 'song']
            for field in required_fields:
                self.assertIn(field, first_song, f"Song should have {field} field")
                self.assertIsNotNone(first_song[field], f"Song {field} should not be None")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_song_details_display_works_correctly(self):
        """Test that song details display works correctly."""
        try:
            # First get list of songs
            songs_response = self.session.get(f"{self.base_url}/api/songs")
            self.assertEqual(songs_response.status_code, 200)
            
            songs_data = songs_response.json()
            self.assertGreater(len(songs_data['songs']), 0, "Should have songs to test")
            
            # Test song details for first song
            first_song = songs_data['songs'][0]
            song_id = first_song['song_id']
            
            details_response = self.session.get(f"{self.base_url}/api/song/{song_id}")
            self.assertEqual(details_response.status_code, 200)
            
            details_data = details_response.json()
            
            # Verify song details structure
            required_fields = ['song_id', 'song', 'artist', 'time', 'assignments']
            for field in required_fields:
                self.assertIn(field, details_data, f"Song details should have {field} field")
            
            # Verify assignments structure
            assignments = details_data['assignments']
            self.assertIsInstance(assignments, dict, "Assignments should be a dictionary")
            
            # Check for expected instrument assignments
            expected_instruments = ['Lead Guitar', 'Rhythm Guitar', 'Bass', 'Battery', 'Singer', 'Keyboards']
            for instrument in expected_instruments:
                self.assertIn(instrument, assignments, f"Should have {instrument} assignment")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_cross_section_navigation_to_musician_selector_works(self):
        """Test that cross-section navigation to musician selector works."""
        try:
            # Get a song with musician assignments
            songs_response = self.session.get(f"{self.base_url}/api/songs")
            self.assertEqual(songs_response.status_code, 200)
            
            songs_data = songs_response.json()
            self.assertGreater(len(songs_data['songs']), 0, "Should have songs to test")
            
            # Find a song with musician assignments
            song_with_musicians = None
            for song in songs_data['songs']:
                details_response = self.session.get(f"{self.base_url}/api/song/{song['song_id']}")
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    assignments = details_data['assignments']
                    
                    # Check if any instrument has a musician assigned
                    musician_names = [name for name in assignments.values() if name and name.strip()]
                    if musician_names:
                        song_with_musicians = details_data
                        break
            
            self.assertIsNotNone(song_with_musicians, "Should find at least one song with musician assignments")
            
            # Verify that we can get musician data for cross-navigation
            musicians_response = self.session.get(f"{self.base_url}/api/musicians")
            self.assertEqual(musicians_response.status_code, 200)
            
            musicians_data = musicians_response.json()
            self.assertIn('musicians', musicians_data)
            self.assertIsInstance(musicians_data['musicians'], list)
            self.assertGreater(len(musicians_data['musicians']), 0, "Should have musicians for navigation")
            
            # Verify that assigned musicians exist in the musicians list
            assignments = song_with_musicians['assignments']
            musician_names = [name for name in assignments.values() if name and name.strip()]
            
            available_musician_names = [m['name'] for m in musicians_data['musicians']]
            
            for musician_name in musician_names:
                self.assertIn(
                    musician_name, 
                    available_musician_names,
                    f"Assigned musician '{musician_name}' should exist in musicians list"
                )
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_song_selector_ui_elements_present(self):
        """Test that song selector UI elements are present in the HTML."""
        try:
            response = self.session.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            
            html_content = response.text
            
            # Check for song selector section
            self.assertIn('id="song-selector"', html_content, "Should have song selector section")
            self.assertIn('class="app-section active"', html_content, "Song selector should be active by default")
            
            # Check for song selection dropdown
            self.assertIn('id="songSelect"', html_content, "Should have song selection dropdown")
            
            # Check for song details display elements
            self.assertIn('id="songDetails"', html_content, "Should have song details display")
            self.assertIn('id="songTitle"', html_content, "Should have song title element")
            self.assertIn('id="songArtist"', html_content, "Should have song artist element")
            self.assertIn('id="musicianAssignments"', html_content, "Should have musician assignments element")
            
            # Check for loading and error states
            self.assertIn('id="loadingState"', html_content, "Should have loading state element")
            self.assertIn('id="errorState"', html_content, "Should have error state element")
            self.assertIn('id="emptyState"', html_content, "Should have empty state element")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_song_selector_javascript_functionality(self):
        """Test that song selector JavaScript functionality is loaded."""
        try:
            # Check main JavaScript file
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            self.assertEqual(response.status_code, 200)
            
            js_content = response.text
            
            # Check for MusicianSongSelector class
            self.assertIn('class MusicianSongSelector', js_content, "Should have MusicianSongSelector class")
            
            # Check for key methods
            self.assertIn('loadSongs()', js_content, "Should have loadSongs method")
            self.assertIn('handleSongSelection', js_content, "Should have handleSongSelection method")
            self.assertIn('displaySongDetails', js_content, "Should have displaySongDetails method")
            self.assertIn('navigateToMusicianSelector', js_content, "Should have navigateToMusicianSelector method")
            
            # Verify that live performance functionality is removed
            self.assertNotIn('LivePerformanceManager', js_content, "Should not have LivePerformanceManager class")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")


if __name__ == '__main__':
    unittest.main()