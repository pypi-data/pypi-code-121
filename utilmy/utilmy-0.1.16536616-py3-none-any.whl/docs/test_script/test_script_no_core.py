# -*- coding: utf-8 -*-
MNAME = "utilmy."
""" utils for




"""
import os, sys, glob, time,gc, datetime, numpy as np, pandas as pd
from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box






#############################################################################################
from utilmy import log, log2

def help():
    """function help"""
    from utilmy import help_create
    print( help_create(MNAME) )


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





###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


