import json
import os
import sys
import time
import urllib.parse
from datetime import date, datetime
from re import match, search
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from locust.clients import HttpSession, ResponseContextManager
from requests import Response

from . import logger
from ._locust_error_handler import log_locust_error, test_response_for_error
from ._save_request_builder import save_builder
from .exceptions import BadCredentialsException, MissingCsrfTokenException, ComponentNotFoundException
from .helper import find_component_by_attribute_in_dict, get_username
from .records_helper import get_url_stub_from_record_list_post_request_url

log = logger.getLogger(__name__)

# TODO: Consider breaking this class up into smaller pieces


RECORD_PATH = "recorded_responses"


class _Interactor:
    def __init__(self, session: HttpSession, host: str, portals_mode: bool = False) -> None:
        """
        Class that represents interactions with the UI and Appian system
        If you want to record all requests made, you can set the record_mode attribute
        on the client, see the mock_client.py in the tests directory as an example

        >>> setattr(self.client, 'record_mode', True)

        Args:
            session: Locust session/client object
            host (str): Host URL inherited from subclass to conform with Mypy standards
            portals_mode (bool): Set to true if attempting to connect to a portals site
        """
        self.client = session
        self.host = host
        self.record_mode = True if hasattr(self.client, "record_mode") else False
        self.datatype_cache = DataTypeCache()
        self.user_agent = ""
        self.portals_mode = portals_mode
        # Set to default as desktop request.
        self.set_user_agent_to_desktop()

    # GENERIC UTILITY METHODS
    def set_user_agent_to_desktop(self) -> None:
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"

    def set_user_agent_to_mobile(self) -> None:
        self.user_agent = "AppianAndroid/20.2 (Google AOSP on IA Emulator, 9; Build 0-SNAPSHOT; AppianPhone)"

    def setup_request_headers(self, uri: str = None) -> dict:
        """
        Generates standard headers for session

        Args:
            uri (str): URI to be assigned as the Referer

        Returns (dict): headers

        Examples:

            >>> self.appian.interactor.setup_request_headers()
        """

        uri = uri if uri is not None else self.host
        headers = {
            "Accept": "application/atom+json,application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en_US",
            "Connection": "keep-alive",
            "User-Agent": self.user_agent,
            "Referer": uri + "/suite/tempo/",
            "X-Appian-Cached-Datatypes": self.datatype_cache.get(),
            "Cookie": "JSESSIONID={}; __appianCsrfToken={}; __appianMultipartCsrfToken={}".format(
                self.client.cookies.get("JSESSIONID", ""),
                self.client.cookies.get("__appianCsrfToken", ""),
                self.client.cookies.get("__appianMultipartCsrfToken", ""),
            ),
            "DNT": "1",
            "X-APPIAN-CSRF-TOKEN": self.client.cookies.get("__appianCsrfToken", ""),
            "X-APPIAN-MP-CSRF-TOKEN": self.client.cookies.get("__appianMultipartCsrfToken", ""),
            "X-Appian-Ui-State": "stateful",
            "X-Appian-Features": self.client.feature_flag,
            "X-Appian-Features-Extended": self.client.feature_flag_extended,
            "x-libraries-suppress-www-authenticate": "true",
            # this should probably go...
            "X-Atom-Content-Type": "application/html",
        }
        if self.portals_mode:
            headers["X-client-mode"] = "SERVERLESS"

        return headers

    def setup_sail_headers(self) -> dict:
        headers = self.setup_request_headers()
        headers.update({'Content-Type': 'application/vnd.appian.tv+json',
                        'Accept': 'application/vnd.appian.tv.ui+json'})
        return headers

    # Headers needed for Record View request, which returns a feed object
    def setup_feed_headers(self) -> dict:
        headers = self.setup_request_headers()
        headers["Accept"] = "application/atom+json; inlineSail=true; recordHeader=true"
        headers["Accept"] = headers["Accept"] + ", application/json; inlineSail=true; recordHeader=true"
        return headers

    def setup_content_headers(self) -> dict:
        headers = self.setup_request_headers()
        headers["Accept"] = "*/*"
        return headers

    def replace_base_path_if_appropriate(self, uri: str) -> str:
        if hasattr(self.client, "base_path_override") and self.client.base_path_override and \
                self.client.base_path_override != '/suite':
            return uri.replace('/suite', self.client.base_path_override, 1)
        return uri

    def post_page(self, uri: str, payload: Any = {}, headers: Dict[str, Any] = None, label: str = None,
                  files: dict = None, check_login: bool = True) -> Response:
        """
        Given a uri, executes POST request and returns response

        Args:
            uri: API URI to be called
            payload: Body of the API request. Can be either JSON or text input to allow for different payload types.
            headers: header for the REST API Call
            label: the label to be displayed by locust

        Returns: Json response of post operation

        """

        if headers is None:
            headers = self.setup_sail_headers()

        uri = self.replace_base_path_if_appropriate(uri)
        username = "No-auth User" if self.portals_mode else get_username(self.auth)
        if files:  # When a file is specified, don't send any data in the 'data' field
            post_payload = None
        elif isinstance(payload, dict):
            post_payload = json.dumps(payload).encode()
        elif isinstance(payload, str):
            post_payload = payload.encode()
        else:
            log_locust_error(Exception("Cannot POST a payload that is not of type dict or string"))
            sys.exit(1)
        with self.client.post(uri, data=post_payload, headers=headers, name=label, files=files,
                              catch_response=True) as resp:  # type: ResponseContextManager
            try:
                test_response_for_error(resp, uri, raise_error=check_login, username=username)
            except Exception as e:
                raise e
            else:
                if check_login:
                    resp.raise_for_status()
            if self.record_mode:
                self.write_response_to_lib_folder(label, resp)
            return resp

    def login(self, auth: list = None, retry: bool = True, check_login: bool = True) -> Tuple[HttpSession, Response]:
        if auth is not None:
            self.auth = auth
        """
        Login to Appian Tempo using given auth

        Args:
            auth: list containing 2 elements. username and password

        Returns: Locust client and response
        """

        uri = self.host + "/suite/"

        # load initial page to get tokens/cookies
        token_uri = uri + '?signin=native'
        resp = self.get_page(token_uri, label="Login.LoadUi", check_login=False)
        log.info(f"Attempting to load page {self.replace_base_path_if_appropriate(token_uri)}")
        payload = {
            "un": self.auth[0],
            "pw": self.auth[1],
            "_spring_security_remember_me": "on",
            "X-APPIAN-CSRF-TOKEN": resp.cookies["__appianCsrfToken"],
        }

        # override headers for login use case
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "Referer": self.host,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        }
        login_url = uri + "auth?appian_environment=tempo"
        log.info(f"Logging in at {self.replace_base_path_if_appropriate(login_url)}")
        log.info(f"Logging in with user {payload['un']}")
        # Post Auth
        resp = self.post_page(
            login_url,
            payload=urllib.parse.urlencode(payload),
            headers=headers,
            label="Login.SubmitAuth",
            check_login=check_login)
        if not resp or not resp.ok:
            raise BadCredentialsException()
        elif "__appianMultipartCsrfToken" not in self.client.cookies:
            if retry:
                log.info("__appianMultipartCsrfToken not found, retrying login")
                time.sleep(1)
                return self.login(auth, retry=False)
            else:
                raise MissingCsrfTokenException(self.client.cookies)
        return self.client, resp

    def check_login(self, resp: ResponseContextManager) -> None:
        """
        Given a response, checks to see if it's possible that we are not logged in and then performs a login if we are not

        Args:
            resp: Response to check

        Returns: None
        """
        is_login_page = '__appianCsrfToken' in resp.cookies
        if resp.ok and is_login_page:
            self.login()
        elif not resp.ok:
            # Check login page actually returns a csrf token
            login_page_resp = self.get_page('/suite/', label="Login.LoadUi", check_login=False)
            if login_page_resp.ok and '__appianCsrfToken' in login_page_resp.cookies:
                self.login()

    def get_page(self, uri: str, headers: Optional[Dict[str, Any]] = None, label: str = None,
                 check_login: bool = True) -> Response:
        """
        Given a uri, executes GET request and returns response

        Args:
            uri: API URI to be called
            headers: header for the REST API Call
            label: the label to be displayed by locust
            check_login: optional boolean to bypass checking if we are logged in

        Returns: Json response of GET operation
        """
        if headers is None:
            if self.portals_mode:
                headers = self.setup_sail_headers()
            else:
                headers = self.setup_request_headers(uri)
        kwargs: Dict[str, Any] = {'name': label, 'catch_response': True}

        uri = self.replace_base_path_if_appropriate(uri)
        if headers is not None:
            kwargs['headers'] = headers
        with self.client.get(uri, **kwargs) as resp:  # type: ResponseContextManager
            if check_login and not self.portals_mode:
                self.check_login(resp)
            if not self.portals_mode:
                username = get_username(self.auth)
                test_response_for_error(resp, uri, raise_error=check_login, username=username)
            if self.record_mode:
                self.write_response_to_lib_folder(label, resp)
            return resp

    def get_webapi(self, uri: str, headers: Dict[str, Any] = None, label: str = None,
                   queryparameters: Dict[str, Any] = {}) -> Response:
        """
        Same as ``get_page``. Additionally it accepts the query parameter to add query parameter while running "GET" operation
        Args:
            uri: API URI to be called
            headers: header for the REST API Call
            label: the label to be displayed by locust
            queryparameters: Queries/Filters

        Returns: Json response of GET operation

        To set custom headers

        >>> headers = self.appian.interactor.setup_request_headers()
        ... headers['Is-Admin'] = 'true'
        ... self.appian.interactor.get_webapi('/suite/webapi/headers', headers=headers)

        To set custom query parameters

        >>> params = {'age': 5, 'start-date': '10-05-2020'}
        ... self.appian.interactor.get_webapi('/suite/webapi/query', queryparameters=params)
        """
        querystring = []
        for k, v in queryparameters.items():
            querystring.append("{}={}".format(k, v))

        uri += "?" + "&".join(querystring)
        resp = self.get_page(uri, headers=headers, label=label)
        return resp

    def upload_document_to_server(self, file_path: str, is_encrypted: bool = False) -> int:
        '''
        Uploads a document to the server, so that it can be used in upload fields
        Args:
            uri: API URI to be called
            file_path: Path to the file to be uploaded

        Returns: Document Id that can be used for upload fields
        ''',

        # Override default headers to avoid sending SAIL headers here
        headers = self.setup_request_headers()
        if is_encrypted:
            headers['encrypted'] = 'true'
        with open(file_path, 'rb') as f:
            resp_label = "Document.Upload." + os.path.basename(file_path).strip(" .")
            files = {"file": f}
            response = self.post_page(
                "/suite/api/tempo/file?validateExtension=false",
                headers=headers,
                label=resp_label,
                files=files)
            if self.record_mode:
                self.write_response_to_lib_folder(resp_label, response)
            else:
                response.raise_for_status()
            doc_id = response.json()[0]["id"]
            return doc_id

    def write_response_to_lib_folder(self, label: Optional[str], response: Response) -> None:
        """
        Used for internal testing, to grab the response and put it in a file of type JSON

        Args:
            label(Optional[str]): Optional label, used to name the file
            response(Response): Response object to write to a file

        Writes to a recorded_responses folder from wherever you run locust
        """
        cleaned_label = label.replace("/", "|") if label else "response"
        file_name = cleaned_label + " " + str(datetime.now())
        file_ending = ".json"
        if not os.path.exists(RECORD_PATH):
            os.mkdir(RECORD_PATH)
        proposed_request_file_name = os.path.join(RECORD_PATH, file_name + "_REQUEST" + file_ending).replace(' ', '_')
        proposed_response_file_name = os.path.join(RECORD_PATH, file_name + "_RESPONSE" + file_ending).replace(' ', '_')
        if response.request.body:
            body = response.request.body
            if isinstance(body, bytes):
                with open(proposed_request_file_name, 'wb') as req_bytes_file:
                    req_bytes_file.write(body)
            elif isinstance(body, str):
                with open(proposed_request_file_name, 'w') as req_str_file:
                    req_str_file.write(body)
        with open(proposed_response_file_name, 'w') as resp_text_file:
            resp_text_file.write(response.text)
        if 'X-Trace-Id' in response.headers:
            log.info(cleaned_label + ' | X-Trace-Id: ' + response.headers['X-Trace-Id'])

    def click_record_link(self, get_url: str, component: Dict[str, Any], context: Dict[str, Any],
                          label: str = None, headers: Dict[str, Any] = None, locust_label: str = "") -> Dict[str, Any]:
        '''
        Use this function to interact specifically with record links, which represent links to new sail forms.
        Args:
            get_url: the url (not including the host and domain) to navigate to
            component: the JSON code for the RecordLink
            context: the Sail context parsed from the json response
            label: the label to be displayed by locust for this action
            headers: header for the REST API call

        Returns: the response of get RecordLink operation as json
        '''

        # The record links in record instance view tabs are 1 level further down
        if '_recordRef' not in component:
            # This is probably a record view link with the link information 1 level further down
            component = component.get('link', "")
        record_ref = component.get('_recordRef', "")

        # Support record views other than /summary by checking the dashboard attribute
        dashboard = component.get('dashboard', "")
        if not dashboard:
            dashboard = "summary"
        record_view_url_stub = f"/view/{dashboard}"
        if not record_ref:
            e = Exception("Cannot find _recordRef attribute in RecordLink component.")
            log_locust_error(e, raise_error=True)
        record_link_url_suffix = record_ref + record_view_url_stub

        # Logic to construct record link URL in tempo and sites
        if "tempo" in get_url:
            record_link_url = "/suite/tempo/records/item/" + record_link_url_suffix
        elif "sites" in get_url and "/record/" in get_url:
            parse_pattern = "/record/"
            record_link_url = get_url[:get_url.index(parse_pattern) + len(parse_pattern)] + record_link_url_suffix
        elif match(r'.*\/page\/\w+$', get_url):
            record_link_url = get_url + "/record/" + record_link_url_suffix
        # Support record links on site pages
        elif "sites" in get_url and "/report" in get_url and "/pages/" in get_url:
            page_search = search(r'(?<=\/pages\/)\w+', get_url)
            if page_search:
                page_name = page_search.group()
            else:
                e = Exception("Unexpected record link URL - couldn't find page name after /pages/")
                log_locust_error(e, raise_error=True)
            parse_pattern = page_name + "/report"
            url_prefix_index = get_url.index(parse_pattern) + len(page_name)
            # record_link_url = get_url[:get_url.index(parse_pattern) + len(page_name)].replace("/pages/",
            record_link_url = get_url[:url_prefix_index].replace("/pages/",
                                                                 "/page/") + "/record/" + record_link_url_suffix
        # Support record view links from a record within a site
        # Also supports record links on a task form (ex: /suite/rest/a/task/latest/JaUHEhaQ1jI7OMif0L/form)
        # Most urls will get caught here
        elif "record" in get_url or "task" in get_url:
            site_name = component.get('siteUrlStub', "")
            page_name = component.get('pageUrlStub', "")
            record_link_url = f"/suite/rest/a/sites/latest/{site_name}/page/{page_name}/record/{record_link_url_suffix}"
        else:
            e = Exception("Unexpected record link URL")
            log_locust_error(e, raise_error=True)

        if not get_url or not record_link_url:
            e = Exception("Cannot make Record Link request.")
            log_locust_error(e, raise_error=True)

        # Clicking a record link returns a record instance feed - use setup_feed_headers to get the correct headers
        headers = self.setup_feed_headers()

        locust_label = locust_label or "Clicking RecordLink: " + component["label"]

        resp = self.get_page(
            self.host + record_link_url, headers=headers, label=locust_label
        )
        return resp.json()

    def click_start_process_link(self, component: Dict[str, Any], process_model_opaque_id: str,
                                 cache_key: str, site_name: str, page_name: str, is_mobile: bool = False,
                                 locust_request_label: str = None) -> Dict[str, Any]:
        '''
        Use this function to interact with start process links, which start a process and return the
        start form.
        Args:
            component: the JSON representing the Start Process Link
            process_model_opaque_id: opaque id for the process model of the Start Process Link
            cache_key: cachekey for the start process link
            site_name: name of site for link in starting process model.
            page_name: name of page for link in starting process model.
            is_mobile: indicates if it should hit the mobile endpoint.
            locust_request_label: label to be used within locust

        Returns: the response of get Start Process Link operation as json
        '''
        if is_mobile:
            spl_link_url = f"/suite/rest/a/model/latest/startProcess/{process_model_opaque_id}?cacheKey={cache_key}"
        else:
            spl_link_url = f"/suite/rest/a/sites/latest/{site_name}/page/{page_name}/startProcess/{process_model_opaque_id}?cacheKey={cache_key}"

        headers = self.setup_sail_headers()
        locust_label = locust_request_label or "Clicking StartProcessLink: " + component["label"]
        resp = self.post_page(
            self.host + spl_link_url, payload={}, headers=headers, label=locust_label
        )
        return resp.json()

    def click_related_action(self, component: Dict[str, Any], record_type_stub: str, opaque_record_id: str,
                             opaque_related_action_id: str, locust_request_label: str = "", open_in_a_dialog: bool = False) -> Dict[str, Any]:
        '''
        Use this function to interact with related action links, which start a process and return the
        start form.
        This can handle both relation actions and related action links that open in a dialog.

        Args:
            component: the JSON representing the Related Action Link
            record_type_stub: record type stub for the record
            opaque_record_id: opaque id for the record
            opaque_related_action_id: opaque id for the related action
            locust_request_label: label to be used within locust
            open_in_a_dialog: Does this link open in a dialog

        Returns: the start form for the related action
        '''

        locust_label = locust_request_label or "Clicking RelatedActionLink: " + component["label"]
        headers = self.setup_request_headers()

        if open_in_a_dialog:
            # This link opens a dialog on the browser
            headers["Accept"] = "application/vnd.appian.tv.ui+json"
            related_action_link_url = f"/suite/rest/a/record/latest/{opaque_record_id}/actionDialog/{opaque_related_action_id}"
            resp = self.get_page(
                self.host + related_action_link_url, headers=headers, label=locust_label
            )
        else:
            # Mobile url not implemented
            # Web url:
            related_action_link_url = f"/suite/rest/a/record/latest/{record_type_stub}/{opaque_record_id}/actions/{opaque_related_action_id}"
            headers = self.setup_sail_headers()
            resp = self.get_page(
                self.host + related_action_link_url, headers=headers, label=locust_label
            )
            json_response = resp.json()
            if json_response.get("empty") == "true" and json_response.get("ui") is None:
                # This means we need to make the POST call to get the UI for the form.
                resp = self.post_page(
                    self.host + related_action_link_url, payload={}, headers=headers, label=locust_label
                )
            else:
                return json_response
        return resp.json()

    # COMPONENT RELATED METHODS

    def click_component(self, post_url: str, component: Dict[str, Any], context: Dict[str, Any],
                        uuid: str, label: str = None, headers: Dict[str, Any] = None,
                        client_mode: str = None) -> Dict[str, Any]:
        '''
            Calls the post operation to click certain SAIL components such as Buttons and Dynamic Links

            Args:
                post_url: the url (not including the host and domain) to post to
                component: the JSON code for the desired component
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                label: the label to be displayed by locust for this action
                headers: header for the REST API call

            Returns: the response of post operation as json
        '''
        if "link" in component:
            wrapper_label = component["label"]
            component = component["link"]
            component["label"] = wrapper_label

        payload = save_builder() \
            .component(component) \
            .context(context) \
            .uuid(uuid) \
            .build()

        locust_label = label or f'Click \'{component["label"]}\' Component'

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    # Aliases for click_component to preserve backwards compatibiltiy and increase readability
    click_button = click_component
    click_link = click_component

    def send_dropdown_update(self, post_url: str, dropdown: Dict[str, Any], context: Dict[str, Any],
                             uuid: str, index: int, label: str = None, url_stub: str = None) -> Dict[str, Any]:
        '''
            Calls the post operation to send an update to a dropdown

            Args:
                post_url: the url (not including the host and domain) to post to
                dropdown: the JSON code for the desired dropdown
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                index: location of the dropdown value
                label: the label to be displayed by locust for this action
                headers: header for the REST API call
                url_stub: the URL stub for the page; only required to interact with user filter dropdowns on a record list

            Returns: the response of post operation as json
        '''
        new_value = {
            "#t": "Integer",
            "#v": index
        }
        # url_stub should only be populated if the page is a record list
        url_stub = url_stub or get_url_stub_from_record_list_post_request_url(post_url)
        payload = save_builder() \
            .component(dropdown) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .record_url_stub(url_stub) \
            .build()

        locust_label = label or f'Select \'{dropdown["label"]}\' Dropdown'

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def send_multiple_dropdown_update(self, post_url: str, multi_dropdown: Dict[str, Any], context: Dict[str, Any],
                                      uuid: str, index: List[int], label: str = None, url_stub: str = None) -> Dict[str, Any]:
        '''
            Calls the post operation to send an update to a multiple dropdown

            Args:
                post_url: the url (not including the host and domain) to post to
                dropdown: the JSON code for the desired dropdown
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                index: locations of the multiple dropdown value
                label: the label to be displayed by locust for this action
                headers: header for the REST API call
                url_stub: the URL stub for the page; only required to interact with user filter dropdowns on a record list

            Returns: the response of post operation as json
        '''
        new_value = {
            "#t": "Integer?list",
            "#v": index
        }
        # url_stub should only be populated if the page is a record list
        url_stub = url_stub or get_url_stub_from_record_list_post_request_url(post_url)
        payload = save_builder() \
            .component(multi_dropdown) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .record_url_stub(url_stub) \
            .build()

        locust_label = label or f'Select \'{multi_dropdown["label"]}\' Dropdown'

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def get_primary_button_payload(self, page_content_in_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finds the primary button from the page content response and creates the payload which can be used to simulate a click

        Args:
            page_content_in_json: full page content that has a primary button

        Returns: payload of the primary button

        """
        primary_button = page_content_in_json["ui"]["contents"][0]["buttons"]["primaryButtons"][0]
        primary_button["#t"] = "ButtonWidget"
        context = page_content_in_json["context"]
        uuid = page_content_in_json["uuid"]
        payload = save_builder() \
            .component(primary_button) \
            .context(context) \
            .uuid(uuid) \
            .build()

        return payload

    def fill_textfield(self, post_url: str, text_field: Dict[str, Any], text: str,
                       context: Dict[str, Any], uuid: str, label: str = None) -> Dict[str, Any]:
        """
        Fill a TextField with the given text
        Args:
            post_url: the url (not including the host and domain) to post to
            text_field: the text field component returned from find_component_by_attribute_in_dict
            text: the text to fill into the text field
            context: the Sail context parsed from the json response
            uuid: the uuid parsed from the json response
            label: the label to be displayed by locust for this action

        Returns: the response of post operation as json

        """
        new_value = {"#t": "Text", "#v": text}
        payload = save_builder() \
            .component(text_field) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = label or f'Fill \'{text_field["label"]}\' TextField'

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def fill_pickerfield_text(self, post_url: str, picker_field: Dict[str, Any], text: str,
                              context: Dict[str, Any], uuid: str, label: str = None) -> Dict[str, Any]:
        """
        Fill a Picker field with the given text and randomly select one of the suggested item
        Args:
            post_url: the url (not including the host and domain) to post to
            picker_field: the picker field component returned from find_component_by_attribute_in_dict
            text: the text to fill into the picker field
            context: the SAIL context parsed from the json response
            uuid: the uuid parsed from the json response
            label: the label to be displayed by locust for this action

        Returns: the response of post operation as json

        """
        new_value = {
            "#t": "PickerData",
            "typedText": text
        }

        payload = save_builder() \
            .component(picker_field) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = label or f'Fill \'{picker_field["label"]}\' PickerField'

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def select_pickerfield_suggestion(self, post_url: str, picker_field: Dict[str, Any], selection: Dict[str, Any],
                                      context: Dict[str, Any], uuid: str, label: str = None) -> Dict[str, Any]:
        """
        Select a Picker field from available selections
        Args:
            post_url: the url (not including the host and domain) to post to
            picker_field: the text field component returned from find_component_by_attribute_in_dict
            selection: the suggested item to select for the picker field
            context: the SAIL context parsed from the json response
            uuid: the uuid parsed from the json response
            label: the label to be displayed by locust for this action

        Returns: the response of post operation as json

        """
        identifiers_list = []
        identifiers_list.append(selection)

        new_value = {
            "#t": "PickerData",
            "identifiers": identifiers_list
        }

        payload = save_builder() \
            .component(picker_field) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = label or f'Fill \'{picker_field["label"]}\' PickerField'

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def select_checkbox_item(self, post_url: str, checkbox: Dict[str, Any],
                             context: Dict[str, Any], uuid: str, indices: list,
                             context_label: str = None) -> Dict[str, Any]:
        '''
            Calls the post operation to send an update to a checkbox to check all appropriate boxes

            Args:
                post_url: the url (not including the host and domain) to post to
                checkbox: the JSON representing the desired checkbox
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                indices: indices of the checkbox
                label: the label to be displayed by locust for this action
                headers: header for the REST API call

            Returns: the response of post operation as json
        '''
        new_value = {
            "#t": "Integer?list",
            "#v": indices if indices else None
        }
        payload = save_builder() \
            .component(checkbox) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = context_label or "Checking boxes for " + checkbox.get("testLabel",
                                                                             checkbox.get("label", "label-not-found"))

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def click_selected_tab(self, post_url: str, tab_group_component: Dict[str, Any], tab_label: str,
                           context: Dict[str, Any], uuid: str) -> Dict[str, Any]:
        '''
            Calls the post operation to send an update to a tabgroup to select a tab

            Args:
                post_url: the url (not including the host and domain) to post to
                tab_group_component: the JSON representing the desired TabButtonGroup SAIL component
                tab_label: Label of the tab to select
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                label: the label of the tab to select. It is one of the tabs inside TabButtonGroup

            Returns: the response of post operation as json
        '''
        tabs_list = tab_group_component["tabs"]
        tab_index = 0
        for index, tab in enumerate(tabs_list):
            try:
                find_component_by_attribute_in_dict("label", tab_label, tab)
                tab_index = index + 1
                break
            except ComponentNotFoundException:
                # These are expected when searching through the tabs to find the one containing the label with value tab_label
                pass

        if tab_index:
            new_value = {
                "#t": "Integer",
                "#v": tab_index
            }
        else:
            raise Exception(f"Cannot click a tab with label: '{tab_label}' inside the TabButtonGroup component")

        payload = save_builder() \
            .component(tab_group_component) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = f"Selecting tab with label: '{tab_label}' inside TabButtonGroup component"

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def select_radio_button(self, post_url: str, buttons: Dict[str, Any], context: Dict[str, Any],
                            uuid: str, index: int, context_label: str = None) -> Dict[str, Any]:
        '''
            Calls the post operation to send an update to a radio button to select the appropriate button

            Args:
                post_url: the url (not including the host and domain) to post to
                buttons: the JSON representing the desired radio button field
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                index: index of the button to be selected
                label: the label to be displayed by locust for this action
                headers: header for the REST API call

            Returns: the response of post operation as json
        '''
        new_value = {
            "#t": "Integer",
            "#v": index
        }
        payload = save_builder() \
            .component(buttons) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        resp = self.post_page(
            self.host + post_url, payload=payload, label=context_label
        )
        return resp.json()

    def _make_file_metadata(self, id: int) -> dict:
        """Produces a file metadata object to use for multifile upload fields

        Args:
            id (int): Document id of the object

        Returns:
            dict: Dictionary of the multifile upload data
        """
        # Spoof some values, as they are needed in the request but don't ultimately matter
        dummy_data = {
            "clientUuid": "0",
            "loadedBytes": 0,
            "fileSizeBytes": 0,
            "extension": "none",
            "name": "no name"
        }
        return {
            "clientUuid": dummy_data["clientUuid"],
            "loadedBytes": dummy_data["loadedBytes"],
            "name": dummy_data["name"],
            "fileSizeBytes": dummy_data["fileSizeBytes"],
            "documentId": {
                "#t": "CollaborationDocument",
                "id": id
            },
            "extension": dummy_data["extension"]
        }

    def upload_document_to_field(self, post_url: str, upload_field: Dict[str, Any],
                                 context: Dict[str, Any], uuid: str, doc_id: Union[int, List[int]],
                                 locust_label: str = None, client_mode: str = 'DESIGN') -> Dict[str, Any]:
        '''
            Calls the post operation to send an update to a upload_field to upload a document or list thereof.
            Requires a previously uploaded document id or ids

            Args:
                post_url: the url (not including the host and domain) to post to
                upload_field: the JSON representing the desired checkbox
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                doc_id: document id or list of document ids for the upload
                context_label: the label to be displayed by locust for this action
                client_mode: where this is being uploaded to, defaults to DESIGN

            Returns: the response of post operation as json
        '''
        new_value: Dict
        # This codepath will only be taken by components older than a certain version
        # all new code will fall into the list path
        if isinstance(doc_id, int):
            new_value = {
                "#t": "CollaborationDocument",
                "id": doc_id
            }
        elif isinstance(doc_id, List):
            new_value = {
                "#t": "FileMetadata?list",
                "#v": [self._make_file_metadata(id) for id in doc_id]
            }
        else:
            log_locust_error(Exception(f"Bad document id or list of document ids: {doc_id}"))
        payload = save_builder() \
            .component(upload_field) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = locust_label or "Uploading Document to " + \
            upload_field.get("label", upload_field.get("testLabel", "Generic FileUpload"))

        headers = self.setup_sail_headers()
        headers['X-Client-Mode'] = client_mode
        resp = self.post_page(
            self.host + post_url, payload=payload, headers=headers, label=locust_label
        )
        return resp.json()

    def update_date_field(self, post_url: str, date_field_component: Dict[str, Any],
                          date_input: date, context: Dict[str, Any], uuid: str,
                          locust_label: str = None) -> Dict[str, Any]:
        '''
            Calls the post operation to update a date field

            Args:
                post_url: the url (not including the host and domain) to post to
                date_field_component: the JSON representing the date field component
                date_input: date field to convert to proper text format
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response

            Returns: the response of post operation as json
        '''
        new_value = {
            "#t": "date",
            "#v": f"{date_input.isoformat()}Z" if date_input else None
        }

        payload = save_builder() \
            .component(date_field_component) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = locust_label or "Filling Date Field for " + \
            date_field_component.get("label", date_field_component.get("testLabel", "DateField"))

        headers = self.setup_sail_headers()

        resp = self.post_page(
            self.host + post_url, payload=payload, headers=headers, label=locust_label
        )
        return resp.json()

    def update_datetime_field(self, post_url: str, datetime_field: Dict[str, Any],
                              datetime_input: datetime, context: Dict[str, Any], uuid: str,
                              locust_label: str = None) -> Dict[str, Any]:
        '''
            Calls the post operation to update a date field

            Args:
                post_url: the url (not including the host and domain) to post to
                datetime_field: the JSON representing the datetime field to edit
                datetime_input: datetime field to convert to the proper text format
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response

            Returns: the response of post operation as json
        '''

        new_value = {
            "#t": "dateTime",
            "#v": f"{datetime_input.replace(second=0, microsecond=0).isoformat()}Z" if datetime_input else None
        }

        payload = save_builder() \
            .component(datetime_field) \
            .context(context) \
            .uuid(uuid) \
            .value(new_value) \
            .build()

        locust_label = locust_label or "Filling Date Time Field for " + \
            datetime_field.get("label", datetime_field.get("testLabel", "DateField"))

        headers = self.setup_sail_headers()

        resp = self.post_page(
            self.host + post_url, payload=payload, headers=headers, label=locust_label
        )
        return resp.json()

    def update_grid_from_sail_form(self, post_url: str,
                                   grid_component: Dict[str, Any], new_grid_save_value: Dict[str, Any],
                                   context: Dict[str, Any], uuid: str,
                                   context_label: str = None) -> Dict[str, Any]:
        """
            Calls the post operation to send a grid update

            Args:
                post_url: the url (not including the host and domain) to post to
                grid_component: the JSON dict representing the grid to update
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                uuid: indices of the checkbox
                context_label: the label to be displayed by locust for this action

            Returns: the response of post operation as jso
        """
        payload = save_builder() \
            .component(grid_component) \
            .context(context) \
            .uuid(uuid) \
            .value(new_grid_save_value) \
            .build()

        locust_label = context_label or "Updating Grid " + grid_component.get("label", "")
        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()

    def interact_with_record_grid(self, post_url: str,
                                  grid_component: Dict[str, Any],
                                  context: Dict[str, Any], uuid: str,
                                  context_label: str = None) -> Dict[str, Any]:
        """
            Calls the post operation to send a record grid update

            Args:
                post_url: the url (not including the host and domain) to post to
                grid_component: the JSON dict representing the grid to update
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                context_label: the label to be displayed by locust for this action

            Returns: the response of post operation as json
        """
        url_stub = post_url.split('/')[-1]
        payload = save_builder() \
            .component(grid_component) \
            .context(context) \
            .uuid(uuid) \
            .record_url_stub(url_stub) \
            .build()

        locust_label = context_label or "Updating Record Grid " + grid_component.get("label", "")
        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        resp.raise_for_status()
        return resp.json()

    def refresh_after_record_action(self, post_url: str, record_action_component: Dict[str, Any],
                                    record_action_trigger_component: Dict[str, Any],
                                    context: Dict[str, Any], uuid: str, label: str = None) -> Dict[str, Any]:
        """
            Calls the post operation to refresh a form after completion of a record action

            Args:
                post_url: the url (not including the host and domain) to post to
                record_action_component: the JSON representing the relevant record action component
                record_action_trigger_component: the JSON representing the form's record action trigger component
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response

            Returns: the response of post operation as json
        """
        # Get the payload for the record action on submit
        record_action_payload = save_builder() \
            .component(record_action_component) \
            .context(context) \
            .uuid(uuid) \
            .value(dict()) \
            .build()

        # Get the payload for the record action trigger
        record_action_trigger_payload = save_builder() \
            .component(record_action_trigger_component) \
            .context(context) \
            .uuid(uuid) \
            .value(dict()) \
            .build()

        # Get both save requests
        record_action_save_request = record_action_payload["updates"]["#v"][0]
        record_action_trigger_save_request = record_action_trigger_payload["updates"]["#v"][0]

        # Update the main payload with the both save requests
        record_action_payload["updates"]["#v"] = [record_action_save_request, record_action_trigger_save_request]

        resp = self.post_page(
            self.host + post_url, payload=record_action_payload, label=label
        )
        return resp.json()

    def click_record_search_button(self, post_url: str, component: Dict[str, Any], context: Dict[str, Any],
                                   uuid: str, label: str = None) -> Dict[str, Any]:
        """
            Calls the post operation to click a record search button

            Args:
                post_url: the url (not including the host and domain) to post to
                component: the JSON code for the desired SearchBoxWidget component
                context: the Sail context parsed from the json response
                uuid: the uuid parsed from the json response
                label: the label to be displayed by locust for this action

            Returns: the response of post operation as json
        """

        # Create a new ButtonWidget component from the SearchBoxWidget
        c_id = component["_cId"]
        action = find_component_by_attribute_in_dict("testLabel", "Applications-searchLink", component)
        if not action:
            raise ComponentNotFoundException(
                f'''Could not find the Applications-searchLink component in the provided component
                ''')
        save_into = action["saveInto"]

        search_box_button_component = {
            "_cId": f"{c_id}_buttonWidget",
            "value": None,
            "saveInto": save_into,
            "saveType": "PRIMARY",
            "#t": "ButtonWidget"
        }

        payload = save_builder() \
            .component(search_box_button_component) \
            .context(context) \
            .uuid(uuid) \
            .build()

        locust_label = label or f'Click \'{component["searchButtonLabel"]}\' Component'

        resp = self.post_page(
            self.host + post_url, payload=payload, label=locust_label
        )
        return resp.json()


class DataTypeCache(object):
    def __init__(self) -> None:
        """
        This class provides a structure to handle data type cache
        """
        self._cached_datatype: Set[str] = set()

    def clear(self) -> None:
        """
        Clears the data type cache
        """
        self._cached_datatype.clear()

    def cache(self, response_in_json: Dict[str, Any]) -> None:
        """
        From the given json response, finds and caches the data type
        Args:
            response_in_json: response of the API request

        """
        if response_in_json is not None and "#s" in response_in_json \
                and response_in_json.get("#s", {}).get("#t", "").endswith("DataType?list"):
            for dt in response_in_json["#s"]["#v"]:
                self._cached_datatype.add(str(dt["id"]))

    def get(self) -> str:
        """
        Concatenates all cached data types and returns a string

        Returns: concatenated cached data type string
        """
        return ",".join(self._cached_datatype)
