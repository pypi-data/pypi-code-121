"""
Sage Intacct AR Invoice
"""

from .api_base import ApiBase


class Invoices(ApiBase):
    """Class for AR Invoice APIs."""
    def __init__(self):
        super().__init__(dimension='create_invoice', post_legacy_method='create_invoice')
