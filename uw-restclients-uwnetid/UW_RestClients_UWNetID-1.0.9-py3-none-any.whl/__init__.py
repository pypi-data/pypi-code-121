# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with
the uwnetid subscription web service.
"""

import logging
import json
from commonconf import settings
from restclients_core.exceptions import DataFailureException
from uw_uwnetid.dao import UWNetID_DAO


INVALID_USER_MSG = "No such NetID"
DAO = UWNetID_DAO()
logger = logging.getLogger(__name__)


def url_version():
    return '/nws/{0}'.format(
        getattr(settings, 'RESTCLIENTS_UWNETID_VERSION', 'v1'))


def url_base():
    return '{0}/uwnetid'.format(url_version())


def get_resource(url):
    response = DAO.getURL(url, {'Accept': 'application/json'})
    logger.debug("GET {0} ==status==> {1}".format(url, response.status))
    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    _test_for_invalid_user(url, response.data)

    logger.debug("GET {0} ==data==> {1}".format(url, response.data))

    return response.data


def post_resource(url, body):
    response = DAO.postURL(url, {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }, body)
    logger.debug("POST {0} ==status==> {1}".format(url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    _test_for_invalid_user(url, response.data)

    logger.debug("POST {0}s ==data==> {1}".format(url, response.data))

    return response.data


def _test_for_invalid_user(url, response_data):
    # 'Bug' with lib API causing requests with no/invalid user to return a 200
    if INVALID_USER_MSG in "{0}".format(response_data):
        json_data = json.loads(response_data)
        raise DataFailureException(url, 404, json_data["errorMessage"])
