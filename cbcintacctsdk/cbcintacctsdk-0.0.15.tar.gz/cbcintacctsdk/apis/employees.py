"""
Sage Intacct employees
"""
from typing import Dict

from .api_base import ApiBase


class Employees(ApiBase):
    """Class for Employees APIs."""
    def __init__(self):
        super().__init__(dimension='EMPLOYEE')
