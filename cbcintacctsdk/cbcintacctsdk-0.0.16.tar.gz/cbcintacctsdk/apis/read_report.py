"""
Sage Intacct AR Invoice
"""

from .api_base import ApiBase


class ReadReport(ApiBase):
    """Class for AR Invoice APIs."""
    def __init__(self):
        super().__init__(dimension='readReport')
