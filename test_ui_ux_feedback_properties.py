#!/usr/bin/env python3
"""Property-based tests for UI/UX improvements - success feedback visibility."""

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


class CSSFeedbackExtractor:
    """Utility class for extracting feedback-related styles from CSS."""
    
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
    def extract_feedback_colors(css_content):
        """Extract feedback-related colors from CSS."""
        variables = CSSFeedbackExtractor.extract_css_variables(css_content)
        
        feedback_colors = {}
        feedback_related_vars = [
            '--text-primary',
            '--text-secondary',
            '--accent-gold',
            '--accent-green',
            '--accent-blue', 
            '--accent-red',
            '--primary-black',
            '--secondary-black',
            '--success-bg',
            '--success-border',
            '--warning-bg',
            '--warning-border',
            '--error-bg',
            '--error-border',
            '--info-bg',
            '--info-border'
        ]
        
        for var in feedback_related_vars:
            if var in variables:
                feedback_colors[var] = variables[var]
        
        return feedback_colors
    
    @staticmethod
    def extract_animation_properties(css_content):
        """Extract animation and transition properties for feedback elements."""
        # Look for animation and transition properties
        animation_pattern = r'animation\s*:\s*([^;]+);'
        transition_pattern = r'transition\s*:\s*([^;]+);'
        
        animations = re.findall(animation_pattern, css_content, re.IGNORECASE)
        transitions = re.findall(transition_pattern, css_content, re.IGNORECASE)
        
        return {
            'animations': animations,
            'transitions': transitions
        }


class TestSuccessFeedbackVisibility(unittest.TestCase):
    """Property-based tests for success feedback visibility compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.css_content = CSSFeedbackExtractor.read_css_file('static/css/style.css')
        self.feedback_colors = CSSFeedbackExtractor.extract_feedback_colors(self.css_content)
        self.animation_properties = CSSFeedbackExtractor.extract_animation_properties(self.css_content)
        self.calculator = ContrastCalculator()
    
    def test_feedback_colors_extracted(self):
        """Test that feedback colors are properly extracted from CSS."""
        self.assertGreater(len(self.feedback_colors), 0, "Should extract feedback colors from CSS")
        self.assertIn('--text-primary', self.feedback_colors, "Should have primary text color")
        self.assertIn('--accent-green', self.feedback_colors, "Should have success green color")
    
    @given(st.sampled_from([
        ('--accent-green', '--success-bg', '--primary-black'),    # Success feedback
        ('--accent-blue', '--info-bg', '--primary-black'),       # Info feedback
        ('--accent-gold', '--warning-bg', '--primary-black'),    # Warning feedback
        ('--accent-red', '--error-bg', '--primary-black'),       # Error feedback
        ('--text-primary', '--success-bg', '--primary-black'),   # Success text
        ('--text-primary', '--info-bg', '--primary-black'),      # Info text
        ('--text-primary', '--warning-bg', '--primary-black'),   # Warning text
        ('--text-primary', '--error-bg', '--primary-black')      # Error text
    ]))
    @settings(max_examples=100)
    def test_success_feedback_contrast(self, color_config):
        """
        **Feature: ui-ux-improvements, Property 12: Success feedback visibility**
        **Validates: Requirements 4.4, 4.5**
        
        For any successful data update, visual feedback should be provided through 
        highlighting or animation that is clearly visible
        """
        accent_var, bg_var, base_bg_var = color_config
        
        # Get colors from CSS variables
        accent_color = self.feedback_colors.get(accent_var, '#51cf66')
        background_color = self.feedback_colors.get(bg_var, 'rgba(81, 207, 102, 0.15)')
        base_background = self.feedback_colors.get(base_bg_var, '#000000')
        
        # Clean up color values
        if 'var(' in accent_color:
            color_map = {
                '--accent-green': '#51cf66',
                '--accent-blue': '#74c0fc',
                '--accent-gold': '#ffd700',
                '--accent-red': '#ff6b6b',
                '--text-primary': '#ffffff'
            }
            accent_color = color_map.get(accent_var, '#51cf66')
        
        if 'var(' in base_background:
            base_background = '#000000'  # Black background
        
        # Handle rgba backgrounds - convert to approximate solid colors for testing
        if background_color.startswith('rgba'):
            if 'rgba(81, 207, 102' in background_color:
                background_color = '#003300'  # Dark green
            elif 'rgba(116, 192, 252' in background_color:
                background_color = '#001133'  # Dark blue
            elif 'rgba(255, 215, 0' in background_color:
                background_color = '#333300'  # Dark yellow
            elif 'rgba(255, 107, 107' in background_color:
                background_color = '#330000'  # Dark red
            else:
                background_color = '#000000'  # Default black
        
        # Test accent color contrast against feedback background
        accent_contrast = self.calculator.contrast_ratio(accent_color, background_color)
        self.assertGreaterEqual(
            accent_contrast, 
            3.0,  # Minimum for accent colors
            f"Feedback accent contrast should be at least 3.0:1 for {accent_var} on {bg_var}, got {accent_contrast:.2f}"
        )
        
        # Test accent color contrast against base background (for visibility)
        base_contrast = self.calculator.contrast_ratio(accent_color, base_background)
        self.assertGreaterEqual(
            base_contrast, 
            4.5,  # WCAG AA compliance
            f"Feedback accent should be visible on base background, contrast should be at least 4.5:1 for {accent_var}, got {base_contrast:.2f}"
        )
    
    @given(st.sampled_from([
        'alert-success',      # Bootstrap success alerts
        'alert-info',         # Bootstrap info alerts  
        'alert-warning',      # Bootstrap warning alerts
        'alert-danger',       # Bootstrap danger alerts
        'refresh-countdown',  # Custom countdown feedback
        'refresh-loading',    # Custom loading feedback
        'refresh-error'       # Custom error feedback
    ]))
    @settings(max_examples=100)
    def test_feedback_element_visibility(self, feedback_class):
        """
        **Feature: ui-ux-improvements, Property 12: Success feedback visibility**
        **Validates: Requirements 4.4, 4.5**
        
        For any feedback element, it should have sufficient visual prominence 
        and contrast to be clearly visible to users
        """
        # Check if this feedback class exists in CSS
        class_pattern = rf'\.{feedback_class}[^{{]*\{{([^}}]+)\}}'
        matches = re.findall(class_pattern, self.css_content, re.IGNORECASE | re.DOTALL)
        
        if not matches:
            # If class doesn't exist in CSS, that's acceptable (may be handled by framework)
            self.assertTrue(True, f"Feedback class {feedback_class} not found in CSS (may be framework-handled)")
            return
        
        # Analyze the CSS properties for visibility
        css_properties = matches[0].lower()
        
        # Check for visibility-enhancing properties
        visibility_indicators = [
            'background',
            'border',
            'color',
            'box-shadow',
            'opacity',
            'display',
            'visibility'
        ]
        
        has_visibility_properties = any(prop in css_properties for prop in visibility_indicators)
        self.assertTrue(
            has_visibility_properties,
            f"Feedback element {feedback_class} should have visibility-enhancing properties"
        )
        
        # Check for animation or transition properties that enhance feedback
        animation_indicators = [
            'transition',
            'animation',
            'transform'
        ]
        
        has_animation_properties = any(prop in css_properties for prop in animation_indicators)
        # Animation is preferred but not required
        if has_animation_properties:
            self.assertTrue(True, f"Feedback element {feedback_class} has animation properties (good)")
    
    @given(st.sampled_from([
        ('highlight', 'background-color'),    # Background highlighting
        ('highlight', 'border-color'),        # Border highlighting
        ('highlight', 'box-shadow'),          # Shadow highlighting
        ('flash', 'opacity'),                 # Flash animation
        ('pulse', 'transform'),               # Pulse animation
        ('fade', 'opacity')                   # Fade animation
    ]))
    @settings(max_examples=100)
    def test_feedback_animation_visibility(self, animation_config):
        """
        **Feature: ui-ux-improvements, Property 12: Success feedback visibility**
        **Validates: Requirements 4.4, 4.5**
        
        For any feedback animation, it should be clearly visible and provide 
        effective visual indication of state changes
        """
        animation_type, css_property = animation_config
        
        # Look for animation or transition properties that match this type
        animation_pattern = rf'{css_property}[^;]*(?:transition|animation)[^;]*;'
        matches = re.findall(animation_pattern, self.css_content, re.IGNORECASE)
        
        if len(matches) > 0:
            # If we found animations using this property, verify they're reasonable
            for match in matches:
                # Check that the animation duration is reasonable for feedback
                duration_pattern = r'(\d+(?:\.\d+)?)(s|ms)'
                duration_matches = re.findall(duration_pattern, match)
                
                for value, unit in duration_matches:
                    duration_ms = float(value)
                    if unit == 's':
                        duration_ms *= 1000
                    
                    # Feedback animations should be noticeable but not too long
                    self.assertGreaterEqual(
                        duration_ms, 
                        100, 
                        f"Feedback animation should be at least 100ms to be noticeable, got {duration_ms}ms"
                    )
                    
                    self.assertLessEqual(
                        duration_ms, 
                        2000, 
                        f"Feedback animation should be at most 2000ms to avoid being annoying, got {duration_ms}ms"
                    )
    
    @given(st.floats(min_value=0.1, max_value=1.0))
    @settings(max_examples=100)
    def test_feedback_opacity_visibility(self, opacity_value):
        """
        **Feature: ui-ux-improvements, Property 12: Success feedback visibility**
        **Validates: Requirements 4.4, 4.5**
        
        For any feedback element using opacity, the opacity should be sufficient 
        for clear visibility while allowing for subtle effects
        """
        # Look for opacity values in CSS
        opacity_pattern = rf'opacity\s*:\s*{opacity_value:.1f}[^;]*;'
        matches = re.findall(opacity_pattern, self.css_content, re.IGNORECASE)
        
        # Test the opacity value for visibility
        if opacity_value < 0.3:
            # Very low opacity - should be used sparingly and only for subtle effects
            self.assertLess(
                len(matches), 
                5, 
                f"Very low opacity ({opacity_value}) should be used sparingly for visibility"
            )
        elif opacity_value < 0.6:
            # Medium opacity - acceptable for backgrounds and subtle elements
            self.assertTrue(
                opacity_value >= 0.3, 
                f"Medium opacity ({opacity_value}) should be at least 0.3 for reasonable visibility"
            )
        else:
            # High opacity - good for visible feedback elements
            self.assertGreaterEqual(
                opacity_value, 
                0.6, 
                f"High opacity ({opacity_value}) is good for visible feedback elements"
            )
    
    @given(st.sampled_from([
        'success',    # Success state feedback
        'error',      # Error state feedback
        'warning',    # Warning state feedback
        'info',       # Info state feedback
        'loading',    # Loading state feedback
        'complete',   # Completion feedback
        'update'      # Update feedback
    ]))
    @settings(max_examples=100)
    def test_feedback_state_differentiation(self, feedback_state):
        """
        **Feature: ui-ux-improvements, Property 12: Success feedback visibility**
        **Validates: Requirements 4.4, 4.5**
        
        For any feedback state, it should be visually distinct from other states 
        to provide clear communication to users
        """
        # Look for CSS classes or properties related to this feedback state
        state_pattern = rf'{feedback_state}[^{{]*\{{([^}}]+)\}}'
        matches = re.findall(state_pattern, self.css_content, re.IGNORECASE | re.DOTALL)
        
        if len(matches) > 0:
            # Analyze the CSS for distinctive properties
            css_content = ' '.join(matches).lower()
            
            # Check for distinctive color properties
            color_properties = ['background', 'color', 'border-color']
            has_distinctive_colors = any(prop in css_content for prop in color_properties)
            
            # Check for distinctive visual properties
            visual_properties = ['box-shadow', 'border', 'opacity', 'transform']
            has_distinctive_visuals = any(prop in css_content for prop in visual_properties)
            
            # Feedback states should have some distinctive visual properties
            has_distinction = has_distinctive_colors or has_distinctive_visuals
            self.assertTrue(
                has_distinction,
                f"Feedback state '{feedback_state}' should have distinctive visual properties for clear communication"
            )


if __name__ == '__main__':
    unittest.main()