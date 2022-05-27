# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UWNetID Subscription 64
"""

from uw_uwnetid.models import Subscription
from uw_uwnetid.subscription import get_netid_subscriptions,\
    select_subscription


subs_code = Subscription.SUBS_CODE_2FA


def get_2fa_subs(netid):
    """
    @return a Subscription object if the subscription for the given uwnetid
            exists. Return None if not exist or an Exception.
    """
    return select_2fa(get_netid_subscriptions(netid, subs_code))


def select_2fa(subscriptions):
    return select_subscription(subs_code, subscriptions)
