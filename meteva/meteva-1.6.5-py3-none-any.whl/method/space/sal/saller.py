# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 11:08:18 2021

@author: 1
"""
import meteva.base as meb
import numpy as np
import pandas as pd
import cv2 as cv
import copy
import math

import sys
sys.path.append(r'F:\Work\MODE\Submit')
from mode import feature_props, feature_comps,data_pre
sys.path.append(r'F:\Work\MODE\tra_test-SAL')
import centdist, imomenter
import numpy as np
from mode.utils import get_attributes_for_feat, remove_key_from_list

def saller(grd_features, d = 'NULL'):
    '''
    out <- list()    #返回的结果是个列表
    a <- attributes(x)    
    if (!is.null(a$names)) 
        a$names <- NULL     #将属性全部赋值为空
    attributes(out) <- a
    '''
    distfun = "rdist"
    out = {}
    #if (x.keys() is not None):
        #x.keys() == 'NULL'        
    '''
    tmp <- x
    y <- tmp$Y.feats
    x <- tmp$X.feats
    binX <- im(tmp$X.labeled)
    binX <- solutionset(binX > 0)
    binY <- im(tmp$Y.labeled)
    binY <- solutionset(binY > 0)
    '''
    tmp = copy.deepcopy(grd_features)
    x = tmp['grd_ob_features']
    y = tmp['grd_fo_features']

    #规范属性，与R保持一致
    def re_attribute(data):
        grd_atts = {}
        m = data > 0
        grd_atts = {"area":x['area'], "dim":x['dim'], "m":m, "Type":x['Type'], 
                    "warning":x['warnings'], "xcol":x['xcol'], "yrow":x['yrow'], 
                    "xrange":x['xrange'], "yrange":x['yrange'], "xstep":x['xstep'],"ystep":x['ystep']}
        return grd_atts
    
    binX = re_attribute(data = tmp['grd_ob_labeled'])
    binY = re_attribute(data = tmp['grd_fo_labeled'])

    '''
    X <- tmp$X
    Y <- tmp$Xhat
    xdim <- dim(X)
    DomRmod <- mean(Y, na.rm = TRUE)
    DomRobs <- mean(X, na.rm = TRUE)
    A <- 2 * (DomRmod - DomRobs)/(DomRmod + DomRobs)
    out$A <- A
    '''
    X = tmp['grd_ob']
    Y = tmp['grd_fo']
    xdim = np.shape(X)
    DomRmod = np.mean(np.mean(Y))
    DomRobs = np.mean(np.mean(X))
    A = 2 * (DomRmod - DomRobs)/(DomRmod + DomRobs)
    out['A'] = A
    '''
    if (is.null(d)) 
        d <- max(xdim, na.rm = TRUE)
    num <- centdist(binY, binX, distfun = distfun, loc = a$loc, ...)
    cenX <- imomenter(tmp$X)$centroid
    cenXhat <- imomenter(tmp$Xhat)$centroid
    numOrig <- sqrt((cenX[1] - cenXhat[1])^2 + (cenX[2] - cenXhat[2])^2)
    '''
    if d == 'NULL':
        d = np.max(xdim)
    num = centdist.centdist(x = binY, y = binX, distfun = distfun, loc = tmp['loc'])    #注意loc是用numpy数组存放还是pandas
    cenX = imomenter.imomenter_matrix(x = tmp['grd_ob'])['centroid']
    cenXhat = imomenter.imomenter_matrix(x = tmp['grd_fo'])['centroid']
    numOrig = math.sqrt((cenX['x'] - cenXhat['x'])**2+(cenX['y'] - cenXhat['y'])**2)
    if d == "NULL":
        L1_alt = 0
    else:
        L1_alt = num/d
    L1 = numOrig/d
    '''
    intRamt = function(id, x) return(sum(x[id$m], na.rm = TRUE))
    
    RnMod = as.numeric(unlist(lapply(y, intRamt, x = Y)))    #Y为原始场，y为单独存放的目标
    RnObs = as.numeric(unlist(lapply(x, intRamt, x = X)))
    
    xRmodN = as.numeric(unlist(lapply(y, centdist, y = binY)))
    xRobsN = as.numeric(unlist(lapply(x, centdist, y = binX)))
    
    RmodSum = sum(RnMod, na.rm = TRUE)
    RobsSum = sum(RnObs, na.rm = TRUE)
    rmod = sum(RnMod * xRmodN, na.rm = TRUE)/RmodSum
    robs = sum(RnObs * xRobsN, na.rm = TRUE)/RobsSum
    L2 = 2 * abs(rmod - robs)/d    
    '''
    def intRamt(grd, grd_feats):
    #掩膜提取函数：grd为原始格点场，grd_feats为获得掩码用的布尔数组
    #将R里面求掩膜的和与最大值的两个函数intRamt、Rmaxer合并了
        grd_feats = data_pre.pick_labels(grd_feats)
    
        Obs_sum = []
        Obs_max = []
        res = {}
        for i in range(1, len(grd_feats)+1):
            #print(i)
            Obsdata_mask = np.mat(grd)    #需要掩膜的原始数据
            Obs_mask = grd_feats["labels_{}".format(i)] < 1     #掩膜范围
            Obs_masked = np.ma.array(Obsdata_mask, mask = Obs_mask)    #返回值有三类masked_array，mask,fill_value
            #求和
            Obs_sum_0 = np.sum(Obs_masked)
            Obs_sum.append(Obs_sum_0)
            #求最大值
            Obs_max_0 = np.max(Obs_masked)
            Obs_max.append(Obs_max_0)
        res = {"sum":Obs_sum, "max":Obs_max}

        return res
    
    RnMod = intRamt(grd = Y, grd_feats = y)["sum"]
    RnObs = intRamt(grd = X, grd_feats = x)["sum"]
    
    xRmodN = []
    xRobsN = []
    y_labels = data_pre.pick_labels(y)
    x_labels = data_pre.pick_labels(x)
    for i in range (1, len(y_labels)+1):
        #print(i)
        y_m = re_attribute(data = y_labels["labels_{}".format(i)])
        xRmodN_0 = centdist.centdist(x = y_m, y = binY)
        xRmodN.append(xRmodN_0)
        
    for i in range(1, len(x_labels)+1):
        #print(i)
        x_m = re_attribute(data = x_labels["labels_{}".format(i)])
        xRobsN_0 = centdist.centdist(x = x_m, y = binX)
        xRobsN.append(xRobsN_0)
    
    RmodSum = np.sum(RnMod)
    RobsSum = np.sum(RnObs)
    
    rmod = np.sum((np.array(RnMod) * np.array(xRmodN))/RmodSum)
    robs = np.sum((np.array(RnObs) * np.array(xRobsN))/RobsSum)
    L2 = 2 * abs(rmod - robs)/d 
    out.update({"L1":L1, "L2":L2, "L":L1 + L2, "L1_alt":L1_alt})
    
    '''
    Rmaxer <- function(id, x) return(max(x[id$m], na.rm = TRUE))
    RnMaxMod <- as.numeric(unlist(lapply(y, Rmaxer, x = Y)))
    RnMaxObs <- as.numeric(unlist(lapply(x, Rmaxer, x = X))) 
    '''
    #Rmaxer函数为求掩膜区域最大值，已经合并到intRamt函数里，此处直接调用
    RnMaxMod = intRamt(grd = Y, grd_feats = y)["max"]
    RnMaxObs = intRamt(grd = X, grd_feats = x)["max"]
    '''
    VmodN <- RnMod/RnMaxMod
    VobsN <- RnObs/RnMaxObs
    Vmod <- sum(RnMod * VmodN, na.rm = TRUE)/RmodSum
    Vobs <- sum(RnObs * VobsN, na.rm = TRUE)/RobsSum
    out$S <- 2 * (Vmod - Vobs)/(Vmod + Vobs)
    '''
    VmodN = np.array(RnMod)/np.array(RnMaxMod)
    VobsN = np.array(RnObs)/np.array(RnMaxObs)
    Vmod = np.sum(np.array(RnMod) * np.array(VmodN))/np.array(RmodSum)
    Vobs = np.sum(np.array(RnObs) * np.array(VobsN))/np.array(RobsSum)
    out['S'] = 2 * (Vmod - Vobs)/(Vmod + Vobs)
    out['class'] = "saller"
    
            
    return out
