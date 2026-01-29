# ui/widgets.py
# Custom styled widgets for RetroArch Rom Manager

from PySide6.QtWidgets import (
    QPushButton, QLabel, QFrame, QVBoxLayout,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QColor, QFont


class StyledButton(QPushButton):
    """Styled button with neon effects for console-style UI."""

    def __init__(self, text: str, button_type: str = 'default', parent=None):
        """
        Initialize styled button.

        Args:
            text: Button text
            button_type: One of 'green', 'blue', 'yellow', 'red', 'default'
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()

    def _setup_style(self):
        """Apply button style based on type."""
        self.setProperty('class', self.button_type)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)

        # Add glow effect for neon buttons
        if self.button_type in ('green', 'blue', 'yellow', 'red'):
            self._add_glow_effect()

    def _add_glow_effect(self):
        """Add subtle glow shadow effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 0)

        glow_colors = {
            'green': QColor('#00ff88'),
            'blue': QColor('#00d4ff'),
            'yellow': QColor('#ffdd00'),
            'red': QColor('#ff4757'),
        }

        color = glow_colors.get(self.button_type, QColor('#e94560'))
        color.setAlpha(100)
        shadow.setColor(color)
        self.setGraphicsEffect(shadow)


class ImagePreview(QFrame):
    """Image preview widget with shadow effect and hover border."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._default_pixmap = None
        self._current_pixmap = None

    def _setup_ui(self):
        """Setup the UI components."""
        self.setProperty('class', 'card')
        self.setMinimumSize(QSize(400, 300))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignCenter)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setProperty('class', 'image-preview')
        self.image_label.setScaledContents(False)
        layout.addWidget(self.image_label)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def set_default_image(self, pixmap: QPixmap):
        """Set the default image to show when no ROM is selected."""
        self._default_pixmap = pixmap
        if self._current_pixmap is None:
            self._display_pixmap(pixmap)

    def set_image(self, pixmap: QPixmap = None):
        """Set the preview image."""
        if pixmap is None or pixmap.isNull():
            self._current_pixmap = None
            if self._default_pixmap:
                self._display_pixmap(self._default_pixmap)
            else:
                self.image_label.clear()
        else:
            self._current_pixmap = pixmap
            self._display_pixmap(pixmap)

    def _display_pixmap(self, pixmap: QPixmap):
        """Display pixmap scaled to fit the label."""
        if pixmap and not pixmap.isNull():
            # Get available size
            available_size = self.image_label.size()
            if available_size.width() < 100:
                available_size = QSize(400, 300)

            # Scale pixmap to fit while maintaining aspect ratio
            scaled = pixmap.scaled(
                available_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

    def clear_image(self):
        """Clear the current image and show default."""
        self._current_pixmap = None
        if self._default_pixmap:
            self._display_pixmap(self._default_pixmap)
        else:
            self.image_label.clear()

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def resizeEvent(self, event):
        """Handle resize event to rescale image."""
        super().resizeEvent(event)
        if self._current_pixmap:
            self._display_pixmap(self._current_pixmap)
        elif self._default_pixmap:
            self._display_pixmap(self._default_pixmap)


class SectionLabel(QLabel):
    """Section header label with styled appearance."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty('class', 'section-title')
        font = self.font()
        font.setPointSize(11)
        font.setBold(True)
        self.setFont(font)


class TitleLabel(QLabel):
    """App title label with styled appearance."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty('class', 'title')
        font = self.font()
        font.setPointSize(16)
        font.setBold(True)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)


class CardFrame(QFrame):
    """Styled card frame with rounded corners and shadow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty('class', 'card')

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)


class MissingImageListItem:
    """Helper class to track ROM items with missing images."""

    @staticmethod
    def set_missing_style(item):
        """Set style for items with missing images."""
        item.setBackground(QColor('#442233'))
        item.setForeground(QColor('#ff6677'))
