# unit_test_mh_eg.py

import os
import sys

#testdir = os.path.dirname(__file__)
#testdir = os.path.realpath(__file__)
testdir = os.getcwd()
srcdir = '../..'
src_path =  os.path.abspath(os.path.join(testdir, srcdir))
sys.path.insert(0, os.path.abspath(src_path))

import unittest
from unittest import mock
#import patch

from mhlib import eg

class TestMhlibEg(unittest.TestCase):
    def test_var(self):
        self.assertEqual(eg.EG_VAR, 'abcd')

    def test_func(self):
        rtn = eg.test()
        self.assertEqual(rtn,'ok')

class TestMhEg(unittest.TestCase):
    def test_runMh(self):
        x = eg.MhEg()
        y = x.runMhEg()
        self.assertEqual( y, 10 )

    @mock.patch('mhlib.eg.MhEg.slow', return_value=3)
    def test_slow(self, mocked_func ):
        x = eg.MhEg()
        rtn = x.slow()
        self.assertEqual(rtn,3)

    @mock.patch('mhlib.l2.l2.L2Mh.slow', return_value=5)
    def test_external_func(self, mocked_func):
        x = eg.MhEg()
        rtn = x.call_external_func()
        self.assertEqual(rtn,5)


if __name__ == '__main__':
    unittest.main()
