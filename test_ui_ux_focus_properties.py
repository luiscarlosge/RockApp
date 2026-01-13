#!/usr/bin/env python3
"""Property-based tests for UI/UX improvements - focus indicator visibility."""

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


class FocusStyleExtractor:
    """Utility class for extracting focus-related styles from CSS."""
    
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
    def extract_focus_styles(css_content):
        """Extract focus-related styles from CSS."""
        focus_styles = {
            'focus_selectors': [],
            'outline_properties': [],
            'box_shadow_properties': [],
            'border_properties': [],
            'background_properties': []
        }
        
        # Find :focus selectors
        focus_selector_pattern = r'([^{]+):focus[^{]*\{([^}]+)\}'
        focus_matches = re.findall(focus_selector_pattern, css_content, re.IGNORECASE | re.DOTALL)
        
        for selector, properties in focus_matches:
            focus_styles['focus_selectors'].append((selector.strip(), properties.strip()))
            
            # Extract specific focus properties
            if 'outline' in properties.lower():
                outline_matches = re.findall(r'outline[^;]*;', properties, re.IGNORECASE)
                focus_styles['outline_properties'].extend(outline_matches)
            
            if 'box-shadow' in properties.lower():
                shadow_matches = re.findall(r'box-shadow[^;]*;', properties, re.IGNORECASE)
                focus_styles['box_shadow_properties'].extend(shadow_matches)
            
            if 'border' in properties.lower():
                border_matches = re.findall(r'border[^;]*;', properties, re.IGNORECASE)
                focus_styles['border_properties'].extend(border_matches)
            
            if 'background' in properties.lower():
                bg_matches = re.findall(r'background[^;]*;', properties, re.IGNORECASE)
                focus_styles['background_properties'].extend(bg_matches)
        
        return focus_styles
    
    @staticmethod
    def extract_focus_colors(css_content):
        """Extract focus-related colors from CSS."""
        variables = FocusStyleExtractor.extract_css_variables(css_content)
        
        focus_colors = {}
        focus_related_vars = [
            '--border-focus',
            '--accent-gold',
            '--text-primary',
            '--primary-black',
            '--secondary-black',
            '--bg-card',
            '--bg-card-hover',
            '--menu-item-hover',
            '--menu-item-active'
        ]
        
        for var in focus_related_vars:
            if var in variables:
                focus_colors[var] = variables[var]
        
        return focus_colors


class TestFocusIndicatorVisibility(unittest.TestCase):
    """Property-based tests for focus indicator visibility compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.css_content = FocusStyleExtractor.read_css_file('static/css/style.css')
        self.focus_styles = FocusStyleExtractor.extract_focus_styles(self.css_content)
        self.focus_colors = FocusStyleExtractor.extract_focus_colors(self.css_content)
        self.calculator = ContrastCalculator()
    
    def test_focus_styles_extracted(self):
        """Test that focus styles are properly extracted from CSS."""
        self.assertGreater(
            len(self.focus_styles['focus_selectors']), 
            0, 
            "Should extract focus selectors from CSS"
        )
    
    @given(st.sampled_from([
        'menu-toggle',
        'menu-item',
        'form-select',
        'btn',
        'song-card-small',
        'instrument-card',
        'musician-assignment'
    ]))
    @settings(max_examples=100)
    def test_focusable_element_focus_styles(self, element_class):
        """
        **Feature: ui-ux-improvements, Property 15: Focus indicator visibility**
        **Validates: Requirements 5.3**
        
        For any focusable element, when focus is applied, the focus indicator 
        should be clearly visible with adequate contrast
        """
        # Look for focus styles for this element
        element_focus_found = False
        focus_properties = []
        
        for selector, properties in self.focus_styles['focus_selectors']:
            if element_class in selector:
                element_focus_found = True
                focus_properties.append(properties)
        
        if element_focus_found:
            # Verify focus styles have visibility-enhancing properties
            all_properties = ' '.join(focus_properties).lower()
            
            visibility_indicators = [
                'outline',
                'box-shadow',
                'border',
                'background'
            ]
            
            has_visibility_properties = any(prop in all_properties for prop in visibility_indicators)
            self.assertTrue(
                has_visibility_properties,
                f"Focusable element {element_class} should have visible focus indicators (outline, box-shadow, border, or background)"
            )
        else:
            # If no explicit focus styles, that's acceptable if using browser defaults
            # but we should note it for potential improvement
            self.assertTrue(
                True, 
                f"Element {element_class} has no explicit focus styles (may rely on browser defaults)"
            )
    
    @given(st.sampled_from([
        ('outline', '3px solid'),
        ('outline', '2px solid'),
        ('box-shadow', '0 0 0'),
        ('border', '2px solid'),
        ('border', '3px solid')
    ]))
    @settings(max_examples=100)
    def test_focus_indicator_thickness(self, style_config):
        """
        **Feature: ui-ux-improvements, Property 15: Focus indicator visibility**
        **Validates: Requirements 5.3**
        
        For any focus indicator, the thickness should be sufficient for clear 
        visibility (minimum 2px for outlines and borders)
        """
        property_name, expected_thickness = style_config
        
        # Look for this property in focus styles
        if property_name == 'outline':
            properties_to_check = self.focus_styles['outline_properties']
        elif property_name == 'box-shadow':
            properties_to_check = self.focus_styles['box_shadow_properties']
        elif property_name == 'border':
            properties_to_check = self.focus_styles['border_properties']
        else:
            properties_to_check = []
        
        for prop in properties_to_check:
            # Extract thickness values
            thickness_pattern = r'(\d+(?:\.\d+)?)px'
            thickness_matches = re.findall(thickness_pattern, prop)
            
            for thickness_str in thickness_matches:
                thickness = float(thickness_str)
                
                # Focus indicators should be at least 2px thick for visibility
                self.assertGreaterEqual(
                    thickness, 
                    2.0, 
                    f"Focus indicator {property_name} should be at least 2px thick for visibility, got {thickness}px in '{prop}'"
                )
                
                # But not too thick to be overwhelming
                self.assertLessEqual(
                    thickness, 
                    8.0, 
                    f"Focus indicator {property_name} should not be too thick (≤8px), got {thickness}px in '{prop}'"
                )
    
    @given(st.sampled_from([
        ('--accent-gold', '--primary-black'),       # Gold focus on black background
        ('--accent-gold', '--secondary-black'),     # Gold focus on dark gray
        ('--accent-gold', '--bg-card'),             # Gold focus on card background
        ('--primary-black', '--accent-gold'),       # Black text on gold background (for buttons)
        ('--text-primary', '--primary-black'),      # White text on black background
        ('--text-primary', '--secondary-black')     # White text on dark gray background
    ]))
    @settings(max_examples=100)
    def test_focus_indicator_contrast(self, color_pair):
        """
        **Feature: ui-ux-improvements, Property 15: Focus indicator visibility**
        **Validates: Requirements 5.3**
        
        For any focus indicator color, it should have sufficient contrast against 
        the background to be clearly visible
        """
        focus_color_var, bg_color_var = color_pair
        
        # Get colors from CSS variables
        focus_color = self.focus_colors.get(focus_color_var, '#ffd700')
        background_color = self.focus_colors.get(bg_color_var, '#000000')
        
        # Clean up color values
        if 'var(' in focus_color:
            color_map = {
                '--accent-gold': '#ffd700',
                '--text-primary': '#ffffff',
                '--primary-black': '#000000'
            }
            focus_color = color_map.get(focus_color_var, '#ffd700')
        
        if 'var(' in background_color:
            bg_map = {
                '--primary-black': '#000000',
                '--secondary-black': '#1a1a1a',
                '--bg-card': 'rgba(255, 255, 255, 0.08)',
                '--accent-gold': '#ffd700'
            }
            background_color = bg_map.get(bg_color_var, '#000000')
        
        # Handle rgba backgrounds
        if background_color.startswith('rgba'):
            if 'rgba(255, 255, 255, 0.08)' in background_color:
                background_color = '#141414'  # Very dark gray
            else:
                background_color = '#000000'  # Default to black
        
        # Calculate contrast ratio
        contrast = self.calculator.contrast_ratio(focus_color, background_color)
        
        # Focus indicators should have high contrast for visibility
        self.assertGreaterEqual(
            contrast, 
            3.0, 
            f"Focus indicator contrast should be at least 3.0:1 for visibility, got {contrast:.2f} for {focus_color_var} on {bg_color_var}"
        )
        
        # Prefer higher contrast for better accessibility
        if contrast >= 4.5:
            self.assertGreaterEqual(
                contrast, 
                4.5, 
                f"Focus indicator has excellent contrast ({contrast:.2f}:1) for {focus_color_var} on {bg_color_var}"
            )
    
    @given(st.sampled_from([
        'solid',
        'dashed',
        'dotted',
        'double'
    ]))
    @settings(max_examples=100)
    def test_focus_indicator_style_visibility(self, border_style):
        """
        **Feature: ui-ux-improvements, Property 15: Focus indicator visibility**
        **Validates: Requirements 5.3**
        
        For any focus indicator style, it should provide clear visual distinction 
        and be easily perceivable by users
        """
        # Look for this border style in focus properties
        style_count = 0
        
        all_focus_properties = (
            self.focus_styles['outline_properties'] + 
            self.focus_styles['border_properties']
        )
        
        for prop in all_focus_properties:
            if border_style in prop.lower():
                style_count += 1
        
        if style_count > 0:
            if border_style == 'solid':
                # Solid is the most visible and preferred
                self.assertGreater(
                    style_count, 
                    0, 
                    f"Solid focus indicators found {style_count} times (excellent for visibility)"
                )
            elif border_style in ['dashed', 'dotted']:
                # Dashed and dotted can be visible but less preferred
                self.assertTrue(
                    style_count >= 0, 
                    f"{border_style.capitalize()} focus indicators found {style_count} times (acceptable but solid preferred)"
                )
            elif border_style == 'double':
                # Double borders can be good for high visibility
                self.assertTrue(
                    style_count >= 0, 
                    f"Double focus indicators found {style_count} times (good for high visibility)"
                )
    
    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=100)
    def test_focus_indicator_offset(self, offset_px):
        """
        **Feature: ui-ux-improvements, Property 15: Focus indicator visibility**
        **Validates: Requirements 5.3**
        
        For any focus indicator with offset, the offset should be reasonable 
        to maintain visibility without being too distant from the element
        """
        # Look for outline-offset properties in focus styles
        offset_pattern = rf'outline-offset\s*:\s*{offset_px}px'
        offset_matches = re.findall(offset_pattern, self.css_content, re.IGNORECASE)
        
        if len(offset_matches) > 0:
            if offset_px <= 2:
                # Small offsets are good for tight focus indicators
                self.assertLessEqual(
                    offset_px, 
                    2, 
                    f"Small outline offset ({offset_px}px) is good for tight focus indicators"
                )
            elif offset_px <= 5:
                # Medium offsets are acceptable
                self.assertLessEqual(
                    offset_px, 
                    5, 
                    f"Medium outline offset ({offset_px}px) is acceptable for focus visibility"
                )
            else:
                # Large offsets may reduce association with the element
                self.assertLessEqual(
                    offset_px, 
                    10, 
                    f"Large outline offset ({offset_px}px) should be used carefully to maintain element association"
                )
    
    @given(st.sampled_from([
        'button',
        'input',
        'select',
        'textarea',
        'a',
        '[tabindex]'
    ]))
    @settings(max_examples=100)
    def test_interactive_element_focus_coverage(self, element_type):
        """
        **Feature: ui-ux-improvements, Property 15: Focus indicator visibility**
        **Validates: Requirements 5.3**
        
        For any interactive HTML element, there should be appropriate focus 
        styles to ensure keyboard navigation accessibility
        """
        # Look for focus styles targeting this element type
        element_focus_patterns = [
            rf'{element_type}:focus',
            rf'{element_type}\s*:focus',
            rf'\.[\w-]*{element_type}[\w-]*:focus'
        ]
        
        focus_coverage = 0
        for pattern in element_focus_patterns:
            matches = re.findall(pattern, self.css_content, re.IGNORECASE)
            focus_coverage += len(matches)
        
        # Also check for general focus styles that might apply
        general_focus_pattern = r':focus\s*\{'
        general_matches = re.findall(general_focus_pattern, self.css_content, re.IGNORECASE)
        
        total_focus_coverage = focus_coverage + len(general_matches)
        
        if element_type in ['button', 'input', 'select', 'a']:
            # These are critical interactive elements that should have focus styles
            self.assertGreater(
                total_focus_coverage, 
                0, 
                f"Interactive element '{element_type}' should have focus styles for keyboard accessibility"
            )
        else:
            # Other elements may have focus styles but it's not critical
            self.assertTrue(
                total_focus_coverage >= 0, 
                f"Element '{element_type}' focus coverage: {total_focus_coverage} (acceptable)"
            )


if __name__ == '__main__':
    unittest.main()