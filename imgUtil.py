import os
from os import path


def findImageAsPixmap(imgPath):
    """Load image and return as QPixmap for PySide6."""
    from PySide6.QtGui import QPixmap

    if not path.isfile(imgPath):
        return None

    pixmap = QPixmap(imgPath)
    return pixmap if not pixmap.isNull() else None

