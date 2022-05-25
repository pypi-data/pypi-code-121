# Author : bb
# Time : 2020/11/18 16:59
# -*- coding: utf-8 -*-

import numpy as np
from sklearn.neighbors import KDTree
np.seterr(divide='ignore',invalid='ignore')

class IDW():
    def __init__(self, y, x,   candidate=15):
        self.disMat = None
        self.idMat = None
        self.disPoint = None
        self.idPoint = None
        self.x = x
        self.y = y
        self.resultMat = None
        self.resultPont = None
        self.candidate = candidate

    def initDictMat(self,ltc,resolution=0.01):
        self.evn = ltc
        self.resolution = resolution
        self.latRange = int((self.evn.n - self.evn.s + 10e-10) // self.resolution) + 1
        self.lonRange = int((self.evn.e - self.evn.w + 10e-10) // self.resolution) + 1
        self.latArr = np.linspace(self.evn.n, self.evn.s, self.latRange)
        self.lonArr = np.linspace(self.evn.w, self.evn.e, self.lonRange)
        latArr = np.linspace(self.evn.n, self.evn.s, self.latRange)
        lonArr = np.linspace(self.evn.w, self.evn.e, self.lonRange)
        lonMat, latMat = np.meshgrid(lonArr, latArr)
        tree = KDTree(np.c_[self.y, self.x])
        xyMesh = np.c_[latMat.reshape(-1), lonMat.reshape(-1)]
        dist, ind = tree.query(xyMesh, k=self.candidate)
        self.disMat = dist.reshape([len(latArr), len(lonArr), self.candidate])
        self.idMat = ind.reshape([len(latArr), len(lonArr), self.candidate])

    def getMat(self,z):
        valMat = z[self.idMat]
        disAll = np.sum(1 / np.power(self.disMat, 2), axis=2)
        dataAll = np.sum(valMat / np.power(self.disMat, 2), axis=2)
        self.resultMat = dataAll / disAll
        self.resultMat[self.disMat[:, :, 0] == 0] = valMat[self.disMat[:, :, 0] == 0, 0]
        return self.resultMat

    def initDictPoints(self,yP, xP):
        tree = KDTree(np.c_[self.y, self.x])
        xyMesh = np.c_[yP, xP]
        dist, ind = tree.query(xyMesh, k=self.candidate)
        self.disPoint = dist
        self.idPoint = ind
        print()

    def getPoint(self, z):
        valPont = z[self.idPoint]
        disAll = np.sum(1 / np.power(self.disPoint, 2),axis=1)
        dataAll = np.sum(valPont / np.power(self.disPoint, 2),axis=1)
        self.resultPont = dataAll / disAll
        self.resultPont[self.disPoint[:,0] == 0] = valPont[self.disPoint[:,0] == 0, 0]
        return self.resultPont









