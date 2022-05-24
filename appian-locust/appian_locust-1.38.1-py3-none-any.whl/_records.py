import json
import random
from typing import Any, Dict, Tuple

import requests

from appian_locust import logger

from ._base import _Base
from ._interactor import _Interactor
from .helper import format_label
from .records_helper import (get_all_records_from_json,
                             get_record_summary_view_response, get_records_from_json_by_column)
from .uiform import SailUiForm
from ._locust_error_handler import log_locust_error

log = logger.getLogger(__name__)

RECORDS_INTERFACE_PATH = "/suite/rest/a/sites/latest/D6JMim/pages/records/interface"
RECORDS_NAV_PATH = "/suite/rest/a/sites/latest/D6JMim/page/records/nav"


class _Records(_Base):
    def __init__(self, interactor: _Interactor) -> None:
        """
        Records class wrapping list of possible activities can be performed with Appian-Tempo-Records.

        Warnings: This class is internal and should not be accessed by tests directly. It can be accessed via the "appian" object

        Note: "appian" is created as part of ``AppianTaskSet``'s ``on_start`` function

        Args:
            session: Locust session/client object
            host (str): Host URL
        """
        self.interactor = interactor

        # When Get All functions called, these variables will be used to cache the values
        self._record_types: Dict[str, Any] = dict()
        self._records: Dict[str, Any] = dict()
        self._errors: int = 0

    def get_records_interface(self, locust_request_label: str = "Records") -> Dict[str, Any]:
        uri = self.interactor.host + RECORDS_INTERFACE_PATH
        headers = self.interactor.setup_sail_headers()
        resp = self.interactor.get_page(uri, headers, f'{locust_request_label}.Interface')
        return resp.json()

    def get_records_nav(self, locust_request_label: str = "Records") -> Dict[str, Any]:
        uri = self.interactor.host + RECORDS_NAV_PATH
        headers = self.interactor.setup_sail_headers()
        resp = self.interactor.get_page(uri, headers, f'{locust_request_label}.Nav')
        return resp.json()

    def get_all(self, search_string: str = None, locust_request_label: str = "Records") -> Dict[str, Any]:
        """
        Retrieves all available "records types" and "records" and associated metadata from "Appian-Tempo-Records"

        Note: All the retrieved data about record types and records is stored in the private variables
        self._record_types and self._records respectively

        Returns (dict): List of records and associated metadata
        """
        try:
            self.get_records_interface(locust_request_label=locust_request_label)
            self.get_records_nav(locust_request_label=locust_request_label)
        except Exception as e:
            log_locust_error(e, error_desc="Response Error", raise_error=False)

        self.get_all_record_types(locust_request_label=locust_request_label)
        for record_type in self._record_types:
            try:
                self.get_all_records_of_record_type(record_type)
            except requests.exceptions.HTTPError as e:
                log.warning(e)
                continue

        return self._records

    def get_all_record_types(self, locust_request_label: str = "Records") -> Dict[str, Any]:
        """
        Navigate to Tempo Records Tab and load all metadata for associated list of record types into cache.

        Returns (dict): List of record types and associated metadata
        """
        uri = "/suite/rest/a/applications/latest/app/records/view/all"
        self._record_types = dict()

        headers = self.interactor.setup_request_headers()
        headers['X-Appian-Features-Extended'] = 'e4bc'
        headers["Accept"] = "application/vnd.appian.tv.ui+json"
        response = self.interactor.get_page(uri=uri, headers=headers, label=locust_request_label)
        json_response = response.json()
        if not(self._is_response_good(response.text)):
            raise(Exception("Unexpected response on Get call of All Records"))

        for current_record_type in json_response["ui"]["contents"][0]["feedItems"]:
            title = current_record_type['title'].strip()
            self._record_types[title] = current_record_type
            self._records[title] = dict()

        return self._record_types

    def get_all_records_of_record_type(self, record_type: str, column_index: int = None) -> Dict[str, Any]:
        """
        Navigate to the desired record type and load all metadata for the associated list of record views into cache.

        Args:
            record_type (str): Name of record type for which we want to enumerate the record instances.
            column_index (int, optional): Column index to only fetch record links from a specific column, starts at 0.

        Returns (dict): List of records and associated metadata

        Examples:

            >>> self.appian.records.get_all_records_of_record_type("record_type_name")
        """

        json_response, _ = self._record_type_list_request(record_type)

        if column_index is not None:
            self._records[record_type], self._errors = get_records_from_json_by_column(json_response, column_index)
        else:
            self._records[record_type], self._errors = get_all_records_from_json(json_response)

        return self._records

    def get_all_records_of_record_type_mobile(self, record_type: str) -> Dict[str, Any]:
        """
        Retrieves all the available "records" for the given record type for a mobile device.

        Todo: Partial match functionality is not yet implemented

        Returns (dict): List of records and associated metadata

        Examples:

            >>> self.appian.records.get_all_records_of_record_type_mobile("record_type_name")
        """
        json_response, _ = self._record_type_list_request(record_type, is_mobile=True)

        self._records[record_type], self._errors = get_all_records_from_json(json_response)

        return self._records

    def get_all_mobile(self, search_string: str = None) -> Dict[str, Any]:
        """
        Retrieves all available "records types" and "records" and associated metadata from "Appian-Tempo-Records"

        Note: All the retrieved data about record types and records is stored in the private variables
        self._record_types and self._records respectively

        Returns (dict): List of records and associated metadata
        """
        self.get_all_record_types()
        for record_type in self._record_types:
            self.get_all_records_of_record_type_mobile(record_type)
        return self._records

    def fetch_record_instance(self, record_type: str, record_name: str, exact_match: bool = True) -> Dict[str, Any]:
        """
        Get the information about a specific record by specifying its name and its record type.

        Args:
            record_type (str): Name of the record type.
            record_name (str): Name of the record which should be available in the given record type
            exact_match (bool): Should record name match exactly or to be partial match. Default : True

        Returns (dict): Specific record's info

        Raises: In case of record is not found in the system, it throws an "Exception"

        Example:
            If full name of record type and record is known,

            >>> self.appian.records.get("record_type_name", "record_name")

            If only partial name is known,

            >>> self.appian.records.get("record_type_name", "record_name", exact_match=False)

        """

        self.fetch_record_type(record_type, exact_match=exact_match)
        _, current_record = super().get(self._records[record_type], record_name, exact_match,
                                        ignore_retry=True)
        if not current_record:
            raise Exception(f"There is no record with name {record_name} found in record type {record_type} (Exact match = {exact_match})")
        return current_record

    get_record = fetch_record_instance

    def fetch_record_type(self, record_type: str, exact_match: bool = True) -> Dict[str, Any]:
        """
            Fetch information about record type from the cache. Raises Exception if record type does not exist in cache.

        Args:
            record_type (str): Name of the record type.


        Returns (dict): Specific record type's info

        Raises: In case the record type is not found in the system, it throws an "Exception"

        Example:

            >>> self.appian.records.get_record_type("record_type_name")

        """
        _, current_record_type = super().get(self._record_types, record_type, exact_match)
        if not current_record_type:
            raise Exception(f"There is no record type with name {record_type} in the system under test (Exact match = {exact_match})")
        return current_record_type

    def visit_record_instance(self, record_type: str = "", record_name: str = "", view_url_stub: str = "", exact_match: bool = True, locust_request_label: str = "") -> Tuple[Dict[str, Any], str]:
        """
        This function calls the API for the specific record view/instance to get its response data.

        Note: This function is meant to only traverse to Record forms, not to interact with them. For that, use visit_record_instance_and_get_form()

        Args:
            record_type (str): Record Type Name. If not specified, a random record type will be selected.
            record_name (str): Name of the record to be called. If not specified, a random record will be selected.
            view_url_stub (str, optional): page/tab to be visited in the record. If not specified, "summary" dashboard will be selected.
            exact_match (bool, optional): Should record type and record name matched exactly as it is or partial match.
            locust_request_label(str,optional): Label used to identify the request for locust statistics

        Returns (tuple): Responses of Record's Get UI call in a dictionary and the request URI as a string.

        Examples:

            If full name of record type and record is known,

            >>> self.appian.records.visit_record_instance("record_type_name", "record_name", "summary")

            If only partial name is known,

            >>> self.appian.records.visit_record_instance("record_type_name", "record_name", "summary", exact_match=False)

            If a random record is desired,

            >>> self.appian.records.visit_record_instance()

            If random record of a specific record type is desired,

            >>> self.appian.records.visit_record_instance("record_type_name")

        """

        if not record_name:
            record_type, record_name = self._get_random_record_instance(record_type)

        if not record_type:
            raise Exception("If record_name parameter is specified, record_type must also be included")

        current_record = self.fetch_record_instance(record_type, record_name, exact_match)

        headers = self.interactor.setup_feed_headers()

        tempo_site_url_stub = current_record["siteUrlStub"]
        opaque_id = current_record["_recordRef"]
        record_label = current_record["label"]

        if not view_url_stub:
            dashboard_val = current_record.get("dashboard")
            view_url_stub = dashboard_val if dashboard_val else "summary"

        locust_label = locust_request_label or f'Records.{record_type}.{record_label}.{view_url_stub}'

        uri = f"/suite/rest/a/sites/latest/{tempo_site_url_stub}/page/records/record/{opaque_id}/view/{view_url_stub}"
        resp = self.interactor.get_page(uri=uri, headers=headers, label=locust_label)
        return resp.json(), uri

    # Alias for the above function to allow backwards compatability
    visit = visit_record_instance

    def visit_record_type(self, record_type: str = "", exact_match: bool = True, is_mobile: bool = False) -> Tuple[Dict[str, Any], str]:
        """
        Navigate into desired record type and retrieve all metadata for associated list of record views.

        Returns (dict): List of records and associated metadata

        Examples:

            >>> self.appian.records.visit_record_type("record_type_name")
        """

        # Make sure caches are not empty
        if not self._records or not self._record_types:
            self.get_all()

        # If no record_type is specified, a random one will be assigned
        if not record_type:
            record_type = self._get_random_record_type()

        return self._record_type_list_request(record_type, is_mobile=is_mobile)

    def visit_record_instance_and_get_feed_form(self, record_type: str = "", record_name: str = "", exact_match: bool = True) -> SailUiForm:
        """
        This function calls the API for the specific record view/instance and returns a SAILUiForm object for "feed" response.
        The returned SailUiForm object can then be used to get header response by using calling get_record_header_form(). The header form
        should have related actions available to interact with.

        Args:
            record_type (str): Record Type Name. If not specified, a random record type will be selected.
            record_name (str): Name of the record to be called. If not specified, a random record will be selected.
            exact_match (bool, optional): Should record type and record name matched exactly as it is or partial match.

        Returns: Custom SailUiForm object that can interact with Appian forms. Use this object to fill textfields, click links/buttons, etc...
        """
        # view_url_stub does not matter in case of feed response for a record instance. Feed Response for each tab on an record instance is the same
        # no matter which dashboard is selected.
        form_json, form_uri = self.visit_record_instance(record_type, record_name, view_url_stub="summary", exact_match=exact_match)
        breadcrumb = f'Records.{record_type}.{record_name}.Feed'
        return SailUiForm(self.interactor, form_json, form_uri, breadcrumb=breadcrumb)

    def visit_record_instance_and_get_form(self, record_type: str = "", record_name: str = "", view_url_stub: str = "", exact_match: bool = False) -> SailUiForm:
        """
        This function calls the API for the specific record view/instance and returns a SAIL form object that Locust users can interact with.

        Note: Since this function is enabled for interactions, it has a higher runtime than visit_record_instance()

        Args:
            record_type (str): Record Type Name. If not specified, a random record type will be selected.
            record_name (str): Name of the record to be called. If not specified, a random record will be selected.
            view_url_stub (str, optional): page/tab to be visited in the record. If not specified, "summary" dashboard will be selected.
            exact_match (bool, optional): Should record type and record name matched exactly as it is or partial match.

        Returns: Custom SailUiForm object that can interact with Appian forms. Use this object to fill textfields, click links/buttons, etc...

        Examples:

            If full name of record type and record is known,

            >>> self.appian.records.visit_and_get_form("record_type_name", "record_name", "summary")

            If only partial name is known,

            >>> self.appian.records.visit_and_get_form("record_type_name", "record_name", "summary", exact_match=False)

            If random record is desired,

            >>> self.appian.records.visit_and_get_form()

            If random record of a specific record type is desired,

            >>> self.appian.records.visit_and_get_form("record_type_name")
        """

        form_json, form_uri = self.visit_record_instance(record_type, record_name, view_url_stub=view_url_stub, exact_match=exact_match)
        # SAIL Code for the Record Summary View is embedded within the response.
        embedded_record_resp = get_record_summary_view_response(form_json)
        breadcrumb = f'Records.{record_type}.{format_label(record_name, "::", 0)}.SailUi'
        return SailUiForm(self.interactor, json.loads(embedded_record_resp), form_uri, breadcrumb=breadcrumb)

    visit_and_get_form = visit_record_instance_and_get_form

    def visit_record_type_and_get_form(self, record_type: str = "", exact_match: bool = False, is_mobile: bool = False) -> SailUiForm:
        """
        This function calls the API for the specific record typew and returns a SAIL form object that Locust users can interact with.

        Note: Since this function is enabled for interactions, it has a higher runtime than visit_record_type()

        Args:
            record_type (str): Record Type Name. If not specified, a random record type will be selected.
            exact_match (bool, optional): Should record type and record name matched exactly as it is or partial match.

        Returns: Custom SailUiForm object that can interact with Appian forms. Use this object to fill textfields, click links/buttons, etc...

        Examples:

            If the full name of record type is known,

            >>> self.appian.records.visit_record_type_and_get_form("record_type_name")

            If only partial name is known,

            >>> self.appian.records.visit_record_type_and_get_form("record_type_name", exact_match=False)

            If random record type is desired,

            >>> self.appian.records.visit_record_type_and_get_form()
        """
        if not self._records or not self._record_types:
            self.get_all()
        form_json, form_uri = self.visit_record_type(record_type, exact_match=exact_match, is_mobile=is_mobile)
        breadcrumb = f'Records.{record_type}.SailUi'
        return SailUiForm(self.interactor, form_json, form_uri, breadcrumb=breadcrumb)

        # ----- Private Functions ----- #

    def _is_response_good(self, response_text: str) -> bool:
        return ('"rel":"x-web-bookmark"' in response_text or '"#t":"CardLayout"' in response_text)

    def _get_random_record_instance(self, record_type: str = "") -> Tuple[str, str]:
        if not self._records or not self._record_types:
            self.get_all()
        if not record_type:
            record_type = self._get_random_record_type()
        record_name = random.choice(list(self._records[record_type].keys()))
        return record_type, record_name

    def _get_random_record_type(self) -> str:
        if not self._records or not self._record_types:
            self.get_all()
        return random.choice(list(self._records.keys()))

    def _record_type_list_request(self, record_type: str, is_mobile: bool = False) -> Tuple[Dict[str, Any], str]:
        if record_type not in self._record_types:
            raise Exception(f"There is no record type with name {record_type} in the system under test")
        record_type_component = self._record_types[record_type]
        record_type_url_stub = record_type_component['link']['value']['urlstub']

        if is_mobile:
            uri = self._get_mobile_records_uri(record_type_url_stub)
        else:
            tempo_site_url_stub = "D6JMim"
            uri = f"/suite/rest/a/sites/latest/{tempo_site_url_stub}/pages/records/recordType/{record_type_url_stub}"

        label = f"Records.{record_type}"
        headers = self.interactor.setup_request_headers()
        headers["Accept"] = "application/vnd.appian.tv.ui+json"
        response = self.interactor.get_page(uri=uri, headers=headers, label=label)
        json_response = response.json()

        return json_response, uri

    def _get_mobile_records_uri(self, record_type_url_stub: str) -> str:
        if not record_type_url_stub:
            raise Exception("Mobile records uri must have a unique stub provided.")
        return f"/suite/rest/a/applications/latest/legacy/tempo/records/type/{record_type_url_stub}/view/all"
