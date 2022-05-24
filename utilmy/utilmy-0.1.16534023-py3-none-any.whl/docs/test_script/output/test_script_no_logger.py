# -*- coding: utf-8 -*-
MNAME = "utilmy."
HELP = """ utils for




"""
import datetime, gc, glob, numpy as np, os, pandas as pd, sys, time
from typing import List, Optional, Tuple, Union
from numpy import ndarray
from box import Box






#############################################################################################


#############################################################################################
from utilmy import log, log2, help_create
def help():
   """function help.
   Doc::
           
          Args:
          Returns:
              
   """
   print( HELP + help_create(MNAME) )


def test_all() -> None:
    """function test_all.
    Doc::
            
        
    """
    log(MNAME)
    test1()
    test2()


def test1() -> None:
    """function test1.
    Doc::
            
            Args:
            Returns:
        
    """
    pass




def test2() -> None:
    """function test2.
    Doc::
            
            Args:
            Returns:
        
    """
    pass

#############################################################################################


def core1(sasas):
    """function core1.
    Doc::
            
            Args:
                sasas:   
            Returns:
                
    """
    pass


def core2(sasas):
    """function core2.
    Doc::
            
            Args:
                sasas:   
            Returns:
                
    """
    pass

def core3(sasas):
    """function core3.
    Doc::
            
            Args:
                sasas:   
            Returns:
                
    """
    pass

def core4(sasas):
    """function core4.
    Doc::
            
            Args:
                sasas:   
            Returns:
                
    """
    pass


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


