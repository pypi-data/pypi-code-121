from cProfile import label
import sys
import rsrfile
import os
import numpy as np
import pandas as pd


def todf(a):
    df = pd.DataFrame(a[1:], columns=a[0])
    return df


def printdf(a, limit=None):
    if limit == None:
        print(todf(a))
    else:
        print(todf(a)[:limit])


def print_mcs(mcs):
    for row in mcs:
        print('\t'.join([str(r) for r in row]))


#fileobj = rsrfile.open(r'./tests/data/mcs_acase.RSR')
fileobj = rsrfile.open(r'./tests/data/cons_acase.RSR')
# printdf(fileobj.param_im)
# printdf(fileobj.ccfg_im)
# printdf(fileobj.attr_im)
# printdf(fileobj.pdf)
# printdf(fileobj.cdf)
# printdf(fileobj.comp_im)
# printdf(fileobj.sys_im)
# printdf(fileobj.eg_im)
printdf(fileobj.mcs, 500)
# print(fileobj.mcs[0])
# printdf(fileobj.be_im)
# print(fileobj.mcs)
