"""This module defines the enum GlobalPermission.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from enum import Enum


class GlobalPermission(str, Enum):
    can_add_users = "can_add_users"
    can_use_snippets = "can_use_snippets"
    can_edit_own_info = "can_edit_own_info"
    can_edit_own_password = "can_edit_own_password"
    can_create_courses = "can_create_courses"
    can_manage_site_users = "can_manage_site_users"
    can_search_users = "can_search_users"
    can_impersonate_users = "can_impersonate_users"
    can_manage_lti_providers = "can_manage_lti_providers"
    can_manage_sso_providers = "can_manage_sso_providers"
    can_manage_site_settings = "can_manage_site_settings"
    can_manage_background_jobs = "can_manage_background_jobs"
    can_create_tenant = "can_create_tenant"
    can_create_courses_for_other_tenants = (
        "can_create_courses_for_other_tenants"
    )
    can_see_other_tenant_statistics = "can_see_other_tenant_statistics"
    can_search_users_other_tenant = "can_search_users_other_tenant"
    can_skip_payment = "can_skip_payment"
    can_edit_pricing = "can_edit_pricing"
    can_see_all_transactions = "can_see_all_transactions"
    can_edit_coupons = "can_edit_coupons"
    can_see_coupons = "can_see_coupons"
