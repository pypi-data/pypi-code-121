# -*- coding: utf-8 -*-
MNAME = "utilmy.docs.test_script.test_script_no_header"
HELP = "util"

import datetime, gc, glob, numpy as np, os, pandas as pd, sys, time

from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box






#############################################################################################
from utilmy import log, log2

def help():
    """function help"""
    from utilmy import help_create
    print( HELP + help_create(MNAME) )


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


