"""
Sage Intacct items
"""
from typing import Dict

from .api_base import ApiBase


class Items(ApiBase):
    """Class for Items APIs."""
    def __init__(self):
        super().__init__(dimension='ITEM')
