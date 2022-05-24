from . import dummy_plone
from example.basetestpackage.integration_base import IntegrationTestCase
from example.basetestpackage.utils import get_configuration_context
from importlib import import_module
from zope.configuration.xmlconfig import include
from zope.configuration.xmlconfig import includeOverrides

import sys
import unittest


# When loading our meta.zcml, z3c.autoinclude/zope/configuration
# tries to import 'plone', because this is our target.
# But we don't have a plone module in our z3c tests.
# So mock it.
try:
    import plone  # noqa
except ImportError:
    sys.modules["plone"] = dummy_plone


class TestIntegration(IntegrationTestCase, unittest.TestCase):
    project_name = "example.z3cintegration"
    target = "plone"
    meta_files = {
        "example.z3cintegration": ["meta.zcml"],
        "z3c.autoinclude": ["meta.zcml"],
        "example.metaoverrides": ["meta.zcml"],
    }
    configure_files = {
        "example.z3cintegration": ["configure.zcml"],
        "example.ploneaddon": [
            "configure.zcml",
            "permissions.zcml",
            "browser/configure.zcml",
        ],
    }
    overrides_files = {
        "example.z3cintegration": ["overrides.zcml"],
        "example.metaoverrides": ["overrides.zcml"],
    }
    features = [
        "metaoverrides",
        "z3cintegration",
    ]

    def setUp(self):
        """Load meta.zcml"""
        # prepare configuration context
        package = import_module(self.project_name)
        self.context = get_configuration_context(package)
        self.load_zcml_file(zcml="meta.zcml")

    def load_zcml_file(self, zcml="configure.zcml", override=False):
        if override:
            includeOverrides(self.context, zcml, self.context.package)
        else:
            include(self.context, zcml, self.context.package)
