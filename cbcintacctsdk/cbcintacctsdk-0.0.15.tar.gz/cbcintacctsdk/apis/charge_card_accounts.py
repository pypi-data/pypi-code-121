"""
Sage Intacct charge card accounts
"""
from typing import Dict

from .api_base import ApiBase


class ChargeCardAccounts(ApiBase):
    """Class for Charge Card Accounts APIs."""
    def __init__(self):
        super().__init__(dimension='CREDITCARD')
