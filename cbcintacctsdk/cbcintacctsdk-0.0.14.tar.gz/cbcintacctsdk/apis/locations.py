"""
Sage Intacct locations
"""
from typing import Dict

from .api_base import ApiBase


class Locations(ApiBase):
    """Class for Locations APIs."""
    def __init__(self):
        super().__init__(dimension='LOCATION')
