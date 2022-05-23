# tests/__init__.py

import unittest
import mh

def mh_test_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(mh)
    return suite
