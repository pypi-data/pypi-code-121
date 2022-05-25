# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.extern import webob

from contrast.api import dtm_pb2
from contrast.utils.timer import now_ms
from contrast.agent.middlewares.route_coverage.common import (
    get_normalized_uri as strip_uri,
)

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class Request(webob.BaseRequest):
    def __init__(self, environ):
        """
        Django is not fully wsgi-compliant, so we need its request body to be passed in
        explicitly.
        """
        super().__init__(environ)

        self._document_type = None
        self._normalized_uri = None

        self.timestamp_ms = now_ms()

    def get_dtm(self):
        """
        Builds the protobuf HttpRequest object from the current Request object
        :return: HttpRequest protobuf dtm
        """
        dtm = dtm_pb2.HttpRequest()

        dtm.uuid = str(id(self))
        dtm.timestamp_ms = self.timestamp_ms

        dtm.sender.ip = self.client_addr or ""
        dtm.sender.host = self.remote_host or ""

        # NOTE: we don't have a reliable way to extract dtm.receiver.ip from the WSGI environ
        dtm.receiver.host = self.domain
        dtm.receiver.port = int(self.host_port)

        dtm.protocol = self.scheme
        dtm.version = self._get_http_version()
        dtm.method = self.method
        dtm.raw = self.path_qs

        dtm.parsed_request_body = True
        dtm.request_body_binary = self.get_body()
        dtm.document_type = self._get_document_type()

        for key, values_list in self.params.dict_of_lists().items():
            str_values = [v for v in values_list if isinstance(v, str)]
            dtm.normalized_request_params[key].key = key
            dtm.normalized_request_params[key].values.extend(str_values)

        # includes Cookies
        dtm.parsed_request_headers = True

        # phase 1 headers
        for header_key, header_value in self.headers.items():
            dtm.request_headers[header_key] = header_value

        for cookie_key, cookie_value in self.cookies.items():
            dtm.normalized_cookies[cookie_key].key = cookie_key
            dtm.normalized_cookies[cookie_key].values.append(cookie_value)

        # multipart headers for any uploaded files
        for field_name, filename in self._get_file_info():
            dtm.multipart_headers.add(key=field_name, value=filename)

        return dtm

    def get_normalized_uri(self):
        """
        A best-effort to remove client-specific information from the path.
        Example:
        /user/123456/page/12 -> /user/{n}/page/{n}
        """
        if self._normalized_uri is not None:
            return self._normalized_uri

        self._normalized_uri = strip_uri(self.path)
        return self._normalized_uri

    def get_body(self, as_text=False, errors="ignore"):
        """
        Get the raw request body in either bytes or as a decoded string.
        Note that we do not use webob's Request.text here, because we do not want this to fail
        in the event of a decoding error.

        :param as_text: Boolean indicating if we should attempt to return a decoded string
        :param errors: String indicating the unicode error handling strategy, passed to decode()
        :return: The request body as either bytes or a decoded string
        """
        if not as_text:
            return self.body

        return self.body.decode(self.charset or "utf-8", errors=errors)

    def _get_http_version(self):
        """
        teamserver expects this field to be a string representing the HTTP version only.
        Using 'HTTP/1.1' is not acceptable and will cause vulnerabilities to be omitted from TS.
        """
        return self.http_version.split("/")[-1]

    def _get_document_type_from_header(self):
        """
        Returns the document type based on the content type header if present
        """
        content_type = self.content_type.lower()

        if not content_type:
            return None
        if "json" in content_type:
            return dtm_pb2.HttpRequest.JSON
        if "xml" in content_type:
            return dtm_pb2.HttpRequest.XML
        if "x-www-form-urlencoded" in content_type or "form-data" in content_type:
            return dtm_pb2.UserInput.PARAMETER_VALUE

        return dtm_pb2.HttpRequest.NORMAL

    def _get_document_type_from_body(self):
        body = self.get_body(as_text=True)

        if body.startswith("<?xml"):
            return dtm_pb2.HttpRequest.XML
        if re.search(r"^\s*[{[]", body):
            return dtm_pb2.HttpRequest.JSON

        return dtm_pb2.HttpRequest.NORMAL

    def _get_document_type(self):
        if self._document_type is not None:
            return self._document_type

        self._document_type = self._get_document_type_from_header()
        if self._document_type is None:
            self._document_type = self._get_document_type_from_body()

        return self._document_type

    def _get_file_info(self):
        """
        Get the field names and filenames of uploaded files
        :return: list of tuples of (field_name, filename)
        """
        file_info = []
        for f in self.POST.values():
            if hasattr(f, "filename") and hasattr(f, "name"):
                file_info.append((f.name, f.filename))
                logger.debug("Found uploaded file: %s", f.filename)

        return file_info
