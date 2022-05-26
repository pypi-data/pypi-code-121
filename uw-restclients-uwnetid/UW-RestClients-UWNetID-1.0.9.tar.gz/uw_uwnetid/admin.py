# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UWNetID Web Service Admin resource.
"""

import logging
import json
from uw_uwnetid.models import Admin
from uw_uwnetid import url_base, get_resource


logger = logging.getLogger(__name__)


def get_admins_for_shared_netid(netid):
    """
    Returns list of Admin resources
    """
    url = _netid_admin_url(netid)
    response = get_resource(url)
    return _json_to_admin(response)


def _netid_admin_url(netid):
    """
    Return UWNetId resource for provided netid supported
    resources
    """
    return "{0}/{1}/admin.json".format(url_base(), netid)


def _json_to_admin(response_body):
    """
    Returns a list of Admin objects
    """
    data = json.loads(response_body)
    adminList = []
    for supported_data in data.get("adminList", []):
        adminList.append(Admin().from_json(
            supported_data))

    return adminList
