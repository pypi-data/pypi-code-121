import enum
import json
import random
from typing import Any, Dict, List, Union

from requests import Response

from . import logger
from ._base import _Base
from ._interactor import _Interactor
from .helper import extract_values, format_label
from .records_helper import (get_all_records_from_json,
                             get_record_summary_view_response)
from .uiform import SailUiForm

log = logger.getLogger(__name__)


class _Sites(_Base):
    TEMPO_SITE_PAGE_NAV = "/suite/rest/a/sites/latest/D6JMim/page/news/nav"
    BROWSER_ACCEPT_HEADER = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"

    def __init__(self, interactor: _Interactor) -> None:
        """
        Sites class wrapping a list of possible activities that can be performed with the Appian Sites Environment

        Warnings: This class is internal and should not be accessed by tests directly. It can be accessed via the "appian" object

        Note: "appian" is created as part of ``AppianTaskSet``'s ``on_start`` function

        Args:
            session: Locust session/client object
            host (str): Host URL

        """
        self.interactor = interactor

        self._sites: Dict[str, Site] = {}
        self._sites_records: Dict[str, Dict[str, Any]] = {}

    def navigate_to_tab(self, site_name: str, page_name: str) -> Response:
        """
        Navigates to a site page, either a record, action or report.

        Args:
            site_name: Site Url stub
            page_name: Page Url stub

        Returns: Response of report/action/record
        """
        if site_name not in self._sites:
            self.get_site_data_by_site_name(site_name)

        if site_name not in self._sites:
            raise SiteNotFoundException(f"The site with name '{site_name}' could not be found")
        site: Site = self._sites[site_name]
        if page_name not in [page.page_name for page in site.pages.values()]:
            raise PageNotFoundException(f"The site with name '{site_name}' does not contain the page {page_name}")
        page = site.pages[page_name]
        page_type = page.page_type.value

        headers = self._setup_headers_with_sail_json()

        self.interactor.get_page(f"/suite/rest/a/sites/latest/{site_name}/page/{page_name}/nav", headers=headers,
                                 label=f"Sites.{site_name}.{page_name}.Nav")
        resp = self.interactor.get_page(f"/suite/rest/a/sites/latest/{site_name}/pages/{page_name}/{page_type}", headers=headers,
                                        label=f"Sites.{site_name}.{page_name}.Ui")
        return resp

    def navigate_to_tab_and_record_if_applicable(self, site_name: str, page_name: str) -> Response:
        """
        Navigates to a site page, either a record, interface, action or report.
        If a record, then clicks on a random record on the first page.

        Note: Any record available in the record list as a recordLink will be hit using this function.  There is no
        guarantee that this record will be of any specific type and may not point to a record view.

        Args:
            site_name: Site Url stub
            page_name: Page Url stub

        Returns: Response of report/action, or in the case of a record, response of record object
        """
        resp = self.navigate_to_tab(site_name, page_name)
        if not self._sites[site_name].pages[page_name].page_type == PageType.RECORD:
            return resp
        headers = self._setup_headers_with_sail_json()
        if page_name not in self._sites_records:
            records_for_page, errors = get_all_records_from_json(resp.json())
            self._sites_records[page_name] = records_for_page
        records = list(self._sites_records[page_name])
        if not records:
            log.error(f"No records found for site={site_name}, page={page_name}")
            return resp
        record_key = random.choice(list(self._sites_records[page_name]))
        label = f"Sites.{site_name}.{page_name}." + format_label(record_key, "::", 0)[:30]
        record_id = record_key.split("::")[1]
        record_resp = self.interactor.get_page(
            f"/suite/sites/{site_name}/page/{page_name}/nav",
            headers=headers,
            label=label + ".Nav")
        # TODO: Add ability to go to arbitrary stubs
        headers = self.interactor.setup_feed_headers()
        record_resp = self.interactor.get_page(
            f"/suite/rest/a/sites/latest/{site_name}/page/{page_name}/record/{record_id}/view/summary",
            headers=headers,
            label=label + ".View")
        return record_resp

    def navigate_to_tab_and_record_get_form(self, site_name: str, page_name: str) -> SailUiForm:
        """
        Navigates to a site page, either a record, action or report.
        If it is a record, then clicks on a random record instance on the first page

        Args:
            site_name: Site Url stub
            page_name: Page Url stub

        Returns: SailUiForm of a report/action, or in the case of a record, SailUiForm of a record instance
        """

        site_page_response: Response = self.navigate_to_tab_and_record_if_applicable(site_name, page_name)
        form_uri = site_page_response.request.path_url
        site_page_json_response = site_page_response.json()
        if site_page_json_response.get("feed"):
            record_view_response = get_record_summary_view_response(site_page_json_response)
            breadcrumb = f"Sites.{site_name}.{page_name}.SailUi"
            return SailUiForm(self.interactor, json.loads(record_view_response), form_uri, breadcrumb=breadcrumb)
        else:
            breadcrumb = f"Sites.{site_name}.{page_name}.SailUi"
            return SailUiForm(self.interactor, site_page_json_response, form_uri, breadcrumb=breadcrumb)

    def get_all(self, search_string: str = None, locust_request_label: str = None) -> Dict[str, Any]:
        """
        Gets and stores data for all sites, including all of their url stubs
        """
        headers = self._setup_headers_with_sail_json()
        all_site_resp = self.interactor.get_page(_Sites.TEMPO_SITE_PAGE_NAV, headers=headers, label="Sites.SiteNames")
        all_site_json = all_site_resp.json()
        for site_info in extract_values(all_site_json, '#t', 'SitePageLink'):
            if 'siteUrlStub' in site_info:
                site_url_stub = site_info['siteUrlStub']
                self.get_site_data_by_site_name(site_url_stub)
        return self._sites

    def get_site_data_by_site_name(self, site_name: str) -> Union['Site', None]:
        """
        Gets site data from just the site url stub

        Args:
            site_name: Site url stub
        Returns: Site object, containing the site name and pages
        """
        headers = self._setup_headers_with_accept()
        # First get site pages
        initial_nav_resp = self.interactor.get_page(f"/suite/rest/a/sites/latest/{site_name}/nav",
                                                    headers=headers,
                                                    label=f"Sites.{site_name}.Nav")
        initial_nav_json = initial_nav_resp.json()
        ui = initial_nav_json['ui']

        display_name = ui.get('siteName')

        # Invalid case
        if not display_name:
            log.error(f"JSON response for navigating to site '{site_name}' was invalid")
            return None

        pages_names = self.get_page_names_from_ui(initial_nav_json)
        site = self._get_and_memoize_site_data(site_name, display_name, pages_names)
        return site

    def get_page_names_from_ui(self, initial_nav_json: Dict[str, Any]) -> List[str]:
        """
        Extracts page names from the nav json

        Args:
            initial_nav_json: JSON from navigating to site tab
        Returns: List of string, representing the page names
        """
        ui = initial_nav_json['ui']
        pages_names = [node['link']['pageUrlStub'] for node in ui['tabs']]
        return pages_names

    def get_site_page(self, site_name: str, page_name: str) -> Union['Page', None]:
        """
        Gets site page from the site url stub and page url stub

        Args:
            site_name: Site url stub
            page_name: Page url stub
        Returns: Page object, representing an individual page of a site
        """
        headers = self._setup_headers_with_sail_json()
        headers['X-Appian-Features-Extended'] = 'e4bc'  # Required by legacy url to return successfully
        page_resp = self.interactor.get_page(f"/suite/rest/a/applications/latest/legacy/sites/{site_name}/page/{page_name}",
                                             headers=headers,
                                             label=f"Sites.{site_name}.{page_name}.Nav")
        page_resp_json = page_resp.json()
        if 'redirect' not in page_resp_json:
            log.error(f"Could not find page data with a redirect for site {site_name} page {page_name}")
            return None
        link_type_raw = page_resp_json['redirect']['#t']
        page_type = self._get_type_from_link_type(link_type_raw)
        return Page(page_name, page_type)

    def visit_and_get_form(self, site_name: str, page_name: str) -> 'SailUiForm':
        """
        Get a SailUiForm for a Task, Report or Action

        Args:
            site_name(str): Site where the page exists
            page_name(str): Page to navigate to

        Returns: SailUiForm

        Example:
            >>> self.appian.sites.visit_and_get_form("site_name","page_name")

        """
        resp: Response = self.navigate_to_tab(site_name, page_name)
        form_uri = resp.request.path_url
        form_json = resp.json()

        breadcrumb = f"Sites.{site_name}.{page_name}.SailUi"
        return SailUiForm(self.interactor, form_json, form_uri, breadcrumb=breadcrumb)

    def _get_and_memoize_site_data(self, site_name: str, display_name: str, pages_names: List[str]) -> 'Site':
        pages = {}
        for page_name in pages_names:
            page = self.get_site_page(site_name, page_name)
            if page:
                pages[page_name] = page

        site = Site(site_name, display_name, pages)
        self._sites[site_name] = site
        return site

    def _get_type_from_link_type(self, link_type: str) -> 'PageType':
        if "InternalActionLink" in link_type:
            return PageType.ACTION
        elif "InternalReportLink" in link_type:
            return PageType.REPORT
        elif "SiteRecordTypeLink" in link_type:
            return PageType.RECORD
        elif "SiteInterfaceLink" in link_type:
            return PageType.INTERFACE
        else:
            raise Exception(f"Invalid Link Type: {link_type}")

    def _setup_headers_with_accept(self) -> dict:
        headers = self.interactor.setup_request_headers()
        headers["Accept"] = self.BROWSER_ACCEPT_HEADER
        return headers

    def _setup_headers_with_sail_json(self) -> dict:
        headers = self.interactor.setup_sail_headers()
        headers["Accept"] = "application/vnd.appian.tv.ui+json"
        return headers


class PageType(enum.Enum):
    ACTION: str = "action"
    REPORT: str = "report"
    RECORD: str = "recordType"
    INTERFACE: str = "interface"


class SiteNotFoundException(Exception):
    pass


class PageNotFoundException(Exception):
    pass


class Site:
    """
    Class representing a single site, as well as its pages
    """

    def __init__(self, name: str, display_name: str, pages: Dict[str, 'Page']):
        self.name = name
        self.display_name = display_name
        self.pages = pages

    def __str__(self) -> str:
        return f"Site(name={self.name},pages=[{self.pages}])"

    def __repr__(self) -> str:
        return self.__str__()


class Page:
    """
    Class representing a single Page within a site
    """

    def __init__(self, page_name: str, page_type: 'PageType') -> None:
        self.page_name = page_name
        self.page_type = page_type

    def __str__(self) -> str:
        return f"Page(name={self.page_name},type={self.page_type})"

    def __repr__(self) -> str:
        return self.__str__()
