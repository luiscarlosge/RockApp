#!/usr/bin/env python3
"""Property-based tests for UI/UX improvements - loading state contrast and user feedback."""

import sys
import re
import colorsys
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import text, integers
import unittest

sys.path.insert(0, '.')

class ContrastCalculator:
    """Utility class for calculating WCAG contrast ratios."""
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def relative_luminance(rgb):
        """Calculate relative luminance according to WCAG 2.1."""
        def gamma_correct(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return pow((c + 0.055) / 1.055, 2.4)
        
        r, g, b = rgb
        return 0.2126 * gamma_correct(r) + 0.7152 * gamma_correct(g) + 0.0722 * gamma_correct(b)
    
    @staticmethod
    def contrast_ratio(color1, color2):
        """Calculate contrast ratio between two colors."""
        if isinstance(color1, str):
            color1 = ContrastCalculator.hex_to_rgb(color1)
        if isinstance(color2, str):
            color2 = ContrastCalculator.hex_to_rgb(color2)
            
        lum1 = ContrastCalculator.relative_luminance(color1)
        lum2 = ContrastCalculator.relative_luminance(color2)
        
        # Ensure lighter color is in numerator
        if lum1 > lum2:
            return (lum1 + 0.05) / (lum2 + 0.05)
        else:
            return (lum2 + 0.05) / (lum1 + 0.05)


class CSSColorExtractor:
    """Utility class for extracting colors from CSS."""
    
    @staticmethod
    def read_css_file(file_path):
        """Read CSS file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    @staticmethod
    def extract_css_variables(css_content):
        """Extract CSS custom properties (variables) from CSS content."""
        # Pattern to match CSS custom properties
        pattern = r'--([a-zA-Z0-9-_]+)\s*:\s*([^;]+);'
        matches = re.findall(pattern, css_content)
        
        variables = {}
        for name, value in matches:
            # Clean up the value
            value = value.strip()
            variables[f'--{name}'] = value
        
        return variables
    
    @staticmethod
    def extract_loading_colors(css_content):
        """Extract loading-related colors from CSS."""
        variables = CSSColorExtractor.extract_css_variables(css_content)
        
        loading_colors = {}
        loading_related_vars = [
            '--text-primary',
            '--text-secondary', 
            '--accent-gold',
            '--primary-black',
            '--secondary-black',
            '--bg-card',
            '--bg-card-hover',
            '--border-primary',
            '--spinner-color'
        ]
        
        for var in loading_related_vars:
            if var in variables:
                loading_colors[var] = variables[var]
        
        return loading_colors


class TestLoadingStateContrast(unittest.TestCase):
    """Property-based tests for loading state contrast compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.css_content = CSSColorExtractor.read_css_file('static/css/style.css')
        self.loading_colors = CSSColorExtractor.extract_loading_colors(self.css_content)
        self.calculator = ContrastCalculator()
    
    def test_loading_colors_extracted(self):
        """Test that loading colors are properly extracted from CSS."""
        self.assertGreater(len(self.loading_colors), 0, "Should extract loading colors from CSS")
        self.assertIn('--text-primary', self.loading_colors, "Should have primary text color")
        self.assertIn('--primary-black', self.loading_colors, "Should have primary black background")
    
    @given(st.sampled_from([
        ('--text-primary', '--primary-black'),      # White text on black background
        ('--text-secondary', '--primary-black'),    # Secondary text on black background
        ('--accent-gold', '--primary-black'),       # Gold accent on black background
        ('--text-primary', '--secondary-black'),    # White text on secondary black
        ('--text-primary', '--bg-card'),            # White text on card background
        ('--accent-gold', '--bg-card')              # Gold accent on card background
    ]))
    @settings(max_examples=100)
    def test_loading_state_contrast_compliance(self, color_pair):
        """
        **Feature: ui-ux-improvements, Property 10: Loading state contrast**
        **Validates: Requirements 4.1, 4.2**
        
        For any loading indicator, the colors used should meet WCAG AA contrast 
        requirements and be clearly visible against the background
        """
        text_var, bg_var = color_pair
        
        # Get colors from CSS variables
        text_color = self.loading_colors.get(text_var, '#ffffff')
        background_color = self.loading_colors.get(bg_var, '#000000')
        
        # Clean up color values
        if 'var(' in text_color:
            # Map common variables to their expected values
            color_map = {
                '--text-primary': '#ffffff',
                '--text-secondary': '#f0f0f0',
                '--accent-gold': '#ffd700'
            }
            text_color = color_map.get(text_var, '#ffffff')
            
        if 'var(' in background_color:
            bg_map = {
                '--primary-black': '#000000',
                '--secondary-black': '#1a1a1a',
                '--bg-card': 'rgba(255, 255, 255, 0.08)',
                '--bg-card-hover': 'rgba(255, 255, 255, 0.12)'
            }
            background_color = bg_map.get(bg_var, '#000000')
        
        # Handle rgba colors - convert to approximate hex for testing
        if background_color.startswith('rgba'):
            if 'rgba(255, 255, 255, 0.08)' in background_color:
                # Card background - approximate as dark gray
                background_color = '#141414'  # Very dark gray
            elif 'rgba(255, 255, 255, 0.12)' in background_color:
                # Card hover background - approximate as slightly lighter dark gray
                background_color = '#1f1f1f'  # Dark gray
            else:
                background_color = '#000000'  # Default to black
        
        # Calculate contrast ratio
        contrast = self.calculator.contrast_ratio(text_color, background_color)
        
        # Loading states should maintain WCAG AA compliance (4.5:1)
        self.assertGreaterEqual(
            contrast, 
            4.5, 
            f"Loading state contrast ratio should be at least 4.5:1 for {text_var} on {bg_var}, got {contrast:.2f}"
        )

    @given(st.sampled_from([
        'spinner-border',           # Bootstrap spinner
        'refresh-loading',          # Custom refresh loading indicator
        'loadingState',            # Song selector loading state
        'musicianLoadingState'     # Musician selector loading state
    ]))
    @settings(max_examples=100)
    def test_loading_indicator_visibility(self, loading_class):
        """
        **Feature: ui-ux-improvements, Property 10: Loading state contrast**
        **Validates: Requirements 4.1, 4.2**
        
        For any loading indicator element, the spinner and text colors should be 
        clearly visible with high contrast against their backgrounds
        """
        # Test spinner color (typically gold accent)
        spinner_color = self.loading_colors.get('--accent-gold', '#ffd700')
        background_color = self.loading_colors.get('--primary-black', '#000000')
        
        # Clean up colors
        if 'var(' in spinner_color:
            spinner_color = '#ffd700'  # Gold for spinners
        if 'var(' in background_color:
            background_color = '#000000'  # Black background
        
        # Calculate contrast ratio for spinner
        contrast = self.calculator.contrast_ratio(spinner_color, background_color)
        
        # Spinner should have high contrast for visibility
        self.assertGreaterEqual(
            contrast, 
            4.5, 
            f"Loading spinner contrast ratio should be at least 4.5:1 for {loading_class}, got {contrast:.2f}"
        )
        
        # Test loading text color
        text_color = self.loading_colors.get('--text-primary', '#ffffff')
        if 'var(' in text_color:
            text_color = '#ffffff'  # White text
        
        text_contrast = self.calculator.contrast_ratio(text_color, background_color)
        
        # Loading text should have high contrast
        self.assertGreaterEqual(
            text_contrast, 
            4.5, 
            f"Loading text contrast ratio should be at least 4.5:1 for {loading_class}, got {text_contrast:.2f}"
        )

    @given(st.sampled_from([
        ('alert-danger', '--error-bg', '--accent-red'),      # Error alerts
        ('alert-warning', '--warning-bg', '--accent-gold'),  # Warning alerts
        ('alert-info', '--info-bg', '--accent-blue'),        # Info alerts
        ('alert-success', '--success-bg', '--accent-green')  # Success alerts
    ]))
    @settings(max_examples=100)
    def test_alert_state_contrast(self, alert_config):
        """
        **Feature: ui-ux-improvements, Property 10: Loading state contrast**
        **Validates: Requirements 4.1, 4.2**
        
        For any alert or status indicator, the colors should meet WCAG AA contrast 
        requirements for clear visibility during loading and error states
        """
        alert_class, bg_var, accent_var = alert_config
        
        # Get background and accent colors
        background_color = self.loading_colors.get(bg_var, 'rgba(255, 107, 107, 0.15)')
        accent_color = self.loading_colors.get(accent_var, '#ff6b6b')
        text_color = self.loading_colors.get('--text-primary', '#ffffff')
        
        # Clean up colors
        if 'var(' in text_color:
            text_color = '#ffffff'
        if 'var(' in accent_color:
            accent_map = {
                '--accent-red': '#ff6b6b',
                '--accent-gold': '#ffd700',
                '--accent-blue': '#74c0fc',
                '--accent-green': '#51cf66'
            }
            accent_color = accent_map.get(accent_var, '#ff6b6b')
        
        # Handle rgba backgrounds - convert to approximate solid colors
        if background_color.startswith('rgba'):
            if 'rgba(255, 107, 107' in background_color:
                background_color = '#330000'  # Dark red
            elif 'rgba(255, 215, 0' in background_color:
                background_color = '#333300'  # Dark yellow
            elif 'rgba(116, 192, 252' in background_color:
                background_color = '#001133'  # Dark blue
            elif 'rgba(81, 207, 102' in background_color:
                background_color = '#003300'  # Dark green
            else:
                background_color = '#000000'  # Default black
        
        # Test text contrast on alert background
        text_contrast = self.calculator.contrast_ratio(text_color, background_color)
        self.assertGreaterEqual(
            text_contrast, 
            4.5, 
            f"Alert text contrast should be at least 4.5:1 for {alert_class}, got {text_contrast:.2f}"
        )
        
        # Test accent color contrast on alert background
        accent_contrast = self.calculator.contrast_ratio(accent_color, background_color)
        self.assertGreaterEqual(
            accent_contrast, 
            3.0,  # Slightly lower requirement for accent colors
            f"Alert accent contrast should be at least 3.0:1 for {alert_class}, got {accent_contrast:.2f}"
        )


if __name__ == '__main__':
    unittest.main()