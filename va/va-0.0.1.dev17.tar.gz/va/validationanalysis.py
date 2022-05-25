"""
validationanalysis.py

ValidationAnalysis is a class including methods for map validation
Methods:
    Orthogonal projections
    Atom and residue inclusion
    Central slice
    Map-density distribution
    Volume estimate
    FSC
    RAPS
    Largest image variance
    Memory prediction

Copyright [2013] EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the
"License"); you may not use this file except in
compliance with the License. You may obtain a copy of
the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.

"""

__author__ = 'Zhe Wang'
__email__ = 'zhe@ebi.ac.uk'
__date__ = '2018-07-24'

import numpy as np
import pandas as pd
from numpy.fft import fftshift, fftn
from PIL import Image
import cv2
from scipy.interpolate import RegularGridInterpolator
from scipy import ndimage
from collections import OrderedDict
from math import floor, ceil, log10, pi
import json
import codecs
import matplotlib as mpl
import bisect
import math
import gc

mpl.use('Agg')
import matplotlib.pyplot as plt
import os, timeit, sys, glob, subprocess
from six import iteritems
from distutils.spawn import find_executable
import re
import mrcfile
# from memory_profiler import profile
from Bio.PDB import PDBParser as orgPDBParser
from Bio.PDB import MMCIFParser
from Bio.PDB.mmcifio import MMCIFIO
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from scipy.fftpack import fftn, fftshift
from va.metrics.strudel import run_strudel
from va.metrics.emda_mmcc import run_realmmcc
from va.metrics.emringer import run_emringer
from va.metrics.threedfsc import run_threedfsc

# if sys.version_info[0] == 2:
#     from TEMPy.EMMap import Map
#     from TEMPy.StructureParser import PDBParser
#     from TEMPy.MapParser import MapParser
#     from TEMPy.ScoringFunctions import ScoringFunctions
#     from TEMPy.StructureBlurrer import StructureBlurrer
#
# else:
#     from TEMPy.maps.em_map import Map
#     from TEMPy.protein.structure_parser import PDBParser
#     from TEMPy.maps.map_parser import MapParser
#     from TEMPy.protein.scoring_functions import ScoringFunctions
#     from TEMPy.protein.structure_blurrer import StructureBlurrer


try:
    from PATHS import MAP_SERVER_PATH
    from PATHS import PROSHADEPATH
    from PATHS import MESHMAKERPATH
    from PATHS import CHIMERA
    from PATHS import OCHIMERA
    from PATHS import LIB_STRUDEL_ROOT
except ImportError:
    MAP_SERVER_PATH = None
    PROSHADEPATH = None
    CHIMERA = None
    MESHMAKERPATH = None
    OCHIMERA = None
    LIB_STRUDEL_ROOT = None

try:
    import vtk
except ImportError:
    print('ChimeraX will be used to produce for the surface view.')


##############################

# def pssum(i, dist, indiaxis, indiaxist, psmap):
#     if i != len(indiaxis) - 1:
#         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
#
#         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
#         return psum


# test 3

def pssum(a, indiaxis, indiaxist, shared_array):
    res = []
    for i in a:
        if i != len(indiaxis) - 1:
            indices = np.argwhere((shared_array > indiaxist[i]) & (shared_array <= indiaxist[i + 1]))
            if i == 0 or i == 1:
                print(np.ndarray.tolist(indices))
                print(len(indices[0]))
                print('indiaxist[{}]={}, indiaxist[{}+1]'.format(i, indiaxist[i], indiaxist[i+1] ))
            res.append(indices)
    return res


# def pcal(a, indiaxis, dist, indiaxist):
#     b = []
#     for i in a:
#         b.append(pssum(i, indiaxis, dist, indiaxist))
#     return b

# def pssum(lenind, psmap):
#     psum = log10(psmap.sum() / len(lenind))
#     return psum
#
# def pcal(a, allindices, allpsmap):
#     b = []
#     print('indside pcal')
#     print(len(allindices))
#     for i in a:
#
#         lenind = allindices[i]
#         psmap = allpsmap[i]
#
#         b.append(pssum(lenind, psmap))
#     return b




############################

class ValidationAnalysis:
    """
    Validation Analysis class

    """

    def __init__(self, map=None, model=None, pid=None, halfeven=None, halfodd=None, rawmap=None, contourlevel=None,
                 emdid=None, dir=None, met=None, resolution=None, fscfile=None, masks=None, modelsmaps=None,
                 strudellib=None, threedfscdir=None, platform=None):
        """

            Constructor function of ValidationAnalysis class

        :param map: Map instance from TEMPy package
        :param model: Model instance from TEMPy CIF file parser
        :param pid: structure id
        :param halfmap: Map instance for FSC calculation
        :param contourlevel: Float value which recommended by the author or EMDB

        """

        self.models = model
        self.map = map
        # self.mapname = os.path.basename(os.path.splitext(map.filename)[0])
        # self.mapname = os.path.basename(map.filename)
        self.mapname = os.path.basename(map.fullname)
        self.pid = pid
        self.emdid = emdid
        self.hmeven = halfeven
        self.hmodd = halfodd
        self.rawmap = rawmap
        self.met = met
        self.resolution = resolution
        self.fscfile = fscfile
        self.allmasks = masks
        self.modelsmaps = modelsmaps
        self.strudellib = strudellib
        self.threedfscdir = threedfscdir
        self.platform = platform
        if contourlevel is not None:
            self.cl = float(contourlevel)
        else:
            self.cl = contourlevel
        if self.emdid:
            digits = [i for i in str(self.emdid)]
            if len(digits) == 4:
                subdir = '{}/{}/'.format(digits[0] + digits[1], self.emdid)
                self.workdir = MAP_SERVER_PATH + subdir + 'va/'
            elif len(digits) == 5:
                subdir = '{}/{}/{}/'.format(digits[0] + digits[1], digits[2], self.emdid)
                self.workdir = MAP_SERVER_PATH + subdir + 'va/'
            else:
                pass
        else:
            self.workdir = dir



    # Glow LUT for color image
    def glowimage(self, im_gray):
        """Applies a glow color map using cv2.applyColorMap()"""

        # Create the LUT:
        lut = np.zeros((256, 1, 3), dtype=np.uint8)
        lut[:, 0, 2] = [0, 1, 1, 2, 2, 3, 4, 6, 8, 11, 13, 15, 18,
                        21, 23, 24, 27, 30, 31, 33, 36, 37, 40, 42, 45, 46,
                        49, 51, 53, 56, 58, 60, 62, 65, 68, 70, 72, 74, 78,
                        80, 82, 84, 86, 89, 91, 93, 96, 98, 100, 102, 104, 106,
                        108, 110, 113, 115, 117, 119, 122, 125, 127, 129, 132, 135, 135,
                        137, 140, 141, 142, 145, 148, 149, 152, 154, 156, 157, 158, 160,
                        162, 164, 166, 168, 170, 171, 173, 174, 176, 178, 179, 180, 182,
                        183, 185, 186, 189, 192, 193, 193, 194, 195, 195, 196, 198, 199,
                        201, 203, 204, 204, 205, 206, 207, 209, 211, 211, 211, 211, 213,
                        215, 216, 216, 216, 216, 218, 219, 219, 219, 220, 222, 223, 223,
                        223, 223, 224, 224, 226, 227, 227, 227, 227, 228, 229, 231, 231,
                        231, 231, 231, 231, 231, 232, 233, 234, 234, 234, 234, 234, 234,
                        235, 237, 238, 238, 238, 238, 238, 238, 238, 238, 239, 240, 242,
                        242, 242, 242, 242, 242, 242, 242, 242, 243, 245, 246, 246, 246,
                        246, 245, 245, 245, 245, 245, 245, 245, 247, 248, 249, 249, 249,
                        249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249,
                        249, 250, 252, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
                        253, 253, 253, 253, 253, 253, 253, 253, 0]

        lut[:, 0, 1] = [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2,
                        2, 2, 2, 2, 3, 3, 3, 3, 4, 5, 5, 5, 5,
                        6, 6, 6, 7, 7, 8, 9, 9, 9, 9, 10, 10, 11,
                        12, 13, 14, 14, 14, 14, 15, 16, 16, 17, 18, 19, 19,
                        19, 20, 21, 22, 23, 24, 24, 25, 27, 28, 28, 28, 29,
                        31, 32, 32, 33, 35, 36, 36, 37, 39, 40, 40, 41, 42,
                        43, 45, 46, 47, 48, 50, 51, 52, 54, 55, 56, 57, 59,
                        62, 63, 65, 66, 68, 70, 71, 73, 74, 75, 77, 79, 81,
                        83, 85, 87, 89, 92, 93, 96, 98, 99, 100, 103, 105, 107,
                        109, 111, 113, 116, 117, 119, 121, 123, 125, 126, 128, 130, 132,
                        135, 137, 139, 140, 142, 144, 145, 147, 148, 150, 152, 154, 156,
                        158, 160, 161, 162, 164, 166, 168, 171, 172, 172, 174, 176, 177,
                        179, 180, 182, 183, 185, 187, 188, 189, 191, 192, 192, 192, 196,
                        200, 201, 201, 202, 203, 204, 206, 208, 210, 212, 213, 213, 214,
                        215, 217, 218, 220, 221, 222, 223, 224, 225, 226, 226, 227, 228,
                        229, 231, 232, 233, 234, 235, 236, 237, 238, 239, 239, 239, 239,
                        241, 242, 243, 243, 243, 244, 245, 247, 247, 247, 247, 247, 247,
                        248, 249, 250, 251, 251, 251, 252, 252, 252, 252, 252, 252, 252,
                        252, 252, 252, 252, 252, 252, 253, 253, 0]

        lut[:, 0, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 4, 4,
                        4, 4, 4, 4, 3, 3, 3, 3, 4, 6, 6, 6, 6,
                        6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                        6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 7, 9, 10,
                        10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
                        10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
                        9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8,
                        8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 7, 7,
                        7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6,
                        6, 6, 6, 6, 7, 10, 12, 12, 12, 12, 12, 12, 13,
                        15, 17, 18, 18, 19, 20, 22, 23, 23, 24, 26, 27, 27,
                        28, 30, 32, 33, 34, 35, 37, 39, 40, 41, 43, 45, 46,
                        48, 50, 52, 54, 55, 57, 58, 61, 63, 65, 67, 70, 72,
                        73, 76, 79, 80, 83, 86, 88, 89, 92, 95, 96, 99, 102,
                        104, 107, 108, 110, 113, 116, 120, 121, 123, 125, 127, 129, 132,
                        135, 137, 140, 143, 146, 149, 150, 153, 155, 158, 160, 162, 165,
                        168, 171, 173, 175, 178, 180, 183, 186, 188, 191, 192, 195, 198,
                        201, 203, 206, 209, 210, 213, 215, 218, 221, 223, 225, 228, 231,
                        233, 236, 238, 241, 244, 246, 250, 252, 255]

        # Modified Glow LUT which make the first four smallest value as green
        # lut[:, 0, 2] = [0, 0, 0, 0, 2, 3, 4, 6, 8, 11, 13, 15, 18,
        #                 21, 23, 24, 27, 30, 31, 33, 36, 37, 40, 42, 45, 46,
        #                 49, 51, 53, 56, 58, 60, 62, 65, 68, 70, 72, 74, 78,
        #                 80, 82, 84, 86, 89, 91, 93, 96, 98, 100, 102, 104, 106,
        #                 108, 110, 113, 115, 117, 119, 122, 125, 127, 129, 132, 135, 135,
        #                 137, 140, 141, 142, 145, 148, 149, 152, 154, 156, 157, 158, 160,
        #                 162, 164, 166, 168, 170, 171, 173, 174, 176, 178, 179, 180, 182,
        #                 183, 185, 186, 189, 192, 193, 193, 194, 195, 195, 196, 198, 199,
        #                 201, 203, 204, 204, 205, 206, 207, 209, 211, 211, 211, 211, 213,
        #                 215, 216, 216, 216, 216, 218, 219, 219, 219, 220, 222, 223, 223,
        #                 223, 223, 224, 224, 226, 227, 227, 227, 227, 228, 229, 231, 231,
        #                 231, 231, 231, 231, 231, 232, 233, 234, 234, 234, 234, 234, 234,
        #                 235, 237, 238, 238, 238, 238, 238, 238, 238, 238, 239, 240, 242,
        #                 242, 242, 242, 242, 242, 242, 242, 242, 243, 245, 246, 246, 246,
        #                 246, 245, 245, 245, 245, 245, 245, 245, 247, 248, 249, 249, 249,
        #                 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249, 249,
        #                 249, 250, 252, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
        #                 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
        #                 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253,
        #                 253, 253, 253, 253, 253, 253, 253, 253, 0]
        #
        # lut[:, 0, 1] = [138, 138, 138, 138, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #                 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2,
        #                 2, 2, 2, 2, 3, 3, 3, 3, 4, 5, 5, 5, 5,
        #                 6, 6, 6, 7, 7, 8, 9, 9, 9, 9, 10, 10, 11,
        #                 12, 13, 14, 14, 14, 14, 15, 16, 16, 17, 18, 19, 19,
        #                 19, 20, 21, 22, 23, 24, 24, 25, 27, 28, 28, 28, 29,
        #                 31, 32, 32, 33, 35, 36, 36, 37, 39, 40, 40, 41, 42,
        #                 43, 45, 46, 47, 48, 50, 51, 52, 54, 55, 56, 57, 59,
        #                 62, 63, 65, 66, 68, 70, 71, 73, 74, 75, 77, 79, 81,
        #                 83, 85, 87, 89, 92, 93, 96, 98, 99, 100, 103, 105, 107,
        #                 109, 111, 113, 116, 117, 119, 121, 123, 125, 126, 128, 130, 132,
        #                 135, 137, 139, 140, 142, 144, 145, 147, 148, 150, 152, 154, 156,
        #                 158, 160, 161, 162, 164, 166, 168, 171, 172, 172, 174, 176, 177,
        #                 179, 180, 182, 183, 185, 187, 188, 189, 191, 192, 192, 192, 196,
        #                 200, 201, 201, 202, 203, 204, 206, 208, 210, 212, 213, 213, 214,
        #                 215, 217, 218, 220, 221, 222, 223, 224, 225, 226, 226, 227, 228,
        #                 229, 231, 232, 233, 234, 235, 236, 237, 238, 239, 239, 239, 239,
        #                 241, 242, 243, 243, 243, 244, 245, 247, 247, 247, 247, 247, 247,
        #                 248, 249, 250, 251, 251, 251, 252, 252, 252, 252, 252, 252, 252,
        #                 252, 252, 252, 252, 252, 252, 253, 253, 0]
        #
        # lut[:, 0, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 4, 4,
        #                 4, 4, 4, 4, 3, 3, 3, 3, 4, 6, 6, 6, 6,
        #                 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
        #                 6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 7, 9, 10,
        #                 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        #                 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
        #                 9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8,
        #                 8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 7, 7,
        #                 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6,
        #                 6, 6, 6, 6, 7, 10, 12, 12, 12, 12, 12, 12, 13,
        #                 15, 17, 18, 18, 19, 20, 22, 23, 23, 24, 26, 27, 27,
        #                 28, 30, 32, 33, 34, 35, 37, 39, 40, 41, 43, 45, 46,
        #                 48, 50, 52, 54, 55, 57, 58, 61, 63, 65, 67, 70, 72,
        #                 73, 76, 79, 80, 83, 86, 88, 89, 92, 95, 96, 99, 102,
        #                 104, 107, 108, 110, 113, 116, 120, 121, 123, 125, 127, 129, 132,
        #                 135, 137, 140, 143, 146, 149, 150, 153, 155, 158, 160, 162, 165,
        #                 168, 171, 173, 175, 178, 180, 183, 186, 188, 191, 192, 195, 198,
        #                 201, 203, 206, 209, 210, 213, 215, 218, 221, 223, 225, 228, 231,
        #                 233, 236, 238, 241, 244, 246, 250, 252, 255]

        # Apply color map using cv2.applyColorMap()
        im_color = cv2.applyColorMap(im_gray, lut)
        return im_color

    def modredhot(self, im_gray):
        """

            Apply modified(use glow LUT first and last value to replace the original rh) red-hot LUT to the gray image
            channel 2- red; channel 1-green; channel 0 - blue
        :param im_gray:
        :return:
        """

        # Create the LUT:
        lut = np.zeros((256, 1, 3), dtype=np.uint8)
        lut[:, 0, 2] = [0, 0, 0, 0, 1, 1, 1, 1, 1, 4, 7, 10, 13,
                        16, 20, 23, 27, 30, 33, 36, 39, 42, 45, 48, 52, 55,
                        58, 61, 65, 68, 71, 74, 78, 81, 84, 87, 90, 93, 96,
                        99, 103, 106, 110, 113, 117, 120, 123, 126, 130, 133, 136, 139,
                        142, 145, 148, 151, 155, 158, 161, 164, 168, 171, 174, 177, 181,
                        184, 187, 190, 193, 196, 200, 203, 207, 210, 213, 216, 220, 223,
                        226, 229, 233, 236, 239, 242, 245, 247, 250, 252, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 0
                        ]

        lut[:, 0, 1] = [138, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 6, 9,
                        12, 16, 19, 22, 25, 29, 32, 35, 38, 42, 45, 48, 51,
                        55, 58, 61, 64, 68, 71, 74, 77, 81, 84, 87, 90, 94,
                        97, 100, 103, 106, 109, 112, 115, 119, 122, 126, 129, 133, 136,
                        139, 142, 145, 148, 151, 154, 158, 161, 164, 167, 171, 174, 177,
                        180, 184, 187, 190, 193, 197, 200, 203, 206, 209, 212, 216, 219,
                        223, 226, 229, 232, 236, 239, 242, 245, 249, 250, 252, 253, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 0]

        lut[:, 0, 0] = [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 4, 6,
                        9, 12, 15, 19, 22, 25, 28, 32, 35, 38, 41, 45, 48,
                        51, 54, 58, 61, 64, 67, 71, 74, 77, 80, 84, 87, 90,
                        93, 97, 100, 103, 106, 110, 113, 116, 119, 122, 125, 128, 131,
                        135, 138, 142, 145, 149, 152, 155, 158, 161, 164, 167, 170, 174,
                        177, 180, 183, 187, 190, 193, 196, 200, 203, 206, 209, 213, 216,
                        219, 222, 225, 228, 232, 235, 239, 242, 245, 248, 252, 252, 253,
                        254, 255, 255, 255, 255, 255, 255, 255, 255]

        # Apply color map using cv2.applyColorMap()
        im_color = cv2.applyColorMap(im_gray, lut)
        return im_color

    def mapincheck(self, mapin, workdirin):

        import inspect
        from mrcfile.mrcfile import MrcFile

        frame = inspect.currentframe()
        func = inspect.getframeinfo(frame.f_back).function
        if mapin is not None:
            if (type(mapin) is str):
                if (os.path.isfile(mapin)):
                    # map = MapParser.readMRC(mapin)
                    map = mrcfile.mmap(mapin, mode='r')
                else:
                    print('Map does not exist.')
                    map = None
            # elif(isinstance(mapin, Map)):
            elif (isinstance(mapin, MrcFile)):
                map = mapin
            else:
                map = None
                print('Function:{} only accept a string of full map name or a TEMPy Map object as input.'.format(func))
        else:
            map = self.map

        if workdirin is not None:
            if (type(workdirin) is str):
                if (os.path.isdir(workdirin)):
                    workdir = workdirin
                else:
                    print('Output directory does not exist.')
                    workdir = None
            else:
                workdir = None
                print('Function:{} only accept a string as the directory parameter.'.format(func))
        else:
            workdir = self.workdir

        return map, workdir

    # @profile
    def resize_img(self, input_arr, output_img):
        """
            rescale image to 300X300, if the input is not square, scale the longer one to 300 and the other one
            accordingly

        :param input_arr: numpy array
        :param output_img: the name with full path of the output image
        :return: None
        """

        height, width = input_arr.shape[0:2]
        if width >= height:
            largerscaler = 300. / width
            newheight = int(ceil(largerscaler * height))
            resized_img = cv2.resize(input_arr, (300, newheight), interpolation=cv2.INTER_LANCZOS4)
        else:
            largerscaler = 300. / height
            newwidth = int(ceil(largerscaler * width))
            resized_img = cv2.resize(input_arr, (newwidth, 300), interpolation=cv2.INTER_LANCZOS4)

        cv2.imwrite(output_img, resized_img)

        return None

    def scale_img(self, projection):
        """
            Give the projection as a 2D numpy array return the scaled projection
        :param projection:
        :return:
        """

        onevalue = True if projection.min() == projection.max() else False
        if onevalue:
            rescaled = np.full((projection.shape), 0.0).astype('uint8')
        else:
            rescaled = (((projection - projection.min()) * 255.0) / (projection.max() - projection.min())).astype(
                'uint8')

        return rescaled

    def get_projection(self, map, type, axis):
        """
            Give map and type, function produce different projection
        :param map: mrcfile map objcet
        :param type: string of normal, max, min, std, median, central, largevar
        :param axis: 2->x, 0->z, 1->y
        :return: numpy array or None for projection
        """

        mapdata = map.data
        if type == 'projection':
            projection = np.sum(mapdata, axis=axis)
        elif type == 'max':
            if self.met != 'tomo':
                projection = np.amax(mapdata, axis=axis)
            else:
                # tomograms use min others use max
                projection = np.amin(mapdata, axis=axis)
        elif type == 'min':
            projection = np.amin(mapdata, axis=axis)
        elif type == 'std':
            projection = np.std(mapdata, axis=axis)
        elif type == 'median':
            projection = np.median(mapdata, axis=axis)
        elif type == 'central':
            if axis == 2:
                xmid = int(float(map.header.nx) / 2)
                projection = map.data[:, :, xmid]
            elif axis == 1:
                ymid = int(float(map.header.ny) / 2)
                projection = map.data[:, ymid, :]
            elif axis == 0:
                zmid = int(float(map.header.nz) / 2)
                projection = map.data[zmid, :, :]
            else:
                projection = None
                print('Wrong axis index (0, 1, 2).')
        elif type == 'largestvariance':
            zlim, ylim, xlim = map.data.shape
            if axis == 2:
                xvar = [ndimage.variance(map.data[:, :, i]) for i in range(0, xlim)]
                xlargeind = int(np.argmax(xvar))
                projection = map.data[:, :, xlargeind]
            elif axis == 1:
                yvar = [ndimage.variance(map.data[:, i, :]) for i in range(0, ylim)]
                ylargeind = int(np.argmax(yvar))
                projection = map.data[:, ylargeind, :]
            elif axis == 0:
                zvar = [ndimage.variance(map.data[i, :, :]) for i in range(0, zlim)]
                zlargeind = int(np.argmax(zvar))
                projection = map.data[zlargeind, :, :]
            else:
                projection = None
                print('Wrong axis index (0, 1, 2).')
        else:
            print('Wrong type. Use one of: projection, max, min, std, median, central, largestvariance.')
            projection = None

        return projection

    def save_scale(self, reposition, axis_letter, mapname, type, errlist, proc_fun=None):
        """
            function save the image and it scaled image
        :param reposition: numpy array of the image
        :param axis_letter: 'x', 'y' or 'z'
        :param mapname: string of the map name
        :param type: one string of projection, max, min, std, median, central, largestvariance
        :param errlist: list contains error string
        :param proc_fun: a image processing function which applied to projection e.g., self.glowimage(),
                        cv2.applyColorMap(xflipped, cv2.COLORMAP_HOT)(rh), self.modredhot(yrotate)(modrh)
        :return: None
        """

        # type_dict = {'projection': 'orthogonal projection', 'max': 'orthogonal maximum-value projection',
        #              'min': 'orthogonal minimim-value projection', 'std': 'orthogonal standard-deviation projection',
        #              'median': 'orthogonal median-value projection', 'central': 'central slices',
        #              'largestvariance': 'largest variance slices'}

        if proc_fun == self.glowimage:
            proj_img_name = '{}{}_glow_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type)
            scaled_proj_img_name = '{}{}_scaled_glow_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type)
        elif type == 'central' or type == 'largestvariance':
            proj_img_name = '{}{}_{}{}_slice.jpeg'.format(self.workdir, mapname, axis_letter, type)
            scaled_proj_img_name = '{}{}_scaled_{}{}_slice.jpeg'.format(self.workdir, mapname, axis_letter, type)
        else:
            proj_img_name = '{}{}_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type)
            scaled_proj_img_name = '{}{}_scaled_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type)


        try:
            cv2.imwrite(proj_img_name, reposition)
        except IOError as ioerr:
            if proc_fun == self.glowimage:
                err = 'Saving {}{} glow projection err:{}'.format(axis_letter, type, ioerr)
            else:
                err = 'Saving original {}{} err:{}'.format(axis_letter, type, ioerr)
            errlist.append(err)
            sys.stderr.write(err + '\n')

        try:
            self.resize_img(reposition, scaled_proj_img_name)
        except:
            if proc_fun == self.glowimage:
                err = 'Saving scaled glow image {}{} err:{}'.format(axis_letter, type, sys.exc_info()[1])
            else:
                err = 'Saving scaled {} {} err:{}'.format(axis_letter, type, sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        return None

    def map_to_img(self, map, axis, type, errlist, proc_fun=None):
        """
            Give the mapdata, output file name, dimension and errlist it produce the correspodning projection
        :param map: mrcfile object
        :param axis: 2->x, 0->z, 1->y
        :param output_name: string of output file name
        :param errlist: list for error string
        :param proc_fun: a image processing function which applied to projection e.g., self.glowimage(),
                        cv2.applyColorMap(xflipped, cv2.COLORMAP_HOT)(rh), self.modredhot(yrotate)(modrh)
        :return: None
        """

        # type_dict = {'projection': 'orthogonal projection', 'max': 'orthogonal maximum-value projection',
        #              'min': 'orthogonal minimim-value projection', 'std': 'orthogonal standard-deviation projection',
        #              'median': 'orthogonal median-value projection', 'centralslice': 'central slices',
        #              'largestvariance': 'largest variance slices'}

        projection = self.get_projection(map, type, axis)
        rescaled = self.scale_img(projection)
        if axis == 2:
            reposition = np.flipud(rescaled)
            axis_letter = 'x'
        elif axis == 1:
            reposition = np.rot90(rescaled)
            axis_letter = 'y'
        elif axis == 0:
            reposition = np.flipud(rescaled)
            axis_letter = 'z'
        else:
            reposition = None
            axis_letter = None
            print('axis should be 0, 1, 2 repesent z, y, x.')

        if reposition is not None and axis_letter is not None:
            mapname = os.path.basename(map.fullname)
            self.save_scale(reposition, axis_letter, mapname, type, errlist)
            if proc_fun:
                # glowimage = self.glowimage(reposition)
                glowimage = proc_fun(reposition)
                self.save_scale(glowimage, axis_letter, mapname, type, errlist, proc_fun)

            # try:
            #     proj_img_name = '{}{}_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type_dict[type])
            #     cv2.imwrite(proj_img_name, reposition)
            # except IOError as ioerr:
            #     err = 'Saving original {} {} err:{}'.format(axis_letter, type_dict[type], ioerr)
            #     errlist.append(err)
            #     sys.stderr.write(err + '\n')
            #
            # try:
            #     scaled_proj_img_name = '{}{}_scaled_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type_dict[type])
            #     self.resize_img(reposition, scaled_proj_img_name)
            # except:
            #     err = 'Saving scaled {} {} err:{}'.format(axis_letter, type_dict[type], sys.exc_info()[1])
            #     errlist.append(err)
            #     sys.stderr.write(err + '\n')
            #
            # if glow:
            #     glowimage = self.glowimage(reposition)
            #     try:
            #         glowname = '{}{}_glow_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type)
            #         cv2.imwrite(glowname, glowimage)
            #     except IOError as ioerr:
            #         xerr = 'Saving {}{} glow projection err:{}'.format(axis, type, ioerr)
            #         errlist.append(xerr)
            #         sys.stderr.write(xerr + '\n')
            #     try:
            #         scaled_glowname = '{}{}_scaled_glow_{}{}.jpeg'.format(self.workdir, mapname, axis_letter, type)
            #         self.resize_img(glowimage, scaled_glowname)
            #     except:
            #         err = 'Saving scaled glow image {} {} err:{}'.format(axis_letter, type_dict[type], sys.exc_info()[1])
            #         errlist.append(err)
            #         sys.stderr.write(err + '\n')

        return None

    # @profile
    def orthogonal_projections(self, mapin=None, workdir=None, label=''):
        """
             Std projection and it glow image
        :param mapin: Input map either mrcfile or filename string
        :param workdir: String of the full work path
        :param label: for raw map use 'raw_'
        :return: None
        """

        map, workdir = self.mapincheck(mapin, workdir)
        mapname = os.path.basename(map.fullname) if map else None
        if map is not None and workdir is not None:
            start = timeit.default_timer()
            errlist = []
            type = 'projection'

            xprojectionname = workdir + mapname + '_xprojection.jpeg'
            xscalename = workdir + mapname + '_scaled_xprojection.jpeg'
            self.map_to_img(map, 2, type, errlist)

            yprojectionname = workdir + mapname + '_yprojection.jpeg'
            yscalename = workdir + mapname + '_scaled_yprojection.jpeg'
            self.map_to_img(map, 1, type, errlist)

            zprojectionname = workdir + mapname + '_zprojection.jpeg'
            zscalename = workdir + mapname + '_scaled_zprojection.jpeg'
            self.map_to_img(map, 0, type, errlist)

            bothjson = dict()
            projectionjson = dict()
            orgprojectionjson = dict()

            projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
            projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
            projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

            orgprojectionjson['x'] = os.path.basename(xprojectionname) if os.path.isfile(xprojectionname) else None
            orgprojectionjson['y'] = os.path.basename(yprojectionname) if os.path.isfile(yprojectionname) else None
            orgprojectionjson['z'] = os.path.basename(zprojectionname) if os.path.isfile(zprojectionname) else None
            bothjson['original'] = orgprojectionjson
            bothjson['scaled'] = projectionjson

            if errlist:
                bothjson['err'] = {'orthogonal_projection_err': errlist}
            finaldict = {label + 'orthogonal_projection': bothjson}

            try:
                with codecs.open(workdir + mapname + '_projection.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except IOError as ioerr:
                jsonerr = 'Saving projection into json error: {}'.format(ioerr)
                sys.stderr.write(jsonerr + '\n')

            end = timeit.default_timer()
            print('Projections time for %s: %s' % (mapname, end - start))
            print('------------------------------------')

        else:
            print('No orthogonal projections without proper map input and the output directory information.')

        return None

    # @profile
    def rawmap_projections(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            self.orthogonal_projections(rawmap, dir, label)
        else:
            print('No raw map to calculate orthogonal projections.')

        return None

    # @profile
    def orthogonal_median(self, mapin=None, workdir=None, label=''):
        """
            Median projection
        :param mapin: Input map either mrcfile or filename string
        :param workdir: String of the full work path
        :param label: for raw map use 'raw_'
        :return: None
        """

        if self.platform == 'emdb':
            map, workdir = self.mapincheck(mapin, workdir)
            mapname = os.path.basename(map.fullname) if map else None
            if map is not None and workdir is not None:
                start = timeit.default_timer()
                errlist = []
                type = 'median'

                xprojectionname = workdir + mapname + '_xmedian.jpeg'
                xscalename = workdir + mapname + '_scaled_xmedian.jpeg'
                self.map_to_img(map, 2, type, errlist)

                yprojectionname = workdir + mapname + '_ymedian.jpeg'
                yscalename = workdir + mapname + '_scaled_ymedian.jpeg'
                self.map_to_img(map, 1, type, errlist)

                zprojectionname = workdir + mapname + '_zmedian.jpeg'
                zscalename = workdir + mapname + '_scaled_zmedian.jpeg'
                self.map_to_img(map, 0, type, errlist)

                bothjson = dict()
                projectionjson = dict()
                orgprojectionjson = dict()

                projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
                projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
                projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

                orgprojectionjson['x'] = os.path.basename(xprojectionname) if os.path.isfile(xprojectionname) else None
                orgprojectionjson['y'] = os.path.basename(yprojectionname) if os.path.isfile(yprojectionname) else None
                orgprojectionjson['z'] = os.path.basename(zprojectionname) if os.path.isfile(zprojectionname) else None

                bothjson['original'] = orgprojectionjson
                bothjson['scaled'] = projectionjson

                if errlist:
                    bothjson['err'] = {'orthogonal_median_err': errlist}
                finaldict = {label + 'orthogonal_median': bothjson}

                try:
                    with codecs.open(workdir + mapname + '_median.json', 'w', encoding='utf-8') as f:
                        json.dump(finaldict, f)
                except IOError as ioerr:
                    jsonerr = 'Saving median projection into json error: {}'.format(ioerr)
                    sys.stderr.write(jsonerr + '\n')

                end = timeit.default_timer()
                print('Median projections time for %s: %s' % (mapname, end - start))
                print('------------------------------------')

                return None
            else:
                print(
                    'No orthogonal median projections without proper map input and the output directory information.')

        return None

    # @profile
    def rawmap_median(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            self.orthogonal_median(rawmap, dir, label)
        else:
            print('No raw map to calculate orthogonal max projections.')


    # @profile
    def orthogonal_min(self, mapin=None, workdir=None, label=''):
        """
             Minimal projection
        :param mapin: Input map either mrcfile or filename string
        :param workdir: String of the full work path
        :param label: for raw map use 'raw_'
        :return: None
        """

        if self.platform == 'emdb':
            map, workdir = self.mapincheck(mapin, workdir)
            mapname = os.path.basename(map.fullname) if map else None
            if map is not None and workdir is not None:
                start = timeit.default_timer()
                errlist = []
                type = 'min'

                xprojectionname = workdir + mapname + '_xmin.jpeg'
                xscalename = workdir + mapname + '_scaled_xmin.jpeg'
                self.map_to_img(map, 2, type, errlist)

                yprojectionname = workdir + mapname + '_ymin.jpeg'
                yscalename = workdir + mapname + '_scaled_ymin.jpeg'
                self.map_to_img(map, 1, type, errlist)

                zprojectionname = workdir + mapname + '_zmin.jpeg'
                zscalename = workdir + mapname + '_scaled_zmin.jpeg'
                self.map_to_img(map, 0, type, errlist)

                bothjson = dict()
                projectionjson = dict()
                orgprojectionjson = dict()

                projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
                projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
                projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

                orgprojectionjson['x'] = os.path.basename(xprojectionname) if os.path.isfile(xprojectionname) else None
                orgprojectionjson['y'] = os.path.basename(yprojectionname) if os.path.isfile(yprojectionname) else None
                orgprojectionjson['z'] = os.path.basename(zprojectionname) if os.path.isfile(zprojectionname) else None

                bothjson['original'] = orgprojectionjson
                bothjson['scaled'] = projectionjson

                if errlist:
                    bothjson['err'] = {'orthogonal_min_err': errlist}
                finaldict = {label + 'orthogonal_min': bothjson}

                try:
                    with codecs.open(workdir + mapname + '_min.json', 'w', encoding='utf-8') as f:
                        json.dump(finaldict, f)
                except IOError as ioerr:
                    jsonerr = 'Saving minimal projection into json error: {}'.format(ioerr)
                    sys.stderr.write(jsonerr + '\n')

                end = timeit.default_timer()
                print('Minimal projections time for %s: %s' % (mapname, end - start))
                print('------------------------------------')

            else:
                print(
                    'No orthogonal minimal projections without proper map input and the output directory information.')

        return None

    # @profile
    def rawmap_min(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            self.orthogonal_min(rawmap, dir, label)
        else:
            print('No raw map to calculate orthogonal min projections.')

    # @profile
    def orthogonal_max(self, mapin=None, workdir=None, label=''):
        """
             Maximal projection and it glow image
        :param mapin: Input map either mrcfile or filename string
        :param workdir: String of the full work path
        :param label: for raw map use 'raw_'
        :return: None
        """

        if self.platform == 'emdb':
            map, workdir = self.mapincheck(mapin, workdir)
            mapname = os.path.basename(map.fullname) if map else None
            if map is not None and workdir is not None:
                start = timeit.default_timer()
                errlist = []
                type = 'max'

                xprojectionname = workdir + mapname + '_xmax.jpeg'
                xscalename = workdir + mapname + '_scaled_xmax.jpeg'
                glowxprojectionname = workdir + mapname + '_glow_xmax.jpeg'
                glowxscalename = workdir + mapname + '_scaled_glow_xmax.jpeg'
                self.map_to_img(map, 2, type, errlist, self.glowimage)

                yprojectionname = workdir + mapname + '_ymax.jpeg'
                yscalename = workdir + mapname + '_scaled_ymax.jpeg'
                glowyprojectionname = workdir + mapname + '_glow_ymax.jpeg'
                glowyscalename = workdir + mapname + '_scaled_glow_ymax.jpeg'
                self.map_to_img(map, 1, type, errlist, self.glowimage)

                zprojectionname = workdir + mapname + '_zmax.jpeg'
                zscalename = workdir + mapname + '_scaled_zmax.jpeg'
                glowzprojectionname = workdir + mapname + '_glow_zmax.jpeg'
                glowzscalename = workdir + mapname + '_scaled_glow_zmax.jpeg'
                self.map_to_img(map, 0, type, errlist, self.glowimage)

                bothjson = dict()
                projectionjson = dict()
                orgprojectionjson = dict()

                projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
                projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
                projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

                orgprojectionjson['x'] = os.path.basename(xprojectionname) if os.path.isfile(xprojectionname) else None
                orgprojectionjson['y'] = os.path.basename(yprojectionname) if os.path.isfile(yprojectionname) else None
                orgprojectionjson['z'] = os.path.basename(zprojectionname) if os.path.isfile(zprojectionname) else None
                bothjson['original'] = orgprojectionjson
                bothjson['scaled'] = projectionjson

                if errlist:
                    bothjson['err'] = {'orthogonal_max_err': errlist}
                finaldict = {label + 'orthogonal_max': bothjson}

                try:
                    with codecs.open(workdir + mapname + '_max.json', 'w',
                                     encoding='utf-8') as f:
                        json.dump(finaldict, f)
                except IOError as ioerr:
                    jsonerr = 'Saving max projection into json error: {}'.format(ioerr)
                    sys.stderr.write(jsonerr + '\n')


                glowbothjson = dict()
                glowprojectionjson = dict()
                gloworgprojectionjson = dict()

                glowprojectionjson['x'] = os.path.basename(glowxscalename) if os.path.isfile(glowxscalename) else None
                glowprojectionjson['y'] = os.path.basename(glowyscalename) if os.path.isfile(glowyscalename) else None
                glowprojectionjson['z'] = os.path.basename(glowzscalename) if os.path.isfile(glowzscalename) else None

                gloworgprojectionjson['x'] = os.path.basename(glowxprojectionname) if os.path.isfile(glowxprojectionname) else None
                gloworgprojectionjson['y'] = os.path.basename(glowyprojectionname) if os.path.isfile(glowyprojectionname) else None
                gloworgprojectionjson['z'] = os.path.basename(glowzprojectionname) if os.path.isfile(glowzprojectionname) else None
                glowbothjson['original'] = gloworgprojectionjson
                glowbothjson['scaled'] = glowprojectionjson

                if errlist:
                    glowbothjson['err'] = {'orthogonal_glow_max_err': errlist}
                glowfinaldict = {label + 'orthogonal_max': glowbothjson}

                try:
                    with codecs.open(workdir + mapname + '_glow_max.json', 'w',
                                     encoding='utf-8') as f:
                        json.dump(glowfinaldict, f)
                except IOError as ioerr:
                    jsonerr = 'Saving glow max projection into json error: {}'.format(ioerr)
                    sys.stderr.write(jsonerr + '\n')

                end = timeit.default_timer()
                print('Max and its glow projections time for %s: %s' % (mapname, end - start))
                print('------------------------------------')

            else:
                print('No orthogonal maximum projections and it glow projections '
                      'without proper map input and the output directory information.')

        return None

    # @profile
    def rawmap_max(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            self.orthogonal_max(rawmap, dir, label)
        else:
            print('No raw map to calculate orthogonal max projections.')

    # @profile
    def orthogonal_std(self, mapin=None, workdir=None, label=''):
        """
             Std projection and it glow image
        :param mapin: Input map either mrcfile or filename string
        :param workdir: String of the full work path
        :param label: for raw map use 'raw_'
        :return: None
        """

        if self.platform == 'emdb':
            map, workdir = self.mapincheck(mapin, workdir)
            mapname = os.path.basename(map.fullname) if map else None
            if map is not None and workdir is not None:
                start = timeit.default_timer()
                errlist = []

                type = 'std'

                xprojectionname = workdir + mapname + '_xstd.jpeg'
                xscalename = workdir + mapname + '_scaled_xstd.jpeg'
                glowxprojectionname = workdir + mapname + '_glow_xstd.jpeg'
                glowxscalename = workdir + mapname + '_scaled_glow_xstd.jpeg'
                self.map_to_img(map, 2, type, errlist, self.glowimage)

                yprojectionname = workdir + mapname + '_ystd.jpeg'
                yscalename = workdir + mapname + '_scaled_ystd.jpeg'
                glowyprojectionname = workdir + mapname + '_glow_ystd.jpeg'
                glowyscalename = workdir + mapname + '_scaled_glow_ystd.jpeg'
                self.map_to_img(map, 1, type, errlist, self.glowimage)

                zprojectionname = workdir + mapname + '_zstd.jpeg'
                zscalename = workdir + mapname + '_scaled_zstd.jpeg'
                glowzprojectionname = workdir + mapname + '_glow_zstd.jpeg'
                glowzscalename = workdir + mapname + '_scaled_glow_zstd.jpeg'
                self.map_to_img(map, 0, type, errlist, self.glowimage)

                bothjson = dict()
                projectionjson = dict()
                orgprojectionjson = dict()

                projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
                projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
                projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

                orgprojectionjson['x'] = os.path.basename(xprojectionname) if os.path.isfile(xprojectionname) else None
                orgprojectionjson['y'] = os.path.basename(yprojectionname) if os.path.isfile(yprojectionname) else None
                orgprojectionjson['z'] = os.path.basename(zprojectionname) if os.path.isfile(zprojectionname) else None
                bothjson['original'] = orgprojectionjson
                bothjson['scaled'] = projectionjson

                if errlist:
                    bothjson['err'] = {'orthogonal_std_err': errlist}
                finaldict = {label + 'orthogonal_std': bothjson}

                try:
                    with codecs.open(workdir + mapname + '_std.json', 'w',
                                     encoding='utf-8') as f:
                        json.dump(finaldict, f)
                except IOError as ioerr:
                    jsonerr = 'Saving std projection into json error: {}'.format(ioerr)
                    sys.stderr.write(jsonerr + '\n')

                glowbothjson = dict()
                glowprojectionjson = dict()
                gloworgprojectionjson = dict()

                glowprojectionjson['x'] = os.path.basename(glowxscalename) if os.path.isfile(glowxscalename) else None
                glowprojectionjson['y'] = os.path.basename(glowyscalename) if os.path.isfile(glowyscalename) else None
                glowprojectionjson['z'] = os.path.basename(glowzscalename) if os.path.isfile(glowzscalename) else None

                gloworgprojectionjson['x'] = os.path.basename(glowxprojectionname) if os.path.isfile(glowxprojectionname) else None
                gloworgprojectionjson['y'] = os.path.basename(glowyprojectionname) if os.path.isfile(glowyprojectionname) else None
                gloworgprojectionjson['z'] = os.path.basename(glowzprojectionname) if os.path.isfile(glowzprojectionname) else None

                glowbothjson['original'] = gloworgprojectionjson
                glowbothjson['scaled'] = glowprojectionjson

                if errlist:
                    glowbothjson['err'] = {'orthogonal_glow_std_err': errlist}
                glowfinaldict = {label + 'orthogonal_glow_std': glowbothjson}

                try:
                    with codecs.open(workdir + mapname + '_glow_std.json', 'w',
                                     encoding='utf-8') as f:
                        json.dump(glowfinaldict, f)
                except IOError as ioerr:
                    jsonerr = 'Saving glow std projection into json error: {}'.format(ioerr)
                    sys.stderr.write(jsonerr + '\n')

                end = timeit.default_timer()
                print('Glow and std projections time for %s: %s' % (mapname, end - start))
                print('------------------------------------')

            else:
                print('No glow and std projections without proper map input and the output directory information.')

        return None

        # Central slices

    # @profile
    def rawmap_std(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            self.orthogonal_std(rawmap, dir, label)
        else:
            print('No raw map to calculate orthogonal std projections.')

    # @profile
    def central_slice(self, mapin=None, workdir=None, label=''):
        """
             Std projection and it glow image
        :param mapin: Input map either mrcfile or filename string
        :param workdir: String of the full work path
        :param label: for raw map use 'raw_'
        :return: None
        """

        map, workdir = self.mapincheck(mapin, workdir)
        mapname = os.path.basename(map.fullname) if map else None
        if map is not None and workdir is not None:
            start = timeit.default_timer()
            errlist = []

            xprojectionname = workdir + mapname + '_xcentral_slice.jpeg'
            xscalename = workdir + mapname + '_scaled_xcentral_slice.jpeg'
            type = 'central'
            self.map_to_img(map, 2, type, errlist)

            yprojectionname = workdir + mapname + '_ycentral_slice.jpeg'
            yscalename = workdir + mapname + '_scaled_ycentral_slice.jpeg'
            self.map_to_img(map, 1, type, errlist)

            zprojectionname = workdir + mapname + '_zcentral_slice.jpeg'
            zscalename = workdir + mapname + '_scaled_zcentral_slice.jpeg'
            self.map_to_img(map, 0, type, errlist)

            xmid = int(float(map.header.nx) / 2)
            ymid = int(float(map.header.ny) / 2)
            zmid = int(float(map.header.nz) / 2)
            indices = {'x': xmid, 'y': ymid, 'z': zmid}

            bothjson = dict()
            projectionjson = dict()
            orgprojectionjson = dict()

            projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
            projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
            projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

            orgprojectionjson['x'] = os.path.basename(xprojectionname) if os.path.isfile(xprojectionname) else None
            orgprojectionjson['y'] = os.path.basename(yprojectionname) if os.path.isfile(yprojectionname) else None
            orgprojectionjson['z'] = os.path.basename(zprojectionname) if os.path.isfile(zprojectionname) else None

            bothjson['original'] = orgprojectionjson
            bothjson['scaled'] = projectionjson
            bothjson['indices'] = indices

            if errlist:
                bothjson['err'] = {'central_slice_err': errlist}
            finaldict = {label + 'central_slice': bothjson}

            try:
                with codecs.open(workdir + mapname + '_centralslice.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except IOError as ioerr:
                jsonerr = 'Saving central slice into json error: {}'.format(ioerr)
                sys.stderr.write(jsonerr + '\n')

            end = timeit.default_timer()
            print('Central slice time for %s: %s' % (mapname, end - start))
            print('------------------------------------')

        else:
            print(
                'No central slice without proper map input and the output directory information.')

        return None

    def rawmap_central_slice(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            self.central_slice(rawmap, dir, label)
        else:
            print('No raw map to calculate central slice.')

    # @profile
    def rawmap_largest_variance(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = "rawmap_"
            self.largest_variance(rawmap, dir, label)
        else:
            print('No raw map to calculate largest variance.')

        return None

    # @profile
    def largest_variance(self, mapin=None, workdir=None, label=''):
        """
             Largest variance
        :param mapin: Input map either mrcfile or filename string
        :param workdir: String of the full work path
        :param label: for raw map use 'raw_'
        :return: None
        """

        map, workdir = self.mapincheck(mapin, workdir)
        mapname = os.path.basename(map.fullname) if map else None
        if map is not None and workdir is not None:
            # map = self.map
            # zlim, ylim, xlim = map.box_size()
            zlim, ylim, xlim = map.data.shape
            start = timeit.default_timer()
            errlist = []
            type = 'largestvariance'

            xprojectionname = workdir + mapname + '_xlargestvariance_slice.jpeg'
            xscalename = workdir + mapname + '_scaled_xlargestvariance_slice.jpeg'
            self.map_to_img(map, 2, type, errlist)

            yprojectionname = workdir + mapname + '_ylargestvariance_slice.jpeg'
            yscalename = workdir + mapname + '_scaled_ylargestvariance_slice.jpeg'
            self.map_to_img(map, 1, type, errlist)

            zprojectionname = workdir + mapname + '_zlargestvariance_slice.jpeg'
            zscalename = workdir + mapname + '_scaled_zlargestvariance_slice.jpeg'
            self.map_to_img(map, 0, type, errlist)

            xvar = [ndimage.variance(map.data[:, :, i]) for i in range(0, xlim)]
            yvar = [ndimage.variance(map.data[:, i, :]) for i in range(0, ylim)]
            zvar = [ndimage.variance(map.data[i, :, :]) for i in range(0, zlim)]
            xlargeind = int(np.argmax(xvar))
            ylargeind = int(np.argmax(yvar))
            zlargeind = int(np.argmax(zvar))

            bothjson = dict()
            projectionjson = dict()
            orgprojectionjson = dict()

            projectionjson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
            projectionjson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
            projectionjson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

            orgprojectionjson['x'] = os.path.basename(xprojectionname) if os.path.isfile(xprojectionname) else None
            orgprojectionjson['y'] = os.path.basename(yprojectionname) if os.path.isfile(yprojectionname) else None
            orgprojectionjson['z'] = os.path.basename(zprojectionname) if os.path.isfile(zprojectionname) else None

            bothjson['original'] = orgprojectionjson
            bothjson['scaled'] = projectionjson
            bothjson['indices'] = {'x': xlargeind, 'y': ylargeind, 'z': zlargeind}

            if errlist:
                bothjson['err'] = {'largest_variance_err': errlist}
            finaldict = {label + 'largest_variance_slice': bothjson}

            try:
                with codecs.open(workdir + mapname + '_largestvariance.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except IOError as ioerr:
                jsonerr = 'Saving largest variance into json error: {}'.format(ioerr)
                sys.stderr.write(jsonerr + '\n')

            end = timeit.default_timer()
            print('Largest variance time for %s: %s' % (mapname, end - start))
            print('------------------------------------')

        else:
            print(
                'No largest variance without proper map input and the output directory information.')

        return None

    # @profile
    def surfaces(self):
        """

            Prouding all the surface related images here

        :return:
        """

        vtkpack, chimeraapp = self.surface_envcheck()
        if self.models is not None:
            sufcheck = [False if model.filename.endswith('.pdb') else True for model in self.models]
        else:
            sufcheck = [True]
        # Add if model is cif using chimera for now
        if self.cl is not None and self.met != 'tomo':
            if vtkpack and False in sufcheck:
                self.surfaceview()
            elif chimeraapp:
                self.surfaceview_chimera(chimeraapp)
                self.rawmapsurface_chimera(chimeraapp)
                if self.platform == 'emdb':
                    self.modelfitsurface(chimeraapp)
                else:
                    print('No model fit surface view for wwpdb platform.')
            else:
                # print('No proper VTK or Chimera can be used for producing surface view. Please check.', file=sys.stderr)
                sys.stderr.write('No proper VTK or Chimera can be used for producing surface view. Please check.\n')
                print('------------------------------------')
        else:
            print('No contour level, no surface view.')
            print('------------------------------------')

    # Surface view VTK way
    def surfaceview(self):
        """

            Produce surface views from X, y, Z directions. When model is there,
            model and map surface views for x, y, z directions were produced.
            This is only possible when we run on the server side as it needs
            vtp files. That means it also need the emdid to produce the
            surface views.


        :return: None
        """
        start = timeit.default_timer()

        outmapximage = outmapyimage = outmapzimage = None
        if self.emdid is not None:
            vtproot = MAP_SERVER_PATH
            digits = [i for i in str(self.emdid)]
            if len(digits) == 4:
                vtpFile = '{}/{}/{}/va/emd_{}_{}.vtp'.format(vtproot, digits[0] + digits[1], self.emdid, self.emdid,
                                                             self.cl)
            elif len(digits) == 5:
                vtpFile = '{}/{}/{}/{}/va/emd_{}_{}.vtp'.format(vtproot, digits[0] + digits[1], digits[2], self.emdid,
                                                                self.emdid,
                                                                self.cl)
            else:
                pass
            if not os.path.isfile(vtpFile):
                print('VTP file of the map does not exist.')
                vtpFile = self.genvtp(self.map.filename)
                print('A vtp file correspond to density map is generated.')


            factGraphics = vtk.vtkGraphicsFactory()
            factGraphics.SetOffScreenOnlyMode(1)
            factGraphics.SetUseMesaClasses(1)
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(vtpFile)
            reader.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.ScalarVisibilityOff()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1.0, 0.8, 0.1)
            actor.GetProperty().SetInterpolationToPhong()
            actor.GetProperty().SetDiffuse(0.9)
            actor.GetProperty().SetSpecular(0.6)
            actor.GetProperty().SetSpecularPower(30)
            actor.GetProperty().BackfaceCullingOn()
            actor.GetProperty().FrontfaceCullingOn()

            # Create the graphics structure. The renderer renders into the render
            # window. The render window interactor captures mouse events and will
            # perform appropriate camera or actor manipulation depending on the
            # nature of the events.

            ren = vtk.vtkRenderer()
            renWin = vtk.vtkRenderWindow()
            renWin.SetOffScreenRendering(1)
            renWin.SetSize(3000, 3000)
            renWin.AddRenderer(ren)

            # Add the actors to the renderer, set the background and size
            # actor.RotateY(90)
            ren.AddActor(actor)
            ren.SetBackground(0.9, 0.9, 0.9)
            ren.GetActiveCamera().SetParallelProjection(1)
            renWin.Render()

            # Output maps images only
            ren.ResetCamera()
            ren.GetActiveCamera().Zoom(1.30)
            outmapzimage = '{}emd_{}_zsurface.jpeg'.format(self.workdir, self.emdid)
            self.write_image(outmapzimage, renWin)

            actor.RotateX(90)
            actor.RotateY(90)
            # ren.ResetCamera()
            outmapyimage = '{}emd_{}_ysurface.jpeg'.format(self.workdir, self.emdid)
            self.write_image(outmapyimage, renWin)

            actor.RotateZ(90)
            actor.RotateX(90)
            # ren.ResetCamera()
            outmapximage = '{}emd_{}_xsurface.jpeg'.format(self.workdir, self.emdid)
            self.write_image(outmapximage, renWin)

            # Model exist
            if self.models:
                for model in self.models:
                    pdbid = model.filename.split('/')[-1].split('.')[0]
                    # Todo: put the final decided path here as for the pdb or ent file
                    # ****: has to use .pdb or .ent for the model need to be changed to cif file
                    # pdbroot = ''
                    entroot = MAP_SERVER_PATH
                    if len(digits) == 4:
                        entFile = '{}{}/{}/va/'.format(entroot, digits[0] + digits[1], self.emdid)
                    elif len(digits) == 5:
                        entFile = '{}{}/{}/{}/va/'.format(entroot, digits[0] + digits[1], digits[2], self.emdid)
                    else:
                        pass
                    model = '{}pdb{}.ent'.format(entFile, pdbid)
                    if not os.path.isfile(model):
                        print('Model: %s is not in the working folder for model map view, please check.' % model)
                    # Change the view back
                    actor.RotateX(-90)
                    actor.RotateZ(-90)
                    actor.RotateY(-90)
                    actor.RotateX(-90)
                    ren.ResetCamera()

                    actor.GetProperty().SetOpacity(0.5)
                    pdb_reader = vtk.vtkPDBReader()
                    model_mapper = vtk.vtkPolyDataMapper()
                    model_actor = vtk.vtkActor()
                    model_actor.GetProperty().SetLineWidth(6)
                    pdb_reader.SetFileName(model)

                    # Test of backbone structure
                    # setup ribbon filter
                    ribbonFilter = vtk.vtkProteinRibbonFilter()
                    ribbonFilter.SetInputConnection(pdb_reader.GetOutputPort())
                    ribbonFilter.Update()
                    model_mapper.SetInputData(ribbonFilter.GetOutput())
                    model_mapper.Update()


                    # model_mapper.SetInputConnection(pdb_reader.GetOutputPort())
                    model_actor.SetMapper(model_mapper)
                    ren.AddActor(model_actor)
                    ren.ResetCamera()
                    ren.GetActiveCamera().Zoom(1.30)
                    renWin.Render()

                    # Output model and maps overlay images
                    outzimage = '{}{}_emd_{}_zsurface.jpeg'.format(self.workdir, pdbid, self.emdid)
                    self.write_image(outzimage, renWin)

                    actor.RotateX(90)
                    actor.RotateY(90)
                    model_actor.RotateX(90)
                    model_actor.RotateY(90)
                    # ren.ResetCamera()
                    outyimage = '{}{}_emd_{}_ysurface.jpeg'.format(self.workdir, pdbid, self.emdid)
                    self.write_image(outyimage, renWin)

                    actor.RotateZ(90)
                    actor.RotateX(90)
                    model_actor.RotateZ(90)
                    model_actor.RotateX(90)
                    # ren.ResetCamera()
                    outximage = '{}{}_emd_{}_xsurface.jpeg'.format(self.workdir, pdbid, self.emdid)
                    self.write_image(outximage, renWin)
            print('Surface views were generated by VTK method.')

            # else:
            #    # Ouput maps images only
            #    ren.ResetCamera()
            #    ren.GetActiveCamera().Zoom(0.55)
            #    outzimage = '{}{}_emd_{}_zsurface.jpeg'.format(self.workdir, pdbid, self.emdid )
            #    write_image(outzimage, renWin)

            #    actor.RotateX(90)
            #    actor.RotateY(90)
            #    #ren.ResetCamera()
            #    outyimage = '{}{}_emd_{}_ysurface.jpeg'.format(self.workdir, pdbid, self.emdid )
            #    self.write_image(outyimage, renWin)

            #    actor.RotateZ(90)
            #    actor.RotateX(90)
            #    #ren.ResetCamera()
            #    outximage = '{}{}_emd_{}_xsurface.jpeg'.format(self.workdir, pdbid, self.emdid )
            #    self.write_image(outximage, renWin)

        else:
            if self.map is not None and self.cl is not None:
                checkvtpresult = self.checkvtp()
                if checkvtpresult:
                    vtpFile = checkvtpresult
                else:
                    # First function here produce vtp file based on map with the cl
                    vtpFile = self.genvtp(self.map.filename)
                    print('A vtp file correspond to density map is generated.')

                factGraphics = vtk.vtkGraphicsFactory()
                factGraphics.SetOffScreenOnlyMode(1);
                factGraphics.SetUseMesaClasses(1)
                reader = vtk.vtkXMLPolyDataReader()
                reader.SetFileName(vtpFile)
                reader.Update()

                mapper = vtk.vtkPolyDataMapper()
                mapper.ScalarVisibilityOff()
                mapper.SetInputConnection(reader.GetOutputPort())

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(1.0, 0.8, 0.1)
                actor.GetProperty().SetInterpolationToPhong()
                actor.GetProperty().SetDiffuse(0.9)
                actor.GetProperty().SetSpecular(0.6)
                actor.GetProperty().SetSpecularPower(30)
                actor.GetProperty().BackfaceCullingOn()
                actor.GetProperty().FrontfaceCullingOn()

                # Create the graphics structure. The renderer renders into the render
                # window. The render window interactor captures mouse events and will
                # perform appropriate camera or actor manipulation depending on the
                # nature of the events.

                ren = vtk.vtkRenderer()
                renWin = vtk.vtkRenderWindow()
                renWin.SetOffScreenRendering(1)
                renWin.SetSize(3000, 3000)
                renWin.AddRenderer(ren)

                # Add the actors to the renderer, set the background and size
                # actor.RotateY(90)
                ren.AddActor(actor)
                ren.SetBackground(0.9, 0.9, 0.9)
                ren.GetActiveCamera().SetParallelProjection(1)
                renWin.Render()

                # Ouput maps images only
                ren.ResetCamera()
                ren.GetActiveCamera().Zoom(1.30)
                outmapzimage = '{}{}_zsurface.jpeg'.format(self.workdir, self.mapname)
                self.write_image(outmapzimage, renWin)

                actor.RotateX(90)
                actor.RotateY(90)
                # ren.ResetCamera()
                outmapyimage = '{}{}_ysurface.jpeg'.format(self.workdir, self.mapname)
                self.write_image(outmapyimage, renWin)

                actor.RotateZ(90)
                actor.RotateX(90)
                # ren.ResetCamera()
                outmapximage = '{}{}_xsurface.jpeg'.format(self.workdir, self.mapname)
                self.write_image(outmapximage, renWin)

                # Model exist
                if self.models:
                    # print "self.models:%s" % self.models
                    for model in self.models:
                        pdbid = model.filename.split('/')[-1].split('.')[0]
                        pdbroot = self.workdir
                        model = '{}pdb{}.ent'.format(pdbroot, pdbid)
                        # Change the view back
                        actor.RotateX(-90)
                        actor.RotateZ(-90)
                        actor.RotateY(-90)
                        actor.RotateX(-90)
                        ren.ResetCamera()

                        actor.GetProperty().SetOpacity(0.5)
                        pdb_reader = vtk.vtkPDBReader()
                        model_mapper = vtk.vtkPolyDataMapper()
                        model_actor = vtk.vtkActor()
                        model_actor.GetProperty().SetLineWidth(6)
                        pdb_reader.SetFileName(model)

                        model_mapper.SetInputConnection(pdb_reader.GetOutputPort())
                        model_actor.SetMapper(model_mapper)
                        ren.AddActor(model_actor)
                        ren.ResetCamera()
                        ren.GetActiveCamera().Zoom(1.50)
                        renWin.Render()

                        # Output model and maps overlay images
                        outzimage = '{}{}_emd_{}_zsurface.jpeg'.format(self.workdir, pdbid, self.mapname)
                        self.write_image(outzimage, renWin)

                        actor.RotateX(90)
                        actor.RotateY(90)
                        model_actor.RotateX(90)
                        model_actor.RotateY(90)
                        # ren.ResetCamera()
                        outyimage = '{}{}_emd_{}_ysurface.jpeg'.format(self.workdir, pdbid, self.mapname)
                        self.write_image(outyimage, renWin)

                        actor.RotateZ(90)
                        actor.RotateX(90)
                        model_actor.RotateZ(90)
                        model_actor.RotateX(90)
                        # ren.ResetCamera()
                        outximage = '{}{}_emd_{}_xsurface.jpeg'.format(self.workdir, pdbid, self.mapname)
                        self.write_image(outximage, renWin)
                print('Surface views were generated by VTK method')
            elif self.cl is None:
                print('Without contour level no surface view will be produced.')

        self.scale_surfaceview()

        outzimage = '{}emd_{}_zsurface.jpeg'.format(self.workdir, self.emdid)

        surfaceviewjson = dict()
        if outmapximage:
            mapxlist = outmapximage.split('_')
            mapxscaleimage = '_'.join(mapxlist[:-1]) + '_scaled_' + mapxlist[-1]
            surfaceviewjson['x'] = os.path.basename(mapxscaleimage) if os.path.isfile(mapxscaleimage) else None
        if outmapyimage:
            mapylist = outmapyimage.split('_')
            mapyscaleimage = '_'.join(mapylist[:-1]) + '_scaled_' + mapylist[-1]
            surfaceviewjson['y'] = os.path.basename(mapyscaleimage) if os.path.isfile(mapyscaleimage) else None
        if outmapzimage:
            mapzlist = outmapzimage.split('_')
            mapzscaleimage = '_'.join(mapzlist[:-1]) + '_scaled_' + mapzlist[-1]
            surfaceviewjson['z'] = os.path.basename(mapzscaleimage) if os.path.isfile(mapzscaleimage) else None
        finaldict = {'map_surface': surfaceviewjson}

        with codecs.open(self.workdir + self.mapname + '_mapsurfaceview.json', 'w',
                         encoding='utf-8') as f:
            json.dump(finaldict, f)

        jpegs = glob.glob(self.workdir + '/*surface.jpeg')
        modelsurf = dict()
        finalmmdict = dict()
        if self.models:
            # print "self.models:%s" % self.models
            for model in self.models:
                modelname = model.filename.split('/')[-1].split('.')[0]
                modelmapsurface = dict()
                for jpeg in jpegs:
                    if modelname in jpeg and 'xsurface' in jpeg:
                        modelmapsurface['x'] = modelname + '_emd_' + self.mapname + '_scaled_xsurface.jpeg'
                    if modelname in jpeg and 'ysurface' in jpeg:
                        modelmapsurface['y'] = modelname + '_emd_' + self.mapname + '_scaled_ysurface.jpeg'
                    if modelname in jpeg and 'zsurface' in jpeg:
                        modelmapsurface['z'] = modelname + '_emd_' + self.mapname + '_scaled_zsurface.jpeg'
                modelsurf[modelname] = modelmapsurface
            finalmmdict['mapmodel_surface'] = modelsurf

            with codecs.open(self.workdir + self.mapname + '_mapmodelsurfaceview.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finalmmdict, f)


        end = timeit.default_timer()
        print('Surfaceview time: {}'.format(end-start))
        print('------------------------------------')

        return None

    # For mask views and central slice of masks
    # @profile
    def masks(self):
        """


        :return:
        """

        vtkpack, chimeraapp = self.surface_envcheck()
        if self.allmasks:
            # When masks data(not segmentation) are ready, switch this on to produce proper central slice of masks
            self.centralMasks()
            if chimeraapp:
                self.maskviewchimera(chimeraapp)
            elif vtkpack:
                self.maskviews()
            else:
                # print('No proper VTK or Chimera can be used for producing mask view. Please check.', file=sys.stderr)
                sys.stderr.write('No proper VTK or ChimeraX can be used for producing mask view. Please check.\n')
                print('------------------------------------')
        else:
            print('No masks for this entry!')
            print('------------------------------------')

    def masksvtp(self, maskresult):
        """
           Produce vtp files for those which does not have a vtp file before
           todo: need to be changed when maskresult returned is a dictionary

        :param masks:
        :return:
        """
        masks = []

        meshmaker = False
        if MESHMAKERPATH is not None:
            meshmaker = True
            meshmakerpath = MESHMAKERPATH
        else:
            try:
                assert find_executable('meshmaker') is not None
                meshmakerpath = find_executable('meshmaker')
                meshmaker = True
            except AssertionError:
                # print('meshmaker executable is not there.', file=sys.stderr)
                sys.stderr.write('meshmaker executable is not there.\n')
            sys.stderr.write('No proper VTK or ChimeraX can be used for producing mask view. Please check.\n')

        if not maskresult:
            return None
        else:
            for mask in maskresult:
                # if mask.endswith('.map'):
                if mask:
                    # maskname = mask[:-4]
                    # maskvtp = maskname + '.vtp'
                    maskvtp = mask + '.vtp'
                if os.path.isfile(maskvtp):
                    masks.append(maskvtp)
                    print('Vtp file for mask: %s exist.' % maskvtp)
                else:
                    masks.append(maskvtp)
                    # Todo:Contour level for masks use 1.0 for now and will be loaded from mmcif file later
                    cmd = meshmakerpath + ' ' + mask + ' -c ' + '1.0' + ' -o ' + maskname + ' -D -v'
                    print(cmd)
                    # if self.emdid:
                    #     cmd = 'source ' + CONDAPATH + ';source activate meshmaker; meshmaker ' + mask + ' -c ' \
                    #           + '1.0' + ' -o ' + maskname + ' -D -v'
                    #     print cmd
                    # else:
                    #     cmd = 'source activate meshmaker; meshmaker ' + mask + ' -c ' \
                    #           + '1.0' + '-o ' + maskname + ' -D -v'
                    #process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process = subprocess.Popen(cmd, shell=True, executable='/bin/bash', cwd=self.workdir)
                    recode = process.wait()
                    code, error = process.communicate()
                    if recode == 0:
                        print('Produce file: %s successfully' % maskvtp)
                    else:
                        print(code, error)
            return masks

    def maskviews(self):
        """
            Generate mask views by using vtk method

        :return:
        """

        maskresult = [item for item in self.allmasks if os.path.isfile(item)]
        masksdict = dict()
        if not maskresult:
            print('There is no masks offered for this map.')
            print('------------------------------------')
        else:
            masks = self.masksvtp(maskresult)
            if masks:
                root = os.path.dirname(masks[0])
                mapvtp = '{}/{}_{}.vtp'.format(self.workdir, self.mapname, str(self.cl))
            for mask in masks:
                masksdict[mask] = self.maskviews_vtk(mapvtp, mask)
            with codecs.open(self.workdir + self.mapname + '_mapmaskview.json', 'w',
                             encoding='utf-8') as f:
                json.dump(masksdict, f)

            print('Masks view by using VTK method.')
        return None

    def maskviewchimera(self, chimeraapp):
        """
            Generate mask views by using chimera method
        :return:
        """

        start = timeit.default_timer()
        errlist = []

        maskresults = [item for item in self.allmasks if os.path.isfile(item)]
        masksdict = dict()
        finaldict = dict()
        if not maskresults:
            print('There is no masks offered for this map.')
        else:
            # for mask in maskresults:
            for mask in self.allmasks:
                try:
                    masksdict[os.path.basename(mask)] = self.maskviews_chimera(mask, chimeraapp)
                except:
                    err = 'Saving mask {} views error: {}.'.format(mask, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
            if errlist:
                masksdict['err'] = {'mask_view_err': errlist}
            finaldict['masks'] = masksdict
            try:
                with codecs.open(self.workdir + self.mapname + '_mapmaskview.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('Masks view by using ChimeraX method.')
            except:
                sys.stderr.write('Saving masks to json error: {}.\n'.format(sys.exc_info()[1]))

        end = timeit.default_timer()
        print('Maskview time: {}'.format(end-start))
        print('------------------------------------')
        return None

    def maskviews_vtk(self, mapvtp, maskvtp):
        """
            Using the vtk method to generate mask views

        :return:
        """

        root = os.path.dirname(maskvtp)
        maskvtpfile = maskvtp[:-4].split('/')[-1]
        mapvtp = root + '/' + self.mapname + '_' + str(self.cl) + '.vtp'


        factGraphics = vtk.vtkGraphicsFactory()
        factGraphics.SetOffScreenOnlyMode(1)
        factGraphics.SetUseMesaClasses(1)
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(mapvtp)
        reader.Update()

        # add map vtp into it
        map_reader = vtk.vtkXMLPolyDataReader()
        map_reader.SetFileName(maskvtp)
        map_mapper = vtk.vtkPolyDataMapper()
        map_mapper.ScalarVisibilityOff()
        map_mapper.SetInputConnection(map_reader.GetOutputPort())
        map_actor = vtk.vtkActor()
        map_actor.SetMapper(map_mapper)

        map_actor.GetProperty().SetColor(0.0, 0.0, 1.0)
        map_actor.GetProperty().SetInterpolationToPhong()
        map_actor.GetProperty().SetDiffuse(0.9)
        map_actor.GetProperty().SetSpecular(0.6)
        map_actor.GetProperty().SetSpecularPower(30)
        map_actor.GetProperty().BackfaceCullingOn()
        map_actor.GetProperty().FrontfaceCullingOn()
        ############

        mapper = vtk.vtkPolyDataMapper()
        mapper.ScalarVisibilityOff()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.8, 0.1)
        actor.GetProperty().SetInterpolationToPhong()
        actor.GetProperty().SetDiffuse(0.9)
        actor.GetProperty().SetSpecular(0.6)
        actor.GetProperty().SetSpecularPower(30)
        actor.GetProperty().BackfaceCullingOn()
        actor.GetProperty().FrontfaceCullingOn()
        actor.GetProperty().SetOpacity(0.5)

        # Create the graphics structure. The renderer renders into the render
        # window. The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.

        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.SetOffScreenRendering(1)
        renWin.SetSize(3000, 3000)
        renWin.AddRenderer(ren)

        # Add the actors to the renderer, set the background and size
        # actor.RotateY(90)
        ren.AddActor(actor)
        ren.AddActor(map_actor)
        ren.SetBackground(0.9, 0.9, 0.9)
        ren.GetActiveCamera().SetParallelProjection(1)
        renWin.Render()

        # Output maps images only
        ren.ResetCamera()
        ren.GetActiveCamera().Zoom(1.30)
        outzimage = '{}{}_zmask.jpeg'.format(self.workdir, maskvtpfile)
        self.write_image(outzimage, renWin)

        actor.RotateX(90)
        actor.RotateY(90)
        map_actor.RotateX(90)
        map_actor.RotateY(90)
        # ren.ResetCamera()
        outyimage = '{}{}_ymask.jpeg'.format(self.workdir, maskvtpfile)
        self.write_image(outyimage, renWin)

        actor.RotateZ(90)
        actor.RotateX(90)
        map_actor.RotateZ(90)
        map_actor.RotateX(90)
        # ren.ResetCamera()
        outximage = '{}{}_xmask.jpeg'.format(self.workdir, maskvtpfile)
        self.write_image(outximage, renWin)
        self.scale_maskimg()

        onemaskdict = dict()
        onemaskdict['x'] = os.path.basename(outximage) if os.path.isfile(outximage) else None
        onemaskdict['y'] = os.path.basename(outyimage) if os.path.isfile(outyimage) else None
        onemaskdict['z'] = os.path.basename(outzimage) if os.path.isfile(outzimage) else None

        return onemaskdict

    def maskviews_chimera(self, mask, chimeraapp):
        """
            Generate mask view by using ChimeraX
            Todo: a contour level needed here for the mask

        :return:
        """

        # mapname = self.workdir + self.mapname + '.map'
        errlist = []
        start = timeit.default_timer()
        mapname = self.workdir + self.mapname
        maskname = mask.split('/')[-1]
        reg_maskname = re.search('emd_.*_msk.map', maskname)
        if reg_maskname:
            out_maskname = '{}_1.map'.format(maskname[:-4])
            print('!! Mask name is old !!')
        else:
            out_maskname = maskname
        maskfn = '{}_{}'.format(maskname, self.mapname)
        chimeracmd = maskfn + '_chimera.cxc'
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        mskcl = self.allmasks[mask]

        # if (mskcl and self.cl) is not None:
        met_check = False
        if self.met == 'tomo':
            if mskcl is not None:
                met_check = True
        elif self.met == 'sp' or self.met == 'heli' or self.met == 'subtomo' or self.met == '2dcrys':
            if (mskcl and self.cl) is not None:
                met_check = True
        if met_check:
            # In case there is no mask contour level, here we use 1.0 instead
            contour = "level " + str(mskcl) if mskcl is not None else 1.0
            with open(self.workdir + chimeracmd, 'w') as f:
                if self.met != 'tomo':
                    f.write(
                        'open ' + str(mapname) + ' format ccp4' + '\n'
                        'open ' + str(maskname) + ' format ccp4' + '\n'
                        "volume #1 style surface expandSinglePlane True " + '\n'
                        "volume #2 style surface expandSinglePlane True " + '\n'
                        "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                        "volume #2 color blue step 1 " + contour + '\n'
                        "volume #1 transparency 0.65" + '\n'
                    )
                else:
                    f.write(
                        'open ' + str(maskname) + ' format ccp4' +'\n'
                        "volume #1 style surface expandSinglePlane True " + '\n'
                        "volume #1 color blue step 1 " + contour + '\n'
                    )
                f.write(
                    # 'open ' + str(mask) + ' format ccp4' +'\n'
                    # "volume #1 style surface expandSinglePlane True " + '\n'
                    # "volume #2 style surface expandSinglePlane True " + '\n'
                    # "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                    # "volume #2 color blue step 1 " + contour + '\n'
                    # "volume #1 transparency 0.65" + '\n'
                    "set bgColor light gray" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_" + str(out_maskname) + "_zmaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    "turn x -90" + '\n'
                    "turn y -90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_" + str(out_maskname) + "_xmaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    "view orient" + '\n'
                    "turn x 90" + '\n'
                    "turn z 90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_" + str(out_maskname) + "_ymaskview.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    "close all" + "\n"
                    "exit"
                )

            if not bindisplay:
                subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                        cwd=self.workdir, shell=True)
            else:
                subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir, shell=True)

            end = timeit.default_timer()
            print('Primary map and mask view time: %s' % (end - start))
            print('------------------------------------')

            self.scale_maskimg()

            onemaskdict = dict()
            for dim in ['x', 'y', 'z']:
                cur_maskview = '{}_{}_{}maskview.jpeg'.format(mapname, out_maskname, dim)
                onemaskdict[dim] = '{}_{}_scaled_{}maskview.jpeg'.format(mapname, out_maskname, dim) if os.path.isfile(cur_maskview) else None

            return onemaskdict
        else:
            print('REMINDER: Missing contour level (primary map or mask or both).')

    def readmasks(self):
        """

            With the masks and read them into the TEMPy object

        :return: readmaks which is a dict(fullmaskname:
        """

        from va.preparation import PreParation as vaprep

        readfun = vaprep()
        readmasks = {}
        errlist = []
        for key in self.allmasks:
            try:
                # readmasks[key] = readfun.frommrc_totempy(key)
                readmasks[key] = readfun.new_frommrc_totempy(key)
            except:
                err = 'Something is wrong with reading mask: {}, {}'.format(key, sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write('There is something wrong with reading map {}\n'.format(key))

        return readmasks, errlist

    def centralMasks(self):
        """

            Produce the central slice of each masks in x, y, z directions

        :return: directory which contatins all the slices information

        """

        start = timeit.default_timer()
        errlist = []
        allmaskdict = dict()

        readmasks, errfromload = self.readmasks()
        errlist.append(errfromload)

        for (key, map) in iteritems(readmasks):
            mapname = os.path.basename(map.fullname)
            map_zsize = map.header.nz
            map_ysize = map.header.ny
            map_xsize = map.header.nx
            xmid = int(float(map_xsize) / 2)
            ymid = int(float(map_ysize) / 2)
            zmid = int(float(map_zsize) / 2)

            # xcentral = map.fullMap[:, :, xmid]
            xcentral = map.data[:, :, xmid]
            xdenom = (xcentral.max() - xcentral.min()) if xcentral.max() != xcentral.min() else 1
            xrescaled = (((xcentral - xcentral.min()) * 255.0) / xdenom).astype('uint8')
            xflipped = np.flipud(xrescaled)
            ximg = Image.fromarray(xflipped)
            try:
                ximg.save(self.workdir + mapname + '_xmaskcentral_slice.jpeg')
            except IOError as ioerr:
                xerr = 'Saving original x central slice of mask err:{}'.format(ioerr)
                errlist.append(xerr)
                sys.stderr.write(xerr + '\n')

            width, height = ximg.size
            xscalename = self.workdir + mapname + '_scaled_xmaskcentral_slice.jpeg'

            try:
                if width > 300 and height > 300:
                    if width >= height:
                        largerscaler = 300. / width
                        newheight = int(ceil(largerscaler * height))
                        imx = Image.fromarray(xflipped).resize((300, newheight), Image.ANTIALIAS)
                        imx.save(xscalename)
                    else:
                        largerscaler = 300. / height
                        newwidth = int(ceil(largerscaler * width))
                        imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.ANTIALIAS)
                        imx.save(xscalename)
                    # imx = Image.fromarray(xflipped).resize((300,300))
                    # imx.save(xscalename)
                else:
                    if width >= height:
                        scaler = 300. / width
                        newheight = int(ceil(scaler * height))
                        imx = Image.fromarray(xflipped).resize((300, newheight), Image.ANTIALIAS)
                        imx.save(xscalename)
                    else:
                        scaler = 300. / height
                        newwidth = int(ceil(scaler * width))
                        imx = Image.fromarray(xflipped).resize((newwidth, 300), Image.ANTIALIAS)
                        imx.save(xscalename)
            except:
                xerr = 'Saving scaled x central slice of mask err:{}'.format(sys.exc_info()[1])
                errlist.append(xerr)
                sys.stderr.write(xerr + '\n')

            # ycentral = map.fullMap[:, ymid, :]
            ycentral = map.data[:, ymid, :]
            ydenom = (ycentral.max() - ycentral.min()) if ycentral.max() != ycentral.min() else 1
            yrescaled = (((ycentral - ycentral.min()) * 255.0) / ydenom).astype('uint8')
            yrotate = np.rot90(yrescaled)
            yimg = Image.fromarray(yrotate)
            try:
                yimg.save(self.workdir + mapname + '_ymaskcentral_slice.jpeg')
            except IOError as ioerr:
                yerr = 'Saving original y central slice of mask err:{}'.format(ioerr)
                errlist.append(yerr)
                sys.stderr.write(yerr + '\n')

            width, height = yimg.size
            yscalename = self.workdir + mapname + '_scaled_ymaskcentral_slice.jpeg'
            try:
                if width > 300 and height > 300:
                    if width >= height:
                        largerscaler = 300. / width
                        newheight = int(ceil(largerscaler * height))
                        imy = Image.fromarray(yrotate).resize((300, newheight), Image.ANTIALIAS)
                        imy.save(yscalename)
                    else:
                        largerscaler = 300. / height
                        newwidth = int(ceil(largerscaler * width))
                        imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.ANTIALIAS)
                        imy.save(yscalename)
                    # imy = Image.fromarray(yrotate).resize((300, 300))
                    # imy.save(yscalename)
                else:
                    if width >= height:
                        scaler = 300. / width
                        newheight = int(ceil(scaler * height))
                        imy = Image.fromarray(yrotate).resize((300, newheight), Image.ANTIALIAS)
                        imy.save(yscalename)
                    else:
                        scaler = 300. / height
                        newwidth = int(ceil(scaler * width))
                        imy = Image.fromarray(yrotate).resize((newwidth, 300), Image.ANTIALIAS)
                        imy.save(yscalename)
            except:
                yerr = 'Saving scaled y central slice of mask err:{}'.format(sys.exc_info()[1])
                errlist.append(yerr)
                sys.stderr.write(yerr + '\n')

            # zcentral = map.fullMap[zmid, :, :]
            zcentral = map.data[zmid, :, :]
            zdenom = (zcentral.max() - zcentral.min()) if zcentral.max() != zcentral.min() else 1
            zrescaled = (((zcentral - zcentral.min()) * 255.0) / zdenom).astype('uint8')
            zflipped = np.flipud(zrescaled)
            zimg = Image.fromarray(zflipped)
            try:
                zimg.save(self.workdir + mapname + '_zmaskcentral_slice.jpeg')
            except IOError as ioerr:
                zerr = 'Saving original z central slice of mask err:{}'.format(ioerr)
                errlist.append(zerr)
                sys.stderr.write(zerr + '\n')

            width, height = zimg.size
            zscalename = self.workdir + mapname + '_scaled_zmaskcentral_slice.jpeg'
            try:
                if width > 300 and height > 300:
                    if width >= height:
                        largerscaler = 300. / width
                        newheight = int(ceil(largerscaler * height))
                        imz = Image.fromarray(zflipped).resize((300, newheight), Image.ANTIALIAS)
                        imz.save(zscalename)
                    else:
                        largerscaler = 300. / height
                        newwidth = int(ceil(largerscaler * width))
                        imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.ANTIALIAS)
                        imz.save(zscalename)
                    # imz = Image.fromarray(zflipped).resize((300, 300))
                    # imz.save(zscalename)
                else:
                    if width >= height:
                        scaler = 300. / width
                        newheight = int(ceil(scaler * height))
                        imz = Image.fromarray(zflipped).resize((300, newheight), Image.ANTIALIAS)
                        imz.save(zscalename)
                    else:
                        scaler = 300. / height
                        newwidth = int(ceil(scaler * width))
                        imz = Image.fromarray(zflipped).resize((newwidth, 300), Image.ANTIALIAS)
                        imz.save(zscalename)
            except:
                zerr = 'Saving original z scaled central slice of mask err:{}'.format(sys.exc_info()[1])
                errlist.append(zerr)
                sys.stderr.write(zerr + '\n')

            cslicejson = dict()
            cslicejson['x'] = os.path.basename(xscalename) if os.path.isfile(xscalename) else None
            cslicejson['y'] = os.path.basename(yscalename) if os.path.isfile(yscalename) else None
            cslicejson['z'] = os.path.basename(zscalename) if os.path.isfile(zscalename) else None

            allmaskdict[mapname] = cslicejson

        if errlist:
            allmaskdict['err'] = {'mask_central_slice_err': errlist}
        finaldict = {'mask_central_slice': allmaskdict}

        try:
            with codecs.open(self.workdir + self.mapname + '_maskcentralslice.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except IOError as ioerr:
            print('Saving masks central slices to json err: {}'.format(ioerr))

        end = timeit.default_timer()
        print('MaksCentralSlice time: %s' % (end - start))
        print('------------------------------------')

        return None

    def checkvtp(self):
        """

            Check if there is a vtp file exist or not

        :return:
        """


        vtpreg = self.workdir + '*.vtp'
        globresult = glob.glob(vtpreg)
        vtpname = '{}{}_{}.vtp'.format(self.workdir, self.mapname, self.cl)
        if vtpname in globresult:
            vtpfullname = vtpname
            print('%s exist already.' % vtpname)
            return vtpfullname
        else:
            if globresult is not None:
                print('vtp file: %s exist, please check.' % globresult)
            return None

    def genvtp(self, fullmappath):
        """

            Generate vtp file for non-server input

        :param fullmappath:
        :return:
        """

        meshmaker = False
        if MESHMAKERPATH is not None:
            meshmaker = True
            meshmakerpath = MESHMAKERPATH
        else:
            try:
                assert find_executable('meshmaker') is not None
                meshmakerpath = find_executable('meshmaker')
                meshmaker = True
            except AssertionError:
                # print('meshmaker executable is not there', file=sys.stderr)
                sys.stderr.write('meshmaker executable is not there.\n')

        if meshmaker and self.cl is not None:
            outvtpname = '{}{}_{}'.format(self.workdir, self.mapname, self.cl)
            cmd = meshmakerpath + ' ' + fullmappath + ' -c ' + str(self.cl) + ' -o ' + outvtpname + ' -D -v'
            process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
            code = process.wait()
            if code == 0:
                result = outvtpname + '.vtp'
                print('Produce file: %s successfully' % result)
                return result
            else:
                print('Meshmaker did not produce the vtp file check the inputs.')
                return None
        else:
            print('Did not find proper meshmaker or the no contour level available .')

        # meshmaker = False
        # try:
        #     assert find_executable('meshmaker') is not None
        #     meshmakerpath = find_executable('meshmaker')
        #     meshmaker = True
        # except AssertionError:
        #     print >> sys.stderr, 'meshmaker executable is not there.'
        #     print >> sys.stderr, 'Try to use the conda environment.'
        #     outvtpname = '{}{}_{}'.format(self.workdir, self.mapname, self.cl)
        #     if self.emdid:
        #         cmd = 'source ' + CONDAPATH + ';source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + ' -o ' + outvtpname + ' -D -v'
        #         print cmd
        #     else:
        #         cmd = 'source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + '-o ' + outvtpname + ' -D -v'
        #     process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        #     code = process.wait()
        #     if code == 0:
        #         result = outvtpname + '.vtp'
        #         print 'Produce file: %s successfully' % result
        #         return result
        #     else:
        #         print 'Meshmaker did not produce the vtip file check the inputs.'
        #         return None
        #
        # if meshmaker:
        #     outvtpname = '{}{}_{}'.format(self.workdir, self.mapname, self.cl)
        #     if self.emdid:
        #         cmd = 'source ' + CONDAPATH + ';source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + ' -o ' + outvtpname + ' -D -v'
        #         print cmd
        #     else:
        #         cmd = 'source activate meshmaker; meshmaker ' + fullmappath + ' -c ' + str(self.cl) + '-o ' + outvtpname + ' -D -v'
        #     #cmd = [meshmakerpath, fullmappath, '-c', str(self.cl), '-o', outvtpname, '-D', '-v']
        #     process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        #     code = process.wait()
        #     if code == 0:
        #         result = outvtpname + '.vtp'
        #         print 'Produce file: %s successfully' % result
        #         return result
        #     else:
        #         print 'Meshmaker did not produce the vtip file check the inputs.'
        #         return None
        # else:
        #     print >> sys.stderr, 'Meshmaker is not installed. There will not any vtp files used to generate surface view.'
        #     return None

    @staticmethod
    def write_image(imageFile, renWin):
        # Write the current view of the renderer to an image
        if imageFile:
            writer = vtk.vtkBMPWriter()
            windowto_image_filter = vtk.vtkWindowToImageFilter()
            windowto_image_filter.SetInput(renWin)
            # image quality
            windowto_image_filter.SetInputBufferTypeToRGB()

            writer.SetFileName(imageFile)
            writer.SetInputConnection(windowto_image_filter.GetOutputPort())
            writer.Write()
        else:
            raise RuntimeError('Need a filename.')

    # Rawmap surface view when two half maps are given
    def rawmapcl(self):
        """

            Calculate a corresponding 'recommended contour level' based on the recommended contour level
            (have tried matching the value scale which get worse result than this one)

        :return: A float which give the contour level
        """

        # numvox = len(self.map.fullMap[self.map.fullMap >= self.cl])
        numvox = len(self.map.data[self.map.data >= self.cl])
        rawmap = self.rawmap
        # rawdata = rawmap.fullMap.flatten()
        rawdata = rawmap.data.flatten()
        flatraw = sorted(rawdata)[::-1]
        rawcl = flatraw[numvox]

        return rawcl


    def findrawmap(self):

        if self.emdid:
            rawmapname = '{}emd_{}_rawmap.map'.format(self.workdir, self.emdid)
        else:
            oddname = os.path.basename(self.hmodd.fullname)
            evenname = os.path.basename(self.hmeven.fullname)
            rawmapname = '{}{}_{}_rawmap.map'.format(self.workdir, oddname, evenname)

        if self.hmodd is not None and self.hmeven is not None:
            if os.path.isfile(rawmapname):
                return rawmapname
            else:

                print('Base on the half maps, rawmap is not produced!!')
                return None
        else:
            return None


    def rawmapsurface_chimera(self, chimeraapp):
        """

            Generate rawmap surfaces if two half maps and rawmap and rawmap contour are there

        :param chimeraapp: binary value to check if ChimeraX is there properly
        :return: None
        """

        # rawmapre = '*_rawmap.map'
        # rawmapname = glob.glob(self.workdir + rawmapre)
        if self.hmodd is not None and self.hmeven is not None:
            rawmapname = self.findrawmap()
        else:
            rawmapname = None

        bindisplay = os.getenv('DISPLAY')

        try:
            rawmapcl = self.rawmapcl()
        except:
            rawmapcl = None
            print('Problem with raw map contour level calculation')

        if (self.hmodd is not None and self.hmeven is not None) and rawmapname and rawmapcl is not None:

            start = timeit.default_timer()
            errlist = []

            mapname = os.path.basename(rawmapname)
            locCHIMERA = chimeraapp
            # rawmap surface view alone
            rawmapchimeracmd = rawmapname + '_chimera.cxc'
            assemble = False
            with open(rawmapchimeracmd, 'w') as f:
                f.write(
                    # Chimera version
                    # 'open ccp4:' + str(mapname) + '\n'
                    # "volume #0 style surface expandSinglePlane True " + '\n'
                    # "volume #0 color #B8860B step 1 " + contour + '\n'
                    # "set projection orthographic" + '\n'
                    # "surftransp 50" + '\n'  # make the surface a little bit see-through
                    # "background solid light gray" + '\n'
                    # "copy file " + str(self.mapname) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    # "turn x -90" + '\n'
                    # "center" + '\n'
                    # "copy file " + str(self.mapname) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    # "turn z -90" + '\n'
                    # "center" + '\n'
                    # "copy file " + str(self.mapname) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    # "close all" + "\n"
                    # "stop"

                    # ChimeraX version
                    "open " + str(rawmapname) + " format ccp4" + '\n'
                    "volume #1 style surface expandSinglePlane True" + '\n'
                    # "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                    "volume #1 step 1 level " + str(rawmapcl) + '\n'
                    "set bgColor white" + '\n'
                    "lighting full \n"
                    "view cofr True \n"
                    "save " + str(mapname) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    "turn x -90" + '\n'
                    "turn y -90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    "view orient" + '\n'
                    "turn x 90" + '\n'
                    "turn z 90" + '\n'
                    "view cofr True" + '\n'
                    "save " + str(mapname) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                    "close all" + "\n"
                    "exit" + '\n'
                )
            try:
                if not bindisplay:
                    subprocess.check_call(locCHIMERA + " --offscreen --nogui " + rawmapchimeracmd,
                                        # stdout=subprocess.STDOUT, cwd=self.workdir, shell=True)
                                            cwd=self.workdir, shell=True)
                else:
                    subprocess.check_call(locCHIMERA + " " + rawmapchimeracmd, cwd=self.workdir, shell=True)

            except subprocess.CalledProcessError as suberr:
                err = 'Raw map surface view by chimera error: {}'.format(suberr)
                errlist.append(err)
                sys.stderr.write(err + '\n')

            print('Raw map surface views were generated by ChimeraX method')
            try:
                self.scale_surfaceview()
            except:
                err = 'Scaling the surface views err: {}'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            rawsurfaceviewjson = dict()

            outmapximage = str(mapname) + '_xsurface.jpeg'
            mapxlist = outmapximage.split('_')
            mapxscaleimage = '_'.join(mapxlist[:-1]) + '_scaled_' + mapxlist[-1]
            rawsurfaceviewjson['x'] = os.path.basename(mapxscaleimage) if os.path.isfile(
                self.workdir + mapxscaleimage) else None

            outmapyimage = str(mapname) + '_ysurface.jpeg'
            mapylist = outmapyimage.split('_')
            mapyscaleimage = '_'.join(mapylist[:-1]) + '_scaled_' + mapylist[-1]
            rawsurfaceviewjson['y'] = os.path.basename(mapyscaleimage) if os.path.isfile(
                self.workdir + mapyscaleimage) else None

            outmapzimage = str(mapname) + '_zsurface.jpeg'
            mapzlist = outmapzimage.split('_')
            mapzscaleimage = '_'.join(mapzlist[:-1]) + '_scaled_' + mapzlist[-1]
            rawsurfaceviewjson['z'] = os.path.basename(mapzscaleimage) if os.path.isfile(
                self.workdir + mapzscaleimage) else None
            if errlist:
                rawsurfaceviewjson['err'] = {'rawmap_surface_err': errlist}

            finaldict = {'rawmap_map_surface': rawsurfaceviewjson}
            rawcldict = {'rawmap_contour_level': {'cl': '{:0.2f}'.format(rawmapcl)}}

            try:
                with codecs.open(self.workdir + mapname + '_rawmapsurfaceview.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except:
                err = 'Saving map surface view json error: {}.'.format(sys.exc_info()[1])
                sys.stderr.write(err + '\n')

            try:
                with codecs.open(self.workdir + mapname + '_rawmapcl.json', 'w', encoding='utf-8') as ff:
                    json.dump(rawcldict, ff)
            except:
                err = 'Saving rawmap contour level json error: {}.'.format(sys.exc_info()[1])
                sys.stderr.write(err + '\n')

            end = timeit.default_timer()
            print('Raw map surface view time: %s' % (end - start))
            print('------------------------------------')

        else:
            print('No raw map or half maps or raw map contour level for raw map surfaces.')


    # Surface Chimera way
    def surfaceview_chimera(self, chimeraapp):
        """
            Generate surface view by using headless Chimera and pychimera

        """
        import mmap

        start = timeit.default_timer()
        errlist = []
        mmerrlist = []
        bindisplay = os.getenv('DISPLAY')

        mapname = self.workdir + self.mapname
        if not os.path.isfile(mapname) and os.path.isfile(self.mapname):
            mapname = self.mapname

        locCHIMERA = chimeraapp
        contour = "level " + str(self.cl) if self.cl is not None else ''
        # map surface view alone
        mapchimeracmd = self.mapname + '_chimera.cxc'
        assemble = False
        with open(self.workdir + mapchimeracmd, 'w') as f:
            f.write(
                # Chimera version
                # 'open ccp4:' + str(mapname) + '\n'
                # "volume #0 style surface expandSinglePlane True " + '\n'
                # "volume #0 color #B8860B step 1 " + contour + '\n'
                # "set projection orthographic" + '\n'
                # "surftransp 50" + '\n'  # make the surface a little bit see-through
                # "background solid light gray" + '\n'
                # "copy file " + str(self.mapname) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "turn x -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(self.mapname) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "turn z -90" + '\n'
                # "center" + '\n'
                # "copy file " + str(self.mapname) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                # "close all" + "\n"
                # "stop"

                # ChimeraX version
                "open " + str(mapname) + " format ccp4" + '\n'
                "volume #1 style surface expandSinglePlane True" + '\n'
                # "volume #1 color #B8860B step 1 level " + str(self.cl) + '\n'
                "volume #1 step 1 level " + str(self.cl) + '\n'
                "set bgColor white" + '\n'
                "lighting full \n"
                "view cofr True \n"
                "save " + str(self.mapname) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "turn x -90" + '\n'
                "turn y -90" + '\n'
                "view cofr True" + '\n'
                "save " + str(self.mapname) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "view orient" + '\n'
                "turn x 90" + '\n'
                "turn z 90" + '\n'
                "view cofr True" + '\n'
                "save " + str(self.mapname) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                "close all" + "\n"
                "exit" + '\n'
            )

        try:
            if not bindisplay:
                subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + mapchimeracmd,
                                      # stdout=subprocess.STDOUT, cwd=self.workdir, shell=True)
                                        cwd=self.workdir, shell=True)
                end = timeit.default_timer()
                print('Primary map surface view time: %s' % (end - start))
                print('------------------------------------')
            else:
                subprocess.check_call(locCHIMERA + " " + self.workdir + mapchimeracmd, cwd=self.workdir, shell=True)
                end = timeit.default_timer()
                print('Primary map surface view time: %s' % (end - start))
                print('------------------------------------')
        except subprocess.CalledProcessError as suberr:
            end = timeit.default_timer()
            err = 'Primary map surface view by chimera error: {}'.format(suberr)
            print('Primary map surface view time: %s' % (end - start))
            print('------------------------------------')
            errlist.append(err)
            sys.stderr.write(err + '\n')


        # map and models view together
        nstart = timeit.default_timer()
        if self.models:
            for model in self.models:
                # pdbid = model.filename.split('/')[-1].split('.')[0]
                pdbid = os.path.basename(model.filename)
                surfacefn = '{}_{}'.format(pdbid, self.mapname)
                chimeracmd = surfacefn + '_chimera.cxc'
                with open(self.workdir + chimeracmd, 'w') as f:
                    f.write(
                        # Chimera version
                        # 'open ccp4:' + str(mapname) + '\n'
                        # "open cif:" + str(model.filename) + '\n'
                        # "volume #0 style surface expandSinglePlane True " + '\n'
                        # "volume #0 color #B8860B step 1 " + contour + '\n'
                        # "set projection orthographic" + '\n'
                        # "surftransp 50" + '\n'  # make the surface a little bit see-through
                        # "background solid light gray" + '\n'
                        # "copy file " + str(surfacefn) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        # "turn x -90" + '\n'
                        # "center" + '\n'
                        # "copy file " + str(surfacefn) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        # "turn z -90" + '\n'
                        # "center" + '\n'
                        # "copy file " + str(surfacefn) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        # "close all" + "\n"
                        # "stop"

                        # ChimeraX version
                        'open ' + str(mapname) + " format ccp4" + '\n'
                        "open " + str(model.filename) + " format mmcif" + '\n'
                        "hide selAtoms" + '\n'
                        "show selAtoms ribbons" + '\n'
                        "color #2 #003BFF" + '\n'
                        "volume #1 style surface expandSinglePlane True " + '\n'
                        "volume #1 color #B8860B step 1 " + contour + '\n'
                        "volume #1 transparency 0.65" + '\n'  # make the surface a little bit see-through
                        "set bgColor light gray" + '\n'
                        "view cofr True \n"
                        "save " + str(surfacefn) + "_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        "turn x -90" + '\n'
                        "turn y -90" + '\n'
                        "view cofr True" + '\n'
                        "save " + str(surfacefn) + "_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        "view orient" + '\n'
                        "turn x 90" + '\n'
                        "turn z 90" + '\n'
                        "view cofr True" + '\n'
                        "save " + str(surfacefn) + "_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                        "close all" + "\n"
                        "exit"

                    )
                with open(str(model.filename)) as f:
                    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    # python 3 mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    if s.find(b'point symmetry operation') != -1:
                        assemble = True
                    else:
                        assemble = False
                chimeracmdassemble = surfacefn + '_chimera_assemble.cxc'
                if assemble:
                    modelname = os.path.basename(model.filename)
                    mapname = os.path.basename(mapname)
                    prefix = '{}_{}'.format(modelname, mapname)

                    with open(self.workdir + chimeracmdassemble, 'w') as f:
                        f.write(
                            # ChimeraX version
                            "open " + str(mapname) + " format ccp4" + '\n'
                            "open " + str(model.filename) + " format mmcif" + '\n'
                            "hide selAtoms" + '\n'
                            "show selAtoms ribbons" + '\n'
                            "color #2 #003BFF" + '\n'
                            "volume #1 style surface expandSinglePlane True" + '\n'
                            "volume #1 color #B8860B step 1 " + contour + '\n'
                            "volume #1 transparency 0.65" + '\n'  # make the surface a little bit see-through
                            "sym #2 assembly 1\n"
                            "set bgColor light gray" + '\n'
                            "view cofr True \n"
                            "save " + str(prefix) + "_assemble_zsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(prefix) + "_assemble_xsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(prefix) + "_assemble_ysurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit" + '\n'
                        )


                try:
                    if not bindisplay:
                        subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                              cwd=self.workdir, shell=True)
                        if assemble:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmdassemble,
                                                  cwd=self.workdir, shell=True)
                        nend = timeit.default_timer()
                        print('Primary map and model view time: %s' % (nend - nstart))
                        print('------------------------------------')
                    else:
                        subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir, shell=True)
                        if assemble:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmdassemble,
                                                  cwd=self.workdir, shell=True)
                        nend = timeit.default_timer()
                        print('Primary map and model view time: %s' % (nend - nstart))
                        print('------------------------------------')

                except subprocess.CalledProcessError as suberr:
                    err = 'Saving model {} and map err: {}'.format(str(model.filename), suberr)
                    mmerrlist.append(err)
                    sys.stderr.write(err + '\n')

        print('Surface views were generated by ChimeraX')
        try:
            self.scale_surfaceview()
        except:
            err = 'Scaling the surface views err: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            mmerrlist.append(err)
            sys.stderr.write(err + '\n')

        surfaceviewjson = dict()
        outmapximage = str(self.mapname) + '_xsurface.jpeg'
        mapxlist = outmapximage.split('_')
        mapxscaleimage = '_'.join(mapxlist[:-1]) + '_scaled_' + mapxlist[-1]
        surfaceviewjson['x'] = os.path.basename(mapxscaleimage) if os.path.isfile(self.workdir + mapxscaleimage) else None

        outmapyimage = str(self.mapname) + '_ysurface.jpeg'
        mapylist = outmapyimage.split('_')
        mapyscaleimage = '_'.join(mapylist[:-1]) + '_scaled_' + mapylist[-1]
        surfaceviewjson['y'] = os.path.basename(mapyscaleimage) if os.path.isfile(self.workdir + mapyscaleimage) else None

        outmapzimage = str(self.mapname) + '_zsurface.jpeg'
        mapzlist = outmapzimage.split('_')
        mapzscaleimage = '_'.join(mapzlist[:-1]) + '_scaled_' + mapzlist[-1]
        surfaceviewjson['z'] = os.path.basename(mapzscaleimage) if os.path.isfile(self.workdir + mapzscaleimage) else None
        if errlist:
            surfaceviewjson['err'] = {'map_surface_err': errlist}

        finaldict = {'map_surface': surfaceviewjson}

        try:
            with codecs.open(self.workdir + self.mapname + '_mapsurfaceview.json', 'w',
                             encoding='utf-8') as f:
                json.dump(finaldict, f)
        except:
            err = 'Saving map surface view json error: {}.'.format(sys.exc_info()[1])
            sys.stderr.write(err + '\n')

        jpegs = glob.glob(self.workdir + '/*surface.jpeg')
        modelsurf = dict()
        finalmmdict = dict()
        if self.models:
            # print "self.models:%s" % self.models
            for model in self.models:
                modelname = os.path.basename(model.filename)
                surfacefn = '{}_{}'.format(modelname, self.mapname)
                modelmapsurface = dict()
                for jpeg in jpegs:
                    if modelname in jpeg and 'xsurface' in jpeg:
                        modelmapsurface['x'] = str(surfacefn) + '_scaled_xsurface.jpeg'
                    if modelname in jpeg and 'ysurface' in jpeg:
                        modelmapsurface['y'] = str(surfacefn) + '_scaled_ysurface.jpeg'
                    if modelname in jpeg and 'zsurface' in jpeg:
                        modelmapsurface['z'] = str(surfacefn) + '_scaled_zsurface.jpeg'
            #     modelsurf[modelname] = modelmapsurface
            # if mmerrlist:
            #     modelsurf['err'] = {'mapmodel_surface_err': mmerrlist}
            # finalmmdict['mapmodel_surface'] = modelsurf
            #
            # try:
            #     with codecs.open(self.workdir + self.mapname + '_mapmodelsurfaceview.json', 'w',
            #                      encoding='utf-8') as f:
            #         json.dump(finalmmdict, f)
            # except:
            #     err = 'Saving model and map surface views json error: {}.'.format(sys.exc_info()[1])
            #     sys.stderr.write(err + '\n')

                with open(str(model.filename)) as f:
                    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    # python 3 mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    if s.find(b'point symmetry operation') != -1:
                        assemble = True
                    else:
                        assemble = False
                assemblemapsurface = dict()
                if assemble:
                    modelname = os.path.basename(model.filename)
                    surfacefn = '{}_{}'.format(modelname, self.mapname)
                    for jpeg in jpegs:
                        if modelname in jpeg and 'xsurface' in jpeg:
                            assemblemapsurface['x_assemble'] = str(surfacefn) + '_assemble_scaled_xsurface.jpeg'
                        if modelname in jpeg and 'ysurface' in jpeg:
                            assemblemapsurface['y_assemble'] = str(surfacefn) + '_assemble_scaled_ysurface.jpeg'
                        if modelname in jpeg and 'zsurface' in jpeg:
                            assemblemapsurface['z_assemble'] = str(surfacefn) + '_assemble_scaled_zsurface.jpeg'

                mergeddict = dict(modelmapsurface, **assemblemapsurface)
                modelsurf[modelname] = mergeddict
        if mmerrlist:
            modelsurf['err'] = {'mapmodel_surface_err': mmerrlist}
        finalmmdict['mapmodel_surface'] = modelsurf

        try:
            with codecs.open(self.workdir + self.mapname + '_mapmodelsurfaceview.json', 'w',
                                encoding='utf-8') as f:
                json.dump(finalmmdict, f)
        except:
            err = 'Saving model and map surface views json error: {}.'.format(sys.exc_info()[1])
            sys.stderr.write(err + '\n')

        end = timeit.default_timer()
        print('Surfaceview time: %s' % (end - start))
        print('------------------------------------')


    def modelfitsurface(self, chimeraapp):

        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*residue_inclusion.json')
        basedir = self.workdir
        mapname = self.mapname
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        errlist = []

        fulinjson = injson[0] if injson else None
        try:
            if fulinjson:
                with open(fulinjson, 'r') as f:
                    args = json.load(f)
            else:
                args = None
                print('There is no residue inclusion json file.')
        except TypeError:
            err = 'Open residue_inclusion error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None:
                models = args['residue_inclusion']
                try:
                    del models['err']
                except:
                    print('Residue inclusion json result is correct')

                print('There is/are %s model(s).' % len(models))

                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            residues = value[key]['residue']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_fit_chimera.cxc'.format(modelname, mapname)
                            print(chimerafname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(model) + " format mmcif" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        for (color, residue) in zip(colors, residues):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # res = re.sub("\D", "", restmp)
                            res = re.findall(r'-?\d+', restmp)[0]
                            fp.write(
                                'color /' + chain + ':' + res + ' ' + color + '\n'
                            )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_zfitsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_xfitsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_yfitsurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} fit surface view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        self.scale_surfaceview()
                    except:
                        err = 'Scaling model fit surface view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*surface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        # print "self.models:%s" % self.models
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.mapname)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xfitsurface' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xfitsurface.jpeg'
                                if modelname in jpeg and 'yfitsurface' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_yfitsurface.jpeg'
                                if modelname in jpeg and 'zfitsurface' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zfitsurface.jpeg'
                            if errlist:
                                modelmapsurface['err'] = {'model_fit_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['modelfit_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.mapname + '_modelfitsurfaceview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write('Saving model fit surface view to json error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('Modelfitsurface time: %s' % (end - start))
                print('------------------------------------')


    def scale_surfaceview(self):
        """
            Scale the surface view images size to 300X300

        :return: None
        """

        # import imageio
        import glob

        for imgfile in glob.glob(self.workdir + '*surface.jpeg'):
            if 'scaled' not in imgfile:
                namelist = imgfile.split('/')[-1].split('_')
                nameone = '_'.join(namelist[:-1])
                nametwo = namelist[-1]
                # npimg = imageio.imread(imgfile)
                npimg = Image.open(imgfile)
                # zoomimg = self.zoomin(npimg, 1.00)
                # im = Image.fromarray(zoomimg).resize((300, 300))
                im = npimg.resize((300, 300))
                im.save(self.workdir + nameone + '_scaled_' + nametwo)

        return None


    def scale_maskimg(self):
        """

        :return: None
        """

        # import imageio
        import glob

        for imgfile in glob.glob(self.workdir + '*maskview.jpeg'):
            if 'scaled' not in imgfile:
                namelist = imgfile.split('/')[-1].split('_')
                nameone = '_'.join(namelist[:-1])
                nametwo = namelist[-1]
                # npimg = imageio.imread(imgfile)
                npimg = Image.open(imgfile)
                # zoomimg = self.zoomin(npimg, 1.00)
                # im = Image.fromarray(zoomimg).resize((300, 300))
                im = npimg.resize((300, 300))
                im.save(self.workdir + nameone + '_scaled_' + nametwo)

        return None


    def zoomin(self,img, factor, **kwargs):
        """
            Zoom in to the surface view images
        :param img: img object of input
        :return:
        """
        from scipy.ndimage import zoom

        h, w = img.shape[:2]
        zoom_tuple = (factor,) * 2 + (1,) * (img.ndim - 2)
        if factor != 1.:
            # Bounding box of the zoomed-in region within the input array
            zh = int(np.round(h / factor))
            zw = int(np.round(w / factor))
            top = (h - zh) // 2
            left = (w - zw) // 2

            out = zoom(img[top:top + zh, left:left + zw], zoom_tuple, **kwargs)
            trim_top = ((out.shape[0] - h) // 2)
            trim_left = ((out.shape[1] - w) // 2)
            out = out[trim_top:trim_top + h, trim_left:trim_left + w]

        # If factor == 1, just return the input array
        else:
            out = img

        return out


    @staticmethod
    def surface_envcheck():
        """

            Check the running environment for surface view.
            If the machine is headless, remind the user vtk or Chimera have to be build in the headless way.
            If vtk can not imported, try use Chimera.

        :return: tuple of vtkpack and chimeraapp binary value
        """

        display = os.getenv('DISPLAY')
        if display is None:
            print('You may running this program on a headless machine. Please make sure either headless VTK or headless' \
                  'ChimeraX are properly installed accordingly.')

        vtkpack = False
        chimeraapp = False
        try:
            import vtk
            vtkpack = True
        except ImportError:
            sys.stderr.write('VTK is not installed or imported properly. Trying to use ChimeraX to produce surface views.\n')

        try:
            if CHIMERA is not None:
                chimeraapp = CHIMERA
                print(chimeraapp)
            else:
                assert find_executable('ChimeraX') is not None
                chimeraapp = find_executable('ChimeraX')
                print(chimeraapp)
        except AssertionError:
            # print('Chimera executable is not there.', file=sys.stderr)
            sys.stderr.write('ChimeraX executable is not there.\n')

        return vtkpack, chimeraapp

    # Density distribution
    # @profile
    def mapdensity_distribution(self):
        """

            produce the map density distribution

        :return: None
        """
        self.density_distribution(self.map)

        return None

    # @profile
    def rawmapdensity_distribution(self):
        """

            Produce raw map density distribution

        :param rawmap: Raw map object
        :return: None
        """

        if self.rawmap is not None:
            self.density_distribution(self.rawmap)
        else:
            print('There is no raw map for density distribution.')
            print('------------------------------------')

        return None

    # @profile
    def density_distribution(self, denmap=None):
        """

            Produce density value distribution information with the density map information.
            x was divided into 128 bins
            y was scaled by logarithmic 10 (for 0 value add 1 to igonre artifacts)

        :param: None
        :return: None

        """

        start = timeit.default_timer()
        bins = 128
        errlist = []
        datadict = {}
        # curmapname = os.path.basename(denmap.filename)
        curmapname = os.path.basename(denmap.fullname)
        if 'rawmap' in curmapname:
            tag = 'rawmap_'
        else:
            tag = ''
        try:
            # mapdata = self.map.getMap()
            mapdata = denmap.data
            flatmap = mapdata.flatten()
            # datamode = self.map.header[3]
            datamode = self.map.header.mode
            uniques, uniquecounts = np.unique(flatmap, return_counts=True)
            uniquelen = len(uniques)
            if datamode == 0:
                bins = uniques
                hist, bin_edges = np.histogram(flatmap, bins=bins)
            elif datamode == 1 or datamode == 6:
                if uniquelen > 1000:
                    inds = np.linspace(0, uniquelen-1, num=128, dtype=np.uint16)
                    bins = np.take(uniques, inds)
                    hist, bin_edges = np.histogram(flatmap, bins=bins)
                else:
                    hist = uniquecounts
                    bin_edges = np.append(uniques, uniques[-1])
            else:
                bins = np.linspace(min(flatmap), max(flatmap), 128)
                hist, bin_edges = np.histogram(flatmap, bins=bins)
            # hist, bin_edges = np.histogram(flatmap, bins=bins)
            hist[hist < 1] = 1
            newhist = np.log10(hist)

            # plt.plot(np.round(bin_edges[:-1], 10).tolist(), np.round(newhist, 10).tolist())
            plt.figure(figsize=(10, 3))
            # plt.hist(flatmap, density=False, bins=bin_edges)
            plt.bar(np.round(bin_edges[:-1], 10).tolist(), np.round(newhist, 10).tolist())
            plt.savefig(self.workdir + '/' + curmapname + '_voxel_distribution.png')

            mode = np.round(bin_edges[:-1][np.argmax(newhist)], 5).tolist()
            datadict = {
                tag + 'density_distribution': {'y': np.round(newhist, 10).tolist(),
                                         'x': np.round(bin_edges[:-1], 10).tolist(),
                                         'mode': mode}}
        except:
            err = 'Density distribution error:{}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {tag + 'density_distribution': {'err': {'density_distribution_error': errlist}}}

        try:
            with codecs.open(self.workdir + curmapname + '_density_distribution.json', 'w',
                             encoding='utf-8') as f:
                json.dump(datadict, f)
        except:
            sys.stderr.write('Saving denisty distribution to json error.')

        end = timeit.default_timer()
        print(tag + 'Density distribution time: %s' % (end - start))
        print('------------------------------------')

        return None

    # Atom and residue includsion
    @staticmethod
    def __floatohex(numlist):
        """

            Produce hex color between red and green

        :param numlist: A list of RGB values
        :return: A list of hex value between R and G with B = 0

        """

        # rgbs = [[int((1 - num) * 255), int(num * 255), 0] for num in numlist]
        # rgbs = [[int((1 - num) * 255)*0.5, 120, int(num * 255)*0.5] for num in numlist]
        numlist = [0 if i < 0 else i for i in numlist]
        rgbs = [[122, int((num) * 255), int(num * 255)] for num in numlist]
        resultlist = []
        resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]
        # for rgb in rgbs:
        #    result = '#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2])
        #    resultlist.append(result)

        return resultlist

    # Atom and residue includsion
    @staticmethod
    def __floatohex_aboveone(numlist):
        """

            Produce hex color between red and green

        :param numlist: A list of RGB values
        :return: A list of hex value between R and G with B = 0

        """

        # rgbs = [[int((1 - num) * 255), int(num * 255), 0] for num in numlist]
        # rgbs = [[int((1 - num) * 255)*0.5, 120, int(num * 255)*0.5] for num in numlist]
        numlist = [0 if i < 0 else i for i in numlist]
        rgbs = [[int(num * 13), 0, int(num * 255)] for num in numlist]
        resultlist = []
        resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]
        # for rgb in rgbs:
        #    result = '#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2])
        #    resultlist.append(result)

        return resultlist

    def __interPolation(self):
        """

            Usc scipy regulargrid interpolation method feed with all maps info

        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: A interpolation function

        """

        # mapdata = self.map.getMap()
        mapdata = self.map.data
        tmpmapdata = np.swapaxes(mapdata, 0, 2)
        clim, blim, alim = mapdata.shape
        x = range(alim)
        y = range(blim)
        z = range(clim)
        myinter = RegularGridInterpolator((x, y, z), tmpmapdata)

        return myinter

    # version 1 by using TEMPy
    def __interthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.models, list):
            models = self.models
        else:
            models.append(self.models)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        mapsig = map.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]

            atomcount = 0
            chaincount = 1
            chainatoms = 0
            chainaiscore = {}
            chainai = 0.

            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                aiprechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                for atom in model:
                    atomcount += 1
                    # if 'H' not in atom.atom_name:
                    onecoor = [atom.x, atom.y, atom.z]
                    oneindex = self.__getindices(onecoor)[1]
                    if oneindex[0] > map.x_size() - 1 or oneindex[0] < 0 or \
                            oneindex[1] > map.y_size() - 1 or oneindex[1] < 0 or \
                            oneindex[2] > map.z_size() - 1 or oneindex[2] < 0:
                        curinterpolation = map.min()
                        atomoutsidenum += 1
                    else:
                        curinterpolation = myinter(oneindex).tolist()[0]
                    interpolations.append(curinterpolation)
                    atominterbin = 1 if curinterpolation > contour else 0
                    if (rescount == 0) or (atom.res_no == preresid and atom.chain == prechain):
                        sumatominterbin += atominterbin
                        rescount += 1
                        preresid = atom.res_no
                        prechain = atom.chain
                        preres = atom.res

                    else:
                        keystr = prechain + ':' + str(preresid) + preres
                        allkeys.append(keystr)
                        # value = float(sumatominterbin)/rescount
                        value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                        allvalues.append(value)
                        sumatominterbin = atominterbin
                        preresid = atom.res_no
                        prechain = atom.chain
                        rescount = 1

                    # Add the chain based atom inclusion score
                    if (atomcount == 1) or (atom.chain == aiprechain):
                        chainatoms += 1
                        aiprechain = atom.chain
                        chainai += atominterbin
                    else:
                        aivalue = round(float(chainai) / chainatoms, 3)
                        aicolor = self.__floatohex([aivalue])[0]
                        # chainaiscore[prechain] = {'value': aivalue, 'color': aicolor}
                        # (Todo) For chain which have the same chain id non-protein part not included yet especially
                        # ligand bind to the protein ligand has the same chain id as the protein, then how to averge
                        # the ligand and the protein together need to take the numbers into account which also means
                        # need to add another value in the dictonary
                        # Need to properly canculated the average of one chain
                        if aiprechain in chainaiscore.keys():
                            # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                            pass
                        else:
                            chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor}

                        chainatoms = 1
                        chaincount += 1
                        chainai = atominterbin
                        aiprechain = atom.chain

                aivalue = round(float(chainai) / chainatoms, 3)
                aicolor = self.__floatohex([aivalue])[0]
                if aiprechain in chainaiscore.keys():
                    # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                    pass
                else:
                    chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor}
                keystr = aiprechain + ':' + str(preresid) + preres
                allkeys.append(keystr)
                value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                allvalues.append(value)
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                 atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict, chainaiscore, atomoutsidenum)

        return result

    # version 2 without using TEMPy for model loading which is working but not optimal for using biopython
    def __newinterthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.models, list):
            models = self.models
        else:
            models.append(self.models)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        # mapsig = map.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]

            atomcount = 0
            chaincount = 1
            chainatoms = 0
            chainaiscore = {}
            chainai = 0.

            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                aiprechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                for atom in model.get_atoms():
                    atomcount += 1
                    # if 'H' not in atom.atom_name:
                    # onecoor = [atom.x, atom.y, atom.z]
                    onecoor = atom.coord
                    oneindex = self.__getindices(onecoor)[1]
                    if oneindex[0] > map.header.nx - 1 or oneindex[0] < 0 or \
                            oneindex[1] > map.header.ny - 1 or oneindex[1] < 0 or \
                            oneindex[2] > map.header.nz - 1 or oneindex[2] < 0:
                        curinterpolation = map.min()
                        atomoutsidenum += 1
                    else:
                        curinterpolation = myinter(oneindex).tolist()[0]
                    interpolations.append(curinterpolation)
                    atominterbin = 1 if curinterpolation > contour else 0

                    if (rescount == 0) or (residue.id[1] == preresid and atom.full_id[2] == prechain):
                        sumatominterbin += atominterbin
                        rescount += 1
                        preresid = residue.id[1]
                        prechain = atom.full_id[2]
                        preres = residue.resname
                    else:
                        keystr = prechain + ':' + str(preresid) + preres
                        allkeys.append(keystr)
                        value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                        allvalues.append(value)
                        sumatominterbin = atominterbin
                        preresid = residue.id[1]
                        prechain = atom.full_id[2]
                        rescount = 1

                    # Add the chain based atom inclusion score
                    if (atomcount == 1) or (atom.full_id[2] == aiprechain):
                        chainatoms += 1
                        # aiprechain = atom.chain
                        aiprechain = atom.full_id[2]
                        chainai += atominterbin
                    else:
                        aivalue = round(float(chainai) / chainatoms, 3)
                        aicolor = self.__floatohex([aivalue])[0]
                        # chainaiscore[prechain] = {'value': aivalue, 'color': aicolor}
                        # (Todo) For chain which have the same chain id non-protein part not included yet especially
                        # ligand bind to the protein ligand has the same chain id as the protein, then how to averge
                        # the ligand and the protein together need to take the numbers into account which also means
                        # need to add another value in the dictonary
                        # Need to properly canculated the average of one chain
                        if aiprechain in chainaiscore.keys():
                            # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                            pass
                        else:
                            chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor}

                        chainatoms = 1
                        chaincount += 1
                        chainai = atominterbin
                        # aiprechain = atom.chain
                        aiprechain = atom.full_id[2]

                aivalue = round(float(chainai) / chainatoms, 3)
                aicolor = self.__floatohex([aivalue])[0]
                if aiprechain in chainaiscore.keys():
                    # chainaiscore[aiprechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                    pass
                else:
                    chainaiscore[aiprechain] = {'value': aivalue, 'color': aicolor}
                keystr = aiprechain + ':' + str(preresid) + preres
                allkeys.append(keystr)
                value = float('%.4f' % round((float(sumatominterbin) / rescount), 4))
                allvalues.append(value)
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                 atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict, chainaiscore, atomoutsidenum)

        return result

    # version 3 for optimal usage of biopython
    def __nnewinterthird(self):
        """

            Interpolate density value of one atom, if indices are on the same plane use nearest method
            otherwise use linear

        :param map: TEMPy map instance
        :param model: Structure instance from TEMPy package mmcif parser
        :return: List contains all density interpolations of atoms from model

        """

        myinter = self.__interPolation()
        # Might having multple models
        models = []
        if isinstance(self.models, list):
            models = self.models
        else:
            models.append(self.models)
        map = self.map
        contour = self.cl
        # Range of contour level values for scaler bar
        # Todo: Right now with fixed number of points on both sides of the recommended contour level, could improve to
        # Todo: generate a reasonable range surround the recommended contour level
        # Setting a smarter range between (contour-sig,contour, countour + sig)
        # mapsig = map.std()
        # mapsig = map.data.std()
        # contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # contourrange = np.concatenate((np.linspace(map.min(), contour, 3, endpoint=False), np.linspace(contour, map.max(), 3)), axis=None)
        # When running for EMDB keep it as a flexible range for onedep or other users only run it once for recommended
        # contour level:

        # if self.emdid:
        #     contourrange = np.concatenate((np.linspace(contour - float(1.5 * mapsig), contour, 3, endpoint=False),
        #                                    np.linspace(contour, contour + float(1.5 * mapsig), 4)), axis=None)
        # else:
        #     contourrange = np.asarray([contour])

        contourrange = np.asarray([contour])
        result = {}
        for model in models:
            allcontoursdict = OrderedDict()
            atomoutsidenum = 0
            modelname = model.filename.split('/')[-1]

            atomcount = 0
            chaincount = 1
            chainatoms = 0
            chainaiscore = {}
            chainai = 0.

            for contour in contourrange:
                interpolations = []
                allkeys = []
                allvalues = []
                preresid = 0
                prechain = ''
                aiprechain = ''
                preres = ''
                rescount = 0
                sumatominterbin = 0
                chainai_atomsno = {}
                for chain in model.get_chains():
                    chainatominterbin = 0
                    chain_atom_count = 0
                    chain_name = chain.id
                    for residue in chain.get_residues():
                        resatominterbin = 0
                        residue_atom_count = 0
                        residue_name = residue.resname
                        residue_no = residue.id[1]
                        for atom in residue.get_atoms():
                            # if 'H' not in atom.name:
                            atomcount += 1
                            residue_atom_count += 1
                            # chain_atom_count += 1
                            onecoor = atom.coord
                            oneindex = self.__getindices(onecoor)[1]
                            # if oneindex[0] > map.x_size() - 1 or oneindex[0] < 0 or \
                            #         oneindex[1] > map.y_size() - 1 or oneindex[1] < 0 or \
                            #         oneindex[2] > map.z_size() - 1 or oneindex[2] < 0:
                            if oneindex[0] > map.header.nx - 1 or oneindex[0] < 0 or \
                                    oneindex[1] > map.header.ny - 1 or oneindex[1] < 0 or \
                                    oneindex[2] > map.header.nz - 1 or oneindex[2] < 0:
                                # curinterpolation = map.min()
                                curinterpolation = map.data.min()
                                atomoutsidenum += 1
                            else:
                                curinterpolation = myinter(oneindex).tolist()[0]
                            interpolations.append(curinterpolation)
                            atominterbin = 1 if curinterpolation > contour else 0
                            resatominterbin += atominterbin
                            if 'H' not in atom.name:
                                chainatominterbin += atominterbin
                                chain_atom_count += 1
                            sumatominterbin += atominterbin

                        # residue inclusion section
                        keystr = chain_name + ':' + str(residue_no) + residue_name
                        allkeys.append(keystr)
                        value = float('%.4f' % round((float(resatominterbin) / residue_atom_count), 4))
                        allvalues.append(value)

                    # chain inclusion section
                    if chain_name in chainai_atomsno.keys():
                        chainatominterbin += chainai_atomsno[chain_name]['value']
                        chain_atom_count += chainai_atomsno[chain_name]['atomsinchain']
                    chainai_atomsno[chain_name] = {'value': chainatominterbin, 'atomsinchain': chain_atom_count}

                for chainname, chain_scores in chainai_atomsno.items():
                    chain_ai = float('%.4f' % round((float(chain_scores['value']) / chain_scores['atomsinchain']), 4))
                    aicolor = self.__floatohex([chain_ai])[0]
                    chainaiscore[chainname] = {'value': chain_ai, 'color': aicolor}
                allcontoursdict[str(contour)] = (allkeys, allvalues)
                print('Model: %s at contour level %s has %s atoms stick out of the density.' % (modelname, contour,
                                                                                                atomoutsidenum))

            # result[modelname] = (interpolations, allkeys, allvalues)
            # result: {modelname #1: (interpolations #1, {contour1: (allkeys, allvalues), contour2: (allkeys, allvalues)
            # ...}), modelname #2: (interpolations #2, {contour1: (allkeys, allvalues),...}),...}
            result[modelname] = (interpolations, allcontoursdict, chainaiscore, atomoutsidenum)

        return result


    def map_matrix(self, apixs, angs):
        """

            calculate the matrix to transform Cartesian coordinates to fractional coordinates
            (check the definination to see the matrix formular)

        :param apixs: array of apix lenght
        :param angs: array of anglex in alpha, beta, gamma order
        :return:
        """

        ang = (angs[0]*math.pi/180, angs[1]*math.pi/180, angs[2]*math.pi/180)
        insidesqrt = 1 + 2 * math.cos(ang[0]) * math.cos(ang[1]) * math.cos(ang[2]) - \
                     math.cos(ang[0])**2 - \
                     math.cos(ang[1])**2 - \
                     math.cos(ang[2])**2

        cellvolume = apixs[0]*apixs[1]*apixs[2]*math.sqrt(insidesqrt)

        m11 = 1/apixs[0]
        m12 = -math.cos(ang[2])/(apixs[0]*math.sin(ang[2]))

        m13 = apixs[1] * apixs[2] * (math.cos(ang[0]) * math.cos(ang[2]) - math.cos(ang[1])) / (cellvolume * math.sin(ang[2]))
        m21 = 0
        m22 = 1 / (apixs[1] * math.sin(ang[2]))
        m23 = apixs[0] * apixs[2] * (math.cos(ang[1]) * math.cos(ang[2]) - math.cos(ang[0])) / (cellvolume * math.sin(ang[2]))
        m31 = 0
        m32 = 0
        m33 = apixs[0] * apixs[1] * math.sin(ang[2]) / cellvolume
        prematrix = [[m11, m12, m13], [m21, m22, m23], [m31, m32, m33]]
        matrix = np.asarray(prematrix)

        return matrix


    def matrix_indices(self, apixs, onecoor):
        """

            Method 2: using the fractional coordinate matrix to calculate the indices when the maps are non-orthogonal

        :return:
        """

        # Method 2: by using the fractional coordinate matrix
        # Chosen as the main function for the current implementation

        # Figure out the order of the x, y, z based on crs info in the header
        # crs = list(self.map.header[16:19])
        crs = [self.map.header.mapc, self.map.header.mapr, self.map.header.maps]
        # ordinds save the indices correspoding to x, y ,z
        ordinds = [crs.index(1), crs.index(2), crs.index(3)]
        # angs = self.map.header[13:16]
        angs = [self.map.header.cellb.alpha, self.map.header.cellb.beta, self.map.header.cellb.gamma]
        matrix = self.map_matrix(apixs, angs)
        result = matrix.dot(np.asarray(onecoor))
        # xindex = result[0] - self.map.header[4 + ordinds[0]]
        # yindex = result[1] - self.map.header[4 + ordinds[1]]
        # zindex = result[2] - self.map.header[4 + ordinds[2]]
        xindex = result[0] - self.map.header.nxstart
        yindex = result[1] - self.map.header.nystart
        zindex = result[2] - self.map.header.nzstart

        return (xindex, yindex, zindex)


    def projection_indices(self, onecoor):
        """

            Method 1: using the projection way to calculate the indices when the maps are non-orthogonal

        :return: tumple which contains all three float new indices in (x, y, z) order
        """

        map = self.map
        zdim = map.header[12]
        znintervals = map.header[9]
        z_apix = zdim / znintervals

        ydim = map.header[11]
        ynintervals = map.header[8]
        y_apix = ydim / ynintervals

        xdim = map.header[10]
        xnintervals = map.header[7]
        x_apix = xdim / xnintervals

        theta = (map.header[13] / 90) * (math.pi / 2)
        beta = (map.header[14] / 90) * (math.pi / 2)
        gamma = (map.header[15] / 90) * (math.pi / 2)

        insidesqrt = 1 + 2 * math.cos(theta) * math.cos(beta) * math.cos(gamma) - \
                     math.cos(theta) * math.cos(theta) - \
                     math.cos(beta) * math.cos(beta) - \
                     math.cos(gamma) * math.cos(gamma)

        cellvolume = x_apix * y_apix * z_apix * math.sqrt(insidesqrt)

        cellheightz = cellvolume / (x_apix * y_apix * math.sin(gamma))
        cellheighty = cellvolume / (x_apix * z_apix * math.sin(beta))
        cellheightx = cellvolume / (z_apix * y_apix * math.sin(theta))

        # Figure out the order of the x, y, z based on crs info in the header
        crs = list(map.header[16:19])
        # ordinds save the indices correspoding to x, y ,z
        ordinds = [crs.index(1), crs.index(2), crs.index(3)]

        # Trying to move the atom coordinate which has not work yet

        # move the coordinate according to move of the map
        # x: c*cos(gamma) + b + a*cos(beta)
        # y: c*sin(gamma) + sqrt(a**2 - (a*cos(beta))**2 - cellhz**2)
        # z: hz
        # a = math.fabs(map.header[4 + ordinds[2]]*z_apix)
        # b = math.fabs(map.header[4 + ordinds[0]]*x_apix)
        # c = math.fabs(map.header[4 + ordinds[1]]*y_apix)
        # # for 8720 seems correct
        # # xshift = c*math.cos(gamma) + b - a*math.cos(beta)
        # # yshift = c*math.sin(gamma)
        # # zshift = (-1)*map.header[4 + ordinds[2]]*cellheightz
        # for 8765 correct
        # xshift = c*math.cos(gamma) + b - a*math.cos(beta)
        # yshift = c*math.sin(gamma)
        # zshift = (-1)*map.header[4 + ordinds[2]]*cellheightz
        # print('---shift---')
        # print(xshift)
        # print(yshift)
        # print(zshift)
        # print(c*math.sin(gamma))
        # print(c)
        # print(math.radians(gamma))
        # print(gamma)
        # print(c*math.cos(gamma))
        # print(b)
        # print(a*math.cos(beta))
        # print(map.header[4 + ordinds[2]])

        # Mehtod 1: Calculateing the distances from the atom to different planes(x'y', x'z', y'z') and divided by
        # The unit cell height(calculated by using unit cell volume divided by the plane surface area) to get the
        # indices, then deduct the origin index which give the final results. When calculating the sign of the
        # distance, find a plane parallel to the projection plane and it pass through the atom, the cutoff of this
        # plane and the correspoding axis give the location of the atom projection cutoff at the axis
        # (this should also be able to used to calculate the final indices(not tried)). If this point is outside
        # the normal cell dimension range, then the distance should be negative and vice verse
        relativex = onecoor[0] - map.header[49]
        relativey = onecoor[1] - map.header[50]
        relativez = onecoor[2] - map.header[51]

        # Z index by using the relativez / cellheightz
        zind = relativez / cellheightz
        zindex = zind - map.header[4 + ordinds[2]]

        # X index by calculating the plane first and then calculate the distance from atom to plane
        # Plane x'z'
        # Ax + By + Cz + D = 0 with three data points: (0, 0, 0), (b, 0, 0),
        # (a*cos(alpha), sqrt(a**2 - (celllhz)**2 - (a*cos(alpha)**2), cellhz), x' unit cell length is b, alpha is
        # the angle between x' and z'(which are the cell axes)
        # By using these three points the plane of x'z' can be calculated
        # A=0, B=cellhz, C = -sqrt(a**2 - (cellhz)**2 - (a*cos(alpha))**2), D=0
        A = 0
        B = cellheightz
        C = -math.sqrt(z_apix ** 2 - cellheightz ** 2 - (z_apix * math.cos(beta)) ** 2)
        D = 0

        # distance from atom to x'z' plane:
        #         |Ax + By + Cz + D|
        # d = -----------------------------
        #       sqrt(A**2 + B**2 + C**2)
        dy = math.fabs(B * relativey + C * relativez) / math.sqrt(A ** 2 + B ** 2 + C ** 2)

        # The parallel plan which pass the atom and intersect with the x is:
        # Ax) + B(y + a) + Cz + D = 0
        # a = -(Ax + By + Cz + D)/A
        # xcut = -a
        ycut = -(A * onecoor[0] + onecoor[1] + (C / B) * onecoor[2])
        ycut = -ycut
        if ycut < 0 or ycut > map.header[0 + ordinds[1]] * y_apix * math.sin(gamma):
            dy = -dy

        yind = dy / cellheighty
        yindex = yind - map.header[4 + ordinds[1]]

        # Plane z'y'
        # Ax + By + Cz + D = 0 with three data points: (0, 0, 0), (a*cos(alpha),
        # sqrt(a**2 - (cellhz)**2 - (a*cos(alpha)**2), cellhz),
        # (d*cos(gamma), d*sin(gamma), 0)
        # beta is the angle between x' and z'; gamma is the angle between x' and y'; d is the cell unit length
        # along y'
        # Using these three points a plane can be calculated
        # A=-tg(beta), B = 1, D=0,
        #      a*cos(alpha)*tg(beta) - t
        # C = --------------------------- ,     t = sqrt(a**2 - (cellhz)**2 - (a*cos(alpha))**2)
        #            cellhz
        # A = -math.tan(gamma)
        # B = 1
        # D = 0
        # t = math.sqrt(z_apix**2 - cellheightz**2 - (z_apix*math.cos(beta))**2)
        # C = (z_apix * math.cos(beta)*math.tan(gamma) - t) / cellheightz

        if map.header[15] == 90.:
            singamma = 1.
            cosgamma = 0.
        else:
            singamma = math.sin(gamma)
            cosgamma = math.cos(gamma)

        if map.header[14] == 90.:
            singbeta = 1.
            cosbeta = 0.
        else:
            sinbeta = math.sin(beta)
            cosbeta = math.cos(beta)

        A = -singamma
        B = cosgamma
        D = 0
        t = math.sqrt(z_apix ** 2 - cellheightz ** 2 - (z_apix * cosbeta) ** 2)
        C = (z_apix * cosbeta * singamma - t * cosgamma) / cellheightz

        # distance from atom to z'y' plane:
        #         |Ax + By + Cz + D|
        # d = -----------------------------
        #       sqrt(A**2 + B**2 + C**2)
        dx = math.fabs(A * relativex + B * relativey + C * relativez) / math.sqrt(A ** 2 + B ** 2 + C ** 2)
        xcut = (-(onecoor[0] + (B / A) * onecoor[1] + (C / A) * onecoor[2]))
        xcut = -xcut
        if xcut < 0 or xcut > map.header[0 + ordinds[0]] * x_apix:
            dx = -dx
        xind = dx / cellheightx
        xindex = xind - map.header[4 + ordinds[0]]


        return(xindex, yindex, zindex)


    def __getindices(self, onecoor):
        """

            Find one atom's indices correspoding to its cubic or plane
            the 8 (cubic) or 4 (plane) indices are saved in indices variable

        :param map: Density map instance from TEMPy.MapParser
        :param onecoor: List contains the atom coordinates in (x, y, z) order
        :return: Tuple contains two list of index: first has the 8 or 4 indices in the cubic;
                 second has the float index of the input atom

        """

        # For non-cubic or skewed density maps, they might have different apix on different axises
        map = self.map
        # zdim = map.header[12]
        # znintervals = map.header[9]
        zdim = map.header.cella.z
        znintervals = map.header.mz
        z_apix = zdim / znintervals

        # ydim = map.header[11]
        # ynintervals = map.header[8]
        ydim = map.header.cella.y
        ynintervals = map.header.my
        y_apix = ydim / ynintervals

        # xdim = map.header[10]
        # xnintervals = map.header[7]
        xdim = map.header.cella.x
        xnintervals = map.header.mx
        x_apix = xdim / xnintervals

        map_zsize = map.header.nz
        map_ysize = map.header.ny
        map_xsize = map.header.nx

        # if map.header[13] == map.header[14] == map.header[15] == 90.:
        if map.header.cellb.alpha == map.header.cellb.beta == map.header.cellb.gamma == 90.:
            # Figure out the order of the x, y, z based on crs info in the header
            # crs = list(map.header[16:19])
            crs = [map.header.mapc, map.header.mapr, map.header.maps]
            # ordinds save the indices correspoding to x, y ,z
            ordinds = [crs.index(1), crs.index(2), crs.index(3)]

            # zindex = float(onecoor[2] - map.header[51]) / z_apix - map.header[4 + ordinds[2]]
            # yindex = float(onecoor[1] - map.header[50]) / y_apix - map.header[4 + ordinds[1]]
            # xindex = float(onecoor[0] - map.header[49]) / x_apix - map.header[4 + ordinds[0]]
            zindex = float(onecoor[2] - map.header.origin.z) / z_apix - map.header.nzstart
            yindex = float(onecoor[1] - map.header.origin.y) / y_apix - map.header.nystart
            xindex = float(onecoor[0] - map.header.origin.x) / x_apix - map.header.nxstart

            zfloor = int(floor(zindex))
            # if zfloor >= map.z_size() - 1:
            if zfloor >= map_zsize - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(floor(yindex))
            # if yfloor >= map.y_size() - 1:
            if yfloor >= map_ysize - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(floor(xindex))
            # if xfloor >= map.x_size() - 1:
            if xfloor >= map_xsize - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1
        else:
            # Method 2: by using the fractional coordinate matrix
            # Chosen as the primary for the current implementation
            apixs = [x_apix, y_apix, z_apix]
            # Method 1: by using the atom projection on planes
            # xindex, yindex, zindex = self.projection_indices(onecoor))
            xindex, yindex, zindex = self.matrix_indices(apixs, onecoor)

            zfloor = int(floor(zindex))
            # if zfloor >= map.z_size() - 1:
            if zfloor >= map_zsize - 1:
                zceil = zfloor
            else:
                zceil = zfloor + 1

            yfloor = int(floor(yindex))
            # if yfloor >= map.y_size() - 1:
            if yfloor >= map_ysize - 1:
                yceil = yfloor
            else:
                yceil = yfloor + 1

            xfloor = int(floor(xindex))
            # if xfloor >= map.x_size() - 1:
            if xfloor >= map_xsize - 1:
                xceil = xfloor
            else:
                xceil = xfloor + 1

        indices = np.array(np.meshgrid(np.arange(xfloor, xceil + 1), np.arange(yfloor, yceil + 1),
                                       np.arange(zfloor, zceil + 1))).T.reshape(-1, 3)
        oneindex = [xindex, yindex, zindex]

        return (indices, oneindex)


    def __getfractions(self, interpolation, model):
        """

            Produce atom inclusion fraction information for full atoms and backbone trace

        :param interpolation: List of interpolation values
        :param map: Electron density map in mrc/map format
        :param model: Protein model in mmcif format
        :return: Tuple contains full atom inclusion fractions and backbone inclusion fractions

        """

        map = self.map
        # bins = np.linspace(map.min(), map.max(), 129)
        bins = np.linspace(map.data.min(), map.data.max(), 129)
        binlist = bins.tolist()
        bisect.insort(binlist, self.cl)
        clindex = binlist.index(self.cl)
        binlist.pop(clindex - 1)
        bins = np.asarray(binlist)

        newinterpolation = []
        for i in range(len(interpolation)):
            # if 'H' not in model[i].atom_name:
            if 'H' not in model[i].fullname:
                newinterpolation.append(interpolation[i])

        # Whole model average atom inlcusion
        entire_average = sum(np.asarray(newinterpolation) > self.cl) / float(len(newinterpolation))

        # Full atom inclusion
        a = []
        templist = np.asarray(newinterpolation)
        for i in bins:
            x = sum(templist > i) / float(len(templist))
            a.append(x)

        traceinter = []
        for i in range(len(interpolation)):
            # if (model[i].atom_name == 'N' or model[i].atom_name == 'C' or model[i].atom_name == 'O' or
            #         model[i].atom_name == 'CA' or model[i].atom_name == "C3'" or model[i].atom_name == "C4'" or
            #         model[i].atom_name == "C5'" or model[i].atom_name == "O3'" or model[i].atom_name == "O5'" or
            #         model[i].atom_name == 'P' or model[i].atom_name == 'OXT'):
            #     traceinter.append(interpolation[i])
            if (model[i].fullname == 'N' or model[i].fullname == 'C' or model[i].fullname == 'O' or
                    model[i].fullname == 'CA' or model[i].fullname == "C3'" or model[i].fullname == "C4'" or
                    model[i].fullname == "C5'" or model[i].fullname == "O3'" or model[i].fullname == "O5'" or
                    model[i].fullname == 'P' or model[i].fullname == 'OXT'):
                traceinter.append(interpolation[i])

        # Backbone inclusion
        b = []
        temptraceinter = np.asarray(traceinter)
        for j in bins:
            y = sum(temptraceinter > j) / float(len(temptraceinter))
            b.append(y)

        return a, b, entire_average

    # @profile
    def atom_inclusion(self):
        """

            Generate atom inclusion and residue atom inclusion information verses different contour level
            Both full atoms and backbone information are included.
            Results wrote to JSON file

        :return: None

        """
        if self.models is None:
            # print('REMINDER: atom inclusion and residue inclusion will not be calculated without model structure.',
            #       file=sys.stderr)
            sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated without '
                             'model structure.\n')
            print('------------------------------------')
        elif self.cl is None:
            # print('REMINDER: atom inclusion and residue inclusion will not be calculated without contour level given '
            #       'by "-cl".', file=sys.stderr)
            sys.stderr.write('REMINDER: atom inclusion and residue inclusion will not be calculated '
                             'without contour level given.\n')
            print('------------------------------------')
        else:
            start = timeit.default_timer()
            map = self.map

            # modelnames = [ model.filename for model in self.models ]
            # version 1 use tempy
            # combinresult = self.__interthird()
            # version 2 use biopython but not optmised for biopython
            # combinresult = self.__newinterthird()
            # version 3 use biopython need more tests and then delete the other two above
            combinresult = self.__nnewinterthird()
            atomindict = OrderedDict()
            resindict = OrderedDict()
            datadict = OrderedDict()
            resdict = OrderedDict()
            counter = 0
            errlist = []
            reserrlist = []
            for key, value in combinresult.items():
                try:
                    # interpolations, allkeys, allvalues = self.__interthird()
                    # interpolations, allkeys, allvalues = value
                    interpolations, allcontoursdict, chainaiscore, atomoutsidebox = value
                    if isinstance(self.models, list):
                        models = [curmodel for curmodel in self.models if key in curmodel.filename]
                    else:
                        models = list()
                        models.append(self.models)

                    if len(models) == 1:
                        model = models[0]
                    elif len(models) == 0:
                        print('There is no model!')
                        exit()
                    else:
                        print('There are more than one model which should be only one.')
                        exit()

                    allatoms = list(model.get_atoms())
                    # result = self.__getfractions(interpolations, model)
                    result = self.__getfractions(interpolations, allatoms)
                    # levels = np.linspace(map.min(), map.max(), 129)
                    levels = np.linspace(map.data.min(), map.data.max(), 129)

                    binlist = levels.tolist()
                    bisect.insort(binlist, self.cl)
                    clindex = binlist.index(self.cl)
                    binlist.pop(clindex - 1)
                    levels = np.asarray(binlist)

                    datadict[str(counter)] = {'name': key, 'level': [round(elem, 6) for elem in levels.tolist()],
                                              'all_atom': [round(elem, 6) for elem in result[0]],
                                              'backbone': [round(elem, 6) for elem in result[1]],
                                              'atomoutside': atomoutsidebox,
                                              'chainaiscore': chainaiscore,
                                              'average_ai_model': round(result[2], 6)
                                              }

                    data_len = len(levels.tolist())
                    plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[0]], '-g', label='Full atom')
                    plt.plot([round(elem, 10) for elem in levels.tolist()], [round(elem, 10) for elem in result[1]], '-b', label='Backbone')
                    plt.plot(data_len * [self.cl], np.linspace(0, 1, data_len), '-r', label='Recommended contour level')
                    plt.legend(loc='lower left')
                    plt.savefig(self.workdir + self.mapname + '_inclusion.png')
                    # exit()
                except:
                    err = 'Atom inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
                if errlist:
                    datadict[str(counter)] = {'err': {'atom_inclusion_err': errlist}}

                contourdict = OrderedDict()
                try:
                    for contour, keysvalues in allcontoursdict.items():
                        allvalues = keysvalues[1]
                        allkeys = keysvalues[0]
                        colours = self.__floatohex(allvalues)
                        contourkey = str(round(float(contour), 6))
                        contourdict[contourkey] = OrderedDict([('color', colours), ('inclusion', allvalues),
                                                               ('residue', allkeys)])

                    contourdict['name'] = key
                    resdict[str(counter)] = contourdict
                except:
                    err = 'Residue inclusion calculation error(Model: {}): {}.'.format(key, sys.exc_info()[1])
                    reserrlist.append(err)
                    sys.stderr.write(err + '\n')
                if reserrlist:
                    resdict[str(counter)] = {'err': {'residue_inclusion_err': reserrlist}}
                counter += 1

            # datadict['err'] = {'atom_inclusion_err': errlist}
            atomindict['atom_inclusion_by_level'] = datadict
            # resdict['err'] = {'residue_inclusion_err': errlist}
            resindict['residue_inclusion'] = resdict

            try:
                with codecs.open(self.workdir + self.mapname + '_atom_inclusion.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(atomindict, f)
            except:
                sys.stderr.write('Saving to atom inclusion json error: {}.\n'.format(sys.exc_info()[1]))

            try:
                with codecs.open(self.workdir + self.mapname + '_residue_inclusion.json', 'w',
                                 encoding='utf-8') as f1:
                    json.dump(resindict, f1)
            except:
                sys.stderr.write('Saving to residue inclusion json error: {}.\n'.format(sys.exc_info()[1]))



            end = timeit.default_timer()
            print('Inclusion time: %s' % (end - start))
            print('------------------------------------')
        return None

    # Volumecontour

    # @profile
    def volumecontour(self):
        """

            Generate Volume versus contour level plot.
            Result wrote to a JSON file.
            View indices as siting on the central of each voxel, no interpolation needed.

        :return: None

        """

        start = timeit.default_timer()
        map = self.map
        # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
        # check functionn frommrc_totempy in preparation.py
        # apix = map.apix
        apix = map.voxel_size.tolist()
        # mapdata = map.getMap()
        mapdata = map.data
        errlist = []
        datadict = dict()
        try:
            bins = np.linspace(mapdata.min(), mapdata.max(), 129)
            hist, bin_edges = np.histogram(mapdata, bins=bins)
            mapsize = map.header.nx * map.header.ny * map.header.nz
            # preresult = map.map_size() - np.cumsum(hist)
            # addedpre = np.insert(preresult, 0, map.map_size())
            preresult = mapsize - np.cumsum(hist)
            addedpre = np.insert(preresult, 0, mapsize)
            # Todo: for non-orthogonal volume this is not the right formula
            # It needs the formula : abc* sqrt(1 + 2*cos(a)*cos(b)*bos(c) - cos(a)**2 - cos(b)**2 - cos(c)**2)
            if type(apix) is tuple:
                basevolume = ((apix[0]*apix[1]*apix[2]) / (10 ** 3))
            else:
                basevolume = ((apix**3) / (10**3))
            tmpresult = addedpre * basevolume
            if self.cl:
                clvolume = (mapdata >= self.cl).sum()
                estvolume = round(clvolume * basevolume, 2)
            else:
                estvolume = None

            if estvolume:
                datadict = {
                    'volume_estimate': {'volume': np.round(tmpresult, 10).tolist(),
                                        'level': np.round(bins, 10).tolist(),
                                        'estvolume': estvolume}}
            else:
                datadict = {
                    'volume_estimate': {'volume': np.round(tmpresult, 10).tolist(),
                                        'level': np.round(bins, 10).tolist()}}
        except:
            err = 'Volume estimate calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        if errlist:
            datadict = {'volume_estimate': {'err': {'volume_estimate_error': errlist}}}
        try:
            with codecs.open(self.workdir + self.mapname + '_volume_contour.json', 'w',
                             encoding='utf-8') as f:
                json.dump(datadict, f)
        except:
            sys.stderr.write('Saving volume estimate to json error:{}.\n'.format(sys.exc_info()[1]))

        end = timeit.default_timer()
        print('Volume contour time: %s' % (end - start))
        print('------------------------------------')

        return None





    ################### test

    # def pssum(self,i, dist, indiaxis):
    #     if i != len(indiaxis) - 1:
    #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
    #         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
    #         return psum

    # def pssum(self,indices):
    #     # if i != len(indiaxis) - 1:
    #     # indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
    #     psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
    #     return psum


    def pararaps(self):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """
        import multiprocessing as mp
        import itertools
        threadcount = 2
        pool = mp.Pool(threadcount)

        if self.map.x_size() == self.map.y_size() == self.map.z_size():
            errlist = []
            start = timeit.default_timer()
            map = self.map
            apix = map.apix
            fftmap = map.fourier_transform()
            psmap = fftmap.copy()
            psmean = np.mean(psmap.fullMap)
            psstd = np.std(psmap.fullMap)
            psmap.fullMap = np.abs((psmap.fullMap - psmean) / psstd) ** 2

            midstart = timeit.default_timer() - start
            print(' -- RAPS Fourier-transformation time: %s' % midstart)

            zgrid = np.arange(floor(psmap.z_size() / 2.0) * -1, ceil(psmap.z_size() / 2.0)) / float(floor(psmap.z_size()))
            ygrid = np.arange(floor(psmap.y_size() / 2.0) * -1, ceil(psmap.y_size() / 2.0)) / float(floor(psmap.y_size()))
            xgrid = np.arange(floor(psmap.x_size() / 2.0) * -1, ceil(psmap.x_size() / 2.0)) / float(floor(psmap.x_size()))
            xdis = xgrid ** 2
            ydis = ygrid ** 2
            zdis = zgrid ** 2
            dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

            allaxis = [zgrid, ygrid, xgrid]
            tmpindiaxis = max(allaxis, key=len)
            indiaxist = tmpindiaxis[tmpindiaxis >= 0]
            indiaxis = np.linspace(0, 1 / (2 * apix), len(indiaxist))
            print('dist:')
            print(allaxis)
            print(dist.shape)
            print(indiaxis)
            print(psmap.z_size())
            print('-------')
            print(dist[98,96,96])


            aps = []
            # for i in range(len(indiaxis)):
            #     if i != len(indiaxis) - 1:
            #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
            #         psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
            #         aps.append(psum)

            allindices = []
            allpsmap = []
            # for i in range(len(indiaxis)):
            #     if i != len(indiaxis) -1:
            #         indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
            #
            #         psum = psmap.fullMap[tuple(indices.T)].sum()
            #         allindices.append(indices)
            #         allpsmap.append(psum)
            # print(allindices)
            odd = []
            even =[]
            counter = 0
            rlist = []
            templist = []
            for i in range(len(indiaxis)-1):
                counter += 1
                if i == 0:
                    templist.append(i)
                elif i % 40 == 0:
                    rlist.append(templist)
                    templist = []
                    templist.append(i)
                else:
                    templist.append(i)

            rlist.append(templist)

            def split_list(inp_list, nr):
                """
                Splits evenly a list
                :param inp_list: list
                :param nr: number of parts
                :return: list of "nr" lists
                """
                new_list = []
                nr_el = 1.0 / nr * len(inp_list)
                for i in range(nr):
                    start = int(round(i * nr_el))
                    end = int(round((i + 1) * nr_el))
                    new_list.append(inp_list[start:end])
                return new_list
            inputlist = range(0, len(indiaxis)-1)
            rlist = split_list(inputlist, threadcount)

            # Try with shared object
            import multiprocessing
            import ctypes
            x, y, z = dist.shape

            shared_array_base = multiprocessing.Array(ctypes.c_double, x*y*z)
            # shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
            shared_array = np.frombuffer(shared_array_base.get_obj())
            shared_array = shared_array.reshape(dist.shape)



            shared_array[:] = dist[:]
            # aps = [pool.apply(pcal, args=(i, allindices, allpsmap)) for i in rlist]
            aps = [pool.apply(pssum, args=(i, indiaxis, indiaxist, shared_array)) for i in rlist]
            # aps = aps[:-1]
            # aps = pool.map(self.pssum, [ i for i in allindices])
            newaps = list(itertools.chain.from_iterable(aps))
            # print(len(newaps))

            for i in range(len(indiaxis)-1):
                if i != len(indiaxis) -1:
                    psum = log10(psmap.fullMap[tuple(newaps[i].T)].sum() / len(newaps[i]))
                    allpsmap.append(psum)

            print(allpsmap)

            ##################

            datadict = {'rotationally_averaged_power_spectrum': {'y': np.round(allpsmap, 4).tolist(),
                                                                 'x': np.round(indiaxis[:-1], 4).tolist()}}
            err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            datadict = {'rotationally_averaged_power_spectrum': {'err': {'raps_err': errlist}}}
            sys.stderr.write(err + '\n')

            if bool(datadict):
                try:
                    with codecs.open(self.workdir + self.mapname + '_raps.json', 'w', encoding='utf-8') as f:
                        json.dump(datadict, f)
                except:
                    sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
            else:
                sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

            end = timeit.default_timer()
            print('RAPS time: %s' % (end - start))
            print('------------------------------------')
        else:
            print('No RAPS calculation for non-cubic map.')
            print('------------------------------------')


        return None

    # @profile
    def rawmap_raps(self):

        rawmap = self.rawmap
        if rawmap is not None:
            dir = self.workdir
            label = 'rawmap_'
            # self.raps(rawmap, dir, label)
            self.new_raps(rawmap, dir, label)
        else:
            print('No raw map to calculate RAPS.')

        return None

    #@profile
    def fourier_transform(self, mapdata):


        new_mapdata = fftshift(fftn(mapdata))
        return new_mapdata

    #@profile
    def raps(self, mapin=None, workdir=None, label=''):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """

        map, workdir = self.mapincheck(mapin, workdir)
        mapname = os.path.basename(map.fullname)

        map_zsize = map.header.nz
        map_ysize = map.header.ny
        map_xsize = map.header.nx

        apix_list = map.voxel_size.tolist()
        apixs = (apix_list[0], apix_list[1], apix_list[2])

        if map is not None and workdir is not None:
            # if map.x_size() == map.y_size() == map.z_size():
            if map.header.nx == map.header.ny == map.header.nz:
                errlist = []
                start = timeit.default_timer()
                datadict = dict()
                try:
                    # map = self.map
                    # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
                    # if type(map.apix) is tuple:
                    if type(apixs) is tuple:
                        # apix = map.apix[0]
                        apix = apixs[0]
                    else:
                        # apix = map.apix
                        apix = apixs
                    # fftmap = map.fourier_transform()
                    fftmap = fftshift(fftn(map.data))
                    # psmap = fftmap.copy()
                    # psmean = np.mean(psmap.fullMap)
                    # psstd = np.std(psmap.fullMap)
                    # psmap.fullMap = np.abs((psmap.fullMap - psmean) / psstd) ** 2
                    psmean = np.mean(fftmap)
                    psstd = np.std(fftmap)
                    fftmap = np.abs((fftmap - psmean) / psstd) ** 2

                    midstart = timeit.default_timer() - start
                    print(' -- RAPS Fourier-transformation time: %s' % midstart)

                    # zgrid = np.arange(floor(psmap.z_size() / 2.0) * -1, ceil(psmap.z_size() / 2.0)) / float(floor(psmap.z_size()))
                    # ygrid = np.arange(floor(psmap.y_size() / 2.0) * -1, ceil(psmap.y_size() / 2.0)) / float(floor(psmap.y_size()))
                    # xgrid = np.arange(floor(psmap.x_size() / 2.0) * -1, ceil(psmap.x_size() / 2.0)) / float(floor(psmap.x_size()))
                    zgrid = np.arange(floor(map_zsize / 2.0) * -1, ceil(map_zsize / 2.0)) / float(floor(map_zsize))
                    ygrid = np.arange(floor(map_ysize / 2.0) * -1, ceil(map_ysize / 2.0)) / float(floor(map_ysize))
                    xgrid = np.arange(floor(map_xsize / 2.0) * -1, ceil(map_xsize / 2.0)) / float(floor(map_xsize))
                    # zgrid = np.arange(floor(psmap.z_size()*2 / 2.0) * -1, ceil(psmap.z_size()*2 / 2.0)) / float(floor(psmap.z_size()))
                    # ygrid = np.arange(floor(psmap.y_size()*2 / 2.0) * -1, ceil(psmap.y_size()*2 / 2.0)) / float(floor(psmap.y_size()))
                    # xgrid = np.arange(floor(psmap.x_size()*2 / 2.0) * -1, ceil(psmap.x_size()*2 / 2.0)) / float(floor(psmap.x_size()))
                    xdis = xgrid ** 2
                    ydis = ygrid ** 2
                    zdis = zgrid ** 2
                    dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

                    allaxis = [zgrid, ygrid, xgrid]
                    tmpindiaxis = max(allaxis, key=len)
                    indiaxist = tmpindiaxis[tmpindiaxis >= 0]
                    # indiaxist = np.arange(0, np.amax(tmpindiaxis),0.0104 )
                    # indiaxist = np.linspace(0, np.amax(tmpindiaxis), 200 )
                    indiaxis = np.linspace(0, 1 / (2 * apix), len(indiaxist))

                    aps = []
                    for i in range(len(indiaxis)):
                        if i == 0:
                            indices = np.argwhere(dist == indiaxist[i])
                            # psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                            psum = log10(fftmap[tuple(indices.T)].sum() / len(indices))
                            aps.append(psum)
                        if i != len(indiaxis) - 1:
                            indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
                            # psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                            psum = log10(fftmap[tuple(indices.T)].sum() / len(indices))
                            aps.append(psum)
                        else:
                            pass
                            # indices = np.argwhere(dist == indiaxist[i])
                            # psum = log10(psmap.fullMap[tuple(indices.T)].sum() / len(indices))
                            # aps.append(psum)
                    print(aps)
                    if aps[0] < 0:
                        aps[0] = aps[1]
                    datadict = {label + 'rotationally_averaged_power_spectrum':  {'y': np.round(aps, 10).tolist(),
                                                                         'x': np.round(indiaxis, 10).tolist()}}
                    plt.plot(np.round(indiaxis, 4).tolist(), np.round(aps, 4).tolist())
                    plt.savefig(workdir + 'raps.png')

                except:
                    err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

                if errlist:
                    datadict = {'rotationally_averaged_power_spectrum': {'err': {'raps_err': errlist}}}

                if bool(datadict):
                    try:
                        with codecs.open(workdir + mapname + '_raps.json', 'w', encoding='utf-8') as f:
                            json.dump(datadict, f)
                    except:
                        sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
                else:
                    sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

                end = timeit.default_timer()
                print('RAPS time for %s: %s' % (mapname, end - start))
                print('------------------------------------')
            else:
                print('No RAPS calculation for non-cubic map.')
                print('------------------------------------')

                return None
        else:
            print('No RAPS without proper map input and the output directory information.')


    # Below Here is the test new raps function area

    def apply_3d_symmetry(self, inds, origin):
        O = origin
        operators = [[np.array([-1, 1, 1]), [O[0] * 2, 0, 0]],
                     [np.array([1, 1, -1]), [0, 0, O[2] * 2]],
                     # [np.array([1, -1, 1]), [0, O[1] * 2, 0]],
                     # [np.array([-1, -1, 1]), [O[0] * 2, O[1] * 2, 0]],
                     [np.array([-1, 1, -1]), [O[0] * 2, 0, O[2] * 2]],]
                     # [np.array([1, -1, -1]), [0, O[1] * 2, O[2] * 2]],
                     # [np.array([-1, -1, -1]), [O[0] * 2, O[1] * 2, O[2] * 2]]]
        ind = np.array(inds)
        res = np.array(inds)
        # w1 = np.where((ind[:, 1] == O[1]) | (ind[:, 0] == O[0]) | (ind[:, 2] == O[2]), True, False)
        # w1 = ind[w1, :]
        # w2 = np.where((ind[:, 1] != O[1]) | (ind[:, 0] != O[0]) | (ind[:, 2] != O[2]), True, False)
        # w2 = ind[w2, :]
        for op in operators[:]:
            # tmp = w2 * op[0] + np.array(op[1])
            tmp = ind * op[0] + np.array(op[1])
            res = np.concatenate((res, tmp))
        # on_axis_res = np.concatenate((w1 * np.array([-1, -1, -1]) + np.array([O[0] * 2, O[1] * 2, O[2] * 2]), w1))
        # res = np.concatenate((res, on_axis_res))
        return np.unique(res, axis=0)

    def generate_shell(self, n1, n2, shape):
        d1 = n1
        d2 = n2
        # O1 = [shape[0]//2, shape[1]//2, shape[2]//2]
        # even number for grid
        # based on fft
        if min(shape) % 2 == 0:
            O1 = [shape[0] / 2, shape[1] / 2, shape[2] / 2]
        else:
            O1 = [(shape[0] - 1) / 2, (shape[1] - 1) / 2, (shape[2] - 1) / 2]
        indices = []
        # make sure
        x_max = int(d2) + int(O1[0]) + 1 if int(d2) + int(O1[0]) < shape[0] else int(d2) + int(O1[0])
        y_max = int(d2) + int(O1[1]) + 1 if int(d2) + int(O1[1]) < shape[1] else int(d2) + int(O1[1])
        for x in range(round(O1[0] + 0.1), x_max):
            for y in range(round(O1[1] + 0.1), y_max):
                xy_dist = math.sqrt((x - O1[0]) ** 2 + (y - O1[1]) ** 2)
                if xy_dist <= d2:
                    if xy_dist == 0:
                        z_min = int(O1[2] + d1)
                        z_max = int(O1[2] + d2)
                    elif xy_dist < d1:
                        z_min = math.sqrt(d1 ** 2 - xy_dist ** 2) + O1[2]
                        z_min = int(z_min)
                        z_max = math.sqrt(d2 ** 2 - xy_dist ** 2) + O1[2]
                    elif d1 <= xy_dist <= d2:
                        z_min = O1[2]
                        z_max = math.sqrt(d2 ** 2 - xy_dist ** 2) + O1[2]
                    else:
                        z_min = O1[2]
                        z_max = O1[2]
                    if int(z_min) < O1[2]:
                        z_min = round(O1[2] + 0.1)
                    z_max = int(z_max) + 1 if int(z_max) < shape[2] else int(z_max)
                    for z in range(int(z_min), z_max):
                        # print(x, y, z)
                        d = math.sqrt(xy_dist ** 2 + ((z - O1[2]) ** 2))
                        if d1 < d <= d2:
                            indices.append([x, y, z])
        all_ind = self.apply_3d_symmetry(indices, O1).astype(int)
        return all_ind

    # @profile
    def new_raps(self, mapin=None, workdir=None, label=''):
        """

            Calculation of the rotationally average power spectrum (RAPS)
            Results wrote to JSON file

        :return: None

        """

        map, workdir = self.mapincheck(mapin, workdir)
        mapname = os.path.basename(map.fullname)
        apix_list = map.voxel_size.tolist()
        apixs = (apix_list[0], apix_list[1], apix_list[2])

        if map is not None and workdir is not None:
            # if map.x_size() == map.y_size() == map.z_size():
            if map.header.nx == map.header.ny == map.header.nz:
                errlist = []
                start = timeit.default_timer()
                datadict = dict()
                try:
                    # map = self.map
                    # temprary solution as the tempy give apix as one value but here from mrcfile we use a tuple
                    # if type(map.apix) is tuple:
                    if type(apixs) is tuple:
                        apix = apixs[0]
                    else:
                        apix = apixs
                    fftmap = fftshift(fftn(map.data))
                    psmean = np.mean(fftmap)
                    psstd = np.std(fftmap)
                    fftmap = np.abs((fftmap - psmean) / psstd) ** 2

                    midstart = timeit.default_timer() - start
                    print(' -- RAPS Fourier-transformation time: %s' % midstart)

                    ## applying new indices function
                    map_shape = fftmap.shape
                    aps = []
                    if map_shape[0] % 2 == 0:
                        org = [map_shape[0] / 2, map_shape[1] / 2, map_shape[2] / 2]
                    else:
                        org = [(map_shape[0] - 1) / 2, (map_shape[1] - 1) / 2, (map_shape[2] - 1) / 2]
                    indiaxis = np.linspace(0, int(org[0]), int(org[0]) + 1) / (map_shape[0] * apix)

                    shell_range = int(max(map_shape) - max(org))
                    for i in range(0, shell_range):
                        indices = self.generate_shell(i, i+1, map_shape)
                        psum = log10(fftmap[tuple(indices.T)].sum() / len(indices))
                        aps.append(psum)
                    if aps[0] < 0:
                        aps[0] = aps[1]
                    if map_shape[0] % 2 == 0:
                        aps.insert(0, aps[0])

                    datadict = {label + 'rotationally_averaged_power_spectrum':  {'y': np.round(aps, 10).tolist(),
                                                                         'x': np.round(indiaxis, 10).tolist()}}
                    plt.plot(np.round(indiaxis, 4).tolist(), np.round(aps, 4).tolist())
                    plt.savefig(workdir + 'raps.png')

                except:
                    err = 'RAPS calculation error: {}.'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

                if errlist:
                    datadict = {'rotationally_averaged_power_spectrum': {'err': {'raps_err': errlist}}}

                if bool(datadict):
                    try:
                        with codecs.open(workdir + mapname + '_raps.json', 'w', encoding='utf-8') as f:
                            json.dump(datadict, f)
                    except:
                        sys.stderr.write('Saving RAPS to json error: {}.'.format(sys.exc_info()[1]))
                else:
                    sys.stderr.write('No raps data in the dictionary, no raps json file.\n')

                end = timeit.default_timer()
                print('RAPS time for %s: %s' % (mapname, end - start))
                print('------------------------------------')
            else:
                print('No RAPS calculation for non-cubic map.')
                print('------------------------------------')

                return None
        else:
            print('No RAPS without proper map input and the output directory information.')

    # Above Here is the test new raps function area


    # New curve intersection functions
    def _rect_inter_inner(self, x1, x2):
        n1 = x1.shape[0] - 1
        n2 = x2.shape[0] - 1
        X1 = np.c_[x1[:-1], x1[1:]]
        X2 = np.c_[x2[:-1], x2[1:]]
        S1 = np.tile(X1.min(axis=1), (n2, 1)).T
        S2 = np.tile(X2.max(axis=1), (n1, 1))
        S3 = np.tile(X1.max(axis=1), (n2, 1)).T
        S4 = np.tile(X2.min(axis=1), (n1, 1))

        return S1, S2, S3, S4

    def _rectangle_intersection(self, x1, y1, x2, y2):
        S1, S2, S3, S4 = self._rect_inter_inner(x1, x2)
        S5, S6, S7, S8 = self._rect_inter_inner(y1, y2)

        C1 = np.less_equal(S1, S2)
        C2 = np.greater_equal(S3, S4)
        C3 = np.less_equal(S5, S6)
        C4 = np.greater_equal(S7, S8)

        ii, jj = np.nonzero(C1 & C2 & C3 & C4)

        return ii, jj

    def curves_intersection(self, x1, y1, x2, y2):
        """
        Get the interscetion of two curves
        return: list of of tuple contains [(x1, y1), (x2, y2), ...] (no duplicated points)
        """
        x1 = np.asarray(x1)
        x2 = np.asarray(x2)
        y1 = np.asarray(y1)
        y2 = np.asarray(y2)

        ii, jj = self._rectangle_intersection(x1, y1, x2, y2)
        if 0 in ii:
            zero_ind = np.where(ii == 0)
            ii = np.delete(ii, zero_ind)
            jj = np.delete(jj, zero_ind)
        if 1 in ii:
            one_ind = np.where(ii == 1)
            ii = np.delete(ii, one_ind)
            jj = np.delete(jj, one_ind)
        n = len(ii)

        dxy1 = np.diff(np.c_[x1, y1], axis=0)
        dxy2 = np.diff(np.c_[x2, y2], axis=0)

        T = np.zeros((4, n))
        AA = np.zeros((4, 4, n))
        AA[0:2, 2, :] = -1
        AA[2:4, 3, :] = -1
        AA[0::2, 0, :] = dxy1[ii, :].T
        AA[1::2, 1, :] = dxy2[jj, :].T

        BB = np.zeros((4, n))
        BB[0, :] = -x1[ii].ravel()
        BB[1, :] = -x2[jj].ravel()
        BB[2, :] = -y1[ii].ravel()
        BB[3, :] = -y2[jj].ravel()

        for i in range(n):
            try:
                T[:, i] = np.linalg.solve(AA[:, :, i], BB[:, i])
            except:
                T[:, i] = np.Inf

        in_range = (T[0, :] >= 0) & (T[1, :] >= 0) & (
                T[0, :] <= 1) & (T[1, :] <= 1)

        xy0 = T[2:, in_range]
        xy0 = xy0.T
        newlist = []
        print(xy0)
        for i in xy0:
            a = tuple(i)
            newlist.append(a)
        res = list(set(newlist))
        res.sort(key=newlist.index)
        nlist = []
        for b in res:
            nlist.append(list(b))
        lres = np.array(nlist)
        print(np.array(nlist))
        print(np.array(nlist)[:, 0])
        print(np.array(nlist)[:, 1])
        return lres[:, 0], lres[:, 1]

    # End of new curve intersection functions



    def __interpolated_intercept(self, x, y1, y2):
        """

            Find the intercept of two curves, given by the same x data

        """

        def intercept(point1, point2, point3, point4):
            """

                Find the intersection between two lines
                the first line is defined by the line between point1 and point2
                the second line is defined by the line between point3 and point4
                each point is an (x,y) tuple.

                So, for example, you can find the intersection between
                intercept((0,0), (1,1), (0,1), (1,0)) = (0.5, 0.5)

                :return: Intercept, in (x,y) format

            """

            def line(p1, p2):
                A = (p1[1] - p2[1])
                B = (p2[0] - p1[0])
                C = (p1[0] * p2[1] - p2[0] * p1[1])

                return A, B, -C

            def intersection(L1, L2):
                D = L1[0] * L2[1] - L1[1] * L2[0]
                Dx = L1[2] * L2[1] - L1[1] * L2[2]
                Dy = L1[0] * L2[2] - L1[2] * L2[0]

                x = Dx / D
                y = Dy / D

                return x, y

            L1 = line([point1[0], point1[1]], [point2[0], point2[1]])
            L2 = line([point3[0], point3[1]], [point4[0], point4[1]])

            R = intersection(L1, L2)

            return R

        idx = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)
        # Remove the first point usually (0, 1) to avoid all curves starting from (0, 1) which pick as one intersection
        if idx.size != 0:
            if idx[0][0] == 0:
                idx = np.delete(idx, 0, 0)
            xc, yc = intercept((x[idx], y1[idx]), ((x[idx + 1], y1[idx + 1])), ((x[idx], y2[idx])),
                               ((x[idx + 1], y2[idx + 1])))
            return xc, yc
        else:
            nullarr = np.empty(shape=(0, 0))
            return nullarr, nullarr

    @staticmethod
    def newmmfsc(cifmodel, map):
        """
            Use cifmomodel and input map to calculate model-map FSC

        :param cifmodel: String of full cif model name
        :param map: String of full map name
        :return:
        """

        modelname = os.path.basename(cifmodel)
        pass




    def mmfsc(self):
        """

            Calculate Model-map FSC based on simulated density map from model

        :return:
        """

        if self.platform == 'emdb':
            start = timeit.default_timer()
            modelsmaps = self.modelsmaps
            ## Todo: Consider putting this err information into the final fsc json file
            modelmapsdict = {}
            oldfiles = []
            if self.met == 'sp' and (modelsmaps is not None):
                for modelmap in modelsmaps:
                    # read model map
                    modelname = os.path.basename(modelmap).split('_')[0]
                    # objmodelmap = self.frommrc_totempy(modelmap)
                    objmodelmap = mrcfile.mmap(modelmap, mode='r')
                    self.fsc(self.map, objmodelmap, label='{}_mm'.format(modelname))
                    oldname = '{}{}_{}_mmfsc.json'.format(self.workdir, self.mapname, modelname)
                    newname = '{}{}'.format(self.workdir, self.mapname + '_' + modelname + '_mmfsc.json')
                    if os.path.isfile(oldname):
                        oldfiles.append(oldname)
                        os.rename(oldname, newname)
                    else:
                        print('{} does not exist, please check.'.format(oldname))
                    modelmapsdict[modelname] = newname
                self.mergemmfsc(modelmapsdict)
                self.deloldmmfsc(oldfiles)
                end = timeit.default_timer()

                print('mmfsc time: %s' % (end - start))
                print('------------------------------------')

            else:
                print('Model-map FSC only calculated for single particle data where there is a fitted model '
                      '(Please use -m sp and -f) or no model map is calculated us -i t/f to switch if on or off.')

        return None

    def deloldmmfsc(self, oldfiles):
        """

            delete separate mmfsc files to avoid merged into the final json

        :param oldfiles:
        :return: None
        """

        if oldfiles:
            for file in oldfiles:
                os.remove(file)
            print('Separate mmfsc files were deleted.')
        else:
            print('No mmfsc exist, no mmfsc file can be deleted')


    def mergemmfsc(self, mmfscdict):
        """

            Merge all *_mmfsc.json files of different models

        :return:
        """

        nfiles = len(list(mmfscdict))
        fulldata = {}
        for i, modelname in zip(range(0, nfiles), list(mmfscdict)):
            file = mmfscdict[modelname]
            if os.path.getsize(file):
                with open(file, 'r') as f:
                    if f is not None:
                        content = json.load(f)
                        if 'err' not in content.keys():
                            fulldata[str(i)] = list(content.values())[0]
                            fulldata[str(i)]['name'] = modelname
                        else:
                            curerr = content.values()[0]['err']
                            fulldata[str(i)]['err'] = curerr


        output = '{}{}_mmfsc.json'.format(self.workdir, self.mapname, )
        finaldata = {}
        finaldata['mmfsc'] = fulldata
        with open(output, 'w') as out:
            json.dump(finaldata, out)

        return None

    def frommrc_totempy(self, fullmapname):
        """
            Transfer the mrcfile map object to TEMPy map object

        :param fullmapname:
        :return: TEMPy map object
        """


        mrcmap = mrcfile.mmap(fullmapname, mode='r')
        mrcheader = mrcmap.header
        mapdata = mrcmap.data.astype('float')
        crs = (mrcheader.mapc, mrcheader.mapr, mrcheader.maps)
        reversecrs = crs[::-1]
        nstarts = (mrcheader.nxstart, mrcheader.nystart, mrcheader.nzstart)
        stdcrs = (3, 2, 1)
        diffcrs = tuple(x-y for x,y in zip(reversecrs, stdcrs))
        if diffcrs != (0, 0, 0):
            if 1 in diffcrs and -1 in diffcrs:
                mapdata = np.swapaxes(mapdata, diffcrs.index(-1), diffcrs.index(1))
            if -2 in diffcrs and 2 in diffcrs:
                mapdata = np.swapaxes(mapdata, diffcrs.index(-2), diffcrs.index(2))
            if 1 in diffcrs and -2 in diffcrs:
                mapdata = np.swapaxes(np.swapaxes(mapdata, 0, 1), 1, 2)
            if -1 in diffcrs and 2 in diffcrs:
                mapdata = np.swapaxes(np.swapaxes(mapdata, 1, 2), 0, 1)
            # mapdata = np.swapaxes(mapdata, 0, 2)

        # mapdata = np.swapaxes(np.swapaxes(mapdata, 0, 2), 1, 2)
        tempyheader = MapParser.readMRCHeader(fullmapname)

        # nx, ny, nz and nxstart, nystart, nzstart haver to be changed accordingly to the data
        tempyheader = list(tempyheader)
        tempyheader[0] = mapdata.shape[2]
        tempyheader[1] = mapdata.shape[1]
        tempyheader[2] = mapdata.shape[0]
        tempyheader[3] = mrcheader.mode.item(0)
        tempyheader[4] = nstarts[0].item(0)
        tempyheader[5] = nstarts[1].item(0)
        tempyheader[6] = nstarts[2].item(0)
        tempyheader[7] = mrcheader.mx.item(0)
        tempyheader[8] = mrcheader.my.item(0)
        tempyheader[9] = mrcheader.mz.item(0)
        tempyheader[10] = mrcheader.cella.x.item(0)
        tempyheader[11] = mrcheader.cella.y.item(0)
        tempyheader[12] = mrcheader.cella.z.item(0)
        tempyheader[13:16] = mrcheader.cellb.tolist()
        tempyheader[16] = crs[0].item(0)
        tempyheader[17] = crs[1].item(0)
        tempyheader[18] = crs[2].item(0)
        tempyheader[19] = mrcheader.dmin.item(0)
        tempyheader[20] = mrcheader.dmax.item(0)
        tempyheader[21] = mrcheader.dmean.item(0)
        tempyheader[22] = mrcheader.ispg.item(0)
        tempyheader[23] = mrcheader.nsymbt.item(0)

        # tempyheader[24] = mrcheader.extra1.item(0)
        # tempyheader[25] = mrcheader.exttyp.item(0)
        # tempyheader[26] = mrcheader.nversion.item(0)
        # tempyheader[27] = mrcheader.extra2.item(0)

        tempyheader[49] = mrcheader.origin.x.item(0)
        tempyheader[50] = mrcheader.origin.y.item(0)
        tempyheader[51] = mrcheader.origin.z.item(0)
        tempyheader[52:55] = ['M', 'A', 'P']

        tempyheader[56] = mrcheader.machst
        tempyheader[57] = mrcheader.rms.item(0)
        # tempyheader[58] = mrcheader.nlabl.item(0)
        # tempyheader[59] = mrcheader.label.item(0)



        # tempyheader[13] = mrcheader.cellb.x.item(0)
        # tempyheader[14] = mrcheader.cellb.y.item(0)
        # tempyheader[15] = mrcheader.cellb.z.item(0)
        # here also keep the nstarts position according to original crs order as in __getindices it automaticlly
        # adjust the calculation based on the
        # tempyheader[4] = int(nstarts[crs.index(1)])
        # tempyheader[5] = int(nstarts[crs.index(2)])
        # tempyheader[6] = int(nstarts[crs.index(3)])
        tempyheader = tuple(tempyheader)
        origin = (float(mrcheader.origin.x), float(mrcheader.origin.y), float(mrcheader.origin.z))
        apix = (mrcheader.cella.x/mrcheader.mx, mrcheader.cella.y/mrcheader.my, mrcheader.cella.z/mrcheader.mz)[0]

        finalmap = Map(mapdata, origin, apix, fullmapname, header=tempyheader)

        # inputmap.fullMap = np.swapaxes(np.swapaxes(mrcfile.mmap(fullmapname).data, 0, 2), 1, 2)
        # print(inputmap.fullMap.shape)
        # print(inputmap.fullMap[1, 3, 66])

        return finalmap



    # @profile
    def fscs(self):
        """



        :return: None
        """
        if self.hmeven is not None and self.hmodd is not None:
            startfsc = timeit.default_timer()
            # self.fsc(self.hmeven, self.hmodd)
            self.new_fsc(self.hmeven, self.hmodd)
            stop = timeit.default_timer()
            print('FSC: %s' % (stop - startfsc))
            print('------------------------------------')
        else:
            print('Mising half map(s).')

        fscxmlre = '*_fsc.xml'
        fscxmlarr = glob.glob(self.workdir + fscxmlre)
        if fscxmlarr or self.fscfile:
            startfsc = timeit.default_timer()
            self.readfsc()
            stop = timeit.default_timer()
            print('Load FSC: %s' % (stop - startfsc))
            print('------------------------------------')
        else:
            print('No given FSC data to be loaded.')

    def readfsc(self, asym=1.0):
        """

        :return:
        """
        import xml.etree.ElementTree as ET

        errlist = []
        finaldict = dict()

        if self.fscfile is not None:
            xlist = []
            ylist = []
            map_zsize = self.map.header.nz
            map_ysize = self.map.header.ny
            map_xsize = self.map.header.nx
            try:
                filefsc = self.workdir + self.fscfile
                tree = ET.parse(filefsc)
                root = tree.getroot()
                for child in root:
                    x = float(child.find('x').text)
                    y = float(child.find('y').text)
                    xlist.append(x)
                    ylist.append(y)
            except:
                err = 'Read FSC from XML error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            try:
                # Grid here to generate for tracing the indices of grids with in the shells.
                zgrid = np.arange(floor(map_zsize / 2.0) * -1, ceil(map_zsize / 2.0)) / float(
                    floor(map_zsize))
                ygrid = np.arange(floor(map_ysize / 2.0) * -1, ceil(map_ysize / 2.0)) / float(
                    floor(map_ysize))
                xgrid = np.arange(floor(map_xsize / 2.0) * -1, ceil(map_xsize / 2.0)) / float(
                    floor(map_xsize))
                xdis = xgrid ** 2
                ydis = ygrid ** 2
                zdis = zgrid ** 2
                # dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

                allaxis = np.array([zgrid, ygrid, xgrid])
                tmpindiaxis = max(allaxis, key=len)
                indiaxist = tmpindiaxis[tmpindiaxis >= 0]
                lindi = len(indiaxist)
                # indiaxis = np.linspace(0, 1 / (2 * cpmap.apix), lindi)

                # Looping through all shells
                threesig = []
                halfbit = []
                onebit = []
                # for i in range(len(indiaxis)):
                for i in range(len(xlist)):
                    # if i < len(indiaxis) - 1:
                        # indices = np.argwhere((dist >= indiaxist[i]) & (dist < indiaxist[i + 1]))

                    volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                    nvoxring = volumediff / (1 ** 3)
                    effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                    if effnvox < 1.0: effnvox = 1.0
                    sqreffnvox = np.sqrt(effnvox)

                    # 3-sigma curve
                    if i != 0:
                        sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                    else:
                        sigvalue = 1
                    threesig.append(sigvalue)

                    # Half bit curve
                    if i != 0:
                        bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                    else:
                        bitvalue = 1
                    halfbit.append(bitvalue)

                    if i != 0:
                        onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                    else:
                        onebitvalue = 1
                    onebit.append(onebitvalue)

                # threesig.append(threesig[-1])
                # halfbit.append(halfbit[-1])
                # onebit.append(onebit[-1])
                if ylist[0] <= 0:
                    ylist[0] = 1

                a = np.asarray(xlist)
                b = np.asarray(ylist)
                c = np.asarray(threesig)
                d = np.asarray(halfbit)
                e = np.asarray(onebit)
                f = np.full((len(xlist)), 0.5)
                g = np.full((len(xlist)), 0.333)
                h = np.full((len(xlist)), 0.143)

                if len(c) < len(b):
                    b = b[:len(c)]
                else:
                    c = c[:len(b)]

                if len(d) < len(b):
                    b = b[:len(d)]
                else:
                    d = d[:len(b)]


                if len(e) < len(b):
                    b = b[:len(e)]
                else:
                    e = e[:len(b)]


                if len(f) < len(b):
                    b = b[:len(f)]
                else:
                    f = f[:len(b)]


                if len(g) < len(b):
                    b = b[:len(g)]
                else:
                    g = g[:len(b)]

                if len(h) < len(b):
                    b = b[:len(h)]
                else:
                    h = h[:len(b)]

                xthreesig, ythreesig = self.__interpolated_intercept(a, b, c)
                xhalfbit, yhalfbit = self.__interpolated_intercept(a, b, d)
                xonebit, yonebit = self.__interpolated_intercept(a, b, e)
                xhalf, yhalf = self.__interpolated_intercept(a, b, f)
                xonethree, yonethree = self.__interpolated_intercept(a, b, g)
                xgold, ygold = self.__interpolated_intercept(a, b, h)

                if xthreesig.size == 0 and ythreesig.size == 0:
                    txthreesig = None
                    tythreesig = None
                else:
                    txthreesig = np.round(xthreesig[0][0], 4)
                    tythreesig = np.round(ythreesig[0][0], 4)

                if xhalfbit.size == 0 and yhalfbit.size == 0:
                    txhalfbit = None
                    tyhalfbit = None
                else:
                    if np.isnan(xhalfbit[0][0]):
                        txhalfbit = None
                        tyhalfbit = None
                        print('!!! The loaded fsc has no intersection with the half bit curve !!!')
                    else:
                        txhalfbit = np.round(xhalfbit[0][0], 4)
                        tyhalfbit = np.round(yhalfbit[0][0], 4)

                if xonebit.size == 0 and yonebit.size == 0:
                    txonebit = None
                    tyonebit = None
                else:
                    txonebit = np.round(xonebit[0][0], 4)
                    tyonebit = np.round(yonebit[0][0], 4)

                if xhalf.size == 0 and yhalf.size == 0:
                    txhalf = None
                    tyhalf = None
                else:
                    txhalf = np.round(xhalf[0][0], 4)
                    tyhalf = np.round(yhalf[0][0], 4)

                if xonethree.size == 0 and yonethree.size == 0:
                    txonethree = None
                    tyonethree = None
                else:
                    txonethree = np.round(xonethree[0][0], 4)
                    tyonethree = np.round(yonethree[0][0], 4)

                if xgold.size == 0 and ygold.size == 0:
                    txgold = None
                    tygold = None
                else:
                    txgold = np.round(xgold[0][0], 4)
                    tygold = np.round(ygold[0][0], 4)

                xlen = len(xlist)

                datadict = {
                    'curves': {'fscy': np.round(np.real(ylist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist()[:xlen],
                               'halfbit': np.round(halfbit, 4).tolist()[:xlen],
                               'onebit': np.round(onebit, 4).tolist()[:xlen], '0.5': f.tolist()[:xlen], '0.333': g.tolist()[:xlen],
                               '0.143': h.tolist()[:xlen],
                               'level': np.round(np.real(xlist), 4).tolist(),
                               'fscx': np.round(np.real(xlist), 4).tolist()},
                    'intersections': {'threesig': {'x': txthreesig, 'y': tythreesig},
                                      'halfbit': {'x': txhalfbit, 'y': tyhalfbit},
                                      'onebit': {'x': txonebit, 'y': tyonebit},
                                      '0.5': {'x': txhalf, 'y': tyhalf},
                                      '0.333': {'x': txonethree, 'y': tyonethree},
                                      '0.143': {'x': txgold, 'y': tygold}}}

                finaldict['load_fsc'] = datadict

                plt.plot(xlist, ylist, label='Provided FSC')
                #plt.plot(indiaxis, threesig, label='3 sigma')
                #plt.plot(indiaxis, halfbit, label='1/2 bit')
                #plt.plot(indiaxis, onebit, label='1 bit')
                plt.plot(xlist[:-1], len(xlist[:-1])*[0.5], linestyle=':', label='_nolegend_')
                #plt.plot(indiaxis, g, label='0.333', linestyle='--')
                plt.plot(xlist[:-1], len(xlist[:-1])*[0.143], linestyle='-.', label='_nolegend_')
                plt.legend()
                plt.savefig(self.workdir + self.mapname + '_fsc.png')
            except:
                err = 'FSC reading error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            if errlist:
                finaldict['load_fsc'] = {'err': {'load_fsc_err': errlist}}

            try:
                with codecs.open(self.workdir + self.mapname + '_loadfsc.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)

                return None
            except:
                sys.stderr.write('Saving loaded FSC to json error:{}.\n'.format(sys.exc_info()[1]))
        else:
            print('No fsc.xml file can be read for FSC information.')


    # @profile
    def fsc(self, mapodd, mapeven, asym=1.0, label=''):
        """

            Calculate FSC based on the two input half maps
            Results wrote to JSON file including resolution at 0.143, 0.333, 0.5 and noise
            level at 0.5-bit, 1-bit, 3-sigma. A corresponding plot is also save as PNG file.

        :param mapodd: TEMPy map instance
        :param mapeven: TEMPy map instance
        :return: None

        """


        # res = (mapodd.header[10]/mapodd.header[7] == mapeven.header[10]/mapeven.header[7]) and \
        #       (mapodd.header[10]/mapodd.header[7] == mapeven.header[10]/mapeven.header[7]) and \
        #       (mapodd.header[10]/mapodd.header[7] == mapeven.header[10]/mapeven.header[7])


        start = timeit.default_timer()
        errlist = []
        datadict = dict()
        finaldict = dict()
        try:
            # assert mapodd.box_size() == mapeven.box_size(), 'The two half maps do not have same size.'
            # assert mapodd.apix == mapeven.apix, 'The two half maps do not have same apix.'
            # oddnan = np.isnan(mapodd.fullMap).any()
            # evennan = np.isnan(mapeven.fullMap).any()
            assert mapodd.data.shape == mapeven.data.shape, 'The two half maps do not have same size.'
            assert mapodd.voxel_size == mapeven.voxel_size, 'The two half maps do not have same apix.'
            oddnan = np.isnan(mapodd.data).any()
            evennan = np.isnan(mapeven.data).any()
            nancheck = oddnan | evennan
            assert not nancheck, 'There is NaN value in half map.'

            map_zsize = mapodd.header.nz
            map_ysize = mapodd.header.ny
            map_xsize = mapodd.header.nx

            apixs = tuple(mapodd.voxel_size.tolist())

            # mapodd.fullMap = fftshift(fftn(mapodd.fullMap))
            # mapeven.fullMap = fftshift(fftn(mapeven.fullMap))
            mapodd_data = fftshift(fftn(mapodd.data))
            mapeven_data = fftshift(fftn(mapeven.data))

            start = timeit.default_timer() - start
            print(' -- FSC Fourier-transformation time: %s' % start)

            # Grid here to generate for tracing the indices of grids with in the shells.
            zgrid = np.arange(floor(map_zsize / 2.0) * -1, ceil(map_zsize / 2.0)) / float(
                floor(map_zsize))
            ygrid = np.arange(floor(map_ysize / 2.0) * -1, ceil(map_ysize / 2.0)) / float(
                floor(map_ysize))
            xgrid = np.arange(floor(map_xsize / 2.0) * -1, ceil(map_xsize / 2.0)) / float(
                floor(map_xsize))
            xdis = xgrid ** 2
            ydis = ygrid ** 2
            zdis = zgrid ** 2
            dist = np.sqrt(zdis[:, None, None] + ydis[:, None] + xdis)

            allaxis = np.array([zgrid, ygrid, xgrid])
            tmpindiaxis = max(allaxis, key=len)
            indiaxist = tmpindiaxis[tmpindiaxis >= 0]
            lindi = len(indiaxist)
            # if type(mapodd.apix) is tuple:
            if type(apixs) is tuple:
                # tapix = mapodd.apix[0]
                tapix = apixs[0]
            else:
                # tapix = mapodd.apix
                tapix = apixs
            indiaxis = np.linspace(0, 1 / (2 * tapix), lindi)

            # Looping through all shells
            corrlist = []
            threesig = []
            halfbit = []
            onebit = []
            for i in range(len(indiaxis)):
                if i == 0:
                    indices = np.argwhere(dist == indiaxis[i])
                    # oddring = mapodd.fullMap[tuple(indices.T)]
                    # evenring = mapeven.fullMap[tuple(indices.T)]
                    oddring = mapodd_data[tuple(indices.T)]
                    evenring = mapeven_data[tuple(indices.T)]

                elif i != len(indiaxis) - 1:
                    indices = np.argwhere((dist > indiaxist[i]) & (dist <= indiaxist[i + 1]))
                    # oddring = mapodd.fullMap[tuple(indices.T)]
                    # evenring = mapeven.fullMap[tuple(indices.T)]
                    oddring = mapodd_data[tuple(indices.T)]
                    evenring = mapeven_data[tuple(indices.T)]

                    # corr = (oddring * np.conj(evenring)).sum()
                    # norcorr = np.real(corr / np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum()))
                    # corrlist.append(norcorr)

                    # volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                    # nvoxring = volumediff / (1 ** 3)
                    # effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                    # if effnvox < 1.0: effnvox = 1.0
                    # sqreffnvox = np.sqrt(effnvox)

                    # # 3-sigma curve
                    # if i != 0:
                    #     sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                    # else:
                    #     sigvalue = 1
                    # threesig.append(sigvalue)
                    #
                    # # Half bit curve
                    # if i != 0:
                    #     bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                    # else:
                    #     bitvalue = 1
                    # halfbit.append(bitvalue)
                    #
                    # if i != 0:
                    #     onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                    # else:
                    #     onebitvalue = 1
                    # onebit.append(onebitvalue)
                else:
                    pass
                    # indices = np.argwhere((dist > indiaxist[i-1]) & (dist <= indiaxist[i]))
                    # oddring = mapodd.fullMap[tuple(indices.T)]
                    # evenring = mapeven.fullMap[tuple(indices.T)]

                    # corr = (oddring * np.conj(evenring)).sum()
                    # norcorr = np.real(corr / np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum()))
                    # corrlist.append(norcorr)
                corr = (oddring * np.conj(evenring)).sum()
                corr_deno = np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum())
                if corr_deno == 0.:
                    norcorr = 0.
                else:
                    norcorr = np.real(corr / corr_deno)
                corrlist.append(norcorr)

                volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                nvoxring = volumediff / (1 ** 3)
                effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                if effnvox < 1.0: effnvox = 1.0
                sqreffnvox = np.sqrt(effnvox)


                # 3-sigma curve
                if i != 0:
                    sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                else:
                    sigvalue = 1
                threesig.append(sigvalue)

                # Half bit curve
                if i != 0:
                    bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                else:
                    bitvalue = 1
                halfbit.append(bitvalue)

                if i != 0:
                    onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                else:
                    onebitvalue = 1
                onebit.append(onebitvalue)
            print(corrlist)

            if corrlist[0] <= 0:
                corrlist[0] = 1
            # corrlist.append(corrlist[-1])
            # threesig.append(threesig[-1])
            # halfbit.append(halfbit[-1])
            # onebit.append(onebit[-1])
            a = np.asarray(indiaxis)
            b = np.asarray(corrlist)
            c = np.asarray(threesig)
            d = np.asarray(halfbit)
            e = np.asarray(onebit)
            f = np.full((len(indiaxis)), 0.5)
            g = np.full((len(indiaxis)), 0.333)
            h = np.full((len(indiaxis)), 0.143)
            # use [:1] to ignore all the curves start from 0,1
            xthreesig, ythreesig = self.__interpolated_intercept(a, b, c)
            xhalfbit, yhalfbit = self.__interpolated_intercept(a, b, d)
            xonebit, yonebit = self.__interpolated_intercept(a, b, e)
            xhalf, yhalf = self.__interpolated_intercept(a, b, f)

            # Check if mm in label then, see which intersecion is the most closest to the given resolution(Todo)
            if 'mm' in label:
                if xhalf.size != 0:
                    newxhalf = abs(xhalf - 1 / float(self.resolution))
                    indmin = np.argmin(newxhalf)
                    xhalf = np.array([xhalf[indmin]])
                    yhalf = np.array([yhalf[indmin]])

            xonethree, yonethree = self.__interpolated_intercept(a, b, g)
            xgold, ygold = self.__interpolated_intercept(a, b, h)

            # Assign intersection value as None when there is no intersection
            if xthreesig.size == 0 and ythreesig.size == 0:
                print('No intersection between FSC and 3-sigma curves. Here use the last point.')
                xthreesig, ythreesig = None, None
            else:
                xthreesig = np.round(xthreesig[0][0], 4)
                ythreesig = np.round(ythreesig[0][0], 4)

            if xhalfbit.size == 0 and yhalfbit.size == 0:
                print('No intersection between FSC and 1/2-bit curves. Here use the last point.')
                xhalfbit, yhalfbit = None, None
            else:
                xhalfbit = np.round(xhalfbit[0][0], 4)
                yhalfbit = np.round(yhalfbit[0][0], 4)

            if xonebit.size == 0 and yonebit.size == 0:
                print('No intersection between FSC and 1-bit curves. Here use the last point.')
                xonebit, yonebit = None, None
            else:
                xonebit = np.round(xonebit[0][0], 4)
                yonebit = np.round(yonebit[0][0], 4)

            if xonethree.size == 0 and yonethree.size == 0:
                print('No intersection between FSC and 0.333 curves. Here use the last point')
                xonethree, yonethree = None, None
            else:
                xonethree = np.round(xonethree[0][0], 4)
                yonethree = np.round(yonethree[0][0], 4)

            if xhalf.size == 0 and yhalf.size == 0:
                print('!!! No intersection between FSC and 0.5 curves. Here use the last point')
                xhalf, yhalf = None, None
            else:
                xhalf = np.round(xhalf[0][0], 4)
                yhalf = np.round(yhalf[0][0], 4)
            if xgold.size == 0 and ygold.size == 0:
                print('!!! No intersection between FSC and 0.143 curves. Here use the last point')
                xgold, ygold = None, None
            else:
                xgold = np.round(xgold[0][0], 4)
                ygold = np.round(ygold[0][0], 4)


            datadict = {
                'curves': {'fsc': np.round(np.real(corrlist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist(),
                           'halfbit': np.round(halfbit, 4).tolist(),
                           'onebit': np.round(onebit, 4).tolist(), '0.5': f.tolist(), '0.333': g.tolist(),
                           '0.143': h.tolist(),
                           'level': np.round(indiaxis, 4).tolist()},
                'intersections': {'threesig': {'x': xthreesig, 'y': ythreesig},
                                  'halfbit': {'x': xhalfbit, 'y': yhalfbit},
                                  'onebit': {'x': xonebit, 'y': yonebit},
                                  '0.5': {'x': xhalf, 'y': yhalf},
                                  '0.333': {'x': xonethree, 'y': yonethree},
                                  '0.143': {'x': xgold, 'y': ygold}}}
            finaldict = dict()
            finaldict[label + 'fsc'] = datadict

            plt.plot(indiaxis, corrlist, label=label + 'FSC')
            # plt.plot(indiaxis, threesig, label='3 sigma')
            plt.plot(indiaxis, halfbit, label='1/2 bit')
            # plt.plot(indiaxis, onebit, label='1 bit')
            plt.plot(indiaxis, f, label='0.5', linestyle=':')
            # plt.plot(indiaxis, g, label='0.333', linestyle='--')
            plt.plot(indiaxis, h, label='0.143', linestyle='-.')
            plt.legend()
            if label:
                plt.savefig(self.workdir + self.mapname + '_' + label + '_fsc.png')
            else:
                plt.savefig(self.workdir + self.mapname + '_fsc.png')

        except:
            err = 'FSC calculation error: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {'err': {label + 'fsc_error': errlist}}
            finaldict[label + 'fsc'] = datadict
        else:
            print('No error in FSC calculation.')

        if bool(datadict) and bool(finaldict):
            try:
                with codecs.open(self.workdir + self.mapname + '_' + label + 'fsc.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('FSC produced by two half maps.')
            except:
                sys.stderr.write('Writing FSC data to json file error: {}.'.format(sys.exc_info()[1]))
        else:
            sys.stderr.write('FSC calculation get none ')

        return None


    # @profile
    def new_fsc(self, mapodd, mapeven, asym=1.0, label=''):
        """

            Calculate FSC based on the two input half maps
            Results wrote to JSON file including resolution at 0.143, 0.333, 0.5 and noise
            level at 0.5-bit, 1-bit, 3-sigma. A corresponding plot is also save as PNG file.

        :param mapodd: TEMPy map instance
        :param mapeven: TEMPy map instance
        :return: None

        """

        start = timeit.default_timer()
        errlist = []
        datadict = dict()
        finaldict = dict()
        try:
            assert mapodd.data.shape == mapeven.data.shape, 'The two half maps do not have same size.'
            assert mapodd.voxel_size == mapeven.voxel_size, 'The two half maps do not have same apix.'
            oddnan = np.isnan(mapodd.data).any()
            evennan = np.isnan(mapeven.data).any()
            nancheck = oddnan | evennan
            assert not nancheck, 'There is NaN value in half map.'
            # Assume all dimension are the same size

            apixs = tuple(mapodd.voxel_size.tolist())

            mapodd_data = fftshift(fftn(mapodd.data))
            mapodd.close()
            mapeven_data = fftshift(fftn(mapeven.data))
            mapeven.close()

            start = timeit.default_timer() - start
            print(' -- FSC Fourier-transformation time: %s' % start)

            if type(apixs) is tuple:
                tapix = apixs[0]
            else:
                tapix = apixs

            # Looping through all shells
            corrlist = []
            threesig = []
            halfbit = []
            onebit = []

            ## applying new indices function
            map_shape = mapodd_data.shape
            if min(map_shape) % 2 == 0:
                org = [map_shape[0] / 2, map_shape[1] / 2, map_shape[2] / 2]
            else:
                org = [(map_shape[0] - 1) / 2, (map_shape[1] - 1) / 2, (map_shape[2] - 1) / 2]
            indiaxis = np.linspace(0, int(min(org)), int(min(org)) + 1) / (min(map_shape) * tapix)
            # indiaxis = np.linspace(0, int(org[0]), int(org[0]) + 1) / (map_shape[0] * tapix)
            shell_range = int(min(map_shape) - min(org))
            for i in range(0, shell_range):
                indices = self.generate_shell(i, i + 1, map_shape)
                oddring = mapodd_data[tuple(indices.T)]
                evenring = mapeven_data[tuple(indices.T)]
                corr = (oddring * np.conj(evenring)).sum()
                corr_deno = np.sqrt((np.abs(oddring) ** 2).sum() * (np.abs(evenring) ** 2).sum())
                if corr_deno == 0.:
                    norcorr = 0.
                else:
                    norcorr = np.real(corr / corr_deno)
                corrlist.append(norcorr)

                volumediff = (4.0 / 3.0) * pi * ((i + 1) ** 3 - i ** 3)
                nvoxring = volumediff / (1 ** 3)
                effnvox = (nvoxring * ((1.5 * 0.66) ** 2)) / (2 * asym)
                if effnvox < 1.0: effnvox = 1.0
                sqreffnvox = np.sqrt(effnvox)

                sigvalue = 3 / (sqreffnvox + 3.0 - 1.0)
                threesig.append(sigvalue)
                bitvalue = (0.2071 + 1.9102 / sqreffnvox) / (1.2071 + 0.9102 / sqreffnvox)
                halfbit.append(bitvalue)
                onebitvalue = (0.5 + 2.4142 / sqreffnvox) / (1.5 + 1.4142 / sqreffnvox)
                onebit.append(onebitvalue)

            corrlist.insert(0, 1)
            threesig.insert(0, 1)
            halfbit.insert(0, 1)
            onebit.insert(0, 1)
            del mapodd_data
            del mapeven_data

            if corrlist[0] <= 0:
                corrlist[0] = 1

            a = np.asarray(indiaxis)
            b = np.asarray(corrlist)
            c = np.asarray(threesig)
            d = np.asarray(halfbit)
            e = np.asarray(onebit)
            f = np.full((len(indiaxis)), 0.5)
            g = np.full((len(indiaxis)), 0.333)
            h = np.full((len(indiaxis)), 0.143)
            # use [:1] to ignore all the curves start from 0,1
            xthreesig, ythreesig = self.__interpolated_intercept(a, b, c)
            xhalfbit, yhalfbit = self.__interpolated_intercept(a, b, d)
            xonebit, yonebit = self.__interpolated_intercept(a, b, e)
            xhalf, yhalf = self.__interpolated_intercept(a, b, f)

            # Check if mm in label then, see which intersecion is the most closest to the given resolution(Todo)
            if 'mm' in label:
                if xhalf.size != 0:
                    newxhalf = abs(xhalf - 1 / float(self.resolution))
                    indmin = np.argmin(newxhalf)
                    xhalf = np.array([xhalf[indmin]])
                    yhalf = np.array([yhalf[indmin]])

            xonethree, yonethree = self.__interpolated_intercept(a, b, g)
            xgold, ygold = self.__interpolated_intercept(a, b, h)

            # Assign intersection value as None when there is no intersection
            if xthreesig.size == 0 and ythreesig.size == 0:
                print('No intersection between FSC and 3-sigma curves. Here use the last point.')
                xthreesig, ythreesig = None, None
            else:
                xthreesig = np.round(xthreesig[0][0], 4)
                ythreesig = np.round(ythreesig[0][0], 4)

            if xhalfbit.size == 0 and yhalfbit.size == 0:
                print('No intersection between FSC and 1/2-bit curves. Here use the last point.')
                xhalfbit, yhalfbit = None, None
            else:
                xhalfbit = np.round(xhalfbit[0][0], 4)
                yhalfbit = np.round(yhalfbit[0][0], 4)

            if xonebit.size == 0 and yonebit.size == 0:
                print('No intersection between FSC and 1-bit curves. Here use the last point.')
                xonebit, yonebit = None, None
            else:
                xonebit = np.round(xonebit[0][0], 4)
                yonebit = np.round(yonebit[0][0], 4)

            if xonethree.size == 0 and yonethree.size == 0:
                print('No intersection between FSC and 0.333 curves. Here use the last point')
                xonethree, yonethree = None, None
            else:
                xonethree = np.round(xonethree[0][0], 4)
                yonethree = np.round(yonethree[0][0], 4)

            if xhalf.size == 0 and yhalf.size == 0:
                print('!!! No intersection between FSC and 0.5 curves. Here use the last point')
                xhalf, yhalf = None, None
            else:
                xhalf = np.round(xhalf[0][0], 4)
                yhalf = np.round(yhalf[0][0], 4)
            if xgold.size == 0 and ygold.size == 0:
                print('!!! No intersection between FSC and 0.143 curves. Here use the last point')
                xgold, ygold = None, None
            else:
                xgold = np.round(xgold[0][0], 4)
                ygold = np.round(ygold[0][0], 4)


            datadict = {
                'curves': {'fsc': np.round(np.real(corrlist), 4).tolist(), 'threesigma': np.round(threesig, 4).tolist(),
                           'halfbit': np.round(halfbit, 4).tolist(),
                           'onebit': np.round(onebit, 4).tolist(), '0.5': f.tolist(), '0.333': g.tolist(),
                           '0.143': h.tolist(),
                           'level': np.round(indiaxis, 4).tolist()},
                'intersections': {'threesig': {'x': xthreesig, 'y': ythreesig},
                                  'halfbit': {'x': xhalfbit, 'y': yhalfbit},
                                  'onebit': {'x': xonebit, 'y': yonebit},
                                  '0.5': {'x': xhalf, 'y': yhalf},
                                  '0.333': {'x': xonethree, 'y': yonethree},
                                  '0.143': {'x': xgold, 'y': ygold}}}
            finaldict = dict()
            finaldict[label + 'fsc'] = datadict

            plt.plot(indiaxis, corrlist, label=label + 'FSC')
            # plt.plot(indiaxis, threesig, label='3 sigma')
            plt.plot(indiaxis, halfbit, label='1/2 bit')
            # plt.plot(indiaxis, onebit, label='1 bit')
            plt.plot(indiaxis, f, label='0.5', linestyle=':')
            # plt.plot(indiaxis, g, label='0.333', linestyle='--')
            plt.plot(indiaxis, h, label='0.143', linestyle='-.')
            plt.legend()
            if label:
                plt.savefig(self.workdir + self.mapname + '_' + label + '_fsc.png')
            else:
                plt.savefig(self.workdir + self.mapname + '_fsc.png')

        except:
            err = 'FSC calculation error: {}'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')

        if errlist:
            datadict = {'err': {label + 'fsc_error': errlist}}
            finaldict[label + 'fsc'] = datadict
        else:
            print('No error in FSC calculation.')

        if bool(datadict) and bool(finaldict):
            try:
                with codecs.open(self.workdir + self.mapname + '_' + label + 'fsc.json', 'w', encoding='utf-8') as f:
                    json.dump(finaldict, f)
                print('FSC produced by two half maps.')
            except:
                sys.stderr.write('Writing FSC data to json file error: {}.'.format(sys.exc_info()[1]))
        else:
            sys.stderr.write('FSC calculation get none ')

        return None

    @staticmethod
    def mempred(resultfile, inputfilesize):
        """

            Produce memory prediction results using linear regression
            based on the data from previous entries.


        :param resultfile: Previous memory usage information in CSV file
        :param inputfilesize: The input density map size
        :return: 0 or y_pred (the predicted memory usage)
        """
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error, r2_score
        from sklearn.model_selection import train_test_split
        from sklearn.model_selection import cross_val_score, cross_val_predict

        data = pd.read_csv(resultfile, header=0)
        data = data.dropna()
        if data.empty:
            print('No useful data in the dataframe.')
            return None
        else:
            newdata = data.iloc[:, 1:]
            sortdata = newdata.sort_values(newdata.columns[0])
            merdata = sortdata.groupby(sortdata.columns[0], as_index=False).mean()
            x = merdata['maprealsize']
            y = merdata['mem']
            if x.shape[0] <= 1:
                print('Sample is too little to split.')
                return None
            X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
            if X_train.empty or X_test.empty or y_train.empty or y_test.empty or len(x.index) < 30:
                print('Sparse data for memory prediction, result may not accurate.')
                return None
            else:
                lrmodel = LinearRegression(fit_intercept=False)
                # Perform CV
                scores = cross_val_score(lrmodel, x.values.reshape(-1, 1), y, cv=6)
                predictions = cross_val_predict(lrmodel, x.values.reshape(-1, 1), y, cv=6)

                lrmodel.fit(X_train.values.reshape(-1, 1), y_train)
                lrpredict = lrmodel.predict(X_test.values.reshape(-1, 1))
                print('6-Fold CV scores:%s' % scores)
                print('CV accuracy: %s' % (r2_score(y, predictions)))
                # print 'Score:%s' % (lrmodel.score(X_test.values.reshape(-1,1), y_test))
                print('Linear model coefficients: %s' % (lrmodel.coef_))
                print('MSE: %s' % (mean_squared_error(y_test, lrpredict)))
                print('Variance score(test accuracy): %s' % (r2_score(y_test, lrpredict)))
                y_pred = lrmodel.predict([[inputfilesize]])

                return y_pred

    @staticmethod
    def savepeakmemory(filename, maxmem):
        """

            Data collected and to be used for prediction for memory usage
            Memory saved as a comma separate CSV file.


        :param filename: String for file which used to collect data
        :param maxmem: Float number which gives peak memory usage of the finished job
        :return: None

        """

        columnname = 'mem'
        # dir = MAP_SERVER_PATH if self.emdid is not None else os.path.dirname(os.path.dirname(self.workdir))
        # filename = dir + 'input.csv'
        memresultfile = filename
        df = pd.read_csv(filename, header=0, sep=',', skipinitialspace=True)
        df[columnname][len(df.index) - 1] = maxmem
        df.to_csv(memresultfile, sep=',', index=False)

        return None



    # @profile
    def symmetry(self):
        """
            Produing symmetry information of the map by using Proshade
            This function using the binary proshade program  not the python api

        :return:  None
        """

        if self.platform == 'emdb':
            start = timeit.default_timer()
            errlist = []
            finaldict = {}
            symmetryRes = False
            resfactor = 1.0
            if self.met is not None and self.resolution is not None:
                if self.met != 'tomo' and self.met != 'heli':
                    proshade = False
                    if PROSHADEPATH:
                        proshadepath = PROSHADEPATH
                        proshade = True

                    else:
                        try:
                            assert find_executable('proshade') is not None
                            proshadepath = find_executable('proshade')
                            proshade = True
                        except AssertionError:
                            # print('proshade executable is not there, please install proshade.', file=sys.stderr)
                            # print('Symmetry information will not be produced.', file=stys.stderr)
                            sys.stderr.write('proshade executable is not there, please install proshade.\n')
                            sys.stderr.write('Symmetry information will not be produced.\n')

                    if proshade:
                        try:
                            fullmappath = '{}{}'.format(self.workdir, self.mapname)
                            if 'ccpem' not in PROSHADEPATH:
                                # cmd = list((PROSHADEPATH + ' -S -f ' + self.map.filename + ' -s ' + str(float(self.resolution) * resfactor)).split(' '))
                                cmd = list((PROSHADEPATH + ' -S -f ' + self.map.fullname + ' -s ' + str(float(self.resolution) * resfactor)).split(' '))
                            else:
                                shareindex = [idx for idx, s in enumerate(PROSHADEPATH.split('/')) if 'ccpem' in s][0] + 1
                                beforeshare = '/'.join(PROSHADEPATH.split('/')[:shareindex])
                                rvpath = '{}/share'.format(beforeshare)
                                # cmd = list((PROSHADEPATH + ' -S -f ' + self.map.filename + ' -s ' + str(float(self.resolution)*1.5) + ' --rvpath ' + rvpath).split(' '))
                                cmd = list((PROSHADEPATH + ' -S -f ' + self.map.fullname + ' -s ' + str(float(self.resolution) * 1.5) + ' --rvpath ' + rvpath).split(' '))
                            print('Symmetry command: {}'.format(' '.join(cmd)))

                            # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            # code = process.wait()
                            # output = process.stdout.read()

                            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.workdir)
                            output = process.communicate('n\n')[0]
                            errproshade = '!!! ProSHADE ERROR !!!'

                            # For python3 migration to python3 with decode problem of string to bytes
                            if sys.version_info[0] >= 3:
                                for item in output.decode('utf-8').split('\n'):
                                    # item = cline.decode('utf-8').strip()
                                    print(item)
                                    if errproshade in item:
                                        errline = item.strip()
                                        errlist.append(errline)
                                        assert errproshade not in output.decode('utf-8'), errline
                            else:
                                for item in output.split('\n'):
                                    print(item)
                                    if errproshade in item:
                                        errline = item.strip()
                                        errlist.append(errline)
                                        assert errproshade not in output.decode('utf-8'), errline

                            proshadefolder = self.workdir + 'proshade_report'
                            sym_tables = '{}/*.table'.format(proshadefolder)
                            nfileinproshade = len([f for f in glob.glob(sym_tables)])
                            # nfileinproshade = len([f for f in os.listdir(proshadefolder) if os.path.isfile(os.path.join(proshadefolder, f))])
                            if nfileinproshade >= 3:
                                symmetryRes = True
                            # splstr = 'RESULTS'
                            # outputspl = output.split('Detected Cyclic symmetry', 1)
                            # outputspl = re.split('RESULTS', output.decode())
                            # if splstr in output.decode():
                            #     print(outputspl[1])
                            # else:
                            #     print(outputspl[0])

                            # self.moveproshadeResult()
                            end = timeit.default_timer()
                            print('Symmetry time: %s' % (end - start))
                            print('------------------------------------')
                        except:
                            err = 'Symmetry calculation error: {}.'.format(sys.exc_info()[1])
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                            print('------------------------------------')

                        if errlist:
                            finaldict['symmetry'] = {'err': {'symmetry_err': errlist}}
                        else:
                            finaldict['symmetry'] = {'symmetry_info': symmetryRes}

                        try:
                            with codecs.open(self.workdir + self.mapname + '_symmetry.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finaldict, f)
                        except IOError as ioerr:
                            sys.stderr.write('Saving symmetry information to json err: {}.\n'.format(ioerr))



                    else:
                        # print('Proshade is not installed. There will be no symmetry information.', file=sys.stderr)
                        sys.stderr.write('Proshade is not installed. There will be no symmetry information.\n')
                        print('------------------------------------')

                else:
                    # print('This is a {} entry, symmetry will not be calculated'.format(self.met), file=sys.stderr)
                    sys.stderr.write('This is a {} entry, symmetry will not be calculated.\n'.format(self.met))
                    print('------------------------------------')

            else:
                # print('EM method and resolution needed to calculated symmetry information!', file=sys.stderr)
                sys.stderr.write('EM method and resolution needed to calculated symmetry information!\n')
                print('------------------------------------')

        return None

    # Q-score related started from here

    def ochimeracheck(self):
        """

            Check where is old Chimera not for ChimeraX

        :return: the path of old Chimera or None with no Chimera
        """

        ochimeraapp = None
        try:
            if OCHIMERA is not None:
                ochimeraapp = OCHIMERA
                print('Chimera: {}'.format(ochimeraapp))
            else:
                assert find_executable('chimera') is not None
                ochimeraapp = find_executable('chimera')
                print('Chimera: {}'.format(ochimeraapp))

            return ochimeraapp
        except AssertionError:
            # print('Chimera executable is not there.', file=sys.stderr)
            sys.stderr.write('ChimeraX executable is not there.\n')
            return ochimeraapp


    def checkqscore(self, ochimeraapp):

        """

            Check if Qscore is properly installed

        :return: Qscore file full path or None
        """

        qscoreapp = None
        # ochimeraapp = '/nfs/msd/chimera/bin/chimera'

        if ochimeraapp:
            # check if ochimeraapp is a symbolic link
            if os.path.islink(ochimeraapp):
                realchimeraapp = os.path.realpath(path)
            else:
                realchimeraapp = ochimeraapp

            if 'Content' in realchimeraapp:
                vorcontent = ochimeraapp.split('Content')[0]
                mapq = vorcontent + 'Contents/Resources/share/mapq/mapq_cmd.py'
                qscoreapp = mapq if os.path.isfile(mapq) else None
            elif 'bin' in realchimeraapp:
                vorcontent = ochimeraapp.split('bin')[0]
                mapq = vorcontent + 'share/mapq/mapq_cmd.py'
                qscoreapp = mapq if os.path.isfile(mapq) else None
            else:
                print('Chimera is not given in a proper executable or symbolic link format.')
        else:
            print('Chimera was not found.')

        return qscoreapp

    # @profile
    def qscore(self):
        """

            Calculate Q-score

        :return:
        """

        if self.platform == 'emdb':
            errlist = []
            qscoreapp = None
            ochimeraapp = None
            mapname = None
            models = None
            # use a fix value for now, may consider as a argument for later
            numofcores = int(os.cpu_count() / 2)

            try:
                ochimeraapp = self.ochimeracheck()
                qscoreapp = self.checkqscore(ochimeraapp)
                # mapname = self.map.filename
                mapname = self.map.fullname
                if self.models is not None:
                    models = ' '.join([model.filename for model in self.models])
                else:
                    print('No fitted model.')

            except:
                err = 'Q-score preparation error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            # models = ' '.join(['myfirst.cif', 'mysecond.cif'])       # fake test point for multiple cif files
            if qscoreapp and self.models:
                # old Qscore
                # qscorecmd = '{} --nogui --nostatus {} {} {}'.format(ochimeraapp, mapname, models, qscoreapp)
                vorcontents = ochimeraapp.split('Contents')[0] if 'Contents' in ochimeraapp else ochimeraapp.split('bin')[0]
                qscorecmd = '{} {} {} {} {} np={} res={}'.format(sys.executable, qscoreapp, vorcontents,
                                                                 mapname, models, numofcores, self.resolution)
                print(qscorecmd)
                lqscorecmd = qscorecmd.split(' ')
                try:
                    process = subprocess.Popen(lqscorecmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.workdir)
                    output = process.communicate('n\n')[0]
                    errqscore = 'error'
                    if sys.version_info[0] >= 3:
                        for item in output.decode('utf-8').split('\n'):
                            # item = cline.decode('utf-8').strip()
                            print(item)
                            if errqscore in item.lower():
                                errline = item.strip()
                                errlist.append(errline)
                                assert errqscore not in output.decode('utf-8'), errline

                    else:
                        for item in output.split('\n'):
                            print(item)
                            if errqscore in item.lower():
                                errline = item.strip()
                                errlist.append(errline)
                                assert errqscore not in output.decode('utf-8'), errline
                    self.postqscore()

                except:
                    err = 'Q-score calculation error: {}'.format(sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

            else:
                print('Chimera is not detected or no fitted model for this entry. Qscore will not be calclated.')

        return None


    def postqscore(self):

        # self.renameqfiles()
        # self.readqscore()
        self.newread_qscore()
        vtkpack, chimeraapp = self.surface_envcheck()
        self.qscoreview(chimeraapp)

    def renameqfiles(self):
        """
            Rename Q-score output files if in-case, they use *_Alt_A/B.cif to produce the result

        :return:
        """
        altfiles = glob.glob('{}/*.*_Alt_*__Q__emd_*.pdb'.format(self.workdir))
        if altfiles:
            for altfile in altfiles:
                altdir = os.path.dirname(altfile)
                altpdb = os.path.basename(altfile)
                newpdb = re.sub('.cif_Alt_.', '', altpdb)
                alttxt = '{}_All.txt'.format(altpdb[:-4])
                newtxt = '{}_All.txt'.format(newpdb[:-4])
                os.rename('{}/{}'.format(altdir, altpdb), '{}/{}'.format(altdir, newpdb))
                os.rename('{}/{}'.format(altdir, alttxt), '{}/{}'.format(altdir, newtxt))
        else:
            print('No alternative coordinates exist.')

        return None

    def newread_qscore(self):
        """

            Load the Q-score cif file match to Qscore 1.8.2 (temparary)
            Output json file with Q-score information derived from cif file

        :return: None
        """

        mapname = self.mapname[:-4]
        qfiles = []
        qscoreerrlist = []
        modelnum = 0
        qscoredict = OrderedDict()
        finaldict = OrderedDict()
        for model in self.models:
            orgmodel = os.path.basename(model.filename)
            curmodel = orgmodel[:-4]
            qfile = '{}{}__Q__{}.cif'.format(self.workdir, curmodel, mapname)
            if os.path.isfile(qfile):
                p = MMCIFParser()
                p._mmcif_dict = MMCIF2Dict(qfile)
                qscores = p._mmcif_dict['_atom_site.Q-score']
                pqscorecif = p.get_structure(qfile, qfile)
                for atom, qscore in zip(pqscorecif.get_atoms(), qscores):
                    # For Q-score output as '?', convert it to value 0 and set the qscore
                    if qscore == '?':
                        qscore = 0.
                    setattr(atom, 'qscore', float(qscore))
                qscorecif = pqscorecif if len(pqscorecif.get_list()) == 1 else pqscorecif[0]
                qfiles.append(qscorecif)
                try:
                    qscoredict[str(modelnum)] = self.newcif_toqdict(qscorecif, orgmodel)
                    modelnum += 1
                except:
                    err = 'Qscore calculation error (Model: {}): {}.'.format(model.filename, sys.exc_info()[1])
                    qscoreerrlist.append(err)
                    sys.stderr.write(err + '\n')

        if qscoredict:
            finaldict['qscore'] = qscoredict
            try:
                with codecs.open(self.workdir + self.mapname + '_qscore.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except:
                sys.stderr.write('Saving to Qscore json error: {}.\n'.format(sys.exc_info()[1]))
        else:
            print('Qscore was not collected, please check!')


        return None

    def newcif_toqdict(self, qscorecif, orgmodel):
        """

            Given cif biopython object and convert to a dictory which contains all data for JSON

        :return: DICT contains Q-score data from mmcif (biopython object)
        """

        residues = []
        colors = []
        qscores = []
        chain_qscore = {}
        qscore_list = [atom.qscore for atom in qscorecif.get_atoms() if atom.qscore > 1.0]
        protein_qscores = [atom.qscore for atom in qscorecif.get_atoms() if atom.qscore < 1.0]
        average_qscore = round(sum(protein_qscores) / len(protein_qscores), 3)
        if qscore_list:
            min_qscore = min(qscore_list)
            max_qscore = max(qscore_list)
        for chain in qscorecif.get_chains():
            curchain_name = chain.id
            curchain_qscore = [atom.qscore for atom in chain.get_atoms() if atom.qscore < 1.0]
            averagecurchain_qscore = round(sum(curchain_qscore) / len(curchain_qscore), 3)
            atoms_inchain = 0
            qscore_inchain = 0.
            for residue in chain:
                curres_name = residue.resname
                curres_id = residue.id[1]
                atoms_inresidue = 0
                qscore_inresidue = 0.
                for atom in residue:
                    if atom.name.startswith('H'):
                        continue
                    atoms_inchain += 1
                    atoms_inresidue += 1
                    curatom_qscore = atom.qscore
                    qscore_inchain += curatom_qscore
                    qscore_inresidue += curatom_qscore
                if atoms_inresidue != 0.:
                    curres_qscore = round(qscore_inresidue / atoms_inresidue, 3)
                else:
                    curres_qscore = 0.
                if curres_qscore > 1.0:
                    if min_qscore == max_qscore:
                        curres_color = '#000000'
                    else:
                        scaled_qscore = (curres_qscore - min_qscore) / (max_qscore - min_qscore)
                        curres_color = self.__floatohex_aboveone([scaled_qscore])[0]
                else:
                    curres_color = self.__floatohex([curres_qscore])[0]

                icode = residue.id[2]
                if icode:
                    curres_string = '{}:{}{}{}'.format(curchain_name, curres_id, icode, curres_name)
                else:
                    curres_string = '{}:{}{}'.format(curchain_name, curres_id, curres_name)
                residues.append(curres_string)
                colors.append(curres_color)
                qscores.append(curres_qscore)
            averageqscore_incolor = self.__floatohex([averagecurchain_qscore])[0]
            chain_qscore[curchain_name] = {'value': averagecurchain_qscore, 'color': averageqscore_incolor}

        tdict = OrderedDict([
            ('averageqscore', average_qscore), ('color', colors),
            ('inclusion', qscores),
            ('residue', residues),
            ('chainqscore', chain_qscore)
        ])

        resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])

        return resultdict


    def readqscore(self):
        """

            Load the Q-score pdb file(temparary)

        :return:
        """

        mapname = self.mapname[:-4]
        qfiles = []
        qscoreerrlist = []
        result = {}
        modelnum = 0
        qscoredict = OrderedDict()
        finaldict = OrderedDict()
        for model in self.models:
            orgmodel = os.path.basename(model.filename)
            curmodel = orgmodel[:-4]
            qfile = '{}{}__Q__{}.pdb'.format(self.workdir, curmodel, mapname)
            if os.path.isfile(qfile):
                p = orgPDBParser()
                pqscorepdb = p.get_structure('myqfile', qfile)
                qscorepdb = pqscorepdb if len(pqscorepdb.get_list()) == 1 else pqscorepdb[0]
                qfiles.append(qscorepdb)
                try:
                    # qscoredict[str(modelnum)] = self.pdbtoqdict(qscorepdb, orgmodel)
                    qscoredict[str(modelnum)] = self.newpdbtoqdict(qscorepdb, orgmodel)
                    modelnum += 1
                except:
                    err = 'Qscore calculation error (Model: {}): {}.'.format(model.filename, sys.exc_info()[1])
                    qscoreerrlist.append(err)
                    sys.stderr.write(err + '\n')

        if qscoredict:
            finaldict['qscore'] = qscoredict
            try:
                with codecs.open(self.workdir + self.mapname + '_qscore.json', 'w',
                                 encoding='utf-8') as f:
                    json.dump(finaldict, f)
            except:
                sys.stderr.write('Saving to Qscore json error: {}.\n'.format(sys.exc_info()[1]))
        else:
            print('Qscore was not collected, please check!')


        return None

    def newpdbtoqdict(self, qscorepdb, orgmodel):
        """

            Given pdb biopython object and convert to a dict which contains all data for JSON

        :return: DICT contains all data
        """

        residues = []
        colors = []
        qscores = []
        chain_qscore = {}
        qscore_list = [atom.bfactor for atom in qscorepdb.get_atoms() if atom.bfactor > 1.0]
        protein_qscores = [atom.bfactor for atom in qscorepdb.get_atoms() if atom.bfactor < 1.0]
        average_qscore = round(sum(protein_qscores) / len(protein_qscores), 3)
        if qscore_list:
            min_qscore = min(qscore_list)
            max_qscore = max(qscore_list)
        for chain in qscorepdb.get_chains():
            curchain_name = chain.id
            curchain_qscore = [atom.bfactor for atom in chain.get_atoms() if atom.bfactor < 1.0]
            averagecurchain_qscore = round(sum(curchain_qscore) / len(curchain_qscore), 3)
            atoms_inchain = 0
            qscore_inchain = 0.
            for residue in chain:
                curres_name = residue.resname
                curres_id = residue.id[1]
                atoms_inresidue = 0
                qscore_inresidue = 0.
                for atom in residue:
                    if atom.name.startswith('H'):
                        continue
                    atoms_inchain += 1
                    atoms_inresidue += 1
                    curatom_qscore = atom.bfactor
                    qscore_inchain += curatom_qscore
                    qscore_inresidue += curatom_qscore
                curres_qscore = round(qscore_inresidue / atoms_inresidue, 3)
                if curres_qscore > 1.0:
                    if min_qscore == max_qscore:
                        curres_color = '#000000'
                    else:
                        scaled_qscore = (curres_qscore - min_qscore) / (max_qscore - min_qscore)
                        curres_color = self.__floatohex_aboveone([scaled_qscore])[0]
                else:
                    curres_color = self.__floatohex([curres_qscore])[0]

                icode = residue.id[2]
                if icode:
                    curres_string = '{}:{}{}{}'.format(curchain_name, curres_id, icode, curres_name)
                else:
                    curres_string = '{}:{}{}'.format(curchain_name, curres_id, curres_name)
                residues.append(curres_string)
                colors.append(curres_color)
                qscores.append(curres_qscore)
            averageqscore_incolor = self.__floatohex([averagecurchain_qscore])[0]
            chain_qscore[curchain_name] = {'value': averagecurchain_qscore, 'color': averageqscore_incolor}

        tdict = OrderedDict([
            ('averageqscore', average_qscore), ('color', colors),
            ('inclusion', qscores),
            ('residue', residues),
            ('chainqscore', chain_qscore)

        ])

        resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])

        return resultdict

    def pdbtoqdict(self, qscorepdb, orgmodel):
        """

            Given pdb biopython object and convert to a dict which contains all data for JSON

        :return: DICT contains all data
        """

        allkeys = []
        allvalues = []
        preresid = 0
        prechain = ''
        aiprechain = ''
        preres = ''
        rescount = 1
        atomcount = 0
        chainatomcount = 0
        resocc = 0.
        allatoms = 0
        allocc = 0.
        chainocc = 0.
        chaincount = 1
        chainatoms = 0
        chainqscore = {}
        for atom in qscorepdb:
            if not atom.atom_name.startswith('H'):
                allatoms += 1
                allocc += atom.temp_fac
                atomcount += 1
                chainatomcount += 1
                if (atomcount == 1) or (atom.res_no == preresid and atom.chain == prechain):
                    preresid = atom.res_no
                    prechain = atom.chain
                    preres = atom.res
                    resocc += atom.temp_fac
                else:
                    atomcount -= 1
                    keystr = prechain + ':' + str(preresid) + preres
                    allkeys.append(keystr)
                    resoccvalue = resocc / atomcount
                    allvalues.append(resoccvalue)
                    preresid = atom.res_no
                    prechain = atom.chain
                    preres = atom.res
                    atomcount = 1
                    rescount += 1
                    resocc = atom.temp_fac
                if (chainatomcount == 1) or (atom.chain == aiprechain):
                    chainatoms += 1
                    aiprechain = atom.chain
                    chainocc += atom.temp_fac
                else:
                    qvalue = round(chainocc / chainatoms, 3)
                    qcolor = self.__floatohex([qvalue])[0]
                    # chainqscore[aiprechain] = {'value': qvalue, 'color': qcolor}
                    if aiprechain in chainqscore.keys():
                        # chainqscore[prechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
                        pass
                    else:
                        chainqscore[aiprechain] = {'value': qvalue, 'color': qcolor}
                    chainatoms = 1
                    chainocc = atom.temp_fac
                    aiprechain = atom.chain
                    chaincount += 1

        qvalue = round(chainocc / chainatoms, 3)
        qcolor = self.__floatohex([qvalue])[0]
        if aiprechain in chainqscore.keys():
            # chainqscore[prechain + '_' + str(aivalue)] = {'value': aivalue, 'color': aicolor}
            pass
        else:
            chainqscore[aiprechain] = {'value': qvalue, 'color': qcolor}
        lastvalue = resocc / atomcount
        keystr = prechain + ':' + str(preresid) + preres
        allkeys.append(keystr)
        allvalues.append(lastvalue)
        colours = self.__floatohex([i for i in allvalues])
        averageocc = allocc / allatoms

        tdict = OrderedDict([
            ('averageocc', round(averageocc, 6)), ('color', colours),
            ('inclusion', [round(elem, 6) for elem in allvalues]),
            ('residue', allkeys),
            ('chainqscore', chainqscore)

        ])

        resultdict = OrderedDict([('name', orgmodel), ('data', tdict)])

        return resultdict

    def qscoreview(self, chimeraapp):
        """

            X, Y, Z images which model was colored by Q-score

        :return:
        """

        # read json
        start = timeit.default_timer()
        injson = glob.glob(self.workdir + '*_qscore.json')
        basedir = self.workdir
        mapname = self.mapname
        locCHIMERA = chimeraapp
        bindisplay = os.getenv('DISPLAY')
        errlist = []

        fulinjson = injson[0] if injson else None
        try:
            if fulinjson:
                with open(fulinjson, 'r') as f:
                    args = json.load(f)
            else:
                args = None
                print('There is no Qscore json file.')
        except TypeError:
            err = 'Open Qscore JSON error: {}.'.format(sys.exc_info()[1])
            errlist.append(err)
            sys.stderr.write(err + '\n')
        else:
            if args is not None:
                models = args['qscore']
                try:
                    del models['err']
                except:
                    print('Qscore json result is correct')

                print('There is/are %s model(s).' % len(models))
                for (key, value) in iteritems(models):
                    # for (key2, value2) in iteritems(value):
                    keylist = list(value)
                    for key in keylist:
                        if key != 'name':
                            colors = value[key]['color']
                            residues = value[key]['residue']
                            qscores = value[key]['inclusion']
                        else:
                            modelname = value[key]
                            model = self.workdir + modelname
                            chimerafname = '{}_{}_qscore_chimera.cxc'.format(modelname, mapname)
                            surfacefn = '{}{}_{}'.format(basedir, modelname, mapname)
                            chimeracmd = chimerafname
                            # pdbmodelname = '{}{}__Q__{}.pdb'.format(basedir, modelname[:-4], mapname[:-4])
                            pdbmodelname = '{}{}__Q__{}.cif'.format(basedir, modelname[:-4], mapname[:-4])

                    with open(self.workdir + chimeracmd, 'w') as fp:
                        fp.write("open " + str(pdbmodelname) + " format mmcif" + '\n')
                        # fp.write("open " + str(pdbmodelname) + " format pdb" + '\n')
                        fp.write('show selAtoms ribbons' + '\n')
                        fp.write('hide selAtoms' + '\n')

                        for (color, residue, qscore) in zip(colors, residues, qscores):
                            chain, restmp = residue.split(':')
                            # Not sure if all the letters should be replaced
                            # 1st way of getting res_id
                            # res_id = re.sub("\D", "", restmp)
                            # 2nd way of getting res
                            res_id = re.findall(r'-?\d+', restmp)[0]
                            fp.write(
                                'color /' + chain + ':' + res_id + ' ' + color + '\n'
                            )
                            if qscore > 1.0:
                                fp.write(
                                    'show /' + chain + ':' + res_id + ' atoms' + '\n'
                                    'style /' + chain + ':' + res_id + ' stick' + '\n'
                                )
                        fp.write(
                            "set bgColor white" + '\n'
                            "lighting soft" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_zqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "turn x -90" + '\n'
                            "turn y -90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_xqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "view orient" + '\n'
                            "turn x 90" + '\n'
                            "turn z 90" + '\n'
                            "view cofr True" + '\n'
                            "save " + str(surfacefn) + "_yqscoresurface.jpeg" + " supersample 3 width 1200 height 1200" + '\n'
                            "close all" + "\n"
                            "exit"
                        )
                    try:
                        if not bindisplay:
                            subprocess.check_call(locCHIMERA + " --offscreen --nogui " + self.workdir + chimeracmd,
                                                  cwd=self.workdir, shell=True)
                            print('Colored models based on Qscore were produced.')
                        else:
                            subprocess.check_call(locCHIMERA + " " + self.workdir + chimeracmd, cwd=self.workdir,
                                                  shell=True)
                            print('Colored models based on Qscore were produced.')
                    except subprocess.CalledProcessError as suberr:
                        err = 'Saving model {} Qscore view error: {}.'.format(modelname, suberr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    try:
                        self.scale_surfaceview()
                    except:
                        err = 'Scaling model Qscore view error: {}.'.format(sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    jpegs = glob.glob(self.workdir + '/*surface.jpeg')
                    modelsurf = dict()
                    finalmmdict = dict()
                    if self.models:
                        # print "self.models:%s" % self.models
                        for model in self.models:
                            modelname = os.path.basename(model.filename)
                            surfacefn = '{}_{}'.format(modelname, self.mapname)
                            modelmapsurface = dict()
                            for jpeg in jpegs:
                                if modelname in jpeg and 'xqscore' in jpeg:
                                    modelmapsurface['x'] = str(surfacefn) + '_scaled_xqscoresurface.jpeg'
                                if modelname in jpeg and 'yqscore' in jpeg:
                                    modelmapsurface['y'] = str(surfacefn) + '_scaled_yqscoresurface.jpeg'
                                if modelname in jpeg and 'zqscore' in jpeg:
                                    modelmapsurface['z'] = str(surfacefn) + '_scaled_zqscoresurface.jpeg'
                            if errlist:
                                modelmapsurface['err'] = {'model_fit_err': errlist}
                            modelsurf[modelname] = modelmapsurface
                        finalmmdict['qscore_surface'] = modelsurf

                        try:
                            with codecs.open(self.workdir + self.mapname + '_qscoreview.json', 'w',
                                             encoding='utf-8') as f:
                                json.dump(finalmmdict, f)
                        except:
                            sys.stderr.write(
                                'Saving Qscore view to JSON error: {}.\n'.format(sys.exc_info()[1]))

                end = timeit.default_timer()
                print('Qscore surface time: %s' % (end - start))
                print('------------------------------------')

    def qscorejson(self):
        """
            Qscore json file feed into the page

        :return:
        """

        pass


    # Qscore related ended here

    def moveproshadeResult(self):

        import shutil

        cwd = os.getcwd()
        srcdir = '{}/proshade_report'.format(cwd)
        desdir = self.workdir
        desprodir = '{}/proshade_report'.format(desdir)
        if os.path.isdir(desprodir):
            shutil.rmtree(desprodir)
        if os.path.isdir(srcdir):
            dest = shutil.move(srcdir, desdir)
        else:
            dest = None
            print('No proshade result to be moved.')

        return dest

    def symmetrytojson(self, output):
        """

            Convert the output of proshade symmetry calculation to json which can be used further

        :param output:
        :return:
        """

        pass

    def strudel(self):
        """

        :return:
        """
        if self.platform == 'emdb' and self.met != 'tomo':
            errlist = []
            final_range = None
            res_ranges = [[2.0, 2.3], [2.3, 2.5], [2.5, 2.8], [2.8, 3.0], [3.0, 3.2], [3.2, 3.5], [3.5, 4.0]]
            try:
                for idx, crange in enumerate(res_ranges):
                    if crange[0] < float(self.resolution) <= crange[1]:
                        final_range = crange
                        break
                else:
                    print('Map did not fall into any available resolution range.')
                    print('------------------------------------')
            except:
                err = 'Strudel motif lib resolution range check error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            strudelapp = None
            # use a fix value for now, may consider as a argument for later
            try:
                # strudelapp = self.checkstrudelscore(ochimeraapp)
                mapname = self.map.fullname
                if self.models is not None:
                    models = ' '.join([model.filename for model in self.models])
                else:
                    print('No fitted model for Strudel calculation.')
                    print('------------------------------------')

            except:
                err = 'Strudel preparation error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            lib_root = None
            if LIB_STRUDEL_ROOT is not None:
                lib_root = LIB_STRUDEL_ROOT
            elif LIB_STRUDEL_ROOT is None and self.strudellib is not None:
                lib_root = self.strudellib
            else:
                lib_root = None

            # if strudelapp and self.models:
            if final_range and self.models:
                for model in self.models:
                    full_model = '{}{}'.format(self.workdir, os.path.basename(model.filename))
                    full_map = '{}{}'.format(self.workdir, self.mapname)
                    lib_path = '{}/motifs_{}-{}'.format(lib_root, final_range[0], final_range[1])
                    out_path = '{}_strudel'.format(full_model)

                    rerr = run_strudel(full_model, full_map, lib_path, out_path, self.platform)
                    if rerr:
                        err = 'Strudel calculation error: {}'.format(rerr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                        print('------------------------------------')

            else:
                print('No model or resolution is not covered in the motif library (<4.0Å) ')
                print('------------------------------------')

        return None




    def real_mmcc(self):
        """
            Calculation real space cross-correlation between primary map and model-map (Refmac)

        :return:
        """

        if self.modelsmaps and self.platform == 'emdb':
            start = timeit.default_timer()
            rmmccc = {}
            mmcc_dict = {}
            errlist = []
            for modelmap in self.modelsmaps:
                print(modelmap)
                modelmap_name = os.path.basename(modelmap)
                try:
                    mmap = mrcfile.mmap(modelmap, mode='r')
                    mmapdata = mmap.data
                    mmcc = run_realmmcc(self.map.data, mmapdata)[1]
                    mmcc_dict[modelmap_name] = mmcc
                except:
                    err = 'Map and model {} real space CC calculation error: {}.'.format(modelmap_name, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')

            if errlist:
                rmmccc['err'] = {'rmmccc_err': errlist}
            else:
                print('No error in rmmccc calculation.')

            rmmccc['rmmccc'] = mmcc_dict
            if rmmccc:
                with codecs.open(self.workdir + self.mapname + '_rmmccscore.json', 'w', encoding='utf-8') as f:
                    json.dump(rmmccc, f)
            else:
                print('No model map CC is calculated, check the error information.')

            end = timeit.default_timer()
            print('Real space model and map Cross-Correlation Coefficient time: %s' % (end - start))
            print('------------------------------------')

        else:
            print('No model map for model and map real space cross-correlation calculation.')
            print('------------------------------------')

        return None


    # @profile
    def smoc(self):

        """

                Calculate SMOC score from TEMPy

        :return:
        """

        from TEMPy.ScoringFunctions import ScoringFunctions

        if self.platform == 'emdb':
            errlist = []
            try:
                chainscoredict = {}
                chainresdict = {}
                for model in self.models:
                    name = os.path.basename(model.filename)
                    chainscore[name], chainres[name] = ScoringFunctions.SMOC(self.map.filename, self.resolution, model,
                     win=11, rigid_body_file=None, sigma_map=0.225, write=False, c_mode=True)
                return chainscoredict, chainresdict
            except:
                err = 'SMOC calculation error: {}.'.format(sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

        return None


    def emringer(self):
        """

            Emringer score

        :return:
        """

        if self.platform == 'emdb' and self.met != 'tomo':
            start = timeit.default_timer()
            errlist = []
            # if strudelapp and self.models:
            if self.models:
                for model in self.models:
                    full_model = '{}{}'.format(self.workdir, os.path.basename(model.filename))
                    full_map = '{}{}'.format(self.workdir, self.mapname)
                    out_path = '{}_emringer'.format(full_model)

                    rerr = run_emringer(full_model, full_map, out_path)
                    end = timeit.default_timer()
                    print('EMRinger time: %s' % (end - start))
                    print('------------------------------------')
                    if rerr:
                        err = 'Strudel calculation error: {}'.format(rerr)
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                        print('------------------------------------')

            else:
                print('No model or resolution is not covered in the motif library (<4.0Å) ')
                print('------------------------------------')

        return None


    def threedfsc(self):
        """

            Emringer score

        :return:
        """

        if self.platform == 'emdb' and self.met != 'tomo':
            if self.threedfscdir is not None:
                start = timeit.default_timer()
                errlist = []
                if self.hmodd is not None and self.hmeven is not None:
                    out_path = '{}_3dfsc'.format(self.map.fullname)
                    vxsizes = self.map.voxel_size
                    if vxsizes.x == vxsizes.y == vxsizes.z and self.hmodd.voxel_size == self.hmeven.voxel_size:
                        rerr = run_threedfsc(self.hmodd.fullname, self.hmeven.fullname, self.map.fullname,
                                             vxsizes.x, out_path, self.threedfscdir)
                        end = timeit.default_timer()
                        print('3DFSC time: %s' % (end - start))
                        if rerr:
                            err = '3DFSC calculation error: {}'.format(rerr)
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                            print('------------------------------------')
                        else:
                            print('------------------------------------')

                    else:
                        print('3DFSC input map need to be cubic and two half maps need to have same voxel size.')
                        print('------------------------------------')

                else:
                    print('No half map information for 3DFSC calculation.')
                    print('------------------------------------')
            else:
                print('No threedfsc information provided, use --threeddir/-threedd <full file path>.')

        return None
