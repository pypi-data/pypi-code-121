# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_uwnetid.supported import get_supported_resources
from uw_uwnetid.util import fdao_uwnetid_override
from restclients_core.exceptions import DataFailureException


@fdao_uwnetid_override
class SupportedResourcesTest(TestCase):
    def test_supported_netids_for_shared(self):
        supported = get_supported_resources('bill')
        self.assertEquals(len(supported), 25)
        shared = 0
        owner = 0
        admin = 0
        for support in supported:
            if support.is_shared_netid():
                shared += 1
                if support.is_owner():
                    owner += 1
                if support.is_admin():
                    admin += 1

        self.assertEquals(shared, 16)
        self.assertEquals(owner, 9)
        self.assertEquals(admin, 13)

    def test_no_supported_netids_for_shared(self):
        try:
            supported = get_supported_resources('javerage')
        except DataFailureException as ex:
            self.assertEquals(ex.status, 404)
