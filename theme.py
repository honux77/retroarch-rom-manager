# theme.py
# Modern Console Theme - PySide6 QSS loader and color constants

import os
from pathlib import Path

# Color Palette - Modern Console Dark Theme
COLORS = {
    # Background colors
    'bg_primary': '#0B0E14',      # Almost black navy
    'bg_secondary': '#111827',    # Dark navy
    'bg_card': '#1F2937',         # Dark gray

    # Text colors
    'text_primary': '#E5E7EB',    # Almost white
    'text_secondary': '#9CA3AF',  # Muted gray
    'text_disabled': '#4B5563',   # Disabled text

    # Accent color
    'accent': '#00FF9C',          # Neon green

    # Neon button colors
    'btn_green': '#00FF9C',       # Neon green
    'btn_green_bg': '#065F46',
    'btn_blue': '#38BDF8',        # Cyan
    'btn_blue_bg': '#075985',
    'btn_yellow': '#FFB000',      # Amber
    'btn_yellow_bg': '#92400E',
    'btn_red': '#EF4444',         # Red
    'btn_red_bg': '#991B1B',

    # State colors
    'hover': '#374151',
    'selected': '#00FF9C',
    'error': '#F87171',
    'success': '#00FF9C',
    'warning': '#FFB000',
}

# Font settings
FONTS = {
    'family': 'Segoe UI, Malgun Gothic, sans-serif',
    'size_title': 16,
    'size_section': 11,
    'size_normal': 10,
    'size_small': 9,
}


def load_stylesheet() -> str:
    """Load QSS stylesheet from file."""
    qss_path = Path(__file__).parent / 'ui' / 'styles.qss'

    if qss_path.exists():
        with open(qss_path, 'r', encoding='utf-8') as f:
            return f.read()

    # Return empty string if file not found
    return ""


def get_color(name: str) -> str:
    """Get color by name."""
    return COLORS.get(name, '#ffffff')


def apply_theme(app):
    """Apply theme to QApplication."""
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)


def get_button_style(button_type: str) -> dict:
    """Get button style properties by type."""
    styles = {
        'green': {
            'background': COLORS['btn_green_bg'],
            'border': COLORS['btn_green'],
            'text': '#ffffff',
        },
        'blue': {
            'background': COLORS['btn_blue_bg'],
            'border': COLORS['btn_blue'],
            'text': '#ffffff',
        },
        'yellow': {
            'background': COLORS['btn_yellow_bg'],
            'border': COLORS['btn_yellow'],
            'text': COLORS['bg_primary'],
        },
        'red': {
            'background': COLORS['btn_red_bg'],
            'border': COLORS['btn_red'],
            'text': '#ffffff',
        },
        'default': {
            'background': COLORS['bg_card'],
            'border': COLORS['bg_secondary'],
            'text': COLORS['text_primary'],
        }
    }
    return styles.get(button_type, styles['default'])
