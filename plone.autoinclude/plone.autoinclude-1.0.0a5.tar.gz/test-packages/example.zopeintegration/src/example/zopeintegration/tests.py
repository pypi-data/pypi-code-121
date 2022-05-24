from example.basetestpackage.integration_base import IntegrationTestCase

import unittest


class TestIntegration(IntegrationTestCase, unittest.TestCase):
    project_name = "example.zopeintegration"
    target = "zope"
    meta_files = {
        "example.zopeintegration": ["meta.zcml"],
        "example.zopeaddon": ["meta.zcml", "browser/meta.zcml"],
        "plone.autoinclude": ["meta.zcml"],
        "example.somethingelse2": ["meta.zcml"],
    }
    configure_files = {
        "example.somethingelse2": ["configure.zcml"],
        "example.zopeintegration": ["configure.zcml"],
        "example.zopeaddon": ["configure.zcml", "browser/configure.zcml"],
    }
    overrides_files = {
        "example.somethingelse2": ["overrides.zcml"],
        "example.zopeintegration": ["overrides.zcml"],
        "example.zopeaddon": ["overrides.zcml", "browser/browser-overrides.zcml"],
    }
    features = [
        "different2",
        "disable-autoinclude",
        "zopeaddon",
        "zopeaddon-browser",
        "zopeintegration",
    ]
