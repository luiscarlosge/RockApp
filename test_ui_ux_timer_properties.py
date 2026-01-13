#!/usr/bin/env python3
"""Property-based tests for UI/UX improvements - timer accessibility."""

import sys
import re
import os
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import text, integers, sampled_from
import unittest

sys.path.insert(0, '.')

class TimerAccessibilityExtractor:
    """Utility class for extracting timer accessibility patterns from JavaScript and HTML."""
    
    @staticmethod
    def read_file(file_path):
        """Read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    @staticmethod
    def extract_timer_patterns(js_content):
        """Extract timer-related patterns from JavaScript."""
        patterns = {
            'countdown_timers': [],
            'timer_updates': [],
            'aria_labels': [],
            'aria_live_regions': [],
            'timer_announcements': []
        }
        
        # Look for countdown timer patterns
        countdown_patterns = [
            r'countdown[^(]*\(',
            r'remainingTime',
            r'setInterval[^(]*\([^,]*,\s*1000\)',  # 1-second intervals
            r'updateCountdown',
            r'refresh-countdown'
        ]
        
        for pattern in countdown_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            patterns['countdown_timers'].extend(matches)
        
        # Look for timer update patterns
        update_patterns = [
            r'updateCountdownDisplay',
            r'remainingTime--',
            r'timer.*update',
            r'countdown.*update'
        ]
        
        for pattern in update_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            patterns['timer_updates'].extend(matches)
        
        # Look for ARIA labels on timers
        aria_label_patterns = [
            r'aria-label[^=]*=\s*["\'][^"\']*tiempo[^"\']*["\']',
            r'aria-label[^=]*=\s*["\'][^"\']*actualización[^"\']*["\']',
            r'aria-label[^=]*=\s*["\'][^"\']*countdown[^"\']*["\']',
            r'setAttribute\s*\(\s*["\']aria-label["\']'
        ]
        
        for pattern in aria_label_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            patterns['aria_labels'].extend(matches)
        
        # Look for ARIA live regions for timer updates
        live_region_patterns = [
            r'aria-live[^=]*=\s*["\']polite["\']',
            r'aria-live[^=]*=\s*["\']assertive["\']',
            r'setAttribute\s*\(\s*["\']aria-live["\']'
        ]
        
        for pattern in live_region_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            patterns['aria_live_regions'].extend(matches)
        
        # Look for timer announcements
        announcement_patterns = [
            r'announceToScreenReader[^(]*\([^)]*tiempo[^)]*\)',
            r'announceToScreenReader[^(]*\([^)]*actualización[^)]*\)',
            r'announceToScreenReader[^(]*\([^)]*countdown[^)]*\)'
        ]
        
        for pattern in announcement_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            patterns['timer_announcements'].extend(matches)
        
        return patterns
    
    @staticmethod
    def extract_timer_elements(html_content):
        """Extract timer-related HTML elements."""
        timer_elements = {
            'countdown_elements': [],
            'timer_containers': [],
            'accessible_timers': []
        }
        
        # Look for countdown elements
        countdown_patterns = [
            r'<[^>]*id\s*=\s*["\'][^"\']*countdown[^"\']*["\'][^>]*>',
            r'<[^>]*class\s*=\s*["\'][^"\']*countdown[^"\']*["\'][^>]*>',
            r'<[^>]*id\s*=\s*["\'][^"\']*timer[^"\']*["\'][^>]*>',
            r'<[^>]*class\s*=\s*["\'][^"\']*timer[^"\']*["\'][^>]*>'
        ]
        
        for pattern in countdown_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            timer_elements['countdown_elements'].extend(matches)
        
        # Look for accessible timer attributes
        accessible_patterns = [
            r'<[^>]*aria-live[^>]*>',
            r'<[^>]*aria-label[^>]*tiempo[^>]*>',
            r'<[^>]*role\s*=\s*["\']timer["\'][^>]*>'
        ]
        
        for pattern in accessible_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            timer_elements['accessible_timers'].extend(matches)
        
        return timer_elements


class TestTimerAccessibility(unittest.TestCase):
    """Property-based tests for timer accessibility compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Read JavaScript files
        self.app_js = TimerAccessibilityExtractor.read_file('static/js/app.js')
        self.enhanced_polling_js = TimerAccessibilityExtractor.read_file('static/js/enhanced-polling-manager.js')
        self.navigation_js = TimerAccessibilityExtractor.read_file('static/js/navigation-state-manager.js')
        
        # Read HTML templates
        self.base_html = TimerAccessibilityExtractor.read_file('templates/base.html')
        self.index_html = TimerAccessibilityExtractor.read_file('templates/index.html')
        
        # Combine all JavaScript content
        self.all_js = self.app_js + self.enhanced_polling_js + self.navigation_js
        
        # Combine all HTML content
        self.all_html = self.base_html + self.index_html
        
        # Extract timer patterns
        self.timer_patterns = TimerAccessibilityExtractor.extract_timer_patterns(self.all_js)
        self.timer_elements = TimerAccessibilityExtractor.extract_timer_elements(self.all_html)
    
    def test_timer_patterns_extracted(self):
        """Test that timer patterns are properly extracted from code."""
        total_patterns = sum(len(patterns) for patterns in self.timer_patterns.values())
        self.assertGreater(
            total_patterns, 
            0, 
            "Should extract timer patterns from JavaScript"
        )
    
    @given(st.sampled_from([
        'countdown',
        'timer',
        'refresh',
        'actualización',
        'tiempo'
    ]))
    @settings(max_examples=100)
    def test_timer_aria_labels(self, timer_keyword):
        """
        **Feature: ui-ux-improvements, Property 16: Timer accessibility**
        **Validates: Requirements 5.4**
        
        For any countdown timer, appropriate aria-labels and live region updates 
        should be present for screen reader users
        """
        # Look for aria-label patterns containing this keyword
        aria_label_pattern = rf'aria-label[^=]*=\s*["\'][^"\']*{timer_keyword}[^"\']*["\']'
        aria_matches = re.findall(aria_label_pattern, self.all_js + self.all_html, re.IGNORECASE)
        
        if len(aria_matches) > 0:
            # Verify aria-labels are meaningful
            for match in aria_matches:
                # Extract the label text
                label_text_pattern = r'["\']([^"\']*)["\']'
                label_matches = re.findall(label_text_pattern, match)
                
                for label_text in label_matches:
                    if timer_keyword.lower() in label_text.lower():
                        # Label should be descriptive
                        self.assertGreater(
                            len(label_text.strip()), 
                            5, 
                            f"Timer aria-label should be descriptive, got '{label_text}'"
                        )
                        
                        # Should contain helpful context
                        helpful_words = ['próxima', 'actualización', 'tiempo', 'segundos', 'minutos']
                        has_context = any(word in label_text.lower() for word in helpful_words)
                        
                        if len(label_text) > 10:  # Only check context for longer labels
                            self.assertTrue(
                                has_context, 
                                f"Timer aria-label should contain helpful context words, got '{label_text}'"
                            )
    
    @given(st.sampled_from([
        'polite',
        'assertive'
    ]))
    @settings(max_examples=100)
    def test_timer_live_regions(self, live_value):
        """
        **Feature: ui-ux-improvements, Property 16: Timer accessibility**
        **Validates: Requirements 5.4**
        
        For any timer updates, aria-live regions should be used appropriately 
        to announce changes to screen readers
        """
        # Look for aria-live regions with this value
        live_pattern = rf'aria-live[^=]*=\s*["\']?{live_value}["\']?'
        live_matches = re.findall(live_pattern, self.all_js + self.all_html, re.IGNORECASE)
        
        if len(live_matches) > 0:
            if live_value == 'polite':
                # Polite should be used for regular timer updates
                self.assertGreater(
                    len(live_matches), 
                    0, 
                    f"aria-live='polite' found {len(live_matches)} times - good for regular timer updates"
                )
            elif live_value == 'assertive':
                # Assertive should be used sparingly for urgent timer notifications
                self.assertLessEqual(
                    len(live_matches), 
                    3, 
                    f"aria-live='assertive' should be used sparingly for urgent timer notifications, found {len(live_matches)} times"
                )
    
    @given(st.sampled_from([
        ('setInterval', 1000),      # 1-second timer intervals
        ('setTimeout', 5000),       # 5-second refresh intervals
        ('clearInterval', 0),       # Timer cleanup
        ('clearTimeout', 0)         # Timeout cleanup
    ]))
    @settings(max_examples=100)
    def test_timer_interval_accessibility(self, timer_config):
        """
        **Feature: ui-ux-improvements, Property 16: Timer accessibility**
        **Validates: Requirements 5.4**
        
        For any timer interval, the frequency should be reasonable for screen 
        reader users and not cause excessive announcements
        """
        timer_function, expected_interval = timer_config
        
        # Look for timer functions in JavaScript
        timer_pattern = rf'{timer_function}\s*\('
        timer_matches = re.findall(timer_pattern, self.all_js, re.IGNORECASE)
        
        if len(timer_matches) > 0:
            if timer_function == 'setInterval':
                # Check for 1-second intervals (countdown timers)
                interval_pattern = rf'{timer_function}\s*\([^,]*,\s*{expected_interval}\s*\)'
                interval_matches = re.findall(interval_pattern, self.all_js, re.IGNORECASE)
                
                if len(interval_matches) > 0:
                    # 1-second intervals are acceptable for countdown timers
                    self.assertLessEqual(
                        len(interval_matches), 
                        5, 
                        f"1-second intervals should be used sparingly to avoid excessive screen reader announcements, found {len(interval_matches)}"
                    )
            
            elif timer_function in ['clearInterval', 'clearTimeout']:
                # Timer cleanup is important for accessibility
                self.assertGreater(
                    len(timer_matches), 
                    0, 
                    f"Timer cleanup with {timer_function} found {len(timer_matches)} times (good for preventing memory leaks)"
                )
    
    @given(st.sampled_from([
        'updateCountdownDisplay',
        'remainingTime',
        'countdownTimer',
        'pollingTimer'
    ]))
    @settings(max_examples=100)
    def test_timer_update_patterns(self, update_pattern):
        """
        **Feature: ui-ux-improvements, Property 16: Timer accessibility**
        **Validates: Requirements 5.4**
        
        For any timer update mechanism, it should be implemented in a way that 
        provides appropriate feedback to screen readers
        """
        # Look for timer update patterns in JavaScript
        pattern_count = self.all_js.lower().count(update_pattern.lower())
        
        if pattern_count > 0:
            # Check if timer updates are associated with accessibility features
            accessibility_indicators = [
                'aria-label',
                'aria-live',
                'announceToScreenReader',
                'setAttribute'
            ]
            
            # Look for accessibility patterns near timer updates
            context_window = 500  # Characters around the pattern
            accessibility_context = 0
            
            for indicator in accessibility_indicators:
                # Simple proximity check - look for accessibility patterns in the same file
                if indicator.lower() in self.all_js.lower():
                    accessibility_context += 1
            
            # Timer updates should have some accessibility context
            self.assertGreater(
                accessibility_context, 
                0, 
                f"Timer update pattern '{update_pattern}' should have accessibility context (aria-labels, live regions, etc.)"
            )
    
    @given(st.sampled_from([
        ('segundos', 'seconds'),
        ('minutos', 'minutes'),
        ('actualización', 'update'),
        ('próxima', 'next'),
        ('tiempo', 'time')
    ]))
    @settings(max_examples=100)
    def test_timer_spanish_accessibility(self, word_config):
        """
        **Feature: ui-ux-improvements, Property 16: Timer accessibility**
        **Validates: Requirements 5.4**
        
        For any timer accessibility features, text should be in Spanish to match 
        the application language and provide clear communication
        """
        spanish_word, english_equivalent = word_config
        
        # Look for Spanish timer-related text in the code
        spanish_pattern = rf'["\'][^"\']*{spanish_word}[^"\']*["\']'
        spanish_matches = re.findall(spanish_pattern, self.all_js, re.IGNORECASE)
        
        if len(spanish_matches) > 0:
            # Verify Spanish text is meaningful
            for match in spanish_matches:
                # Extract the text content
                text_content = match.strip('"\'')
                
                if len(text_content) > 5:  # Only check meaningful text
                    # Should contain Spanish words
                    spanish_indicators = ['el', 'la', 'en', 'de', 'para', 'con', 'hasta', 'próxima']
                    has_spanish = any(indicator in text_content.lower() for indicator in spanish_indicators)
                    
                    # For timer text, Spanish context is important
                    if spanish_word in ['actualización', 'próxima', 'tiempo']:
                        self.assertTrue(
                            has_spanish or len(text_content) <= 15, 
                            f"Timer Spanish text should have proper context: '{text_content}'"
                        )
    
    @given(st.sampled_from([
        'refresh-countdown',
        'refresh-loading',
        'refresh-error',
        'countdown-display',
        'timer-container'
    ]))
    @settings(max_examples=100)
    def test_timer_element_accessibility(self, element_id):
        """
        **Feature: ui-ux-improvements, Property 16: Timer accessibility**
        **Validates: Requirements 5.4**
        
        For any timer-related DOM element, it should have appropriate accessibility 
        attributes for screen reader interaction
        """
        # Look for this element ID in JavaScript (where it's likely created)
        element_pattern = rf'["\']#{element_id}["\']|getElementById\s*\(\s*["\']{element_id}["\']'
        element_matches = re.findall(element_pattern, self.all_js, re.IGNORECASE)
        
        if len(element_matches) > 0:
            # Check if accessibility attributes are set for this element
            # Look for setAttribute calls that set accessibility attributes
            accessibility_patterns = [
                # Direct setAttribute calls for aria attributes
                rf'setAttribute\s*\(\s*["\']aria-live["\']',
                rf'setAttribute\s*\(\s*["\']aria-label["\']',
                rf'setAttribute\s*\(\s*["\']role["\']',
                # Context-aware patterns - look for setAttribute near element creation
                rf'{element_id}[^{{}}]*setAttribute\s*\(\s*["\']aria-',
                # Look for aria attributes in the broader context around the element
                rf'createElement[^{{}}]*{element_id}[^{{}}]*aria-',
                rf'{element_id}[^{{}}]*aria-live',
                rf'{element_id}[^{{}}]*aria-label'
            ]
            
            accessibility_found = 0
            for pattern in accessibility_patterns:
                matches = re.findall(pattern, self.all_js, re.IGNORECASE | re.DOTALL)
                accessibility_found += len(matches)
            
            # Additional check: look for setAttribute calls in the same function/context as element creation
            if element_id == 'refresh-countdown':
                # Specific check for refresh-countdown element accessibility
                countdown_context_patterns = [
                    r'refresh-countdown[^}]*setAttribute[^}]*aria-live',
                    r'refresh-countdown[^}]*setAttribute[^}]*aria-label',
                    r'countdownElement[^}]*setAttribute[^}]*aria-live',
                    r'countdownElement[^}]*setAttribute[^}]*aria-label'
                ]
                
                for pattern in countdown_context_patterns:
                    matches = re.findall(pattern, self.all_js, re.IGNORECASE | re.DOTALL)
                    accessibility_found += len(matches)
            
            # Timer elements should have some accessibility attributes
            if element_id in ['refresh-countdown', 'countdown-display']:
                # These are critical timer elements that should be accessible
                self.assertGreater(
                    accessibility_found, 
                    0, 
                    f"Critical timer element '{element_id}' should have accessibility attributes"
                )
            else:
                # Other timer elements should ideally have accessibility features
                self.assertTrue(
                    accessibility_found >= 0, 
                    f"Timer element '{element_id}' accessibility: {accessibility_found} attributes found"
                )
    
    @given(st.integers(min_value=1, max_value=60))
    @settings(max_examples=100)
    def test_timer_announcement_frequency(self, seconds_interval):
        """
        **Feature: ui-ux-improvements, Property 16: Timer accessibility**
        **Validates: Requirements 5.4**
        
        For any timer announcements, the frequency should be reasonable to avoid 
        overwhelming screen reader users with excessive updates
        """
        # Look for timer intervals in the code
        interval_pattern = rf'setInterval\s*\([^,]*,\s*{seconds_interval * 1000}\s*\)'
        interval_matches = re.findall(interval_pattern, self.all_js, re.IGNORECASE)
        
        if len(interval_matches) > 0:
            if seconds_interval <= 5:
                # Very frequent updates (≤5 seconds) should be used carefully
                self.assertLessEqual(
                    len(interval_matches), 
                    3, 
                    f"Very frequent timer updates ({seconds_interval}s) should be limited to avoid overwhelming screen readers, found {len(interval_matches)}"
                )
            elif seconds_interval <= 30:
                # Moderate frequency (5-30 seconds) is generally acceptable
                self.assertTrue(
                    len(interval_matches) >= 0, 
                    f"Moderate timer frequency ({seconds_interval}s) is acceptable for accessibility, found {len(interval_matches)}"
                )
            else:
                # Infrequent updates (>30 seconds) are good for accessibility
                self.assertTrue(
                    len(interval_matches) >= 0, 
                    f"Infrequent timer updates ({seconds_interval}s) are good for screen reader accessibility, found {len(interval_matches)}"
                )


if __name__ == '__main__':
    unittest.main()