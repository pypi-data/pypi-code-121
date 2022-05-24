from example.basetestpackage.package_base import PackageTestCase

import unittest


class TestPackage(PackageTestCase, unittest.TestCase):
    project_name = "ExampleCamelCase"
    meta_files = []
    configure_files = ["configure.zcml"]
    overrides_files = []
    standard_z3c_autoinclude = True
