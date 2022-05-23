"""
Sage Intacct Tax items
"""
from typing import Dict

from .api_base import ApiBase


class TaxDetails(ApiBase):
    """Class for TaxItems APIs."""
    def __init__(self):
        super().__init__(dimension='TAXDETAIL')
