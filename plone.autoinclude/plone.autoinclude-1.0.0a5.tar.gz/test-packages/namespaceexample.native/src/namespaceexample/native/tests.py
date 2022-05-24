from example.basetestpackage.package_base import PackageTestCase

import unittest


class TestPackage(PackageTestCase, unittest.TestCase):
    project_name = "namespaceexample.native"
    meta_files = []
    configure_files = ["configure.zcml", "permissions.zcml", "browser/configure.zcml"]
    overrides_files = []
    standard_z3c_autoinclude = True
