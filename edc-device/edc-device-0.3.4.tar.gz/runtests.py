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

app_name = "edc_device"
base_dir = dirname(abspath(__file__))

DEFAULT_SETTINGS = DefaultTestSettings(
    calling_file=__file__,
    template_dirs=[os.path.join(base_dir, app_name, "tests", "templates")],
    APP_NAME=app_name,
    BASE_DIR=base_dir,
    ETC_DIR=os.path.join(base_dir, app_name, "tests", "etc"),
    EDC_NAVBAR_VERIFY_ON_LOAD=IGNORE,
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_crypto_fields.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "django_celery_results",
        "django_celery_beat",
        "multisite",
        "edc_appointment.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "edc_auth.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_export.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_locator.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_model_wrapper.apps.AppConfig",
        "edc_navbar.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_pharmacy.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_randomization.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
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
