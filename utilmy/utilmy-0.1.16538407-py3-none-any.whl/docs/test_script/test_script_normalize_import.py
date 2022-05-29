# -*- coding: utf-8 -*-
MNAME = "utilmy."
""" utils for




"""
import os, sys, glob, time,gc, datetime, numpy as np, pandas as pd
import types
import abc
import ccxt
from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box






#############################################################################################
from utilmy import log, log2

def help():
    """function help"""
    from utilmy import help_create
    print( help_create(__file__) )


def log3():
    """function help"""
    pass

#############################################################################################
def test_all() -> None:
    """function test_all

    """
    log(MNAME)
    test1()
    test2()


def test1() -> None:
    """function test1
    Args:
    Returns:

    """
    pass




def test2() -> None:
    """function test2
    Args:
    Returns:

    """
    pass

#############################################################################################


def core1(sasas):
    pass


def core2(sasas):
    pass

def core3(sasas):
    pass

def core4(sasas):
    pass


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


