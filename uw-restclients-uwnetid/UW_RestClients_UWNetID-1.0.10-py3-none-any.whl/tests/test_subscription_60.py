# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_uwnetid.models import SubscriptionPermit
from uw_uwnetid.subscription_60 import get_kerberos_subs_permits,\
    is_current_undergrad, is_former_undergrad, is_current_student_employee,\
    is_current_grad, is_former_grad, is_former_student_employee,\
    is_current_staff, is_former_staff, get_kerberos_subs, is_former_pce,\
    is_current_faculty, is_former_faculty, is_current_alumni,\
    is_current_clinician, is_former_clinician, is_current_retiree
from restclients_core.exceptions import DataFailureException
from uw_uwnetid.util import fdao_uwnetid_override


@fdao_uwnetid_override
class KerberosSubsTest(TestCase):

    def test_subs_permits(self):
        permit = SubscriptionPermit(mode="implicit",
                                    category_code=1,
                                    category_name="Undergraduate",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_undergrad())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=2,
                                    category_name="Grad",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_grad())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=4,
                                    category_name="Staff",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_staff())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=5,
                                    category_name="Faculty",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_faculty())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=14,
                                    category_name="Student Employee",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_student_employee())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=13,
                                    category_name="Clinician",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_clinician())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=17,
                                    category_name="Clinician",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_clinician_netid_only())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=16,
                                    category_name="Alumni",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_alumni())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=34,
                                    category_name="Retired Staff",
                                    status_code=1,
                                    status_name="current")
        self.assertTrue(permit.is_category_retiree())
        self.assertTrue(permit.is_status_current())

        permit = SubscriptionPermit(mode="implicit",
                                    category_code=16,
                                    category_name="Alumni",
                                    status_code=3,
                                    status_name="former")
        self.assertTrue(permit.is_status_former())

    def test_get_kerberos_subs_permits(self):
        permits = get_kerberos_subs_permits("javerage")
        self.assertFalse(is_current_staff(permits))
        self.assertTrue(is_current_alumni(permits))
        self.assertTrue(is_current_undergrad(permits))
        self.assertTrue(is_current_student_employee(permits))

        permits = get_kerberos_subs_permits("jinternational")
        self.assertTrue(is_current_grad(permits))
        self.assertTrue(is_former_undergrad(permits))
        self.assertTrue(is_current_student_employee(permits))
        self.assertTrue(is_former_staff(permits))
        self.assertFalse(is_current_faculty(permits))
        self.assertFalse(is_current_clinician(permits))

        subs = get_kerberos_subs("bill")
        self.assertTrue(subs.is_status_active())

        permits = get_kerberos_subs_permits("bill")
        self.assertTrue(is_current_staff(permits))
        self.assertTrue(is_former_grad(permits))
        self.assertTrue(is_former_student_employee(permits))
        self.assertFalse(is_current_faculty(permits))
        self.assertFalse(is_current_clinician(permits))

        permits = get_kerberos_subs_permits("phil")
        self.assertFalse(is_current_staff(permits))
        self.assertTrue(is_current_faculty(permits))
        self.assertTrue(is_current_alumni(permits))

        permits = get_kerberos_subs_permits("fred")
        self.assertTrue(is_current_clinician(permits))

        permits = get_kerberos_subs_permits("james")
        self.assertTrue(is_current_clinician(permits))

        permits = get_kerberos_subs_permits("retiree")
        self.assertTrue(is_former_faculty(permits))
        self.assertTrue(is_former_staff(permits))
        self.assertTrue(is_former_grad(permits))
        self.assertTrue(is_current_retiree(permits))
        self.assertTrue(is_former_pce(permits))

    def test_unpermitted(self):
        subs = get_kerberos_subs("none")
        self.assertFalse(subs.is_status_active())
        self.assertFalse(subs.is_status_inactive())
        self.assertFalse(subs.permitted)

    def test_expiring_subs(self):
        subs = get_kerberos_subs("eight")
        self.assertTrue(subs.is_status_active())
        self.assertFalse(subs.is_status_inactive())
        self.assertFalse(subs.permitted)

    def test_invalid_user(self):
        # Testing error message in a 200 response
        self.assertRaises(DataFailureException,
                          get_kerberos_subs,
                          "invalidnetid")
        # Testing non-200 response
        self.assertRaises(DataFailureException,
                          get_kerberos_subs,
                          "jnewstudent")
