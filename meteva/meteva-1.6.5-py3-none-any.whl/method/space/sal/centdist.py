# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 18:30:00 2021
"""
import numpy as np
import sys

from meteva.method.space.mode.feature_props import feature_props


def centdist(x, y, distfun = "rdist", loc = None):
    xcen = feature_props(grd_feature = x, which_comps = ["centroid"],loc = loc)
    ycen = feature_props(grd_feature = y, which_comps = ["centroid"],loc = loc)
    x1 = np.array((xcen['centroid']['x'],xcen['centroid']['y'])).reshape(1,2)
    x2 = np.array((ycen['centroid']['x'],ycen['centroid']['y'])).reshape(1,2)
    out = np.sqrt(np.sum(np.square(x1 - x2)))
    return out