# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UWNetID Subscription Web Service.
"""

from datetime import datetime
import logging
import json
from uw_uwnetid.models import (
    UwEmailForwarding, Subscription, SubscriptionPostResponse)
from uw_uwnetid import url_version, url_base, get_resource, post_resource


logger = logging.getLogger(__name__)


def get_email_forwarding(netid):
    """
    deprecated: use subscription_105.get_email_forwarding
    """
    subscriptions = get_netid_subscriptions(netid,
                                            Subscription.
                                            SUBS_CODE_U_FORWARDING)
    for subscription in subscriptions:
        if (subscription.subscription_code == Subscription.
                SUBS_CODE_U_FORWARDING):
            return_obj = UwEmailForwarding()
            if subscription.data_value:
                return_obj.fwd = subscription.data_value
            return_obj.permitted = subscription.permitted
            return_obj.status = subscription.status_name
            return return_obj

    return None


def get_netid_subscriptions(netid, subscription_codes):
    """
    Returns a list of uwnetid.subscription objects
    corresponding to the netid and subscription code or list provided
    """
    url = _netid_subscription_url(netid, subscription_codes)
    response = get_resource(url)
    return _json_to_subscriptions(response)


def select_subscription(subs_code, subscriptions):
    """
    Return the uwnetid.subscription object with the subs_code.
    """
    if subs_code and subscriptions:
        for subs in subscriptions:
            if (subs.subscription_code == subs_code):
                return subs
    return None


def modify_subscription_status(netid, subscription_code, status):
    """
    Post a subscription 'modify' action for the given netid
    and subscription_code
    """
    url = _netid_subscription_url(netid, subscription_code)
    body = {
        'action': 'modify',
        'value': str(status)
    }

    response = post_resource(url, json.dumps(body))
    return _json_to_subscriptions(response)


def update_subscription(netid, action, subscription_code, data_field=None):
    """
    Post a subscription action for the given netid and subscription_code
    """
    url = '{0}/subscription.json'.format(url_version())
    action_list = []

    if isinstance(subscription_code, list):
        for code in subscription_code:
            action_list.append(_set_action(
                netid, action, code, data_field))
    else:
        action_list.append(_set_action(
            netid, action, subscription_code, data_field))

    body = {'actionList': action_list}
    response = post_resource(url, json.dumps(body))
    return _json_to_subscription_post_response(response)


def _set_action(netid, action, subscription_code, data_field):
    action = {
        'uwNetID': netid,
        'action': action,
        'subscriptionCode': str(subscription_code)
    }

    if isinstance(data_field, tuple) and len(data_field) == 2:
        action[data_field[0]] = str(data_field[1])
    elif isinstance(data_field, dict):
        for (k, v) in data_field.items():
            action[k] = v

    return action


def _netid_subscription_url(netid, subscription_codes):
    """
    Return UWNetId resource for provided netid and subscription
    code or code list
    """
    return "{0}/{1}/subscription/{2}".format(
        url_base(), netid,
        (','.join([str(n) for n in subscription_codes])
         if isinstance(subscription_codes, (list, tuple))
         else subscription_codes))


def _json_to_subscriptions(response_body):
    """
    Returns a list of Subscription objects
    """
    data = json.loads(response_body)
    subscriptions = []
    for subscription_data in data.get("subscriptionList", []):
        subscriptions.append(Subscription().from_json(
            data.get('uwNetID'), subscription_data))

    return subscriptions


def _json_to_subscription_post_response(response_body):
    """
    Returns a list of SubscriptionPostResponse objects
    """
    data = json.loads(response_body)
    response_list = []
    for response_data in data.get("responseList", []):
        response_list.append(
            SubscriptionPostResponse().from_json(response_data))

    return response_list
