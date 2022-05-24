import hashlib

from PyQt5.QtGui import QColor


def byte_hash(s: str) -> int:
    """
    Compute a one-byte hash of a string.
    """
    return hashlib.sha256(s.encode()).digest()[0]


def concept_color(concept: str) -> QColor:
    """
    Compute a color for a concept based on its name.
    """
    color = QColor()
    color.setHsv(byte_hash(concept) % 256, 255, 255)
    return color.lighter()
