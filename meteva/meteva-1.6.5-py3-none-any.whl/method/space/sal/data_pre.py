# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 16:02:42 2021

@author: 1
"""
import sys
sys.path.append(r'F:\Work\MODE\Submit')
from mode.utils import get_attributes_for_feat, remove_key_from_list

tmp_x = x['Xlabelsfeature']
tmp_y = x['Ylabelsfeature']
            
remove_list = ['Type', 'xrange', 'yrange', 'dim', 'xstep', 'ystep', 'warnings', 'xcol', 'yrow', 'area']
xkeys = remove_key_from_list(list(tmp_x.keys()), remove_list)
ykeys = remove_key_from_list(list(tmp_y.keys()), remove_list)
xattribute = {}
yattribute = {}
for i in range(len(xkeys)):
    xmat = tmp_x[xkeys[i]]
    if xmat.dtype.name is not 'bool':
        xmat = (xmat == 1)
    xmat = {"m": xmat}
    xmat.update(xattribute)
for i in range (len(ykeys)):
    ymat = tmp_y[ykeys[i]]
    if ymat.dtype.name is not 'bool':
        ymat = (ymat == 1)
    ymat = {"m": ymat}
    ymat.update(yattribute)