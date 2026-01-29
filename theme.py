# theme.py
# Modern Console Theme - PySide6 QSS loader and color constants

import os
from pathlib import Path

# Color Palette - Modern Console Dark Theme
COLORS = {
    # Background colors
    'bg_primary': '#1a1a2e',      # Deep navy (main background)
    'bg_secondary': '#16213e',    # Dark blue (sub background)
    'bg_card': '#0f3460',         # Card/panel background

    # Text colors
    'text_primary': '#e8e8e8',    # Light gray (main text)
    'text_secondary': '#aaaacc',  # Muted text
    'text_disabled': '#666688',   # Disabled text

    # Accent color
    'accent': '#e94560',          # Hot pink/neon red

    # Neon button colors (console style)
    'btn_green': '#00ff88',       # Y button - Execute (neon green)
    'btn_green_bg': '#00aa66',
    'btn_blue': '#00d4ff',        # X button - Info (neon blue)
    'btn_blue_bg': '#0088cc',
    'btn_yellow': '#ffdd00',      # B button - Translate (neon yellow)
    'btn_yellow_bg': '#ccaa00',
    'btn_red': '#ff4757',         # A button - Delete (neon red)
    'btn_red_bg': '#cc3344',

    # State colors
    'hover': '#1a4a7a',
    'selected': '#e94560',
    'error': '#ff6677',
    'success': '#00ff88',
    'warning': '#ffdd00',
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
