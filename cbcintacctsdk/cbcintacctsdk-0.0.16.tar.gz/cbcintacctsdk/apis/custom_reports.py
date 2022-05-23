"""
Sage Intacct custom reports
"""
from typing import Dict

from .api_base import ApiBase


class CustomReports(ApiBase):
    """Class for Expense Reports APIs."""
    def __init__(self):
        super().__init__(dimension='custom_reports') #post_legacy_method='create_invoice')

    # def update_attachment(self, key: str, supdocid: str):
    #     """
    #     Update expense reports with supdocid
    #     Parameters:
    #         key (str): A parameter to update expense reports by the key. (required).
    #         supdoc (str): A parameter to update attachment ID for the expense report. (required).
    #     Returns:
    #         Dict in Expense Reports update schema.
    #     """
    #     data = {
    #         'update_expensereport': {
    #             '@key': key,
    #             'supdocid': supdocid
    #         }
    #     }
         #return self.format_and_send_request(data)

    def read_report(self, data: Dict) -> str:
        return self._construct_read_custom_report(data)


