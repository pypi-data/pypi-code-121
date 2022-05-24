from example.basetestpackage.package_base import PackageTestCase

import unittest


class TestPackage(PackageTestCase, unittest.TestCase):
    project_name = "example.multipleeps"
    meta_files = []
    configure_files = ["configure.zcml"]
    overrides_files = []
    features = []
