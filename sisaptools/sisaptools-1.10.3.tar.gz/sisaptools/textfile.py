# -*- coding: utf8 -*-

"""
Eines per treballar amb fitxers de text.
"""

from .constants import APP_CHARSET, IS_PYTHON_3


class TextFile(object):
    """Classe principal."""

    def __init__(self, filename):
        """Obertura del fitxer segons la versió de l'intèrpret."""
        if IS_PYTHON_3:
            self.file = open(filename, 'w', encoding=APP_CHARSET)
        else:
            self.file = open(filename, 'w+b')

    def write_iterable(self, iterable, delimiter, endline):
        """
        Escriptura d'un iterable al fitxer.
        Seria millor que la conversió a str fos un mètode,
        però es torna 'molt' més lent...
        """
        data = endline.join(
            [delimiter.join(
                [str(field) if field or field == 0 else '' for field in row]
            ) for row in iterable]
        )
        self.write(data)

    def write(self, data):
        """Escriptura d'un text al fitxer."""
        self.file.write(data)

    def __enter__(self):
        """Context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager."""
        self.file.close()
