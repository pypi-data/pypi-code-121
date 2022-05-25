#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
"""Module to define base handler for external API calls"""

import json
import logging

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    ProxyError,
    ReadTimeout,
    SSLError,
    Timeout,
    TooManyRedirects,
)

LOGGER = logging.getLogger("root")


class ApiHandler:
    """Base class for calling any external APIs"""

    def __init__(
        self, 
        url: str, 
        api_key: str, 
        tenant_schema:str,
        timeout: int,
        logging: bool = True
    ):
        self.url = url
        self.__api_key = api_key
        self.__logging = logging
        self.__tenant_schema = tenant_schema

        self._timeout = timeout

        self.connection_exceptions = (
            ConnectionError,
            ProxyError,
            ReadTimeout,
            SSLError,
            Timeout,
            TooManyRedirects,
        )

    def get_headers(self, **kwargs):
        """Builds and return headers for each request"""
        kwargs.setdefault("Content-Type", "application/json")
        kwargs.setdefault("Accept", "application/json")
        kwargs.setdefault("Authorization", self.__api_key)

        return kwargs

    def send_request(
        self,
        method,
        params=None,
        payload=None,
        log_config: dict = None,
        add_custom_fields: bool = False,
        event=None,
        event_type="ENVELOPE"
    ):
        """Send API request for the given URL with the specified method, params and payload"""
        headers = self.get_headers()

        if self.__logging:
            LOGGER.info("[DOCUSIGN] - [%s: %s]", method, self.url)

        log_entry = None
        response = None
        if log_config:
            if (
                "model" not in log_config
                or "user" not in log_config
                or "loan" not in log_config
                or "timezone" not in log_config
            ):
                raise Exception("Invalid log dict")

        if payload:
            if add_custom_fields:
                payload = json.loads(payload)
                if len(payload["customFields"]) > 1:
                    #TODO: Logic to be added if we need to include multiple custom fields in future
                    pass
                else:
                    custom_fields = {
                        "listItems" : ["TenantSchema"],
                        "fieldId" : "1",
                        "name" : "TenantSchema",
                        "value" : self.__tenant_schema,
                        "show" : False,
                        "required" : False,
                    }
                    payload["customFields"]["listCustomFields"].append(custom_fields)
                payload = json.dumps(payload)

        try:
            if log_config:
                log_entry = log_config["model"](
                    loan=log_config["loan"],
                    requested_by=log_config["user"],
                    request_url=f"{method}: {self.url}",
                    request_headers=headers,
                    request_body=payload,
                    request_time=log_config["timezone"].now(),
                    tin=log_config["tin"],
                    request_ip=log_config["request_ip"],
                    event_type=event_type,
                    event=event,
                )

            response = requests.request(
                method,
                self.url,
                timeout=self._timeout,
                headers=headers,
                params=params,
                # TODO: Try changing to json=payload
                data=payload,
            )

            if self.__logging:
                LOGGER.info(
                    "[DOCUSIGN] - Received [%s] response for [%s: %s]",
                    response.status_code,
                    method,
                    self.url,
                )

            response_text = response.text
            if method and method == "GET" and ("/documents/combined" in self.url or "/documents/archive" in self.url) and response.status_code == 200:
                response_text = f"Document download successfull for {self.url}"

            if log_entry:
                log_entry.response_code = response.status_code
                log_entry.response_body = response_text
                log_entry.response_time = log_entry.request_time + response.elapsed
                log_entry.save()

            response.raise_for_status()
            return response
        except self.connection_exceptions as excp:
            if log_config:
                if response:
                    response_time = log_entry.request_time + response.elapsed
                else:
                    response_time = log_entry.request_time
                log_entry = log_config["model"](
                    loan=log_config["loan"],
                    requested_by=log_config["user"],
                    request_url=f"{method}: {self.url}",
                    request_headers=headers,
                    request_body=payload,
                    request_time=log_config["timezone"].now(),
                    response_code = 0,
                    response_body = excp,
                    response_time = response_time,
                )
                log_entry.save()
            if self.__logging:
                LOGGER.error(
                    "[DOCUSIGN] - Exception while connecting to DocuSign. URL: [%s: %s]. Error: [%s]",
                    method,
                    self.url,
                    excp,
                )
                raise
        except HTTPError as excp:
            if log_config:
                if response:
                    response_time = log_entry.request_time + response.elapsed
                else:
                    response_time = log_entry.request_time
                log_entry = log_config["model"](
                    loan=log_config["loan"],
                    requested_by=log_config["user"],
                    request_url=f"{method}: {self.url}",
                    request_headers=headers,
                    request_body=payload,
                    request_time=log_config["timezone"].now(),
                    response_code = response.status_code,
                    response_body = excp,
                    response_time = response_time,
                )
                log_entry.save()
            if self.__logging:
                LOGGER.error(
                    "[DOCUSIGN] - Received bad response. Status code: [%s] for [%s: %s]. Error: [%s]",
                    response.status_code,
                    method,
                    self.url,
                    excp,
                )
            if response.status_code in [400, 401, 404, 415]:
                return response
            else:
                raise Exception(
                    f"[DOCUSIGN] - Received bad response. Status code: [{response.status_code}] for [{method}: {self.url}]. Error: [{response.text}]"
                ) from excp
