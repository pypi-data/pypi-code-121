# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Alma Services."""

from invenio_alma.services.alma import AlmaRESTUrls, AlmaSRUUrls
from invenio_alma.services.config import AlmaRESTConfig, AlmaSRUConfig


def test_alma_rest_urls():
    """Test rest urls."""

    mms_id = "12345-12345"
    api_key = "api_key"
    api_host = "api_host"
    config = AlmaRESTConfig(api_key, api_host)
    urls = AlmaRESTUrls(config)

    expected = f"https://{api_host}/almaws/v1/bibs?mms_id={mms_id}&apikey={api_key}"
    assert urls.url_get(mms_id) == expected

    expected = f"https://{api_host}/almaws/v1/bibs/{mms_id}?apikey={api_key}"
    assert urls.url_put(mms_id) == expected


def test_alma_sru_urls():
    """Test sru urls."""

    search_key = ""
    domain = ""
    institution_code = ""
    search_value = ""
    config = AlmaSRUConfig(search_key, domain, institution_code)
    urls = AlmaSRUUrls(config)

    expected_query = f"query=alma.{search_key}={search_value}"
    expected_parameters = f"version=1.2&operation=searchRetrieve&{expected_query}"
    expected = f"https://{domain}/view/sru/{institution_code}?{expected_parameters}"
    assert urls.url(search_value) == expected
