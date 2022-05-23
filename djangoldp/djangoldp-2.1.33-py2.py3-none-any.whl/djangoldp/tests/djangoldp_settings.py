"""
This module is meant to be used as a testing LDP package.

It contains configuration elements imported by a djangoldp-package
when the django server is setup.
"""

# define an extra variables
MYPACKAGEVAR = 'ok'
USE_I18N = False

# register an extra middleware
MIDDLEWARE = [
    'djangoldp.tests.dummy.middleware.DummyMiddleware'
]

# register an extra installed app
INSTALLED_APPS = [
    'djangoldp.tests.dummy.apps.DummyConfig'
]
