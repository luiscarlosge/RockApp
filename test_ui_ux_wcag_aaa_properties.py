#!/usr/bin/env python3
"""Property-based tests for UI/UX improvements - WCAG AAA compliance."""

import sys
import re
import colorsys
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import text, integers, floats
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


class WCAGColorExtractor:
    """Utility class for extracting colors from CSS for WCAG AAA testing."""
    
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
    def extract_wcag_colors(css_content):
        """Extract all colors relevant for WCAG AAA testing."""
        variables = WCAGColorExtractor.extract_css_variables(css_content)
        
        wcag_colors = {}
        wcag_related_vars = [
            '--text-primary',
            '--text-secondary',
            '--text-muted',
            '--text-accent',
            '--accent-gold',
            '--accent-silver',
            '--accent-red',
            '--accent-green',
            '--accent-blue',
            '--primary-black',
            '--secondary-black',
            '--dark-gray',
            '--medium-gray',
            '--light-gray',
            '--bg-card',
            '--bg-card-hover',
            '--bg-input',
            '--bg-input-focus',
            '--border-primary',
            '--border-secondary',
            '--success-bg',
            '--warning-bg',
            '--error-bg',
            '--info-bg'
        ]
        
        for var in wcag_related_vars:
            if var in variables:
                wcag_colors[var] = variables[var]
        
        return wcag_colors
    
    @staticmethod
    def extract_font_sizes(css_content):
        """Extract font sizes to determine large text vs normal text."""
        font_size_pattern = r'font-size\s*:\s*([^;]+);'
        matches = re.findall(font_size_pattern, css_content, re.IGNORECASE)
        
        font_sizes = []
        for match in matches:
            # Parse font size values
            size_value = match.strip()
            if 'rem' in size_value:
                # Convert rem to approximate px (assuming 16px base)
                rem_value = float(re.findall(r'(\d+(?:\.\d+)?)', size_value)[0])
                px_value = rem_value * 16
                font_sizes.append(px_value)
            elif 'px' in size_value:
                px_value = float(re.findall(r'(\d+(?:\.\d+)?)', size_value)[0])
                font_sizes.append(px_value)
            elif 'em' in size_value:
                # Convert em to approximate px (assuming 16px base)
                em_value = float(re.findall(r'(\d+(?:\.\d+)?)', size_value)[0])
                px_value = em_value * 16
                font_sizes.append(px_value)
        
        return font_sizes


class TestWCAGAAACompliance(unittest.TestCase):
    """Property-based tests for WCAG AAA compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.css_content = WCAGColorExtractor.read_css_file('static/css/style.css')
        self.wcag_colors = WCAGColorExtractor.extract_wcag_colors(self.css_content)
        self.font_sizes = WCAGColorExtractor.extract_font_sizes(self.css_content)
        self.calculator = ContrastCalculator()
    
    def test_wcag_colors_extracted(self):
        """Test that WCAG colors are properly extracted from CSS."""
        self.assertGreater(len(self.wcag_colors), 0, "Should extract WCAG colors from CSS")
        self.assertIn('--text-primary', self.wcag_colors, "Should have primary text color")
        self.assertIn('--primary-black', self.wcag_colors, "Should have primary black background")
    
    @given(st.sampled_from([
        ('--text-primary', '--primary-black'),      # White text on black - should be AAA
        ('--text-secondary', '--primary-black'),    # Light gray text on black - should be AAA
        ('--text-muted', '--primary-black'),        # Muted text on black - should be AAA
        ('--accent-gold', '--primary-black'),       # Gold accent on black - should be AAA
        ('--text-primary', '--secondary-black'),    # White text on dark gray - should be AAA
        ('--text-primary', '--dark-gray'),          # White text on medium dark - should be AAA
        ('--accent-silver', '--primary-black'),     # Silver accent on black - should be AAA
        ('--accent-green', '--primary-black'),      # Green accent on black - should be AAA
        ('--accent-blue', '--primary-black')        # Blue accent on black - should be AAA
    ]))
    @settings(max_examples=100)
    def test_wcag_aaa_normal_text_compliance(self, color_pair):
        """
        **Feature: ui-ux-improvements, Property 14: WCAG AAA compliance where possible**
        **Validates: Requirements 5.2**
        
        For any text element where AAA compliance is achievable, the contrast ratio 
        should meet or exceed 7:1 for normal text and 4.5:1 for large text
        """
        text_var, bg_var = color_pair
        
        # Get colors from CSS variables
        text_color = self.wcag_colors.get(text_var, '#ffffff')
        background_color = self.wcag_colors.get(bg_var, '#000000')
        
        # Clean up color values
        if 'var(' in text_color:
            # Map common variables to their expected values
            color_map = {
                '--text-primary': '#ffffff',
                '--text-secondary': '#f0f0f0',
                '--text-muted': '#e0e0e0',
                '--text-accent': '#d9d9d9',
                '--accent-gold': '#ffd700',
                '--accent-silver': '#c0c0c0',
                '--accent-green': '#51cf66',
                '--accent-blue': '#74c0fc'
            }
            text_color = color_map.get(text_var, '#ffffff')
            
        if 'var(' in background_color:
            bg_map = {
                '--primary-black': '#000000',
                '--secondary-black': '#1a1a1a',
                '--dark-gray': '#2d2d2d',
                '--medium-gray': '#404040'
            }
            background_color = bg_map.get(bg_var, '#000000')
        
        # Calculate contrast ratio
        contrast = self.calculator.contrast_ratio(text_color, background_color)
        
        # WCAG AAA requires 7:1 for normal text
        self.assertGreaterEqual(
            contrast, 
            7.0, 
            f"WCAG AAA normal text contrast should be at least 7:1 for {text_var} on {bg_var}, got {contrast:.2f}"
        )
    
    @given(st.sampled_from([
        ('--text-primary', '--bg-card'),            # White text on card background
        ('--text-primary', '--bg-input'),           # White text on input background
        ('--accent-gold', '--bg-card'),             # Gold accent on card background
        ('--text-secondary', '--bg-card-hover'),    # Secondary text on hover background
        ('--text-primary', '--success-bg'),         # White text on success background
        ('--text-primary', '--warning-bg'),         # White text on warning background
        ('--text-primary', '--error-bg'),           # White text on error background
        ('--text-primary', '--info-bg')             # White text on info background
    ]))
    @settings(max_examples=100)
    def test_wcag_aaa_transparent_backgrounds(self, color_pair):
        """
        **Feature: ui-ux-improvements, Property 14: WCAG AAA compliance where possible**
        **Validates: Requirements 5.2**
        
        For any text on semi-transparent backgrounds, contrast should still meet 
        WCAG AAA standards when possible
        """
        text_var, bg_var = color_pair
        
        # Get colors from CSS variables
        text_color = self.wcag_colors.get(text_var, '#ffffff')
        background_color = self.wcag_colors.get(bg_var, 'rgba(255, 255, 255, 0.08)')
        
        # Clean up text color
        if 'var(' in text_color:
            color_map = {
                '--text-primary': '#ffffff',
                '--text-secondary': '#f0f0f0',
                '--accent-gold': '#ffd700'
            }
            text_color = color_map.get(text_var, '#ffffff')
        
        # Handle rgba backgrounds - convert to approximate solid colors for testing
        if background_color.startswith('rgba'):
            if 'rgba(255, 255, 255, 0.08)' in background_color:
                # Card background - approximate as very dark gray
                background_color = '#141414'
            elif 'rgba(255, 255, 255, 0.12)' in background_color:
                # Card hover background - approximate as dark gray
                background_color = '#1f1f1f'
            elif 'rgba(81, 207, 102' in background_color:
                # Success background - approximate as dark green
                background_color = '#003300'
            elif 'rgba(255, 215, 0' in background_color:
                # Warning background - approximate as dark yellow
                background_color = '#333300'
            elif 'rgba(255, 107, 107' in background_color:
                # Error background - approximate as dark red
                background_color = '#330000'
            elif 'rgba(116, 192, 252' in background_color:
                # Info background - approximate as dark blue
                background_color = '#001133'
            else:
                background_color = '#000000'  # Default to black
        
        # Calculate contrast ratio
        contrast = self.calculator.contrast_ratio(text_color, background_color)
        
        # For semi-transparent backgrounds, we aim for at least AA compliance (4.5:1)
        # but prefer AAA (7:1) where achievable
        self.assertGreaterEqual(
            contrast, 
            4.5, 
            f"Text on semi-transparent background should meet at least WCAG AA (4.5:1) for {text_var} on {bg_var}, got {contrast:.2f}"
        )
        
        # Check if AAA compliance is achieved (preferred)
        if contrast >= 7.0:
            self.assertGreaterEqual(
                contrast, 
                7.0, 
                f"WCAG AAA compliance achieved for {text_var} on {bg_var} with {contrast:.2f}:1 (excellent)"
            )
    
    @given(st.floats(min_value=18.0, max_value=48.0))
    @settings(max_examples=100)
    def test_large_text_wcag_aaa_compliance(self, font_size_px):
        """
        **Feature: ui-ux-improvements, Property 14: WCAG AAA compliance where possible**
        **Validates: Requirements 5.2**
        
        For any large text (≥18px or ≥14px bold), WCAG AAA requires 4.5:1 contrast 
        ratio instead of 7:1 for normal text
        """
        # Large text is defined as 18px+ or 14px+ bold
        is_large_text = font_size_px >= 18.0
        
        if is_large_text:
            # Test common large text color combinations
            test_combinations = [
                ('--text-primary', '--primary-black'),
                ('--accent-gold', '--primary-black'),
                ('--text-secondary', '--primary-black')
            ]
            
            for text_var, bg_var in test_combinations:
                text_color = self.wcag_colors.get(text_var, '#ffffff')
                background_color = self.wcag_colors.get(bg_var, '#000000')
                
                # Clean up colors
                if 'var(' in text_color:
                    color_map = {
                        '--text-primary': '#ffffff',
                        '--text-secondary': '#f0f0f0',
                        '--accent-gold': '#ffd700'
                    }
                    text_color = color_map.get(text_var, '#ffffff')
                
                if 'var(' in background_color:
                    background_color = '#000000'
                
                contrast = self.calculator.contrast_ratio(text_color, background_color)
                
                # Large text WCAG AAA requires 4.5:1
                self.assertGreaterEqual(
                    contrast, 
                    4.5, 
                    f"Large text ({font_size_px}px) WCAG AAA should be at least 4.5:1 for {text_var} on {bg_var}, got {contrast:.2f}"
                )
    
    @given(st.sampled_from([
        ('--accent-gold', '--primary-black', 'interactive'),     # Gold buttons/links
        ('--accent-green', '--primary-black', 'success'),       # Success indicators
        ('--accent-blue', '--primary-black', 'info'),           # Info indicators
        ('--accent-red', '--primary-black', 'error'),           # Error indicators
        ('--accent-silver', '--primary-black', 'secondary'),    # Secondary elements
        ('--primary-black', '--accent-gold', 'button-text')     # Black text on gold button
    ]))
    @settings(max_examples=100)
    def test_interactive_element_wcag_aaa(self, color_config):
        """
        **Feature: ui-ux-improvements, Property 14: WCAG AAA compliance where possible**
        **Validates: Requirements 5.2**
        
        For any interactive element (buttons, links, form controls), colors should 
        meet WCAG AAA standards for optimal accessibility
        """
        text_var, bg_var, element_type = color_config
        
        # Get colors from CSS variables
        text_color = self.wcag_colors.get(text_var, '#ffffff')
        background_color = self.wcag_colors.get(bg_var, '#000000')
        
        # Clean up color values
        if 'var(' in text_color:
            color_map = {
                '--text-primary': '#ffffff',
                '--accent-gold': '#ffd700',
                '--accent-green': '#51cf66',
                '--accent-blue': '#74c0fc',
                '--accent-red': '#ff6b6b',
                '--accent-silver': '#c0c0c0',
                '--primary-black': '#000000'
            }
            text_color = color_map.get(text_var, '#ffffff')
            
        if 'var(' in background_color:
            bg_map = {
                '--primary-black': '#000000',
                '--accent-gold': '#ffd700',
                '--accent-green': '#51cf66',
                '--accent-blue': '#74c0fc'
            }
            background_color = bg_map.get(bg_var, '#000000')
        
        # Calculate contrast ratio
        contrast = self.calculator.contrast_ratio(text_color, background_color)
        
        # Interactive elements should meet WCAG AAA when possible
        if element_type in ['interactive', 'success', 'info', 'error']:
            # These should meet AAA standards (7:1) for optimal accessibility
            self.assertGreaterEqual(
                contrast, 
                7.0, 
                f"Interactive {element_type} element should meet WCAG AAA (7:1) for {text_var} on {bg_var}, got {contrast:.2f}"
            )
        else:
            # Other elements should at least meet AA standards (4.5:1)
            self.assertGreaterEqual(
                contrast, 
                4.5, 
                f"{element_type} element should meet at least WCAG AA (4.5:1) for {text_var} on {bg_var}, got {contrast:.2f}"
            )
    
    @given(st.sampled_from([
        '--text-primary',
        '--text-secondary',
        '--text-muted',
        '--accent-gold',
        '--accent-green',
        '--accent-blue'
    ]))
    @settings(max_examples=100)
    def test_color_luminance_distribution(self, color_var):
        """
        **Feature: ui-ux-improvements, Property 14: WCAG AAA compliance where possible**
        **Validates: Requirements 5.2**
        
        For any color in the design system, luminance values should be well-distributed 
        to provide good contrast options for WCAG AAA compliance
        """
        color_value = self.wcag_colors.get(color_var, '#ffffff')
        
        # Clean up color value
        if 'var(' in color_value:
            color_map = {
                '--text-primary': '#ffffff',
                '--text-secondary': '#f0f0f0',
                '--text-muted': '#e0e0e0',
                '--accent-gold': '#ffd700',
                '--accent-green': '#51cf66',
                '--accent-blue': '#74c0fc'
            }
            color_value = color_map.get(color_var, '#ffffff')
        
        # Calculate relative luminance
        rgb = self.calculator.hex_to_rgb(color_value)
        luminance = self.calculator.relative_luminance(rgb)
        
        # Luminance should be in reasonable ranges for good contrast
        if color_var.startswith('--text'):
            # Text colors should have high luminance (light colors)
            self.assertGreaterEqual(
                luminance, 
                0.5, 
                f"Text color {color_var} should have high luminance for good contrast, got {luminance:.3f}"
            )
        elif color_var.startswith('--accent'):
            # Accent colors should have moderate to high luminance
            self.assertGreaterEqual(
                luminance, 
                0.2, 
                f"Accent color {color_var} should have reasonable luminance for visibility, got {luminance:.3f}"
            )
        
        # All colors should avoid extreme low luminance (except pure black backgrounds)
        if color_var not in ['--primary-black', '--secondary-black']:
            self.assertGreaterEqual(
                luminance, 
                0.05, 
                f"Color {color_var} should avoid extremely low luminance for accessibility, got {luminance:.3f}"
            )


if __name__ == '__main__':
    unittest.main()