#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

def calc_timestamp_anchor_in_hour(curTs, interval):
    tslicecount = int(3600 / interval)
    if tslicecount <= 0:
        tslicecount = 1
    st = time.localtime(curTs)
    tmin = st.tm_min
    tsec = st.tm_sec
    if tslicecount > 60:
        step = int(60 / (tslicecount / 60))
        tsec = st.tm_sec - (st.tm_sec % step)
    else:
        step = int(60 / tslicecount)
        tsec = 0
        tmin = st.tm_min - (st.tm_min % step)
    cvtTs = time.mktime((st.tm_year, st.tm_mon, st.tm_mday, st.tm_hour, tmin, tsec, st.tm_wday, st.tm_yday, st.tm_isdst))

    return cvtTs
