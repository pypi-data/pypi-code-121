#!/usr/bin/env python3

import numpy as np
import os
import struct
from datetime import datetime

# Compatible with MM-PIHM 1.0.0-rc4

def read_mesh(pihm_dir, simulation):
    '''
    Read MM-PIHM mesh input file.
    '''

    # Check if simulation is an ensemble member
    if simulation.rfind(".") != -1:
        if simulation[simulation.rfind(".") + 1:].isnumeric():
            simulation = simulation[0:simulation.rfind(".")]

    # Full file name
    fname = '%s/input/%s/%s.mesh' % (pihm_dir, simulation, simulation)

    # Read mesh file into an array of strings with leading white spaces removed
    # Line starting with "#" are not read in
    with open(fname) as file:
        meshstr = [line.strip() for line in file if line.strip() and line.strip()[0] != '#']

    # Read number of elements
    num_elem = int(meshstr[0].split()[1])

    # Read nodes information
    tri = []
    for line in meshstr[2:2 + num_elem]:
        tri.append([int(c) - 1 for c in line.split()[1:4]])

    # Read number of nodes
    num_nodes = int(meshstr[2 + num_elem].split()[1])

    # Read X, Y, ZMIN, and ZMAX
    x = []
    y = []
    zmin = []
    zmax = []
    for line in meshstr[4 + num_elem:4 + num_elem + num_nodes]:
        strs = line.split()[1:]
        x.append(float(strs[0]))
        y.append(float(strs[1]))
        zmin.append(float(strs[2]))
        zmax.append(float(strs[3]))

    return (num_elem, num_nodes, np.array(tri), np.array(x), np.array(y), np.array(zmin), np.array(zmax))


def read_river(pihm_dir, simulation):
    '''
    Read MM-PIHM river input file
    '''

    # Check if simulation is an ensemble member
    if simulation.rfind(".") != -1:
        if simulation[simulation.rfind(".") + 1:].isnumeric():
            simulation = simulation[0:simulation.rfind(".")]

    # Full file name
    fname = '%s/input/%s/%s.riv' % (pihm_dir, simulation, simulation)

    # Read river file into an array of strings with leading white spaces removed
    # Line starting with "#" are not read in
    with open(fname) as file:
        riverstr = [line.strip() for line in file if line.strip() and line.strip()[0] != '#']

    # Read number of river segments
    num_rivers = int(riverstr[0].split()[1])

    # Read nodes and outlets information
    from_nodes = []
    to_nodes = []
    outlets = []
    for line in riverstr[2:2 + num_rivers]:
        strs = line.split()[0:4]
        from_nodes.append(int(strs[1]) - 1)
        to_nodes.append(int(strs[2]) - 1)
        if int(strs[3]) == -3:
            outlets.append(int(strs[0]) - 1)

    return (num_rivers, np.array(from_nodes), np.array(to_nodes), np.array(outlets))


def read_output(pihm_dir, simulation, outputdir, ext):
    '''
    Read MM-PIHM output file
    '''

    # Read number of river segments and elements from input files
    num_rivers, _, _, _ = read_river(pihm_dir, simulation)
    num_elem, _, _, _, _, _, _ = read_mesh(pihm_dir, simulation)

    # Determine output dimension, variable name and unit from extension
    dim = num_rivers if ext[0:6] == 'river.' else num_elem

    # Default values
    varname = 'MM-PIHM output'
    unit = 'N/A'

    DESC, UNIT, LOC = range(3)

    outputs = {
        # PIHM output
        'surf': ['Surface water', 'm', [0, 0]],
        'unsat': ['Unsaturated zone storage', 'm', [0, 0]],
        'gw': ['Groundwater storage', 'm', [0, 0]],
        'river.stage': ['River stage', 'm', [0, 0]],
        'snow': ['Water equivalent snow depth', 'm', [0, 0]],
        'is': ['Interception storage', 'm', [0, 0]],
        'infil': ['Infiltration', 'm s$^{-1}$', [0, 0]],
        'recharge': ['Recharge', 'm s$^{-1}$', [0, 0]],
        'ec': ['Canopy evaporation', 'm s$^{-1}$', [0, 0]],
        'ett': ['Transpiration', 'm s$^{-1}$', [0, 0]],
        'edir': ['Soil evaporation', 'm s$^{-1}$', [0, 0]],
        'river.flx': ['River flux %s', 'm$^3$ s$^{-1}$', [9, 9]],
        'subflx': ['Subsurface flux %s', 'm$^3$ s$^{-1}$', [6, 6]],
        'surfflx': ['Surface flux %s', 'm$^3$ s$^{-1}$', [7, 7]],
        # Flux module output
        't1': ['Land surface temperature', 'K', [0, 0]],
        'stc': ['Soil temperature (Layer %s)', 'K', [3, 3]],
        'smc': ['Soil moisture content (Layer %s)', 'm$^3$ m$^{-3}$', [3, 3]],
        'swc': ['Soil water content (Layer %s)', 'm$^3$ m$^{-3}$', [3, 3]],
        'snowh': ['Snow depth', 'm', [0, 0]],
        'iceh': ['Ice depth', 'm', [0, 0]],
        'albedo': ['Albedo', '-', [0, 0]],
        'le': ['Latent heat flux', 'W m$^{-2}$', [0, 0]],
        'sh': ['Sensible heat flux', 'W m$^{-2}$', [0, 0]],
        'g': ['Ground heat flux', 'W m$^{-2}$', [0, 0]],
        'etp': ['Potential evaporation', 'W m$^{-2}$', [0, 0]],
        'esnow': ['Snow sublimation', 'W m$^{-2}$', [0, 0]],
        'rootw': ['Root zone vailable soil moisture', '-', [0, 0]],
        'soilm': ['Total soil moisture', 'm', [0, 0]],
        'solar': ['Solar radiation', 'W m$^{-2}$', [0, 0]],
        'ch': ['Surface exchange coefficient', 'm s$^{-1}$', [0, 0]],
        # BGC module output
        'lai': ['LAI', 'm$^2$ m$^{-2}$', [0, 0]],
        'npp': ['NPP', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'nep': ['NEP', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'nee': ['NEE', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'gpp': ['GPP', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'mr': ['Maintenace respiration', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'gr': ['Growth respiration', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'hr': ['Heterotrophic respiration', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'fire': ['Fire losses', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'litfallc': ['Litter fall', 'kgC m$^{-2}$ day$^{-1}$', [0, 0]],
        'vegc': ['Vegetation carbon', 'kgC m$^{-2}$', [0, 0]],
        'agc': ['Aboveground carbon', 'kgC m$^{-2}$', [0, 0]],
        'litrc': ['Litter carbon', 'kgC m$^{-2}$', [0, 0]],
        'soilc': ['Soil carbon', 'kgC m$^{-2}$', [0, 0]],
        'totalc': ['Total carbon', 'kgC m$^{-2}$', [0, 0]],
        'sminn': ['Soil mineral nitrogen', 'kgN m$^{-2}$', [0, 0]],
        # Cycles output
        'eres': ['Residue evaporation', 'm s$^{-1}$', [0, 0]],
        'grain_yield': ['%s grain yield', 'Mg ha$^{-1}$', [11, 12]],
        'forage_yield': ['%s forage yield', 'Mg ha$^{-1}$', [12, 13]],
        'shoot': ['%s shoot biomass', 'Mg ha$^{-1}$', [5, 6]],
        'root': ['%s root biomass', 'Mg ha$^{-1}$', [4, 5]],
        'radintcp': ['%s radiation interception', '-', [8, 9]],
        'wstress': ['%s water stress', '-', [7, 8]],
        'nstress': ['%s N stress', '-', [7, 8]],
        'transp': ['%s transpiration', 'mm day$^{-1}$', [6, 7]],
        'pottransp': ['%s potential transpiration', 'mm day$^{-1}$', [9, 10]],
        'no3': ['Soil profile NO$_3^-$', 'Mg ha$^{-1}$', [0, 0]],
        'nh4': ['Soil profile NH$_4^+$', 'Mg ha$^{-1}$', [0, 0]],
        'river.no3': ['River NO$_3^-$', 'Mg ha$^{-1}$', [0, 0]],
        'river.nh4': ['River NH$_4^+$', 'Mg ha$^{-1}$', [0, 0]],
        'denitrif': ['Denitrification', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'nitrif': ['Nitrification', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'immobil': ['N immobilization', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'mineral': ['N mineralization', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'volatil': ['N volatilization', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'no3leaching': ['NO$_3^-$ leaching', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'nh4leaching': ['NH$_4^+$ leaching', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'soc': ['Soil organic carbon', 'Mg ha$^{-1}$', [0, 0]],
        'n2o_nitrif': ['N$_2$O emission from nitrification', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'n2o_denitrif': ['N$_2$O emission from denitrification', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'n_harvest': ['N in harvest', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'n_fert': ['N from fertilization', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'n_auto': ['N auto added', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        'n_fix': ['N fixation', 'Mg ha$^{-1}$ day$^{-1}$', [0, 0]],
        # Deep groundwater module output
        'deep.unsat': ['Deep zone unsaturated storage', 'm', [0, 0]],
        'deep.gw': ['Deep groundwater storage', 'm', [0, 0]],
        'deep.infil': ['Deep zone infiltration', 'm s$^{-1}$', [0, 0]],
        'deep.recharge': ['Deep zone recharge', 'm s$^{-1}$', [0, 0]],
        'deep.flow': ['Deep layer lateral flow %s', 'm$^3$ s$^{-1}$', [9, 9]],
        # RT module output
        'conc': ['%s concentration', 'mol L$^{-1}$', [4, 5]],
        'deep.conc': ['Deep zone %s concentration', 'mol L$^{-1}$', [9, 10]],
        'river.conc': ['Stream %s concentration', 'mol L$^{-1}$', [10, 11]],
        'river.chflx': ['River %s flux',  'kmol s$^{-1}$', [11, 12]],
    }

    # Find output description and unit
    for key, val in outputs.items():
        tmpstr = ext.lower() if val[LOC][0] == 0 else ext[0:val[LOC][0]].lower()
        if tmpstr == key:
            varname = val[DESC] % (ext[val[LOC][1]:]) if val[LOC][1] > 0 else val[DESC]
            unit = val[UNIT]
            break

    # Full file name (binary file)
    fname = '%s/output/%s/%s.%s.dat' % (pihm_dir, outputdir, simulation, ext)

    # Check size of output file
    fsize = int(os.path.getsize(fname) / 8)

    with open(fname, 'rb') as binfile:
        # Read binary output file
        data_str = binfile.read()
        data_tuple = struct.unpack('%dd' %(fsize), data_str)

        # Rearrange read values to numpy array
        data_array = np.resize(data_tuple, (int(fsize / (dim + 1)), dim + 1))

        # Output values
        sim_val = data_array[:, 1:]

        # Convert simulation time
        sim_time = [datetime.utcfromtimestamp(data_array[i, 0]) for i in range(int(fsize / (dim + 1)))]

    return (np.array(sim_time), sim_val, varname, unit)
