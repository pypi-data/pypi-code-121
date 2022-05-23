# perf_test

import os
import sys

#testdir = os.path.dirname(__file__)
#testdir = os.path.realpath(__file__)
testdir = os.getcwd()
srcdir = '../..'
src_path =  os.path.abspath(os.path.join(testdir, srcdir))
sys.path.insert(0, os.path.abspath(src_path))

from pycrunch_trace.client.api import trace


from mhlib.l2 import l2


def test_l2_var():
    l2.L2EG_VAR,'efgh'

def test_l2_slow():
    x = l2.L2Mh()
    rtn = x.run()
    import time
    time.sleep(3)

def test_l2_ext():
    x = l2.L2Mh()
    rtn = x.slow()
    rtn = x.slow()

@trace
def run():
    test_l2_var()
    test_l2_slow()
    test_l2_ext()

if __name__ == '__main__':
    print ( sys.executable)
    print ( sys.version)
    print ( "Load the session file to http: // app.pytrace.com /")
    run()
