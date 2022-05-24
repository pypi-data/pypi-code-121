from typing import Any, Dict

from ._base import _Base
from ._interactor import _Interactor
from ._locust_error_handler import log_locust_error, test_response_for_error
from .helper import format_label
from .uiform import SailUiForm

REPORTS_INTERFACE_PATH = "/suite/rest/a/sites/latest/D6JMim/pages/reports/interface"
REPORTS_NAV_PATH = "/suite/rest/a/sites/latest/D6JMim/page/reports/nav"


class _Reports(_Base):
    def __init__(self, interactor: _Interactor) -> None:
        """
        Reports class wrapping list of possible activities can be performed with Appian-Tempo-Reports.

        Warnings: This class is internal and should not be accessed by tests directly. It can be accessed via the "appian" object

        Note: "appian" is created as part of ``AppianTaskSet``'s ``on_start`` function

        Args:
            session: Locust session/client object
            host (str): Host URL

        """
        self.interactor = interactor

        # When Get All functions called, these variables will be used to cache the values
        self._reports: Dict[str, Any] = dict()
        self._errors: int = 0

    def get_reports_interface(self, locust_request_label: str = "Reports") -> Dict[str, Any]:
        uri = self.interactor.host + REPORTS_INTERFACE_PATH
        headers = self.interactor.setup_sail_headers()
        resp = self.interactor.get_page(uri, headers, f'{locust_request_label}.Interface')
        return resp.json()

    def get_reports_nav(self, locust_request_label: str = "Reports") -> Dict[str, Any]:
        uri = self.interactor.host + REPORTS_NAV_PATH
        headers = self.interactor.setup_sail_headers()
        resp = self.interactor.get_page(uri, headers, f'{locust_request_label}.Nav')
        return resp.json()

    def get_all(self, search_string: str = None, locust_request_label: str = "Reports.Feed") -> Dict[str, Any]:
        """
        Retrieves all the available "reports" and associated metadata from "Appian-Tempo-Reports"

        Note: All the retrieved data about reports is stored in the private variable self._reports

        Returns (dict): List of reports and associated metadata

        Examples:

            >>> self.appian.reports.get_all()

        """
        try:
            self.get_reports_interface(locust_request_label=locust_request_label)
            self.get_reports_nav(locust_request_label=locust_request_label)
        except Exception as e:
            log_locust_error(e, error_desc="Response Error", raise_error=False)

        uri = "/suite/rest/a/uicontainer/latest/reports"

        self._reports = dict()
        error_key_string = "ERROR::"
        error_key_count = 0

        response = self.interactor.get_page(uri=uri, label=locust_request_label)

        try:
            for current_item in response.json()['feed']['entries']:
                try:
                    title = current_item['title'].strip()
                    report_url_stub = current_item['links'][1]['href'].rsplit(
                        '/', 1)[1]
                    key = title + "::" + report_url_stub
                    self._reports[key] = current_item
                except Exception as e:
                    error_key_count += 1
                    self._reports[error_key_string + str(error_key_count)] = {}
                    log_locust_error(e, error_desc="Corrupt Report Error", location=uri, raise_error=False)
            self._errors = error_key_count
        except Exception as e:
            log_locust_error(e, error_desc="No Reports Returned", location=uri, raise_error=False)
            return self._reports
        return self._reports

    def get_report(self, report_name: str, exact_match: bool = True) -> Dict[str, Any]:
        """
        Get the information about specific report by name.

        Args:
            report_name (str): Name of the report
            exact_match (bool): Should report name match exactly or to be partial match. Default : True

        Returns (dict): Specific Report's info

        Raises: In case of report is not found in the system, it throws an "Exception"

        Example:
            If full name of report is known,

            >>> self.appian.reports.get("report_name")

            If only partial name is known,

            >>> self.appian.reports.get("report_name", exact_match=False)

        """
        _, current_report = super().get(self._reports, report_name, exact_match)
        if not current_report:
            raise (Exception("There is no report with name {} in the system under test (Exact match = {})".format(
                report_name, exact_match)))
        return current_report

    def visit(self, report_name: str, exact_match: bool = True) -> Dict[str, Any]:
        """
        This function calls the API for the specific report to get its "form" data

        Args:
            report_name (str): Name of the report to be called.
            exact_match (bool, optional): Should report name match exactly or to be partial match. Default : True

        Returns (dict): Response of report's Get UI call in dictionary

        Examples:

            If full name of report is known,

            >>> self.appian.reports.visit("report_name")

            If only partial name is known,

            >>> self.appian.reports.visit("report_name", exact_match=False)

        """

        report_under_test = self.get_report(report_name, exact_match)

        headers = self.interactor.setup_request_headers()
        headers["Accept"] = "application/vnd.appian.tv.ui+json"

        # navigation request
        tempo_site_url_stub = "D6JMim"
        uri = "/suite/rest/a/sites/latest/{}/page/reports/nav".format(
            tempo_site_url_stub)
        label = "Reports.Nav." + format_label(report_name, "::", 0)
        self.interactor.get_page(uri=uri, headers=headers, label=label)  # report request
        report_url_stub = report_under_test['links'][1]['href'].rsplit('/', 1)[1]
        uri = "/suite/rest/a/sites/latest/{}/pages/reports/report/{}/reportlink".format(tempo_site_url_stub,
                                                                                        report_url_stub)
        label = "Reports.GetUi." + format_label(report_name, "::", 0)
        resp = self.interactor.get_page(uri=uri, headers=headers, label=label)
        test_response_for_error(resp)
        resp.raise_for_status()
        return resp.json()

    def visit_and_get_form(self, report_name: str, exact_match: bool = True) -> SailUiForm:
        report_resp: dict = self.get_report(report_name, exact_match)

        tempo_site_url_stub = "D6JMim"
        report_url_stub = report_resp['links'][1]['href'].rsplit(
            '/', 1)[1]

        form_uri = f"/suite/rest/a/sites/latest/{tempo_site_url_stub}/pages/reports/report/{report_url_stub}/reportlink"
        form_json = self.visit(report_name, exact_match)

        breadcrumb = f'Reports.SailUi.{format_label(report_name, "::", 0)}'
        return SailUiForm(self.interactor, form_json, form_uri, breadcrumb=breadcrumb)
