""" test package_tree
"""
import unittest
import os
import sys
import copy
from ciocore import package_tree
from package_fixtures import *


class ToNameTest(unittest.TestCase):

    def setUp(self):
        self.packages = copy.deepcopy(BLENDER_DATA)

    def test_major(self):
        pkg = self.packages[0]
        expected = "blender 1 linux"
        self.assertEqual(package_tree.to_name(pkg), expected)

    def test_major_minor(self):
        pkg = self.packages[1]
        expected = "blender 1.0 linux"
        self.assertEqual(package_tree.to_name(pkg), expected)

    def test_major_minor_release(self):
        pkg = self.packages[2]
        expected = "blender 1.0.2 linux"
        self.assertEqual(package_tree.to_name(pkg), expected)

    def test_major_minor_release_build(self):
        pkg = self.packages[3]
        expected = "blender 1.0.2.3 linux"
        self.assertEqual(package_tree.to_name(pkg), expected)

    def test_bad_platform(self):
        with self.assertRaises(KeyError):
            pkg = self.packages[0]
            pkg["platform"] = "bad"
            package_tree.to_name(pkg)

class SoftwareDataInitTest(unittest.TestCase):
    def setUp(self):
        """
        Pad out with just enough fields to allow link_plugin_packages() to run.
        """
        self.packages = copy.deepcopy(SOFTWARE_DATA)

    def test_smoke(self):
        pt = package_tree.PackageTree([])
        self.assertIsInstance(pt, package_tree.PackageTree)

    def test_init_with_filter_host_products(self):
        pt = package_tree.PackageTree(self.packages, "maya", "blender")
        self.assertEqual(len(pt.as_dict()["children"]), len(MAYA_DATA+BLENDER_DATA))
 
    def test_init_with_one_product(self):
        pt = package_tree.PackageTree(self.packages, product="redshift")
        self.assertEqual(len(pt.as_dict()["children"]), len(REDSHIFT_DATA))
 
    def test_init_with_all_product(self):
        pt = package_tree.PackageTree(self.packages)
        self.assertEqual(len(pt.as_dict()["children"]), len(HOST_DATA))

    def test_filter_platform(self):
        pt = package_tree.PackageTree(self.packages, platforms=["windows"])
        expected = [h for h in HOST_DATA if h["platform"] == "windows"]
        self.assertEqual( len(pt.as_dict()["children"]) , len(expected) )

    def test_filter_platform_and_product(self):
        pt = package_tree.PackageTree(self.packages, product="c4d", platforms=["linux"])
        expected = [h for h in C4D_DATA if h["platform"] == "windows"]
        self.assertEqual(len(pt._tree["children"]),  len(expected))

    def test_raise_bad_platform(self):
        with self.assertRaises(KeyError):
            pt = package_tree.PackageTree(self.packages, platforms=["bad"])

    def test_nonexistent_product_falsy(self):
        pt = package_tree.PackageTree(self.packages, product="noexist")
        self.assertFalse(pt)

    def test_good_product_truthy(self):
        pt = package_tree.PackageTree(self.packages, product="redshift")
        self.assertTrue(pt)

    def test_as_dict_returns_underlying_tree(self):
        pt = package_tree.PackageTree(self.packages)
        self.assertEqual(pt.as_dict(), pt._tree)
        self.assertIsInstance(pt.as_dict(), dict)


class SoftwareDataFindersTest(unittest.TestCase):

    def setUp(self):
        self.packages = copy.deepcopy(SOFTWARE_DATA)
        self.pt = package_tree.PackageTree(self.packages, product="maya")
 
    def test_find_root_path(self):
        path = "maya 1.1 linux"
        pkg = self.pt.find_by_path(path)
        self.assertEqual(package_tree.to_name(pkg), path)

    def test_find_leaf_path(self):
        path = "maya 1.1 linux/redshift 1 linux"
        pkg = self.pt.find_by_path(path)
        self.assertEqual(package_tree.to_name(pkg), "redshift 1 linux")

    def test_find_nonexistent_path_return_none(self):
        path = "maya 1.1 linux/redshift 3 linux"
        pkg = self.pt.find_by_path(path)
        self.assertEqual(pkg, None)

    def test_find_empty_path_return_none(self):
        path = ""
        pkg = self.pt.find_by_path(path)
        self.assertEqual(pkg, None)

    def test_find_root(self):
        name = 'maya 1.1 linux'
        result = self.pt.find_by_name(name)
        self.assertEqual(package_tree.to_name(result), name)

    def test_find_root_when_limit_1(self):
        name = 'maya 1.1 linux'
        result = self.pt.find_by_name(name, 1)
        self.assertEqual(package_tree.to_name(result), name)

    def test_find_plugin_level(self):
        name = "redshift 1 linux"
        result = self.pt.find_by_name(name)
        self.assertEqual(package_tree.to_name(result), name)

    def test_dont_find_plugin_level_when_limited(self):
        name = "redshift 1 linux"
        result = self.pt.find_by_name(name, 1)
        self.assertEqual(result, None)

class SoftwarePlatformsSetTest(unittest.TestCase):
    # There are Windows packages in c4d but not Maya.
    def setUp(self):
        self.packages = copy.deepcopy(SOFTWARE_DATA)
   
    def test_only_linux(self):
        pt = package_tree.PackageTree(self.packages, product="maya")
        self.assertEqual({"linux"}, pt.platforms())

    def test_linux_and_windows(self):
        pt = package_tree.PackageTree(self.packages, product="c4d")
        self.assertEqual({"windows", "linux"}, pt.platforms())


class SupportedHostNamesTest(unittest.TestCase):
    def setUp(self):
        self.packages = copy.deepcopy(SOFTWARE_DATA)

    def test_supported_host_names(self):
        self.pt = package_tree.PackageTree(self.packages, product="maya")
        host_names = self.pt.supported_host_names()
        self.assertEqual(len(host_names), 3)
        self.assertIn('maya 1.1 linux', host_names)

    def test_supported_host_names_windows(self):
        self.pt = package_tree.PackageTree(self.packages, product="c4d", platforms=["windows"])
        host_names = self.pt.supported_host_names()
        self.assertEqual(len(host_names), 1)
        self.assertIn('c4d 1.0 windows', host_names)


class SupportedPluginsTest(unittest.TestCase):
    def setUp(self):
        self.packages = copy.deepcopy(SOFTWARE_DATA)
        self.pt = package_tree.PackageTree(self.packages, product="maya")
        self.one_hostname = 'maya 1.0 linux'

    def test_supported_plugins_keys(self):
        plugins = self.pt.supported_plugins(self.one_hostname)
        self.assertIsInstance(plugins[0], dict)
        self.assertIn("plugin",plugins[0])
        self.assertIn("versions",plugins[0])

    def test_supported_plugins_and_versions_count(self):
        plugins = self.pt.supported_plugins(self.one_hostname)
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["versions"], ["1", "2"])

if __name__ == "__main__":
    unittest.main()
