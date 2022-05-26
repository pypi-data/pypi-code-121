# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UWNetID Category Web Service.
"""
import logging
import json
from uw_uwnetid import url_version, url_base, get_resource, post_resource
from uw_uwnetid.models import Category


logger = logging.getLogger(__name__)


def get_netid_categories(netid, category_codes):
    """
    Return a list of uwnetid.models Category objects
    corresponding to the netid and category code or list provided
    """
    url = _netid_category_url(netid, category_codes)
    response = get_resource(url)
    return _json_to_categories(response)


def update_catagory(netid, category_code, status):
    """
    Post a subscriptionfor the given netid
    and category_code
    """
    url = "{0}/category".format(url_version())
    body = {
        "categoryCode": category_code,
        "status": status,
        "categoryList": [{"netid": netid}]
    }

    response = post_resource(url, json.dumps(body))
    return json.loads(response)


def _netid_category_url(netid, category_codes):
    """
    Return UWNetId resource for provided netid and category
    code or code list
    """
    return "{0}/{1}/category/{2}".format(
        url_base(), netid,
        (','.join([str(n) for n in category_codes])
         if isinstance(category_codes, (list, tuple))
         else category_codes))


def _json_to_categories(response_body):
    """
    Returns a list of Category objects
    """
    data = json.loads(response_body)
    categories = []
    for category_data in data.get("categoryList", []):
        categories.append(Category().from_json(
            data.get('uwNetID'), category_data))

    return categories
