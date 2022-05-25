import sys
import yaml

import django
from django.conf import settings as django_settings
from djangoldp.conf.ldpsettings import LDPSettings
from djangoldp.tests.server_settings import yaml_config

# load test config
config = yaml.safe_load(yaml_config)
ldpsettings = LDPSettings(config)
django_settings.configure(ldpsettings)

django.setup()
from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests([
    'djangoldp.tests.tests_settings',
    'djangoldp.tests.tests_ldp_model',
    'djangoldp.tests.tests_model_serializer',
    'djangoldp.tests.tests_ldp_viewset',
    'djangoldp.tests.tests_user_permissions',
    'djangoldp.tests.tests_guardian',
    'djangoldp.tests.tests_anonymous_permissions',
    'djangoldp.tests.tests_post',
    'djangoldp.tests.tests_update',
    'djangoldp.tests.tests_auto_author',
    'djangoldp.tests.tests_get',
    'djangoldp.tests.tests_delete',
    'djangoldp.tests.tests_sources',
    'djangoldp.tests.tests_pagination',
    'djangoldp.tests.tests_inbox',
    'djangoldp.tests.tests_backlinks_service',
    'djangoldp.tests.tests_cache'
])
if failures:
    sys.exit(failures)
