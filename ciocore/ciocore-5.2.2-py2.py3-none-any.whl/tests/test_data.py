""" test data

   isort:skip_file
"""
import json
import os
import sys
import unittest
from mock import patch
from ciocore import data

PROJECTS = [
    "Deadpool",
    "Harry Potter & the chamber of secrets",
    "Captain Corelli's Mandolin",
    "Gone with the Wind"
]

from package_fixtures import *
from instance_type_fixtures import *

class TestDataSingleton(unittest.TestCase):
 
    def setUp(self):
        projects_patcher = patch('ciocore.api_client.request_projects', return_value=PROJECTS)
        software_packages_patcher = patch('ciocore.api_client.request_software_packages', return_value=SOFTWARE_DATA)
        
        self.mock_projects = projects_patcher.start()
        self.mock_software_packages = software_packages_patcher.start()

        self.addCleanup(projects_patcher.stop)
        self.addCleanup(software_packages_patcher.stop)
        data.__data__ = {}
        data.__products__ = None

class TestDataAllInstanceTypes(TestDataSingleton):

    def setUp(self):
        super(TestDataAllInstanceTypes, self).setUp()
        instance_types_patcher = patch('ciocore.api_client.request_instance_types', return_value=ALL_INSTANCE_TYPES)
        self.mock_instance_types = instance_types_patcher.start()
        self.addCleanup(instance_types_patcher.stop)

    def test_init_empty_projects_global(self):
        data.init()
        self.assertEqual(data.products(), []) 


    def test_init_stores_all_args(self):
        data.init("a", "b", "c")
        self.assertEqual(data.products(), ["a", "b", "c"]) 


    def test_data_raises_if_not_initialized(self):
        with self.assertRaises(ValueError):
            data.data()

    def test_valid(self):
        self.assertEqual(data.valid(), False) 
        data.init()
        data.data()
        self.assertEqual(data.valid(), True) 

    def test_clear(self):
        data.init()
        data.data()
        self.assertEqual(data.valid(), True) 
        data.clear()
        self.assertEqual(data.valid(), False) 

    def test_does_not_refresh_if_not_force(self):
        data.init()
        p1 = data.data()["projects"]
        self.assertEqual(len(p1), 4) 
        self.mock_projects.return_value =  ["a", "b"]
        p2 = data.data()["projects"]
        self.assertEqual(p2, p1) 

    def test_does_refresh_if_force_all(self):
        data.init()
        p1 = data.data()["projects"]
        self.assertEqual(len(p1), 4) 
        self.mock_projects.return_value =  ["a", "b"]
        p2 = data.data(force=True)["projects"]
        self.assertNotEqual(p2, p1) 
        self.assertEqual(len(p2), 2) 
        
    def test_get_data_for_one_product(self):
        data.init("c4d")
        inst = data.data()["instance_types"]
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 2) 

    def test_auto_filter_instance_types_based_on_software_plaforms(self):
        data.init("maya")
        inst = data.data()["instance_types"]

    def test_several_products(self):
        data.init("c4d", "maya")
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 5)

    def test_one_product_can_be_a_plugin(self):
        data.init("redshift")
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 4)

    def test_several_products_ignore_plugins(self):
        data.init("redshift", "c4d")
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 2)

class TestDataHomogenousInstanceTypes(TestDataSingleton):

    def setUp(self):
        """
        The orchestrator provides only one platform.
        """
        super(TestDataHomogenousInstanceTypes, self).setUp()
        instance_types_patcher = patch('ciocore.api_client.request_instance_types', return_value=LIN_INSTANCE_TYPES)
        self.mock_instance_types = instance_types_patcher.start()
        self.addCleanup(instance_types_patcher.stop)

    def test_linux_only_instance_types(self):
        data.init()
        it = data.data()["instance_types"]
        self.assertEqual(len(it), 4) 

    def test_linux_only_packages_when_linux_only_instance_types(self):
        data.init("c4d")
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 1)

    def test_platforms_method_only_linux(self):
        data.init("c4d")
        data.data()
        self.assertEqual({"linux"}, data.platforms()) 

    def test_several_products(self):
        data.init("c4d", "maya")
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 4)
  

class TestBackwardsCompatibiliity(TestDataSingleton):

    def setUp(self):
        super(TestBackwardsCompatibiliity, self).setUp()
        instance_types_patcher = patch('ciocore.api_client.request_instance_types', return_value=ALL_INSTANCE_TYPES)
        self.mock_instance_types = instance_types_patcher.start()
        self.addCleanup(instance_types_patcher.stop)

    def test_product_keyword_translates_to_single_arg(self):
        data.init(product="c4d")
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 2) 

    def test_product_keyword_all_translates_to_all_products(self):
        data.init(product="all")
        sw = data.data()["software"]
        self.assertEqual(len(sw.supported_host_names()), 11) 

    def test_data_raises_if_both_products_and_kwarg_given(self):
        with self.assertRaises(ValueError):
             data.init("maya", product="c4d")

    def test_data_raises_if_both_products_and_kwarg_given(self):
        with self.assertRaises(ValueError):
             data.init("maya", product="c4d")

