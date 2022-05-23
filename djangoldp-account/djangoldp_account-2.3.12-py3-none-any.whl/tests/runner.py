import sys
import yaml

import django
from django.conf import settings as django_settings
from djangoldp.conf.ldpsettings import LDPSettings

# create a test configuration
config = {
    # add the packages to the reference list
    'ldppackages': ['djangoldp_account', 'djangoldp_account.tests'],

    # required values for server
    'server': {
        'JABBER_DEFAULT_HOST': ''
    }
}

ldpsettings = LDPSettings(config)
django_settings.configure(ldpsettings)

django.setup()
from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests([
    'djangoldp_account.tests.tests_auth_backends',
    'djangoldp_account.tests.tests_update',
])
if failures:
    sys.exit(failures)
