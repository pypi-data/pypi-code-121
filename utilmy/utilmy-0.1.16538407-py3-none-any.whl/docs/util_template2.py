#### BLOCK HEADER  #######################################################
# -*- coding: utf-8 -*-
MNAME = "utilmy."
HELP = """ utils for

"""





#### BLOCK IMPORT  ######################################################
import os, sys, glob, time,gc, datetime, numpy as np, pandas as pd
from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box





#### BLOCK logger  ######################################################
from utilmy import log, log2, help_create

def help():
    print( HELP + help_create(__file__) )






#### BLOCK test  ########################################################
def test_all() -> None:
    """function test_all"""
    log(MNAME)
    test1()
    test2()


def test1() -> None:
    """ test """
    pass




def test2() -> None:
    """ test """
    pass








#### BLOCK CORE  #########################################################
"""
Nothing to do

"""











#### BLOCK FOOTER  ########################################################
if __name__ == "__main__":
    import fire
    fire.Fire()

    ## local_path = "utilmy/" +  __file__.split("utilmy")[1] 
    ### python {local_path}   test_all


