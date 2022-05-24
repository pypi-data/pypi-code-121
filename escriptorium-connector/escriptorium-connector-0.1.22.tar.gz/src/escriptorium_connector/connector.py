# TODO: We should add a full testing suite for the connector.
# See the beginnings in ../../tests/test_documents.py

# TODO: add a docker-compose.yml which can spin up a working
# escriptorium instance for running the tests.


# region General Imports
import dataclasses
import ssl
from dataclasses import asdict
from io import BytesIO
from typing import Any, Tuple, Union, List, Dict, Type, TypeVar
from lxml import html
import requests
from escriptorium_connector.dtos.line_dtos import PostMoveLine, PostMoveLines, PutBulkUpdateLines
from requests.packages.urllib3.util import Retry
import logging
import json
import time
from pydantic.error_wrappers import ValidationError

# endregion

# region Logging setup

logger = logging.getLogger(__name__)

# endregion

# region LocalImports
from escriptorium_connector.utils import (
    TimeoutWebsocket,
    get_all_forms,
    get_form_details,
)
from escriptorium_connector.connector_errors import (
    EscriptoriumonnectorInitError,
    EscriptoriumConnectorHttpError,
    EscriptoriumConnectorDtoSyntaxError,
    EscriptoriumConnectorDtoTypeError,
    EscriptoriumConnectorDtoValidationError,
)
from escriptorium_connector.dtos import (
    GetProjects,
    GetProject,
    PostProject,
    PutProject,
    GetDocuments,
    GetDocument,
    PostDocument,
    PutDocument,
    GetParts,
    GetPart,
    PostPart,
    PutPart,
    GetLines,
    GetLine,
    PostLine,
    PutLine,
    GetLineTypes,
    GetLineType,
    PostLineType,
    GetAnnotationTaxonomy,
    GetAnnotationTaxonomies,
    PostAnnotationTaxonomy,
    PagenatedResponse,
    GetUser,
    GetRegions,
    GetRegion,
    PostRegion,
    GetRegionTypes,
    GetRegionType,
    PostRegionType,
    GetComponent,
    GetComponents,
    PostComponent,
    GetAbbreviatedTranscription,
    PostAbbreviatedTranscription,
    GetTranscription,
    GetTranscriptions,
    PostTranscription,
)

# endregion

# region HTTP Adapter

# Default timeouts for http requests
# See https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
from requests.adapters import HTTPAdapter


DEFAULT_HTTP_TIMEOUT = 5  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_HTTP_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


# endregion

# region Generics
P = TypeVar("P", bound=PagenatedResponse)
T = TypeVar("T")
# endregion

HttpUpload = Dict[str, Tuple[str, bytes]]

# JSON dataclass support (See: https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses)
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class EscriptoriumConnector:
    # region Init
    def __init__(
        self,
        base_url: str,
        username: str = None,
        password: str = None,
        api_key: str = None,
        api_url: str = None,
        project: str = None,
        verify_ssl: bool = True,
    ):
        """Simplified access to eScriptorium

        The eScriptorium connector is a class that enables convenient access to
        an online instance of the eScriptorium platform's HTTP API. After creating an
        EscriptoriumConnector object, the object can be used to interact with the API
        by means of the various functions it provides. The connector may be initialized
        either with a username and password, or with an api_key.

        Args:
            base_url (str): The base url of the eScriptorium server you wish to connect to (trailing / is optional)
            username (str, optional): The username used to logon to the eScriptorium website
            password (str, optional): The password used to logon to the eScriptorium website
            api_key (str, optional): The api key used to the eScriptorium API (only necessary if no username and password is provided)
            api_url (str, optional): The url path to the api (trailing / is optional). Defaults to {base_url}api/
            project (str, optional): The name of the eScriptorium project to use by default. Defaults to None.
            verify_ssl (bool, optional): Whether to very the SSL certificate of the eScriptorium server. Defaults to True.

        Raises:
            EscriptoriumConnectorHttpError: A description of the error returned from the eScriptorium HTTP API

        Examples:
            Creating the connector and performing operations:

            >>> from escriptorium_connector import EscriptoriumConnector
            >>> from escriptorium_connector.dtos import (
            ...     PostDocument,
            ...     ReadDirection,
            ...     LineOffset,
            ... )

            >>> url = "https://www.escriptorium.fr"
            >>> username = "my_username"
            >>> password = "my_password"
            >>>
            >>> connector = EscriptoriumConnector(url, username, password)
            >>> new_project_name = "test_project"
            >>> user_data = connector.get_user()
            >>> user_id = user_data.count
            >>> new_project = connector.create_project({"name": new_project_name, "slug": new_project_name, "owner": user_id})
            >>> new_document = PostDocument(
            ...     "test-doc", project_name, "Latin", ReadDirection.LTR, LineOffset.BASELINE, []
            ... )
            >>> my_doc = connector.create_document(new_document)
        """

        # Raise an error if no authentication is provided
        if username is None and password is None and api_key is None:
            raise EscriptoriumonnectorInitError(
                "Must either init with a username+password or an api_key"
            )

        # Raise an error when authenticating with username+password, but one or the other is missing
        if api_key is None and (username is None or password is None):
            raise EscriptoriumonnectorInitError(
                "Must either init with a username+password or an api_key"
            )

        # Setup retries and timeouts for HTTP requests
        retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=[  # Used method_whitelist instead of methods_available for backwards compatability
                "HEAD",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            ],
            backoff_factor=1,
        )
        adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)

        def assert_status_hook(response, *args, **kwargs):
            try:
                response.raise_for_status()
            except requests.HTTPError as err:
                raise EscriptoriumConnectorHttpError(err.response.text, err)

        self.http = requests.Session()
        if not verify_ssl:
            self.http.verify = False
        self.http.hooks["response"] = [assert_status_hook]
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)

        # Make sure the urls terminates with a front slash
        self.base_url = base_url if base_url[-1] == "/" else base_url + "/"
        self.api_url = (
            f"""{self.base_url}api/"""
            if api_url is None
            else api_url
            if api_url[-1] == "/"
            else f"""{api_url}/"""
        )

        self.http.headers.update({"Accept": "application/json"})

        # Collect the API key if none was submitted.
        if api_key is None:
            login_url = f"""{self.base_url}login/"""
            result = self.http.get(login_url)
            tree = html.fromstring(result.text)
            self.csrfmiddlewaretoken = list(
                set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value"))
            )[0]
            payload = {
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": self.csrfmiddlewaretoken,
            }
            result = self.http.post(
                login_url,
                data=payload,
                headers={**self.http.headers, "referer": login_url},
            )
            self.cookie = "; ".join(
                [f"""{k}={v}""" for k, v in self.http.cookies.get_dict().items()]
            )
            result = self.http.get(self.base_url + "profile/apikey/")
            tree = html.fromstring(result.text)
            api_key = list(
                set(tree.xpath("//button[@id='api-key-clipboard']/@data-key"))
            )[0]
        self.http.headers.update({"Authorization": f"""Token {api_key}"""})

        self.project_name = project
        self.project = self.get_project_pk_by_name(self.project_name)

    # endregion

    # region Websockets (not used)
    def __on_message(self, ws, message):  # pragma: no cover
        logging.debug(message)

    def __on_error(self, ws, error):  # pragma: no cover
        logging.debug(error)

    def __on_close(self, ws, close_status_code, close_msg):  # pragma: no cover
        logging.debug("### websocket closed ###")
        logging.debug(close_status_code)
        logging.debug(close_msg)

    def __on_open(self, ws):  # pragma: no cover
        logging.debug("### websocket opened ###")

    # endregion

    # region HTTP calls
    def __get_url(self, url: str) -> requests.Response:
        return self.http.get(url)

    def __post_url(
        self,
        url: str,
        payload: dict,
        files: Union[HttpUpload, None] = None,
        as_form_data: bool = False,
    ) -> requests.Response:
        prepared_payload = json.loads(json.dumps(payload, cls=EnhancedJSONEncoder))
        return (
            self.http.post(url, data=prepared_payload, files=files)
            if files is not None
            else (
                self.http.post(url, data=prepared_payload)
                if as_form_data
                else self.http.post(url, json=prepared_payload)
            )
        )

    def __put_url(
        self, url: str, payload: dict, files: Union[HttpUpload, None] = None
    ) -> requests.Response:
        prepared_payload = json.loads(json.dumps(payload, cls=EnhancedJSONEncoder))
        return (
            self.http.put(url, data=prepared_payload, files=files)
            if files is not None
            else self.http.put(url, json=prepared_payload)
        )

    def __delete_url(self, url: str) -> requests.Response:
        return self.http.delete(url)

    def __serialize_response(
        self, response: requests.Response, url: str, return_cls: Type[T]
    ) -> T:
        r_json = response.json()
        try:
            # Some endpoints return an unnamed list, which needs to be treated in a special way.
            # First, we make sure this is a list
            is_return_cls_list = getattr(return_cls, '__origin__', None) == list  # Non generic types have no __origin__ property
            is_response_list = type(r_json) == list
            if is_return_cls_list and is_response_list:
                # Both types are lists (if only one of them is a list, the else clause will cause a TypeError, which is what we want anyway)

                # We need to validate each entry of the response
                entry_type = return_cls.__args__[0]  # This is the expected list entry type
                obj = list([entry_type(**j) for j in r_json]) 
            else:
                obj = return_cls(**r_json)
        except SyntaxError as e:
            raise EscriptoriumConnectorDtoSyntaxError(
                e, response.status_code, url, response.text
            )
        except TypeError as e:
            raise EscriptoriumConnectorDtoTypeError(
                e, response.status_code, url, response.text
            )
        except ValidationError as e:
            raise EscriptoriumConnectorDtoValidationError(
                e, response.status_code, url, response.text
            )
        return obj

    def __get_url_serialized(self, url: str, return_cls: Type[T]) -> T:
        r = self.http.get(url)
        return self.__serialize_response(r, url, return_cls)

    def __post_url_serialized(
        self,
        url: str,
        payload: dict,
        return_cls: Type[T],
        files: Union[HttpUpload, None] = None,
    ) -> T:
        r = self.__post_url(url, payload, files)
        return self.__serialize_response(r, url, return_cls)

    def __put_url_serialized(
        self,
        url: str,
        payload: dict,
        return_cls: Type[T],
        files: Union[HttpUpload, None] = None,
    ) -> T:
        r = self.__put_url(url, payload, files)
        return self.__serialize_response(r, url, return_cls)

    def __get_paginated_response(self, url: str, return_cls: Type[P]) -> P:
        all_docs = self.__get_url_serialized(url, return_cls)
        info = all_docs
        while info.next is not None:
            info = self.__get_url_serialized(info.next, return_cls)
            all_docs.results = all_docs.results + info.results

        return all_docs

    # endregion

    # region Project API
    def set_connector_project_by_name(self, project_name: str):
        self.project_name = project_name
        self.project = self.get_project_pk_by_name(self.project_name)

    def set_connector_project_by_pk(self, project_pk: int):
        self.project = project_pk
        self.project_name = (self.get_project(self.project)).name

    def get_projects(self) -> GetProjects:
        return self.__get_paginated_response(f"{self.api_url}projects/", GetProjects)

    def get_project(self, pk: int) -> GetProject:
        return self.__get_url_serialized(f"{self.api_url}projects/{pk}", GetProject)

    def get_project_pk_by_name(
        self, project_name: Union[str, None]
    ) -> Union[int, None]:
        if project_name is None or project_name == "":
            return None

        all_projects = (self.get_projects()).results
        matching_projects = [x for x in all_projects if x.name == project_name]
        return matching_projects[0].id if matching_projects else None

    def create_project(self, project_data: PostProject) -> GetProject:
        return self.__post_url_serialized(
            f"{self.api_url}projects/", asdict(project_data), GetProject
        )

    # def create_project(self, project_name: str) -> Union[GetProject, None]:
    #     new_project_data = PostProject(
    #         name=project_name, csrfmiddlewaretoken=self.csrfmiddlewaretoken
    #     )
    #     r = self.http.post(f"{self.base_url}projects/", data=asdict(new_project_data), headers=self.http.headers)
    #     project_pk = self.get_project_pk_by_name(project_name)
    #     return self.get_project(project_pk) if project_pk is not None else None

    def update_project(self, project_data: PutProject) -> GetProject:
        return self.__put_url_serialized(
            f"{self.api_url}projects/", asdict(project_data), GetProject
        )

    def delete_project(self, project_pk: int):
        return self.__delete_url(f"{self.api_url}projects/{project_pk}")

    def verify_project_exists(self, project_pk: int) -> bool:
        try:
            self.get_project(project_pk)
            return True
        except:
            return False

    # endregion

    # region Document API
    def get_documents(self) -> GetDocuments:
        return self.__get_paginated_response(f"{self.api_url}documents/", GetDocuments)

    def get_document(self, pk: int) -> GetDocument:
        return self.__get_url_serialized(f"{self.api_url}documents/{pk}/", GetDocument)

    def create_document(self, doc_data: PostDocument) -> GetDocument:
        return self.__post_url_serialized(
            f"{self.api_url}documents/", asdict(doc_data), GetDocument
        )

    def update_document(self, pk: int, doc_data: PutDocument) -> GetDocument:
        return self.__put_url_serialized(
            f"{self.api_url}documents/{pk}/", asdict(doc_data), GetDocument
        )

    def delete_document(self, pk: int):
        return self.__delete_url(f"{self.api_url}documents/{pk}/")

    # endregion

    # region Part API
    def get_document_parts(self, doc_pk: int) -> GetParts:
        return self.__get_paginated_response(
            f"{self.api_url}documents/{doc_pk}/parts/", GetParts
        )

    def get_document_part(self, doc_pk: int, part_pk: int) -> GetPart:
        return self.__get_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/", GetPart
        )

    def get_document_part_image(self, doc_pk: int, part_pk: int) -> bytes:
        part = self.get_document_part(doc_pk, part_pk)
        return self.get_image(part.image.uri)

    def get_document_part_thumbnail(
        self, doc_pk: int, part_pk: int, large: bool = False
    ) -> bytes:
        # The thumbnails are not immediately generated,
        # retry a couple times before giving up
        num_tries = 5
        current_try = 0
        part = self.get_document_part(doc_pk, part_pk)
        needed_size_exists = (
            part.image.thumbnails.large is not None
            if large
            else part.image.thumbnails.card is not None
        )

        while not needed_size_exists and current_try < num_tries:
            time.sleep(4)
            part = self.get_document_part(doc_pk, part_pk)
            needed_size_exists = (
                part.image.thumbnails.large is not None
                if large
                else part.image.thumbnails.card is not None
            )

        image_url = part.image.thumbnails.large if large else part.image.thumbnails.card
        if image_url is None:
            raise Exception(
                f"""Could not find a {"large" if large else "card"} thumbnail for doc {doc_pk}, part {part_pk}"""
            )

        return self.get_image(image_url)

    def create_document_part(
        self,
        document_pk: int,
        image_data_info: PostPart,
        filename: str,
        image_data: bytes,
    ) -> GetPart:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{document_pk}/parts/",
            asdict(image_data_info),
            GetPart,
            {"image": (filename, image_data)},
        )

    def update_document_part(
        self,
        doc_pk: int,
        part_pk: int,
        image_data_info: PutPart,
    ) -> GetPart:
        return self.__put_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/",
            asdict(image_data_info),
            GetPart,
        )

    def delete_document_part(self, doc_pk: int, part_pk: int):
        self.__delete_url(f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/")

    def delete_document_parts_by_index(self, doc_pk: int, start: int, end: int):
        """Deletes N parts from the documents, starting with and including the
        item at the `start` index and ending with but *not* including the item at
        the `end` index.

        Args:
            doc_pk (int): PK of the document from which to remove the parts
            start (int): Index of the first part to be removed according to the
            order in which the document parts are returned (check the part `order`
            attribute to be sure)
            end (int): The index at which to stop deleting document partsaccording
            to the order in which the document parts are returned (check the part
            `order` attribute to be sure). The item at this index (if it exists)
            will not be deleted.
        """

        if start > end:
            return

        parts = (self.get_document_parts(doc_pk)).results

        if start > len(parts) < end:
            return

        for part in parts[start:end]:
            self.delete_document_part(doc_pk, part.pk)

    # endregion

    # region Up/Download API

    # region Text Up/Download
    def download_part_alto_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
    ) -> Union[bytes, None]:
        """Download one or more ALTO/XML files from the document.

        Args:
            document_pk (int): Desired document
            part_pk (Union[List[int], int]): Desired document part or parts
            transcription_pk (int): The desired transcription

        Returns:
            Union[bytes, None]: The response is None if the XML could not be downloaded.
            Otherwise it is a bytes object with the contents of the downloaded zip file.
            You will need to unzip these bytes in order to access the XML data (zipfile can do this).
        """

        return self.__download_part_output_transcription(
            document_pk, part_pk, transcription_pk, "alto"
        )

    def download_part_pagexml_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
    ) -> Union[bytes, None]:
        """Download one or more PageXML files from the document.

        Args:
            document_pk (int): Desired document
            part_pk (Union[List[int], int]): Desired document part or parts
            transcription_pk (int): The desired transcription

        Returns:
            Union[bytes, None]: The response is None if the XML could not be downloaded.
            Otherwise it is a bytes object with the contents of the downloaded zip file.
            You will need to unzip these bytes in order to access the XML data (zipfile can do this).
        """

        return self.__download_part_output_transcription(
            document_pk, part_pk, transcription_pk, "pagexml"
        )

    def download_part_text_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
    ) -> Union[bytes, None]:
        """Download one or more TXT files from the document.

        Args:
            document_pk (int): Desired document
            part_pk (Union[List[int], int]): Desired document part or parts
            transcription_pk (int): The desired transcription

        Returns:
            Union[bytes, None]: The response is None if the XML could not be downloaded.
            Otherwise it is a bytes object with the contents of the downloaded zip file.
            You will need to unzip these bytes in order to access the XML data (zipfile can do this).
        """

        return self.__download_part_output_transcription(
            document_pk, part_pk, transcription_pk, "text"
        )

    def __download_part_output_transcription(
        self,
        document_pk: int,
        part_pk: Union[List[int], int],
        transcription_pk: int,
        output_type: str,
    ) -> Union[bytes, None]:
        if self.cookie is None:
            raise Exception("Must use websockets to download ALTO exports")

        download_link = None
        ws = (
            TimeoutWebsocket(sslopt={"cert_reqs": ssl.CERT_NONE})
            if self.http.verify is False
            else TimeoutWebsocket()
        )
        ws.connect(
            f"{self.base_url.replace('http', 'ws')}ws/notif/",
            cookie=self.cookie,
        )
        r = self.__post_url(
            f"{self.api_url}documents/{document_pk}/export/",
            {
                "task": "export",
                "csrfmiddlewaretoken": self.csrfmiddlewaretoken,
                "transcription": transcription_pk,
                "file_format": output_type,
                "region_types": [
                    x.pk for x in self.get_document_region_types(document_pk)
                ]
                + ["Undefined", "Orphan"],
                "document": document_pk,
                "parts": part_pk,
            },
            as_form_data=True,
        )

        message = ws.recv(30)
        ws.close()
        logging.debug(message)
        msg = json.loads(message)
        if "export" in msg["text"].lower():
            for entry in msg["links"]:
                if entry["text"].lower() == "download":
                    download_link = entry["src"]

        if download_link is None:
            logging.warning(
                f"Did not receive a link to download ALTO export for {document_pk}, {part_pk}, {transcription_pk}"
            )
            return None
        alto_request = self.__get_url(f"{self.base_url}{download_link}")

        if alto_request.status_code != 200:
            return None

        return alto_request.content

    def upload_part_transcription(
        self,
        document_pk: int,
        transcription_name: str,
        filename: str,
        file_data: BytesIO,
        override: str = "off",
    ):
        """Upload a txt, PageXML, or ALTO file.

        Args:
            document_pk (int): Document PK
            transcription_name (str): Transcription name
            filename (str): Filename
            file_data (BytesIO): File data as a BytesIO
            override (str): Whether to override existing segmentation data ("on") or not ("off", default)

        Returns:
            null: Nothing
        """

        request_payload = {"task": "import-xml", "name": transcription_name}
        if override == "on":
            request_payload["override"] = "on"

        return self.__post_url(
            f"{self.api_url}documents/{document_pk}/imports/",
            request_payload,
            {"upload_file": (filename, file_data)},
        )

    # endregion

    # region Image Download

    def get_image(self, img_url: str) -> bytes:
        sanitized_img_url = img_url.lstrip("/")
        r = self.__get_url(f"{self.base_url}{sanitized_img_url}")
        return r.content

    # endregion

    # endregion

    # region Line API

    def get_document_part_line(
        self, doc_pk: int, part_pk: int, line_pk: int
    ) -> GetLine:
        return self.__get_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/{line_pk}/",
            GetLine,
        )

    def get_document_part_lines(self, doc_pk: int, part_pk: int) -> GetLines:
        return self.__get_paginated_response(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/", GetLines
        )

    def create_document_part_line(
        self, doc_pk: int, part_pk: int, new_line: PostLine
    ) -> GetLine:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/",
            asdict(new_line),
            GetLine,
        )

    def update_document_part_line(
        self, doc_pk: int, part_pk: int, line_pk: int, new_line: PutLine
    ) -> GetLine:
        return self.__put_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/{line_pk}/",
            asdict(new_line),
            GetLine,
        )

    def delete_document_part_line(
        self, doc_pk: int, part_pk: int, line_pk: int
    ) -> requests.Response:
        return self.__delete_url(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/{line_pk}"
        )

    def move_lines(
        self, doc_pk: int, part_pk: int, lines: PostMoveLines
    ) -> List[PostMoveLine]: 
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/lines/move/",
            asdict(lines),
            List[PostMoveLine]
        )

    def bulk_update_lines(self, doc_pk: int, park_pk: int, lines:list[GetLine], fields: list[str]) -> list[GetLine]:
        if 'pk' not in fields:
            fields.append('pk')

        line_dicts = [{ fld: getattr(line, fld) for fld in fields } for line in lines]  # Will raise a key error if fields has an incorrect field name

        
        result = self.__put_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{park_pk}/lines/bulk_update/",
            dict(lines=line_dicts),
            PutBulkUpdateLines)

        return result.lines

    # endregion

    # region Line Type API

    def get_document_line_types(self, doc_pk: int) -> List[GetLineType]:
        doc_data = self.get_document(doc_pk)
        return [x for x in doc_data.valid_line_types]

    def get_line_types(self) -> GetLineTypes:
        return self.__get_paginated_response(f"{self.api_url}types/line/", GetLineTypes)

    def get_line_type(self, line_type_pk: int) -> GetLineType:
        return self.__get_url_serialized(
            f"{self.api_url}types/line/{line_type_pk}/", GetLineType
        )

    def create_line_type(self, line_type: PostLineType) -> GetLineType:
        return self.__post_url_serialized(
            f"{self.api_url}types/line/", asdict(line_type), GetLineType
        )

    def update_line_type(
        self, line_type_pk: int, line_type: PostLineType
    ) -> GetLineType:
        return self.__put_url_serialized(
            f"{self.api_url}types/line/{line_type_pk}/", asdict(line_type), GetLineType
        )

    def delete_line_type(self, line_type_pk: int) -> requests.Response:
        return self.__delete_url(f"{self.api_url}types/line/{line_type_pk}/")

    # region document valid line types

    # TODO: Warning, these functions are a hack to get past the lack of support
    # in the API for creating document valid line types. They use a form POST
    # to the eScriptorium website, since no API is available. They do NOT work
    # if any annotation components, image annotations, or text annotations have
    # already been created. The whole situation is quite poor right now and
    # awaiting a fix.

    def create_document_line_types_by_pk(self, doc_pk: int, line_type_pks: List[int]):
        # Get the current ontology information
        ontology_url = f"{self.base_url}document/{doc_pk}/ontology/"
        forms = get_all_forms(
            ontology_url,
            self.http,
        )
        ontology_form = forms[0]
        form_details = get_form_details(ontology_form)
        data = {}
        # Copy all existing data
        for input_tag in form_details["inputs"]:
            if input_tag["name"] not in data:
                data[input_tag["name"]] = []
            data[input_tag["name"]].append(input_tag["value"])

        # Change only the valid region types
        data["valid_line_types"] = data["valid_line_types"] + line_type_pks

        res = self.http.post(
            ontology_url,
            data=data,
            headers={**self.http.headers, "Referer": ontology_url},
        )

    def create_document_line_type_by_pk(self, doc_pk: int, line_type_pk: int):
        self.create_document_line_types_by_pk(doc_pk, [line_type_pk])

    def create_document_line_types(self, doc_pk: int, line_type_names: List[str]):
        # Make sure all the desired line types exist and get their PKs
        current_line_types = self.get_line_types().results
        current_line_type_names = [x.name for x in current_line_types]
        non_existant_line_types = [
            x for x in line_type_names if x not in current_line_type_names
        ]
        line_type_pks = [x.pk for x in current_line_types if x.name in line_type_names]
        for non_existant_line_type in non_existant_line_types:
            new_line_type = self.create_line_type(
                PostLineType(name=non_existant_line_type)
            )
            line_type_pks.append(new_line_type.pk)

        self.create_document_line_types_by_pk(doc_pk, line_type_pks)

    def create_document_line_type(self, doc_pk: int, line_type_name: str):
        return self.create_document_line_types(doc_pk, [line_type_name])

    def delete_document_line_types_by_pk(self, doc_pk: int, line_type_pks: List[int]):
        # Get the current ontology information
        ontology_url = f"{self.base_url}document/{doc_pk}/ontology/"
        forms = get_all_forms(
            ontology_url,
            self.http,
        )
        ontology_form = forms[1]
        form_details = get_form_details(ontology_form)
        data = {}
        # Copy all existing data
        for input_tag in form_details["inputs"]:
            if input_tag["name"] not in data:
                data[input_tag["name"]] = []
            data[input_tag["name"]].append(input_tag["value"])

        # Change only the valid region types
        data["valid_line_types"] = [
            x for x in data["valid_line_types"] if x not in line_type_pks
        ]

        res = self.http.post(
            ontology_url,
            data=data,
            headers={**self.http.headers, "Referer": ontology_url},
        )

    def delete_document_line_type_by_pk(self, doc_pk: int, line_type_pk: int):
        self.delete_document_line_types_by_pk(doc_pk, [line_type_pk])

    def delete_document_line_types(self, doc_pk: int, line_type_names: List[str]):
        # Get the PKs of all line types to be deleted
        current_line_types = self.get_line_types().results
        delete_pks = [x.pk for x in current_line_types if x.name in line_type_names]

        self.delete_document_line_types_by_pk(doc_pk, delete_pks)

    def delete_document_line_type(self, doc_pk: int, line_type_name: str):
        self.delete_document_line_types(doc_pk, [line_type_name])

    # endregion

    # endregion

    # region Region API

    def get_document_part_region(
        self, doc_pk: int, part_pk: int, region_pk: int
    ) -> Union[GetRegion, None]:
        regions = self.get_document_part_regions(doc_pk, part_pk)
        region = [x for x in regions if x.pk == region_pk]
        return region[0] if region else None

    def get_document_part_regions(self, doc_pk: int, part_pk: int) -> List[GetRegion]:
        result = self.__get_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/", GetPart
        )
        return result.regions

    def create_document_part_region(
        self, doc_pk: int, part_pk: int, region: PostRegion
    ) -> GetRegion:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/blocks/",
            asdict(region),
            GetRegion,
        )

    # endregion

    # region Region Type API

    def get_region_types(self) -> GetRegionTypes:
        return self.__get_paginated_response(
            f"{self.api_url}types/block/", GetRegionTypes
        )

    def get_document_region_types(self, doc_pk: int) -> List[GetRegionType]:
        doc_data = self.get_document(doc_pk)
        return [x for x in doc_data.valid_block_types]

    def create_region_type(self, region_type: PostRegionType) -> GetRegionType:
        return self.__post_url_serialized(
            f"{self.api_url}types/block/", asdict(region_type), GetRegionType
        )

    # region document valid region types

    # TODO: Warning, these functions are a hack to get past the lack of support
    # in the API for creating document valid region types. They use a form POST
    # to the eScriptorium website, since no API is available. They do NOT work
    # if any annotation components, image annotations, or text annotations have
    # already been created. The whole situation is quite poor right now and
    # awaiting a fix.

    def create_document_region_types_by_pk(
        self, doc_pk: int, region_type_pks: List[int]
    ):
        # Get the current ontology information
        ontology_url = f"{self.base_url}document/{doc_pk}/ontology/"
        forms = get_all_forms(
            ontology_url,
            self.http,
        )
        ontology_form = forms[0]
        form_details = get_form_details(ontology_form)
        data = {}
        # Copy all existing data
        for input_tag in form_details["inputs"]:
            if input_tag["name"] not in data:
                data[input_tag["name"]] = []
            data[input_tag["name"]].append(input_tag["value"])

        # Change only the valid region types
        data["valid_block_types"] = data.get("valid_block_types", "") + region_type_pks

        res = self.http.post(
            ontology_url,
            data=data,
            headers={**self.http.headers, "Referer": ontology_url},
        )

    def create_document_region_type_by_pk(self, doc_pk: int, region_type_pk: int):
        self.create_document_region_types_by_pk(doc_pk, [region_type_pk])

    def create_document_region_types(self, doc_pk: int, region_type_names: List[str]):
        # Make sure all the desired region types exist and get their PKs
        current_region_types = self.get_region_types().results
        current_region_type_names = [x.name for x in current_region_types]
        non_existant_region_types = [
            x for x in region_type_names if x not in current_region_type_names
        ]
        region_type_pks = [
            x.pk for x in current_region_types if x.name in region_type_names
        ]
        for non_existant_region_type in non_existant_region_types:
            new_region_type = self.create_region_type(
                PostRegionType(name=non_existant_region_type)
            )
            region_type_pks.append(new_region_type.pk)

        self.create_document_region_types_by_pk(doc_pk, region_type_pks)

    def create_document_region_type(self, doc_pk: int, region_type_pk: str):
        return self.create_document_region_types(doc_pk, [region_type_pk])

    def delete_document_region_types_by_pk(
        self, doc_pk: int, region_type_pks: List[int]
    ):
        # Get the current ontology information    
        ontology_url = f"{self.base_url}document/{doc_pk}/ontology/"
        forms = get_all_forms(
            ontology_url,
            self.http,
        )
        ontology_form = forms[0]
        form_details = get_form_details(ontology_form)
        data = {}
        # Copy all existing data
        for input_tag in form_details["inputs"]:
            if input_tag["name"] not in data:
                data[input_tag["name"]] = []
            data[input_tag["name"]].append(input_tag["value"])

        # Change only the valid region types
        data["valid_block_types"] = [
            x for x in data["valid_block_types"] if x not in region_type_pks
        ]

        res = self.http.post(
            ontology_url,
            data=data,
            headers={**self.http.headers, "Referer": ontology_url},
        )

    def delete_document_region_type_by_pk(self, doc_pk: int, region_type_pk: int):
        self.delete_document_region_types_by_pk(doc_pk, [region_type_pk])

    def delete_document_region_types(self, doc_pk: int, region_type_names: List[str]):
        # Get the PKs of all region types to be deleted
        current_region_types = self.get_region_types().results
        delete_pks = [x.pk for x in current_region_types if x.name in region_type_names]

        self.delete_document_region_types_by_pk(doc_pk, delete_pks)

    def delete_document_region_type(self, doc_pk: int, region_type_name: str):
        self.delete_document_region_types(doc_pk, [region_type_name])

    # endregion

    # endregion

    # region Transcription API
    def get_document_part_line_transcription(
        self, doc_pk: int, part_pk: int, line_pk: int, line_transcription_pk: int
    ) -> Union[GetTranscription, None]:
        transcriptions = self.get_document_part_line_transcriptions(
            doc_pk, part_pk, line_pk
        )
        transcription = [x for x in transcriptions if x.pk == line_transcription_pk]
        return transcription[0] if transcription else None

    def get_document_part_line_transcription_by_transcription(
        self, doc_pk: int, part_pk: int, line_pk: int, transcription_pk: int
    ) -> Union[GetTranscription, None]:
        transcriptions = self.get_document_part_line_transcriptions(
            doc_pk, part_pk, line_pk
        )
        transcription = [
            x for x in transcriptions if x.transcription == transcription_pk
        ]
        return transcription[0] if transcription else None

    def get_document_part_line_transcriptions(
        self, doc_pk: int, part_pk: int, line_pk: int
    ) -> List[GetTranscription]:
        line = self.get_document_part_line(doc_pk, part_pk, line_pk)
        return line.transcriptions if line.transcriptions is not None else []

    def get_document_transcription(
        self, doc_pk: int, transcription_pk: int
    ) -> GetAbbreviatedTranscription:
        return self.__get_url_serialized(
            f"{self.api_url}documents/{doc_pk}/transcriptions/{transcription_pk}/",
            GetAbbreviatedTranscription,
        )

    def create_document_transcription(
        self, doc_pk: int, transcription_name: PostAbbreviatedTranscription
    ) -> GetAbbreviatedTranscription:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/transcriptions/",
            asdict(transcription_name),
            GetAbbreviatedTranscription,
        )

    def delete_document_transcription(
        self, doc_pk: int, transcription_pk: int
    ) -> requests.Response:
        return self.__delete_url(
            f"{self.api_url}documents/{doc_pk}/transcriptions/{transcription_pk}/"
        )

    def get_document_transcriptions(
        self, doc_pk: int
    ) -> List[GetAbbreviatedTranscription]:
        r = self.__get_url(f"{self.api_url}documents/{doc_pk}/transcriptions/")
        r_json = r.json()
        return [GetAbbreviatedTranscription(**x) for x in r_json]

    def create_document_part_transcription(
        self, doc_pk: int, parts_pk: int, transcription: PostTranscription
    ) -> GetTranscription:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/parts/{parts_pk}/transcriptions/",
            asdict(transcription),
            GetTranscription,
        )

    def get_document_part_transcriptions(
        self, doc_pk: int, part_pk: int
    ) -> GetTranscriptions:
        return self.__get_paginated_response(
            f"{self.api_url}documents/{doc_pk}/parts/{part_pk}/transcriptions/",
            GetTranscriptions,
        )

    # endregion

    # region Annotation API
    def get_document_annotations(self, doc_pk: int) -> GetAnnotationTaxonomies:
        return self.__get_paginated_response(
            f"""{self.api_url}documents/{doc_pk}/taxonomies/annotations/""",
            GetAnnotationTaxonomies,
        )

    def get_document_annotation(
        self, doc_pk: int, annotation_pk
    ) -> GetAnnotationTaxonomy:
        return self.__get_url_serialized(
            f"""{self.api_url}documents/{doc_pk}/taxonomies/annotations/{annotation_pk}/""",
            GetAnnotationTaxonomy,
        )

    def create_document_annotation(
        self, doc_pk: int, annotation: PostAnnotationTaxonomy
    ) -> GetAnnotationTaxonomy:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/taxonomies/annotations/",
            asdict(annotation),
            GetAnnotationTaxonomy,
        )

    def update_document_annotation(
        self, doc_pk: int, annotation_pk: int, annotation: PostAnnotationTaxonomy
    ) -> GetAnnotationTaxonomy:
        return self.__put_url_serialized(
            f"{self.api_url}documents/{doc_pk}/taxonomies/annotations/{annotation_pk}/",
            annotation.__dict__,
            GetAnnotationTaxonomy,
        )

    def delete_document_annotation(self, doc_pk: int, annotation_pk: int):
        self.__delete_url(
            f"{self.api_url}documents/{doc_pk}/taxonomies/annotations/{annotation_pk}/"
        )

    def get_document_components(self, doc_pk: int) -> GetComponents:
        return self.__get_paginated_response(
            f"{self.api_url}documents/{doc_pk}/taxonomies/components/", GetComponents
        )

    def create_document_component(
        self, doc_pk: int, component: PostComponent
    ) -> GetComponent:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/taxonomies/components/",
            asdict(component),
            GetComponent,
        )

    def update_document_component(
        self, doc_pk: int, component_pk: int, component: PostComponent
    ) -> GetComponent:
        return self.__post_url_serialized(
            f"{self.api_url}documents/{doc_pk}/taxonomies/components/{component_pk}/",
            asdict(component),
            GetComponent,
        )

    def delete_document_component(self, doc_pk: int, component_pk: int):
        return self.__delete_url(
            f"{self.api_url}documents/{doc_pk}/taxonomies/components/{component_pk}/",
        )

    # endregion

    # region User API

    # TODO: this function is simply wrong! I cannot figure out for the life
    # of me how to get my user PK via API or otherwise. You need the user
    # PK to create a new project, otherwise, it seems unnecessary.
    def get_user(self) -> GetUser:
        return self.__get_paginated_response(f"""{self.api_url}user""", GetUser)

    # endregion
