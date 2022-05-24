from example.basetestpackage.package_base import PackageTestCase

import unittest


class TestPackage(PackageTestCase, unittest.TestCase):
    project_name = "example.zopeaddon"
    meta_files = ["meta.zcml", "browser/meta.zcml"]
    configure_files = ["configure.zcml", "browser/configure.zcml"]
    overrides_files = ["overrides.zcml", "browser/browser-overrides.zcml"]
    features = ["zopeaddon", "zopeaddon-browser"]
