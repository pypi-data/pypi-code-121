#!/usr/bin/python3
# -*- coding: Utf-8 -*-

from Libs import io_lib, search_lib

import numpy as np
import cv2, glob, os, re, pickle, copy, traceback, random, time


from geopy.distance import geodesic
from geopy.geocoders import Nominatim

try:
    geolocator  = Nominatim(user_agent="Mobba")
    location    = geolocator.geocode("Grenoble")
    ORIGIN = None
    if location is not None:
        ORIGIN = (location.latitude, location.longitude)

    ORIGINS = {}

    location = geolocator.geocode('France')
    if location is not None:
        ORIGINS['France'] = (location.latitude, location.longitude)
except:
    pass

if __name__ == '__main__':
    print(proxies)
    pass
    
