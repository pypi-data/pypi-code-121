import sys
import os
import numpy as np
import cv2
import json
from collections import defaultdict
import unittest
import torch

sys.path.insert(0, os.path.abspath('')) # Test files from current path rather than installed module
from pymlutil.jsonutil import *

test_config = 'test.yaml'

class Test(unittest.TestCase):
    def test_cmd(self):
        result, _, _ = cmd('ls -la', check=True, timeout=5)
        self.assertEqual(result, 0)

    def test_yaml(self):
        test = ReadDict(test_config)
        assert test is not None
        assert 'test_yaml' in test
        self.assertEqual(test['test_yaml'][0]['zero'], 0)
        self.assertEqual(test['test_yaml'][1]['one'], 1)
        self.assertEqual(test['test_yaml'][2]['two'], 2)

if __name__ == '__main__':
    unittest.main()