# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:08:21 2021
"""
import copy
import math 
import numpy as np
import pandas as pd

def Mij(x, s = 'NULL', i = 0, j = 0):
    xd = x.shape
    if s == 'NULL':
        dim0 = xd[0]
        dim1 = xd[1]
        range0 = np.tile(np.arange(1, dim0+1), dim1)
        range1 = (np.arange(1, dim1+1)).repeat(dim0)
        s = np.stack((range0, range1), axis=-1)
    s[:, 0] = s[:, 0]**i
    s[:, 1] = s[:, 1]**j
    s = np.prod(s, axis = 1)    #每一行的两个元素相乘
    s = np.transpose(s.reshape((xd[1], xd[0])))    #变为两个矩阵相乘
    res = np.sum(np.sum(s * x))
        
    return res

def imomenter_matrix(x, loc = 'NULL'):
    out = {}
    #x为原始的观测场，非二值化的矩阵
    if loc == 'NULL':
        xd = x.shape
        dim0 = xd[0]
        dim1 = xd[1]
        range0 = np.tile(np.arange(1, dim0+1), dim1)
        range1 = (np.arange(1, dim1+1)).repeat(dim0)
        loc = np.stack((range0, range1), axis=-1)    
    M00 = Mij(x, s = loc.copy())
    M10 = Mij(x, s = loc.copy(), i = 1)
    M01 = Mij(x, s = loc.copy(), j = 1)
    M11 = Mij(x, s = loc.copy(), i = 1, j = 1)
    M20 = Mij(x, s = loc.copy(), i = 2)
    M02 = Mij(x, s = loc.copy(), j = 2)
    xbar = M10/M00
    ybar = M01/M00
    cen = pd.DataFrame(np.array([[xbar, ybar]]), columns=["x", "y"])
    mu11 = M11/M00 - xbar * ybar
    mu20 = M20/M00 - xbar**2
    mu02 = M02/M00 - ybar**2
    theta = 0.5 * math.atan2(2 * mu11, mu20 - mu02)
    out['area'] = M00
    out['centroid'] = cen
    out['orientation.angle'] = theta
    raw = pd.DataFrame(np.array([[M00, M10, M01, M11, M20, M02]]), 
                       columns=["M00", "M10", "M01", "M11", "M20", "M02"])
    out['raw.moments'] = raw
    out['cov'] = np.array([[mu20, mu11], [mu11, mu02]])
    out['class'] = "imomented"
    return out 

