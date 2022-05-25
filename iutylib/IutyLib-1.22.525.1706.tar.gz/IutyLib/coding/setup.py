import sys
sys.path.insert(0,"./")
import time
from test import unittest,_unittest_,skip


def init():
    return 1
    

class A:
    def add(a,b):
        return a+b
    
    @unittest
    def testaddinclass():
        rst = A.add(1,2)
        assert rst == 3, "not exactly"
@skip
@unittest
def testinit():
    
    assert init() == 0, "mmm"

@unittest
def testadd():
    rst = A.add(1,2)
    assert rst == 3, "not exactly"

