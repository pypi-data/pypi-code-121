# test1.py


import os
import sys

testdir = os.getcwd()
srcdir = '../..'
src_path =  os.path.abspath(os.path.join(testdir, srcdir))
sys.path.insert(0, os.path.abspath(src_path))


import mh
from mhlib import eg
# import mhlib.eg as eg
from  mhlib.l2 import l2



def test():
    print ('#'*40)
    print ('file under test:', mh)
    print ('version:', mh.__version__)
    print ('doc:', mh.__doc__)
    print ('dir:', dir(mh))
    print ('.'*10)
    print ('file under test:', eg)
    print ('doc:', eg.__doc__)
    print ('dir:', dir(eg))
    print ('.'*10)
    print ('file under test:', l2)
    print ('doc:', l2.__doc__)
    print ('dir:', dir(l2))


if __name__ == '__main__':
    test()
    print ('Done')
