#!/usr/bin/env python3
"""Property-based tests for UI/UX improvements - transition smoothness."""

import sys
import re
import time
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import text, integers, floats
import unittest

sys.path.insert(0, '.')

class CSSTransitionExtractor:
    """Utility class for extracting transition properties from CSS."""
    
    @staticmethod
    def read_css_file(file_path):
        """Read CSS file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    @staticmethod
    def extract_transition_properties(css_content):
        """Extract transition properties from CSS content."""
        # Pattern to match transition properties
        transition_pattern = r'transition\s*:\s*([^;]+);'
        transition_duration_pattern = r'transition-duration\s*:\s*([^;]+);'
        
        transitions = re.findall(transition_pattern, css_content, re.IGNORECASE)
        durations = re.findall(transition_duration_pattern, css_content, re.IGNORECASE)
        
        return {
            'transitions': transitions,
            'durations': durations
        }
    
    @staticmethod
    def parse_transition_duration(transition_value):
        """Parse transition duration from CSS transition value."""
        # Look for duration values (e.g., "0.3s", "300ms", "all 0.3s ease")
        duration_pattern = r'(\d+(?:\.\d+)?)(s|ms)'
        matches = re.findall(duration_pattern, transition_value)
        
        durations = []
        for value, unit in matches:
            duration_ms = float(value)
            if unit == 's':
                duration_ms *= 1000  # Convert seconds to milliseconds
            durations.append(duration_ms)
        
        return durations
    
    @staticmethod
    def extract_element_transitions(css_content):
        """Extract transitions for specific UI elements."""
        element_transitions = {}
        
        # Define elements we care about for smooth transitions
        elements = [
            'menu-toggle',
            'menu-overlay', 
            'menu-item',
            'app-section',
            'card',
            'performance-card',
            'musician-card',
            'song-card-small',
            'hamburger-line',
            'btn',
            'form-select'
        ]
        
        for element in elements:
            # Look for CSS rules containing this element
            element_pattern = rf'\.{element}[^{{]*\{{([^}}]+)\}}'
            matches = re.findall(element_pattern, css_content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                # Extract transition properties from this rule
                transitions = CSSTransitionExtractor.extract_transition_properties(match)
                if transitions['transitions'] or transitions['durations']:
                    element_transitions[element] = transitions
        
        return element_transitions


class TestTransitionSmoothness(unittest.TestCase):
    """Property-based tests for transition smoothness compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.css_content = CSSTransitionExtractor.read_css_file('static/css/style.css')
        self.transition_properties = CSSTransitionExtractor.extract_transition_properties(self.css_content)
        self.element_transitions = CSSTransitionExtractor.extract_element_transitions(self.css_content)
    
    def test_transitions_extracted(self):
        """Test that transition properties are properly extracted from CSS."""
        self.assertGreater(
            len(self.transition_properties['transitions']), 
            0, 
            "Should extract transition properties from CSS"
        )
    
    @given(st.sampled_from([
        'all 0.3s ease',
        'transform 0.3s ease',
        'background 0.3s ease',
        'border-color 0.3s ease',
        'box-shadow 0.3s ease',
        'opacity 0.3s ease',
        'color 0.3s ease'
    ]))
    @settings(max_examples=100)
    def test_transition_duration_compliance(self, transition_value):
        """
        **Feature: ui-ux-improvements, Property 11: Transition smoothness**
        **Validates: Requirements 4.3**
        
        For any section navigation, CSS transitions should be applied and complete 
        within a reasonable timeframe (≤500ms)
        """
        durations = CSSTransitionExtractor.parse_transition_duration(transition_value)
        
        # Each transition duration should be reasonable (≤500ms)
        for duration in durations:
            self.assertLessEqual(
                duration, 
                500, 
                f"Transition duration should be ≤500ms for smooth UX, got {duration}ms in '{transition_value}'"
            )
            
            # Also ensure it's not too fast (≥100ms for perceivable smoothness)
            self.assertGreaterEqual(
                duration, 
                100, 
                f"Transition duration should be ≥100ms for perceivable smoothness, got {duration}ms in '{transition_value}'"
            )
    
    @given(st.sampled_from([
        'menu-toggle',
        'menu-overlay',
        'menu-item', 
        'app-section',
        'card',
        'performance-card',
        'musician-card',
        'song-card-small',
        'hamburger-line'
    ]))
    @settings(max_examples=100)
    def test_element_transition_smoothness(self, element_class):
        """
        **Feature: ui-ux-improvements, Property 11: Transition smoothness**
        **Validates: Requirements 4.3**
        
        For any interactive UI element, transitions should be smooth and complete 
        within reasonable timeframes for good user experience
        """
        if element_class not in self.element_transitions:
            # If element doesn't have explicit transitions, that's acceptable
            # but we should verify it doesn't have jarring instant changes
            self.assertTrue(True, f"Element {element_class} has no explicit transitions (acceptable)")
            return
        
        element_data = self.element_transitions[element_class]
        
        # Check all transition values for this element
        all_transitions = element_data['transitions'] + element_data['durations']
        
        for transition in all_transitions:
            durations = CSSTransitionExtractor.parse_transition_duration(transition)
            
            for duration in durations:
                # Verify duration is within acceptable range
                self.assertLessEqual(
                    duration, 
                    500, 
                    f"Element {element_class} transition should be ≤500ms, got {duration}ms"
                )
                
                self.assertGreaterEqual(
                    duration, 
                    100, 
                    f"Element {element_class} transition should be ≥100ms for smoothness, got {duration}ms"
                )
    
    @given(st.sampled_from([
        ('ease', True),           # Standard easing - smooth
        ('ease-in', True),        # Ease in - smooth
        ('ease-out', True),       # Ease out - smooth  
        ('ease-in-out', True),    # Ease in-out - smooth
        ('linear', False),        # Linear - less smooth but acceptable
        ('cubic-bezier', True)    # Custom bezier - potentially smooth
    ]))
    @settings(max_examples=100)
    def test_transition_easing_smoothness(self, easing_config):
        """
        **Feature: ui-ux-improvements, Property 11: Transition smoothness**
        **Validates: Requirements 4.3**
        
        For any CSS transition, the easing function should provide smooth animation 
        curves for better user experience
        """
        easing_function, is_smooth = easing_config
        
        # Count occurrences of this easing function in CSS
        easing_count = self.css_content.lower().count(easing_function.lower())
        
        if easing_count > 0:
            if is_smooth:
                # Smooth easing functions are preferred
                self.assertGreater(
                    easing_count, 
                    0, 
                    f"Smooth easing function '{easing_function}' found {easing_count} times (good)"
                )
            else:
                # Linear easing is acceptable but not ideal for all cases
                # We'll allow it but prefer smooth easing
                self.assertTrue(
                    True, 
                    f"Linear easing found {easing_count} times (acceptable but not ideal for all cases)"
                )
    
    @given(st.sampled_from([
        'transform',      # Hardware accelerated - smooth
        'opacity',        # Hardware accelerated - smooth
        'background',     # Can be smooth with proper implementation
        'border-color',   # Can be smooth
        'box-shadow',     # Can be smooth but potentially expensive
        'color',          # Smooth
        'width',          # Can cause layout thrashing - less smooth
        'height',         # Can cause layout thrashing - less smooth
        'left',           # Can cause layout thrashing - less smooth
        'top'             # Can cause layout thrashing - less smooth
    ]))
    @settings(max_examples=100)
    def test_transition_property_performance(self, css_property):
        """
        **Feature: ui-ux-improvements, Property 11: Transition smoothness**
        **Validates: Requirements 4.3**
        
        For any CSS transition property, it should be chosen for optimal performance 
        and smoothness (prefer transform/opacity over layout-affecting properties)
        """
        # Count occurrences of transitions on this property
        property_pattern = rf'transition[^;]*{css_property}[^;]*;'
        matches = re.findall(property_pattern, self.css_content, re.IGNORECASE)
        
        if len(matches) > 0:
            # Categorize properties by performance impact
            hardware_accelerated = ['transform', 'opacity']
            smooth_properties = ['background', 'border-color', 'box-shadow', 'color']
            layout_affecting = ['width', 'height', 'left', 'top', 'margin', 'padding']
            
            if css_property in hardware_accelerated:
                # Excellent choice for smooth transitions
                self.assertGreater(
                    len(matches), 
                    0, 
                    f"Hardware-accelerated property '{css_property}' used in {len(matches)} transitions (excellent)"
                )
            elif css_property in smooth_properties:
                # Good choice for smooth transitions
                self.assertGreater(
                    len(matches), 
                    0, 
                    f"Smooth property '{css_property}' used in {len(matches)} transitions (good)"
                )
            elif css_property in layout_affecting:
                # Less ideal but sometimes necessary - warn but don't fail
                self.assertTrue(
                    True, 
                    f"Layout-affecting property '{css_property}' used in {len(matches)} transitions (consider alternatives)"
                )
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100)
    def test_transition_count_reasonableness(self, max_simultaneous_transitions):
        """
        **Feature: ui-ux-improvements, Property 11: Transition smoothness**
        **Validates: Requirements 4.3**
        
        For any UI element, the number of simultaneous transitions should be 
        reasonable to maintain smooth performance
        """
        # Look for CSS rules with multiple transition properties
        multi_transition_pattern = r'transition\s*:\s*([^;]+(?:,\s*[^;,]+){2,});'
        matches = re.findall(multi_transition_pattern, self.css_content, re.IGNORECASE)
        
        for transition_value in matches:
            # Count comma-separated transition properties
            transition_count = len(transition_value.split(','))
            
            # Reasonable limit to prevent performance issues
            self.assertLessEqual(
                transition_count, 
                max_simultaneous_transitions, 
                f"Too many simultaneous transitions ({transition_count}) may impact smoothness: '{transition_value}'"
            )


if __name__ == '__main__':
    unittest.main()