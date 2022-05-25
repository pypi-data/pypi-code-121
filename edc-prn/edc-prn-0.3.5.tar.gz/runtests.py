#!/usr/bin/env python
import logging
import os
import sys
from os.path import abspath, dirname

import django
from django.conf import settings
from django.test.runner import DiscoverRunner
from edc_constants.constants import IGNORE
from edc_test_utils import DefaultTestSettings

app_name = "edc_prn"
base_dir = dirname(abspath(__file__))

DEFAULT_SETTINGS = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=os.path.join(base_dir, app_name, "tests", "etc"),
    EDC_BOOTSTRAP=3,
    EDC_NAVBAR_VERIFY_ON_LOAD=IGNORE,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_crypto_fields.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_reference.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "visit_schedule_app.apps.AppConfig",
        "edc_prn.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    # add_lab_dashboard_middleware=True,
    use_test_urls=True,
).settings


def main():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    django.setup()
    failures = DiscoverRunner(failfast=True).run_tests([f"{app_name}.tests"])
    sys.exit(failures)


if __name__ == "__main__":
    logging.basicConfig()
    main()
