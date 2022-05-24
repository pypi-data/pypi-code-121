from example.basetestpackage.package_base import PackageTestCase

import unittest


class TestPackage(PackageTestCase, unittest.TestCase):
    project_name = "example.addon"
    features = ["addon"]
    # We do not use target=plone.
    standard_z3c_autoinclude = False
