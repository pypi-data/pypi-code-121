#!/usr/bin/env python
import logging
import sys
from os.path import abspath, dirname

import django
from django.conf import settings
from django.test.runner import DiscoverRunner
from edc_test_utils import DefaultTestSettings

app_name = "edc_model_form"
base_dir = dirname(abspath(__file__))

DEFAULT_SETTINGS = DefaultTestSettings(
    APP_NAME="edc_model_form",
    BASE_DIR=base_dir,
    ALLOWED_HOSTS=["localhost"],
    STATIC_URL="/static/",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "multisite",
        "edc_device.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_model_form.apps.AppConfig",
    ],
).settings


def main():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    django.setup()
    tags = [t.split("=")[1] for t in sys.argv if t.startswith("--tag")]
    failures = DiscoverRunner(failfast=True, tags=tags).run_tests([f"{app_name}.tests"])
    sys.exit(failures)


if __name__ == "__main__":
    logging.basicConfig()
    main()
