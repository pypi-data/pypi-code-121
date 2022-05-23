#!/usr/bin/env python

"""
mainva.py

mainva class used to run the main function of validation
analysis

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



import timeit
import os
import sys
from memory_profiler import memory_usage
from va.validationanalysis import ValidationAnalysis
from va.preparation import PreParation as prep
from va.metrics.strudel import run_strudel
import threading
try:
    from PATHS import MAP_SERVER_PATH
except ImportError:
    MAP_SERVER_PATH = None
from memory_profiler import profile
sys.stdout.flush()

def allruns(validationobj, runs):
    """
        Each single run included here

    :param validationobj: validation object from ValidationAnalysis module
    :param runs: list of string which represent each of the function
    :return: None
    """

    # Projections
    if 'projection' in runs:
        validationobj.orthogonal_projections()
        validationobj.rawmap_projections()
        validationobj.orthogonal_max()
        validationobj.rawmap_max()
        validationobj.orthogonal_min()
        validationobj.rawmap_min()
        validationobj.orthogonal_median()
        validationobj.rawmap_median()
        validationobj.orthogonal_std()
        validationobj.rawmap_std()

    # Central slice
    if 'central' in runs:
        validationobj.central_slice()
        validationobj.rawmap_central_slice()

    # Largest variance
    if 'largestvariance' in runs:
        validationobj.largest_variance()
        validationobj.rawmap_largest_variance()

    # Generate atom inclusion and residue inclusion json file
    if 'inclusion' in runs:
        validationobj.atom_inclusion()

    # Sureface views
    if 'surface' in runs:
        validationobj.surfaces()

    # Masks views
    if 'mask' in runs:
        validationobj.masks()

    # Desnity distribution
    if 'density' in runs:
        validationobj.mapdensity_distribution()
        validationobj.rawmapdensity_distribution()

    # Contour level verses volume
    if 'volume' in runs:
        validationobj.volumecontour()

    # rmcc/CCC
    if 'rmmcc' in runs:
        validationobj.real_mmcc()

    # RAPS
    if 'raps' in runs:
        # validationobj.raps()
        validationobj.new_raps()
        validationobj.rawmap_raps()
        # validationobj.pararaps()

    # FSC
    if 'fsc' in runs:
        validationobj.fscs()

    # Sureface views
    if 'surface' in runs:
        validationobj.surfaces()

    # mmFSC
    if 'mmfsc' in runs:
        validationobj.mmfsc()

    # Symmetry
    if 'symmetry' in runs:
        validationobj.symmetry()

    # Strudel
    if 'strudel' in runs:
        validationobj.strudel()

    # Q-score
    if 'qscore' in runs:
        validationobj.qscore()

    # SMOC
    if 'smoc' in runs:
        validationobj.smoc()

    # EMringer
    if 'emringer' in runs:
        validationobj.emringer()

    # 3DFSC
    # if '3dfsc' in runs:
    #     validationobj.threedfsc()

    return None


def inallruns(validationobj, runs):
    """
        Each single run included here

    :param validationobj: validation object from ValidationAnalysis module
    :param runs: list of string which represent each of the function
    :return: None
    """

    def without_strudel():
        # Projections
        if 'projection' in runs:
            validationobj.orthogonal_projections()
            validationobj.rawmap_projections()
            validationobj.orthogonal_max()
            validationobj.orthogonal_std()

        # Central slice
        if 'central' in runs:
            validationobj.central_slice()
            validationobj.rawmap_central_slice()

        # Largest variance
        if 'largestvariance' in runs:
            validationobj.imgvariance()
            validationobj.rawmap_imgvariance()

        # Generate atom inclusion and residue inclusion json file
        if 'inclusion' in runs:
            validationobj.atom_inclusion()

        # Sureface views
        if 'surface' in runs:
            validationobj.surfaces()

        # Masks views
        if 'mask' in runs:
            validationobj.masks()

        # Desnity distribution
        if 'density' in runs:
            validationobj.mapdensity_distribution()
            validationobj.rawmapdensity_distribution()

        # Contour level verses volume
        if 'volume' in runs:
            validationobj.volumecontour()

        # rmcc/CCC
        if 'rmmcc' in runs:
            validationobj.real_mmcc()

        # RAPS
        if 'raps' in runs:
            validationobj.raps()
            validationobj.rawmap_raps()
            # validationobj.pararaps()

        # FSC
        if 'fsc' in runs:
            validationobj.fscs()

        # mmFSC
        if 'mmfsc' in runs:
            validationobj.mmfsc()

        # Symmetry
        if 'symmetry' in runs:
            validationobj.symmetry()

        # # Strudel
        # if 'strudel' in runs:
        #     validationobj.strudel()

        # Q-score
        if 'qscore' in runs:
            validationobj.qscore()

        # SMOC
        if 'smoc' in runs:
            validationobj.smoc()

        # EMringer
        if 'emringer' in runs:
            validationobj.emringer()

        # 3DFSC
        # if '3dfsc' in runs:
        #     validationobj.threedfsc()

        # Local resolution

        return None

    def strudel_only():
        # Strudel
        if 'strudel' in runs:
            validationobj.strudel()

        return None

    t = threading.Thread(target=strudel_only)
    t1 = threading.Thread(target=without_strudel)
    t.start()
    t1.start()
    t.join()
    t1.join()

# @profile
def main():

    start_first = timeit.default_timer()

    # Preparation
    prepobj = prep()
    position = prepobj.args.positions

    if not prepobj.args.positions:
        # Read map
        inputmap, mapsize, mapdimension = prepobj.read_map()

        # Read model
        inputmodel, pid, modelsize = prepobj.read_model()

        # Get model map names
        modelsmaps, _ = prepobj.modelstomaps()

        # Read half map
        halfeven, halfodd, rawmap, halfmapsize = prepobj.read_halfmaps()

        # Contour level
        contourlevel = prepobj.contourlevel

        # Read run parameters
        runs = prepobj.runs()

        # EMDID
        emdid = prepobj.emdid
        dir = None if emdid is not None else prepobj.dir

        # Resolution and EM method
        resolution, emmethod = prepobj.resolution, prepobj.method

        # fscfile
        fscfile = prepobj.fscfile

        # strudel lib
        strudellib = prepobj.mofit_libpath

        # 3DFSC root directory
        threed_fsc_dir = prepobj.threedfscdir

        # Masks
        masks = prepobj.masks

        # Memory prediction
        memmsg = None
        # if len(runs) == 10 and 'mask' not in runs:
        memmsg = prepobj.memmsg(mapsize)

        # Platform either wwpdb or emdb(default)
        platform = prepobj.platform
        print('Executed under: {} platform.'.format(platform))

        # VA starts here on
        print('%sValidation Analysis%s' % (20*'=', 20*'='))
        validationobj = ValidationAnalysis(inputmap, inputmodel, pid, halfeven, halfodd, rawmap, contourlevel, emdid,
                                           dir, emmethod, resolution, fscfile, masks, modelsmaps, strudellib,
                                           threed_fsc_dir, platform)

        # Run all the validation piceces and give the peak memory consumption
        if len(runs) == 9 and 'mask' not in runs:
            mem = max(memory_usage((allruns, (validationobj, runs)), multiprocess=True, include_children=True))
            print('The memory peak is: {}.'.format(mem))
        else:
            mem = 0.
            allruns(validationobj, runs)

        # Change cif file to the original one
        prepobj.change_cifname()
        # Merge all jsons
        prepobj.finiliszejsons()

        stop = timeit.default_timer()
        alltime = stop - start_first
        # print('Memory usage peak: %s.' % mem)
        print('All time: %s' % alltime)


        # Save data for memory prediction
        #if runs['all'] is True:
        if len(runs) == 9 and 'mask' not in runs:
            if inputmodel is not None and modelsize is not None:
                modelout = sum(modelsize)/len(modelsize) if len(inputmodel) != 0 else 0
                vout = MAP_SERVER_PATH if emdid is not None else os.path.dirname(os.path.dirname(dir))
                with open(vout + '/input.csv', 'a+') as f:
                    if os.stat(vout + '/input.csv').st_size == 0:
                        f.write('%s,%s,%s,%s,%s,%s,%s\n' % ('mapname', 'maprealsize', 'halfmapsize', 'modelrealsize', 'mapdimension', 'alltime', 'mem'))
                    f.write('%s,%s,%s,%s,%s,%s,%s\n' % (prepobj.mapname, mapsize, halfmapsize, modelout, mapdimension, alltime, mem))
                f.close()
            else:
                vout = MAP_SERVER_PATH if emdid is not None else os.path.dirname(os.path.dirname(dir))
        else:
            vout = None

        return None
    elif position == 'strudel':
        run_strudel(prepobj.full_modelpath, prepobj.full_mappath, prepobj.mofit_libpath, prepobj.strdout)


if __name__ == '__main__':
    main()

