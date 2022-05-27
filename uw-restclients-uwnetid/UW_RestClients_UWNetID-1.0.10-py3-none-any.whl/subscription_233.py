# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UWNetID Subscription Web Service.
"""

import logging
from uw_uwnetid.models import SubscriptionPermit, Subscription
from uw_uwnetid.subscription import get_netid_subscriptions


logger = logging.getLogger(__name__)


def get_office365edu_prod_subs(netid):
    """
    Return a restclients.models.uwnetid.Subscription objects
    on the given uwnetid
    """
    subs = get_netid_subscriptions(netid,
                                   Subscription.SUBS_CODE_OFFICE_365)
    if subs is not None:
        for subscription in subs:
            if (subscription.subscription_code ==
                    Subscription.SUBS_CODE_OFFICE_365):
                return subscription
    return None


def get_office365edu_test_subs(netid):
    """
    Return a restclients.models.uwnetid.Subscription objects
    on the given uwnetid
    """
    subs = get_netid_subscriptions(netid,
                                   Subscription.SUBS_CODE_OFFICE_365_TEST)
    if subs is not None:
        for subscription in subs:
            if (subscription.subscription_code ==
                    Subscription.SUBS_CODE_OFFICE_365_TEST):
                return subscription
    return None
