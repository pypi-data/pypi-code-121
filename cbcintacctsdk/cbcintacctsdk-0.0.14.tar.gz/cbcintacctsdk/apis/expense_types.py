"""
Sage Intacct expense types
"""
from typing import Dict

from .api_base import ApiBase


class ExpenseTypes(ApiBase):
    """Class for Expense Types APIs."""
    def __init__(self):
        super().__init__(dimension='EEACCOUNTLABEL')
