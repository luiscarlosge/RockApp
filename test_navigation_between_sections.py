#!/usr/bin/env python3
"""
Test navigation between sections after feature removal
Tests hamburger menu, section switching, and keyboard navigation work correctly
Requirements: 4.3
"""

import sys
import unittest
import requests
import json
import time
from unittest.mock import patch, Mock

sys.path.insert(0, '.')


class NavigationBetweenSectionsTest(unittest.TestCase):
    """Test navigation between sections after feature removal."""
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = "http://127.0.0.1:5001"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def test_hamburger_menu_works_correctly_with_two_sections(self):
        """Test that hamburger menu works correctly with two sections."""
        try:
            response = self.session.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            
            html_content = response.text
            
            # Check for hamburger menu elements
            self.assertIn('class="menu-toggle"', html_content, "Should have menu toggle button")
            self.assertIn('class="menu-overlay"', html_content, "Should have menu overlay")
            self.assertIn('class="menu-item"', html_content, "Should have menu items")
            
            # Check for exactly two sections (song-selector and musician-selector)
            self.assertIn('data-section="song-selector"', html_content, "Should have song selector menu item")
            self.assertIn('data-section="musician-selector"', html_content, "Should have musician selector menu item")
            
            # Verify that live performance section is NOT present
            self.assertNotIn('data-section="live-performance"', html_content, "Should NOT have live performance menu item")
            
            # Check that both sections exist in the DOM
            self.assertIn('id="song-selector"', html_content, "Should have song selector section")
            self.assertIn('id="musician-selector"', html_content, "Should have musician selector section")
            
            # Verify that live performance section is NOT present
            self.assertNotIn('id="live-performance"', html_content, "Should NOT have live performance section")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_section_switching_works_correctly(self):
        """Test that section switching works correctly."""
        try:
            # Check main JavaScript file for section switching functionality
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            self.assertEqual(response.status_code, 200)
            
            js_content = response.text
            
            # Check for HamburgerMenuSystem class
            self.assertIn('class HamburgerMenuSystem', js_content, "Should have HamburgerMenuSystem class")
            
            # Check for navigation methods
            self.assertIn('navigateToSection', js_content, "Should have navigateToSection method")
            self.assertIn('setActiveSection', js_content, "Should have setActiveSection method")
            self.assertIn('updateActiveMenuItem', js_content, "Should have updateActiveMenuItem method")
            
            # Check for section initialization
            self.assertIn('initializeSectionContent', js_content, "Should have initializeSectionContent method")
            
            # Verify that only two sections are handled
            # Check that song-selector and musician-selector are referenced
            self.assertIn("'song-selector'", js_content, "Should reference song-selector")
            self.assertIn("'musician-selector'", js_content, "Should reference musician-selector")
            
            # Verify that live performance references are removed
            self.assertNotIn("'live-performance'", js_content, "Should NOT reference live-performance")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_keyboard_navigation_works_correctly(self):
        """Test that keyboard navigation works correctly (Alt+1, Alt+2, Alt+m)."""
        try:
            # Check main JavaScript file for keyboard navigation
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            self.assertEqual(response.status_code, 200)
            
            js_content = response.text
            
            # Check for keyboard event handling
            self.assertIn("addEventListener('keydown'", js_content, "Should have keydown event listener")
            self.assertIn('e.altKey', js_content, "Should handle Alt key combinations")
            
            # Check for specific keyboard shortcuts
            self.assertIn("case '1':", js_content, "Should handle Alt+1 shortcut")
            self.assertIn("case '2':", js_content, "Should handle Alt+2 shortcut")
            self.assertIn("case 'm':", js_content, "Should handle Alt+m shortcut")
            
            # Verify that Alt+1 navigates to song-selector
            alt1_index = js_content.find("case '1':")
            if alt1_index != -1:
                # Look for song-selector navigation within reasonable distance
                alt1_section = js_content[alt1_index:alt1_index + 200]
                self.assertIn('song-selector', alt1_section, "Alt+1 should navigate to song-selector")
            
            # Verify that Alt+2 navigates to musician-selector
            alt2_index = js_content.find("case '2':")
            if alt2_index != -1:
                # Look for musician-selector navigation within reasonable distance
                alt2_section = js_content[alt2_index:alt2_index + 200]
                self.assertIn('musician-selector', alt2_section, "Alt+2 should navigate to musician-selector")
            
            # Verify that Alt+3 (live performance) is NOT present
            self.assertNotIn("case '3':", js_content, "Should NOT have Alt+3 shortcut for live performance")
            
            # Verify that Alt+m toggles menu
            altm_index = js_content.find("case 'm':")
            if altm_index != -1:
                # Look for menu toggle within reasonable distance
                altm_section = js_content[altm_index:altm_index + 200]
                self.assertIn('toggleMenu', altm_section, "Alt+m should toggle menu")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_navigation_accessibility_features(self):
        """Test that navigation accessibility features are present."""
        try:
            response = self.session.get(self.base_url)
            self.assertEqual(response.status_code, 200)
            
            html_content = response.text
            
            # Check for ARIA attributes on menu elements
            self.assertIn('aria-expanded', html_content, "Menu toggle should have aria-expanded")
            self.assertIn('aria-hidden', html_content, "Menu overlay should have aria-hidden")
            
            # Check for screen reader support
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            js_content = response.text
            
            # Check for screen reader announcements
            self.assertIn('announceToScreenReader', js_content, "Should have screen reader announcement function")
            self.assertIn('aria-live', js_content, "Should use aria-live for announcements")
            
            # Check for focus management
            self.assertIn('focus()', js_content, "Should manage focus for accessibility")
            self.assertIn('trapFocus', js_content, "Should trap focus within menu")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_cross_section_navigation_integration(self):
        """Test that cross-section navigation integration works."""
        try:
            # Check for navigation state manager
            response = self.session.get(f"{self.base_url}/static/js/navigation-state-manager.js")
            
            # If navigation state manager exists, test it
            if response.status_code == 200:
                js_content = response.text
                
                # Check for NavigationStateManager class
                self.assertIn('NavigationStateManager', js_content, "Should have NavigationStateManager class")
                
                # Check for cross-navigation methods
                self.assertIn('navigateToMusicianFromSong', js_content, "Should have navigateToMusicianFromSong method")
                self.assertIn('navigateToSongFromMusician', js_content, "Should have navigateToSongFromMusician method")
            
            # Check main app.js for cross-navigation functionality
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            self.assertEqual(response.status_code, 200)
            
            js_content = response.text
            
            # Check for cross-navigation methods in main classes
            self.assertIn('navigateToMusicianSelector', js_content, "Should have navigateToMusicianSelector method")
            self.assertIn('navigateToSongSelector', js_content, "Should have navigateToSongSelector method")
            
            # Check for session storage usage for preselection
            self.assertIn('sessionStorage', js_content, "Should use sessionStorage for preselection")
            self.assertIn('preselectedMusician', js_content, "Should handle preselected musician")
            self.assertIn('preselectedSong', js_content, "Should handle preselected song")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")
    
    def test_menu_state_synchronization(self):
        """Test that menu state synchronization works correctly."""
        try:
            # Check main JavaScript file for menu state synchronization
            response = self.session.get(f"{self.base_url}/static/js/app.js")
            self.assertEqual(response.status_code, 200)
            
            js_content = response.text
            
            # Check for menu state synchronization methods
            self.assertIn('updateActiveMenuItem', js_content, "Should have updateActiveMenuItem method")
            self.assertIn('getCurrentSection', js_content, "Should have getCurrentSection method")
            
            # Check for active class management
            self.assertIn("classList.add('active')", js_content, "Should add active class")
            self.assertIn("classList.remove('active')", js_content, "Should remove active class")
            
            # Check for aria-current attribute management
            self.assertIn('aria-current', js_content, "Should manage aria-current attribute")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Application server not running")


if __name__ == '__main__':
    unittest.main()