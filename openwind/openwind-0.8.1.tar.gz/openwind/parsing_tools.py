#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file

"""Tools for parsing files from other software, and writing OW compatible file."""

import numpy as np
import os

def convert_RESONANS_file(filename):
    # add suffix '_OW' to avoid the deletion of source file if a csv is given
    file_ow = os.path.splitext(filename)[0] + '_OW.csv'

    lengthes = []
    input_radii = []
    output_radii = []

    # read RESONANS file format (hole not accounted for yet)
    n=0
    with open(filename,'r') as file:
        # first lines are special
        line = next(file)
        N=int(line)

        line = next(file)
        Nb_holes = int(line)
        if(Nb_holes > 0):
            raise ValueError("Holes are not yet accounted for in RESONANS format. "
                             +"Please format your instrument in a native Openwind format. "+
                             "Feel free to send us a RESONANS file with holes along with format explanations.")


        line = next(file)
        Nb_fing = int(line)

        line = next(file)
        temperature = float(line)

        line = next(file)
        comp_type = line.split('\n')[0]

        line = next(file)
        name = line.split('\n')[0]

        while(n<N):
            line=next(file)
            if(line.startswith('#')):
                # this is a comment
                continue

            # data are provided in blocks of 5 lines
            # 1- L
            L = float(line)
            line = next(file)
            # 2- Rin
            Rin = float(line)
            line = next(file)
            # 3- Rout
            Rout = float(line)
            line = next(file)
            # 4- nb holes
            nb_holes = int(float(line))
            line = next(file)
            # 5- nb subdiv
            nb_subdiv = int(float(line))

            lengthes.append(L)
            input_radii.append(Rin)
            output_radii.append(Rout)
            n=n+1
    # next lines are for RESONANS visualization
    # the instrument is defined from the bell : we flip it
    lengthes = np.flipud(lengthes)
    input_radii = np.flipud(input_radii)
    output_radii = np.flipud(output_radii)

    #  write openwind format file
    Ltot = 0
    with open(file_ow,'w') as file:
        for (L,Rin,Rout) in zip(lengthes,input_radii,output_radii):
            file.write(f"{Ltot} {Ltot+L} {Rin} {Rout} linear \n")
            Ltot = Ltot+L

    return file_ow
