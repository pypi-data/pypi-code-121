"""
Sage Intacct AR Invoice
"""

from .api_base import ApiBase
from typing import Dict


class ARInvoices(ApiBase):
    """Class for AR Invoice APIs."""

    def __init__(self):
        super().__init__(dimension='ARINVOICE', post_legacy_method='create_invoice')

    def create_invoice(self, data: Dict) -> str:
        return self._construct_post_legacy_payload(data)

    def delete_duplicate_invoices(self, data: Dict) -> str:   #, post_legacy_method='delete') -> str:
        # self.post_legacy_method = post_legacy_method
        return self._construct_delete(data)

    def update(self, data: Dict) -> str:
        self.post_legacy_method = 'update_invoice'
        return self._construct_post_legacy_payload(data)

