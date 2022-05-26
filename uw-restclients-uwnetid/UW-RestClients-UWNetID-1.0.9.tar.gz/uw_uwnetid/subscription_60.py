# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interface for interacting with the UWNetID Subscription Web Service.
"""

from uw_uwnetid.models import SubscriptionPermit, Subscription
from uw_uwnetid.subscription import get_netid_subscriptions,\
    select_subscription


subs_code = Subscription.SUBS_CODE_KERBEROS


def get_kerberos_subs_permits(netid):
    """
    Return a list of restclients.models.uwnetid.SubscriptionPermit objects
    on the given uwnetid
    """
    subs = get_kerberos_subs(netid)
    if subs is not None:
        return subs.permits
    return None


def get_kerberos_subs(netid):
    """
    Return a Subscription object on the given uwnetid
    """
    return _select_kerberos(get_netid_subscriptions(netid, subs_code))


def _select_kerberos(subs):
    return select_subscription(subs_code, subs)


def _has_desired_permit(permits, acategory, astatus):
    """
    return True if permits has one whose
    category_code and status_code match with the given ones
    """
    if permits is None:
        return False
    for permit in permits:
        if permit.category_code == acategory and\
           permit.status_code == astatus:
            return True
    return False


def is_current_alumni(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.ALUMNI_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE)


def is_current_grad(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.GRAD_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE)


def is_former_grad(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.GRAD_C_CODE,
                               SubscriptionPermit.FORMER_STATUS_CODE) and\
        not is_current_grad(subs_permits)


def is_current_undergrad(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.UNDERGRAD_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE)


def is_former_undergrad(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.UNDERGRAD_C_CODE,
                               SubscriptionPermit.FORMER_STATUS_CODE) and\
        not is_current_undergrad(subs_permits)


def is_current_pce(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.EO_TECHFEE_STUD_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE) or\
        _has_desired_permit(subs_permits,
                            SubscriptionPermit.EO_NON_TECHFEE_STUD_C_CODE,
                            SubscriptionPermit.CURRENT_STATUS_CODE)


def is_former_pce(subs_permits):
    return (_has_desired_permit(subs_permits,
                                SubscriptionPermit.EO_TECHFEE_STUD_C_CODE,
                                SubscriptionPermit.FORMER_STATUS_CODE) or
            _has_desired_permit(subs_permits,
                                SubscriptionPermit.EO_NON_TECHFEE_STUD_C_CODE,
                                SubscriptionPermit.FORMER_STATUS_CODE)) and\
        not is_current_pce(subs_permits)


def is_current_staff(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.STAFF_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE)


def is_former_staff(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.STAFF_C_CODE,
                               SubscriptionPermit.FORMER_STATUS_CODE) and\
        not is_current_staff(subs_permits)


def is_current_faculty(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.FACULTY_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE)


def is_former_faculty(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.FACULTY_C_CODE,
                               SubscriptionPermit.FORMER_STATUS_CODE) and\
        not is_current_faculty(subs_permits)


def is_current_student_employee(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.STUDENT_EMPLOYEE_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE)


def is_former_student_employee(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.STUDENT_EMPLOYEE_C_CODE,
                               SubscriptionPermit.FORMER_STATUS_CODE) and\
        not is_current_student_employee(subs_permits)


def is_current_clinician(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.CLINICIAN_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE) or\
        _has_desired_permit(subs_permits,
                            SubscriptionPermit.CLINICIAN_NETID_C_CODE,
                            SubscriptionPermit.CURRENT_STATUS_CODE)


def is_former_clinician(subs_permits):
    return (_has_desired_permit(subs_permits,
                                SubscriptionPermit.CLINICIAN_C_CODE,
                                SubscriptionPermit.FORMER_STATUS_CODE) or
            _has_desired_permit(subs_permits,
                                SubscriptionPermit.CLINICIAN_NETID_C_CODE,
                                SubscriptionPermit.FORMER_STATUS_CODE)) and\
        not is_current_clinician(subs_permits)


def is_current_retiree(subs_permits):
    return _has_desired_permit(subs_permits,
                               SubscriptionPermit.RETIREE_C_CODE,
                               SubscriptionPermit.CURRENT_STATUS_CODE)
