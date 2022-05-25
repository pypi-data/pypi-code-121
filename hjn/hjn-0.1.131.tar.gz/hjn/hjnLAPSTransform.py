# -*- coding:utf-8 -*-
# Author:hujunnan

import numpy as np

# p = Proj("+proj=lcc +lat_0=30 +lon_0= 102 +lat_1=30 +lat_2=60")

class LAPSTransfrom():
    def __init__(self,p,lonMat, latMat,env=None,step=0.03):
        xMat, yMat = p(lonMat, latMat)
        x0 = np.min(xMat)
        y0 = np.max(yMat)
        if env is None:
            n,s,w,e = np.max(latMat),np.min(latMat),np.min(lonMat),np.max(lonMat)
            lat0 = n
            lat1 = s
            lon0 = w
            lon1 = e
        else:
            lat0 = env.n
            lat1 = env.s
            lon0 = env.w
            lon1 = env.e
        self.step = step
        self.rangeLat = int(np.ceil(((lat0 - lat1) / step))) + 1
        self.rangeLon = int(np.ceil(((lon1 - lon0) / step))) + 1
        self.latArr = np.asarray([lat0 - i*step for i in range(self.rangeLat)],np.float64)
        self.lonArr = np.asarray([lon0 + i*step for i in range(self.rangeLon)],np.float64)
        latMatCHN = np.repeat([self.latArr], self.rangeLon, axis=0).T
        lonMatCHN = np.repeat([self.lonArr], self.rangeLat, axis=0)
        latMatCHNArr = latMatCHN.reshape(-1)
        lonMatCHNArr = lonMatCHN.reshape(-1)
        x, y = p(lonMatCHNArr, latMatCHNArr)
        self.latIdx = ((y0 - y) / (step*100000) + 0.5).astype(int)
        self.lonIdx = ((x - x0) / (step*100000) + 0.5).astype(int)
        self.latMaskValid = np.logical_or(self.latIdx < 0, self.latIdx >= latMat.shape[0])
        self.lonMaskValid = np.logical_or(self.lonIdx < 0, self.lonIdx >= latMat.shape[1])
        self.latIdx[self.latMaskValid] = 0
        self.lonIdx[self.lonMaskValid] = 0

    def LambertToLatLon(self,t):
        lambertMat = t[self.latIdx, self.lonIdx]
        lambertMat = lambertMat.reshape([self.rangeLat, self.rangeLon])
        lambertMat[self.latMaskValid.reshape([self.rangeLat, self.rangeLon])] = np.nan
        lambertMat[self.lonMaskValid.reshape([self.rangeLat, self.rangeLon])] = np.nan
        return lambertMat

