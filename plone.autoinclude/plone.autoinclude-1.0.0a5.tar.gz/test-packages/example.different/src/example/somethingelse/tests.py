from example.basetestpackage.package_base import PackageTestCase

import unittest


class TestPackage(PackageTestCase, unittest.TestCase):
    project_name = "example.different"
    module_name = "example.somethingelse"
    uses_plone_autoinclude = False
    standard_z3c_autoinclude = True
    features = ["different"]
