# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

provide basic python unittest.TestSuite of the following test cases:
    - hyssop.util, worker, and executor
    - hyssop.project.web config validation, components and controllers

use get_test_suite() to get the default or extend test suite by inheriting "hyssop.unit_test.UnitTestTypes."

Usage:
    - to create unit_test extension module:

        0. the hierarchy of folders and files looks like:

            server_directory/
                server_config.yaml
                unit_test/
                    __init__.py
                    foo.py

        1. "foo.py" defines class FooTestCase:

            from hyssop.unit_test import UnitTestCase
            
            class FooTestCase(UnitTestCase):
                # override this test method
                def test(self):
                    # test modules...

        2. "__init__.py" defines the enum class allows load the test case classes dynamically,

            from hyssop.unit_test import UnitTestTypes

            class ExTestTypes(UnitTestTypes):
                FooTest = ('foo_test', 'foo', 'FooTestCase')

        3. In the commond prompt, run command "python -m hyssop test <server_directory>" 
            to test all the extend test cases defined in "__init__.py"

Modified By: hsky77
Last Updated: November 22nd 2020 12:23:32 pm
'''

import unittest

from .base import UnitTestTypes, UnitTestCase


class DefaultUnitTestTypes(UnitTestTypes):
    TestUtil = ('test_util', 'util', 'UtilTestCase')
    TestWorker = ('test_worker', 'util_worker', 'WorkerTestCase')


def get_test_suite() -> unittest.TestSuite:
    """get test suite of unittest module. 
    It will try to load extend test suite if specifed in server folder "unit_test", elsewise default test suite.
    Default test suite tests util and web modules of hyssop
    """

    suite = unittest.TestSuite()
    # extension tests
    try:
        enums = UnitTestTypes.get_unittest_enum_class()
    except:
        pass

    enums = enums if enums else [DefaultUnitTestTypes]

    # default tests
    for enum in enums:
        for test_case in enum:
            test_cls = test_case.import_class()
            suite.addTest(test_cls('test'))

    return suite
