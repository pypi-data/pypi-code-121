"""
Sage Intacct Checking Accounts
"""
from .api_base import ApiBase


class CheckingAccounts(ApiBase):
    """Class for Checking Accounts APIs."""
    def __init__(self):
        super().__init__(dimension='CHECKINGACCOUNT')

