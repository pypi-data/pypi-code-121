"""
Sage Intacct customers
"""
from typing import Dict

from .api_base import ApiBase


class Customers(ApiBase):
    """Class for Customers APIs."""
    def __init__(self):
        super().__init__(dimension='CUSTOMER')

    def update_customer(self, data, dimension='update_customer'):
        self.dimension = dimension
        return self._construct_post_legacy_payload(data)
