"""
Sage Intacct AR Invoice
"""

from .api_base import ApiBase
from typing import Dict

class ARAdjustment(ApiBase):
    """Class for AR Invoice APIs."""
    def __init__(self):
        super().__init__(dimension='ARADJUSTMENT', post_legacy_method='ARADJUSTMENT')

    def create_aradjustment(self, data):
        return self._construct_post_legacy_aradjustment_payload(data)

    def update(self, data):
        self.post_legacy_method = 'update_aradjustment'
        return self._construct_post_legacy_aradjustment_payload(data)

    def delete_duplicate_aradjustments(self, data: Dict) -> str:   #, post_legacy_method='delete') -> str:
        # self.post_legacy_method = post_legacy_method
        return self._construct_delete(data)