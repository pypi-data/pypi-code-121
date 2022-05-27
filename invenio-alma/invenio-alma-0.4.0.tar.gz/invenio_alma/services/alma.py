# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Alma Service."""

import requests
from lxml.etree import fromstring, tostring

from .config import AlmaRESTConfig, AlmaSRUConfig
from .errors import AlmaAPIError, AlmaRESTError


# pylint: disable-next=unused-argument
def jpath_to_xpath(field_json_path):
    """Convert json path to xpath."""
    # TODO
    return ""


class AlmaRESTUrls:
    """Alma REST urls."""

    def __init__(self, config):
        """Constructor Alma REST Urls."""
        self.config = config

    @property
    def base_url(self):
        """Base url."""
        return f"https://{self.config.api_host}/almaws/v1/bibs"

    def url_get(self, mms_id):
        """Alma rest api get record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        return f"{self.base_url}?mms_id={mms_id}&apikey={self.config.api_key}"

    def url_put(self, mms_id):
        """Alma rest api put record url.

        :param mms_id (str): alma record id

        :return str: alma api url.
        """
        return f"{self.base_url}/{mms_id}?apikey={self.config.api_key}"


class AlmaSRUUrls:
    """Alma SRU urls."""

    def __init__(self, config):
        """Constructor for Alma SRU urls."""
        self.config = config
        self.search_value = ""

    @property
    def base_url(self):
        """Base url."""
        return f"https://{self.config.domain}/view/sru/{self.config.institution_code}"

    @property
    def query(self):
        """Query."""
        return f"query=alma.{self.config.search_key}={self.search_value}"

    @property
    def parameters(self):
        """Parameters."""
        return f"version=1.2&operation=searchRetrieve&{self.query}"

    def url(self, search_value):
        """Alma sru url to retrieve record by search value."""
        self.search_value = search_value
        return f"{self.base_url}?{self.parameters}"


class AlmaAPIBase:
    """Alma remote base service."""

    def __init__(self, xpath_to_records, namespaces=None):
        """Constructor alma api base service."""
        self.xpath_to_records = xpath_to_records
        self.namespaces = namespaces if namespaces else {}

    @property
    def headers(self):
        """Headers."""
        return {
            "content-type": "application/xml",
            "accept": "application/xml",
        }

    @staticmethod
    def parse_alma_record(data):
        """Parse Alma record."""
        data = data.encode("utf-8")

        return fromstring(data)

    def extract_alma_records(self, data):
        """Extract record from request.

        :param data (str): result list

        :return lxml.Element: extracted record
        """
        record = self.parse_alma_record(data)

        # extract single record
        bibs = record.xpath(self.xpath_to_records, namespaces=self.namespaces)

        if len(bibs) == 0:
            msg = f"xpath: {self.xpath_to_records} does not find records."
            raise AlmaAPIError(msg=msg)

        return bibs

    def get(self, url):
        """Alma base api get request.

        :param url (str): url to api

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        response = requests.get(url, headers=self.headers)
        if response.status_code >= 400:
            raise AlmaAPIError(code=response.status_code, msg=response.text)
        return self.extract_alma_records(response.text)


class AlmaREST(AlmaAPIBase):
    """Alma REST service class."""

    def __init__(self):
        """Constructor alma rest service."""
        super().__init__(".//bib/record")

    def put(self, url, data):
        """Alma rest api put request.

        :param url (str): url to api
        :param data (str): payload

        :raises AlmaRESTError if request was not successful

        :return str: response content
        """
        response = requests.put(url, data, headers=self.headers)
        if response.status_code >= 400:
            raise AlmaRESTError(code=response.status_code, msg=response.text)
        return response.text


class AlmaSRU(AlmaAPIBase):
    """Alma SRU Service class."""

    def __init__(self):
        """Constructor alma sru service."""
        namespaces = {
            "srw": "http://www.loc.gov/zing/srw/",
            "slim": "http://www.loc.gov/MARC21/slim",
        }
        super().__init__(".//srw:recordData/slim:record", namespaces)


class AlmaRESTService:
    """Alma service class."""

    def __init__(self, config, urls, service):
        """Constructor for AlmaService."""
        self.config = config
        self.urls = urls
        self.service = service

    @classmethod
    def build(cls, api_key, api_host, config=None, urls=None, service=None):
        """Build method."""
        config = config if config else AlmaRESTConfig(api_key, api_host)
        urls = urls if urls else AlmaRESTUrls(config)
        service = service if service else AlmaREST()
        return cls(config, urls, service)

    def get_record(self, mms_id):
        """Get Record from alma."""
        api_url = self.urls.url_get(mms_id)
        return self.service.get(api_url)  # return etree

    @staticmethod
    # pylint: disable-next=unused-argument
    def get_field(record, field_json_path, subfield_value=""):
        """Get field by json path and subfield value if it is set."""
        xpath = jpath_to_xpath(field_json_path)
        field = record.xpath(xpath)

        # TODO check about multiple results
        # allowed only one field, otherwise we have a problem and should sys.exit()

        return field

    @staticmethod
    # pylint: disable-next=unused-argument
    def replace_field(field, new_subfield_value, new_subfield_template=""):
        """Replace in-inplace the subfield value with the new subfield value.

        Replace also the metametadata of the field if the template is set.
        """
        # TODO: implement new_subfield_template != ""

        field.text = new_subfield_value

    def update_alma_record(self, mms_id, record):
        """Update the record on alma side."""
        data = tostring(record)  # TODO check if .decode("UTF-8") is necessary
        url_put = self.urls.url_put(mms_id)
        self.service.put(url_put, data)

    def update_field(
        self,
        mms_id,
        field_json_path,
        new_subfield_value,
        subfield_value="",
        new_subfield_template="",
    ):
        """Update field."""
        record = self.get_record(mms_id)
        field = self.get_field(record, field_json_path, subfield_value)  # reference
        self.replace_field(field, new_subfield_value, new_subfield_template)  # in-place
        self.update_alma_record(mms_id, record)


class AlmaSRUService:
    """AlmaSRUService."""

    def __init__(self, config, urls, service):
        """Constructor for AlmaService."""
        self.config = config
        self.urls = urls
        self.service = service

    @classmethod
    def build(
        cls, search_key, domain, institution_code, config=None, urls=None, service=None
    ):
        """Build sru service."""
        config = (
            config if config else AlmaSRUConfig(search_key, domain, institution_code)
        )
        urls = urls if urls else AlmaSRUUrls(config)
        service = service if service else AlmaSRU()
        return cls(config, urls, service)

    def get_record(self, ac_number):
        """Get the record."""
        url = self.urls.url(ac_number)
        return self.service.get(url)
