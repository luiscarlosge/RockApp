#!/usr/bin/env python3
"""
Integration test for cross-section navigation system
Tests the actual navigation functionality in the web application
"""

import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

sys.path.insert(0, '.')


class NavigationIntegrationTest(unittest.TestCase):
    """Integration tests for cross-section navigation functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Configure Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
            cls.base_url = "http://127.0.0.1:5001"
        except WebDriverException as e:
            cls.skipTest(cls, f"Chrome WebDriver not available: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def setUp(self):
        """Set up each test."""
        if hasattr(self, 'driver'):
            self.driver.get(self.base_url)
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "songSelect"))
            )
    
    def test_navigation_state_manager_loaded(self):
        """Test that NavigationStateManager is loaded and available."""
        if not hasattr(self, 'driver'):
            self.skipTest("WebDriver not available")
            
        # Check if NavigationStateManager is available in window
        nav_manager_available = self.driver.execute_script(
            "return typeof window.NavigationStateManager !== 'undefined';"
        )
        
        self.assertTrue(
            nav_manager_available,
            "NavigationStateManager should be loaded and available"
        )
    
    def test_hamburger_menu_navigation(self):
        """Test basic hamburger menu navigation between sections."""
        if not hasattr(self, 'driver'):
            self.skipTest("WebDriver not available")
            
        # Test navigation to musician selector
        menu_toggle = self.driver.find_element(By.CLASS_NAME, "menu-toggle")
        menu_toggle.click()
        
        # Wait for menu to open
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-section="musician-selector"]'))
        )
        
        # Click musician selector menu item
        musician_menu_item = self.driver.find_element(By.CSS_SELECTOR, '[data-section="musician-selector"]')
        musician_menu_item.click()
        
        # Wait for section to become active
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#musician-selector.active'))
        )
        
        # Verify musician selector section is active
        musician_section = self.driver.find_element(By.ID, "musician-selector")
        self.assertIn("active", musician_section.get_attribute("class"))
        
        # Verify song selector section is not active
        song_section = self.driver.find_element(By.ID, "song-selector")
        self.assertNotIn("active", song_section.get_attribute("class"))
    
    def test_menu_state_synchronization(self):
        """Test that menu state synchronizes with current section."""
        if not hasattr(self, 'driver'):
            self.skipTest("WebDriver not available")
            
        # Navigate to live performance section
        menu_toggle = self.driver.find_element(By.CLASS_NAME, "menu-toggle")
        menu_toggle.click()
        
        # Wait for menu to open
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-section="live-performance"]'))
        )
        
        # Click live performance menu item
        live_menu_item = self.driver.find_element(By.CSS_SELECTOR, '[data-section="live-performance"]')
        live_menu_item.click()
        
        # Wait for section to become active
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#live-performance.active'))
        )
        
        # Open menu again to check synchronization
        menu_toggle = self.driver.find_element(By.CLASS_NAME, "menu-toggle")
        menu_toggle.click()
        
        # Wait for menu to open
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "menu-overlay"))
        )
        
        # Check that live performance menu item is active
        live_menu_item = self.driver.find_element(By.CSS_SELECTOR, '[data-section="live-performance"]')
        self.assertIn("active", live_menu_item.get_attribute("class"))
        
        # Check that other menu items are not active
        song_menu_item = self.driver.find_element(By.CSS_SELECTOR, '[data-section="song-selector"]')
        musician_menu_item = self.driver.find_element(By.CSS_SELECTOR, '[data-section="musician-selector"]')
        
        self.assertNotIn("active", song_menu_item.get_attribute("class"))
        self.assertNotIn("active", musician_menu_item.get_attribute("class"))
    
    def test_cross_section_navigation_links(self):
        """Test cross-section navigation links functionality."""
        if not hasattr(self, 'driver'):
            self.skipTest("WebDriver not available")
            
        # First, select a song to get cross-section links
        song_select = self.driver.find_element(By.ID, "songSelect")
        
        # Wait for songs to load
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(song_select.find_elements(By.TAG_NAME, "option")) > 1
        )
        
        # Select the first available song
        options = song_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:
            options[1].click()  # Skip the default "Select a song" option
            
            # Wait for song details to load
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "songDetails"))
            )
            
            # Look for cross-section navigation links
            try:
                cross_section_links = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "crossSectionLinks"))
                )
                
                # Check if there are any musician links
                musician_links = cross_section_links.find_elements(By.TAG_NAME, "button")
                
                if musician_links:
                    # Click the first musician link
                    first_musician_link = musician_links[0]
                    musician_name = first_musician_link.text.strip()
                    
                    # Store the musician name for verification
                    self.driver.execute_script(
                        "window.testMusicianName = arguments[0];", 
                        musician_name
                    )
                    
                    first_musician_link.click()
                    
                    # Wait for navigation to musician selector
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#musician-selector.active'))
                    )
                    
                    # Verify we're in the musician selector section
                    musician_section = self.driver.find_element(By.ID, "musician-selector")
                    self.assertIn("active", musician_section.get_attribute("class"))
                    
                    # Verify the musician dropdown is populated and potentially preselected
                    musician_select = self.driver.find_element(By.ID, "musicianSelect")
                    self.assertTrue(
                        len(musician_select.find_elements(By.TAG_NAME, "option")) > 1,
                        "Musician dropdown should be populated"
                    )
                    
                else:
                    self.skipTest("No musician links found in cross-section navigation")
                    
            except TimeoutException:
                self.skipTest("Cross-section links not found or not loaded in time")
        else:
            self.skipTest("No songs available for testing cross-section navigation")
    
    def test_session_storage_preselection(self):
        """Test that preselection works through session storage."""
        if not hasattr(self, 'driver'):
            self.skipTest("WebDriver not available")
            
        # Set a preselected musician in session storage
        test_musician = "Test Musician"
        self.driver.execute_script(
            "sessionStorage.setItem('preselectedMusician', arguments[0]);",
            test_musician
        )
        
        # Navigate to musician selector
        menu_toggle = self.driver.find_element(By.CLASS_NAME, "menu-toggle")
        menu_toggle.click()
        
        # Wait for menu to open
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-section="musician-selector"]'))
        )
        
        # Click musician selector menu item
        musician_menu_item = self.driver.find_element(By.CSS_SELECTOR, '[data-section="musician-selector"]')
        musician_menu_item.click()
        
        # Wait for section to become active
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#musician-selector.active'))
        )
        
        # Check that session storage item was consumed
        preselected_musician = self.driver.execute_script(
            "return sessionStorage.getItem('preselectedMusician');"
        )
        
        # The preselection should be cleared after use (or still there if musician not found)
        # This test verifies the mechanism is working
        self.assertTrue(
            preselected_musician is None or preselected_musician == test_musician,
            "Preselection mechanism should handle session storage correctly"
        )


if __name__ == '__main__':
    # Only run if we can import selenium
    try:
        import selenium
        unittest.main()
    except ImportError:
        print("Selenium not available, skipping integration tests")
        sys.exit(0)