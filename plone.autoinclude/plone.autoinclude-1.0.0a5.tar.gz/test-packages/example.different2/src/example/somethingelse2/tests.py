from example.basetestpackage.package_base import PackageTestCase

import unittest


class TestPackage(PackageTestCase, unittest.TestCase):
    project_name = "example.different2"
    module_name = "example.somethingelse2"
    features = ["different2"]
