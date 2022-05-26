#!/usr/bin/python

"""
Speech Transmission Index (STI) test script

Copyright (C) 2011 Jon Polom <jmpolom@wayne.edu>
Licensed under the GNU General Public License
"""

from datetime import date
from .sti import stiFromAudio, readwav
import  numpy as np

__author__ = "Jonathan Polom <jmpolom@wayne.edu>"
__date__ = date(2011, 4, 22)
__version__ = "0.5"

def cal_sti(refFile,testFile):
    # read audio
    refAudio, refRate = readwav(refFile)
    degrAudio, degrRate = readwav(testFile)

    ntimes = 20 // (len(refAudio) // refRate) + 2
    finalrefAudio, finaldegrAudio = np.repeat(refAudio, ntimes, 0), np.repeat(degrAudio, ntimes, 0)
    # calculate the STI. Visually verify console output.
    stis = stiFromAudio(finalrefAudio, finaldegrAudio, refRate, name=testFile)
    
    return stis

if __name__ == '__main__':
    cal_sti('','')
