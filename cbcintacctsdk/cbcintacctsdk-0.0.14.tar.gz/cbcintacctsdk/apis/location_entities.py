"""
Sage Intacct Location Entities
"""
from .api_base import ApiBase


class LocationEntities(ApiBase):
    """Class for Location Entities APIs."""
    def __init__(self):
        super().__init__(dimension='LOCATIONENTITY')
