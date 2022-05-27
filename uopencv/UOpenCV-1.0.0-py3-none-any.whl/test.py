# -*- coding:utf-8 -*-

'''
test program
'''

import sys
import os

#import matplotlib
#matplotlib.use('WXAgg')  # wxPythonを使う場合、matplotlibのバックエンドを標準のTkAggからWXAggに変えておかないとハングアップする

from UOpenCV import UOpenCV 

if len(sys.argv) == 2:
    fname = sys.argv[1]
else:
    fname = 'lena.png'

color = UOpenCV(fname).imshow()
gray  = color.grayscale().imshow()
bin   = gray.threshold().imshow()


color.waitKey()
