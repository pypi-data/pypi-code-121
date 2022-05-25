"""Exceptions module for the PyVSS."""

from typing import Dict, Optional


class VssError(RuntimeError):
    """Vss Error module."""

    _http_code: int = 0
    message: str
    http_headers: Dict = {}

    @property
    def http_code(self):
        """Get HTTP Code."""
        return self._http_code

    @http_code.setter
    def http_code(self, val):
        """Set HTTP Code."""
        self._http_code = int(val)

    @http_code.deleter
    def http_code(self):
        """Delete HTTP Code."""
        del self._http_code

    def __init__(
        self,
        message: str,
        http_code: Optional[int] = 0,
        http_headers: Optional[Dict] = None,
    ):
        """Initialize class."""
        self.message = message
        self.http_code = http_code
        if http_headers is not None:
            self.http_headers = http_headers
        super().__init__(self.message)

    def __str__(self):
        """Get string representation."""
        return f'{self.message} HTTP Code: {self.http_code}'
