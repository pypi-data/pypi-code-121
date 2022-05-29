#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as so


def solve_stst(mod):

    evars = mod["vars"]
    sys = mod["sys"]
    inits = mod.get("init")
    stst = mod.get("stst")

    def sys_stst(x):

        xss = ()
        for i, v in enumerate(evars):
            if v in stst:
                xss += (stst[v],)
            else:
                xss += (x[i],)

        XSS = np.array(x)
        trueXSS = np.array(xss)

        return sys(XSS, XSS, XSS, trueXSS)

    init = ()
    for v in evars:

        if v in stst.keys():
            init += (stst[v],)
        elif v in inits.keys():
            init += (inits[v],)
        else:
            init += (1.0,)

    res = so.root(sys_stst, init)

    if not res["success"] or np.any(np.abs(sys_stst(res["x"])) > 1e-8):
        raise Exception("Steady state not found")

    rdict = dict(zip(evars, res["x"]))
    return rdict


def solve_current(XLag, XPrime, mod):

    evars = mod["vars"]
    sys = mod["sys"]
    inits = mod.get("init")
    stst = mod.get("stst")

    sys_current = lambda x: sys(XLag, x, XPrime, stst.values())
    res = so.root(sys_current, XPrime)

    if not res["success"]:
        raise Exception("Current state not found")

    err = np.max(np.abs(sys_current(res["x"])))
    if err > 1e-8:
        print("Maximum error exceeds tolerance with %s." % err)

    return res["x"]
