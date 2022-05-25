import os
import shutil
import glob
import re

from pdbtools import pdb_splitmodel
from prody import *


def gen_conf(path_to_pdb, home_dir, job_id, pdb_id, conformers, average_rmsd):

    natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\\d+)', s)] 

    #------------------------------------------------------ extract models from input ensemble --------------------------------------------------------------


    # split input PDB file into seperate models
    pdb_splitmodel.run(pdb_splitmodel.check_input([path_to_pdb]))

    # make dir to store split PDBs
    os.makedirs(job_id+'/models/',exist_ok=True)
    for pdb in glob.glob(pdb_id+'_*.pdb'):
        shutil.move(pdb,job_id+'/models/')


    #----------------------------------------------------------- generate conformers -------------------------------------------------------------------------

    # use prody run ANM to generate conformers for each model in input ensemble

    for pdb in sorted(glob.glob(home_dir+'/'+job_id+"/models/"+pdb_id+"_*.pdb"),key=natsort):
        
        parsed_pdb = parsePDB(pdb)
        parsed_pdb_ca = parsed_pdb.select('calpha')

        anm = ANM(pdb)
        anm.buildHessian(parsed_pdb_ca)
        anm.calcModes()

        bb_anm, all_atoms = extendModel(anm, parsed_pdb_ca, parsed_pdb.select('all'))

        ensemble = sampleModes(bb_anm[:3], all_atoms, n_confs=conformers, rmsd=average_rmsd)
        all_atoms = all_atoms.copy()
        all_atoms.addCoordset(ensemble)
        
        heavy = all_atoms.select('heavy')   # don't keep hydrogens, let AMBER add these during refinement to avoid naming issues

        os.makedirs(job_id+'/anm/',exist_ok=True) # save confomers here
        writePDB(job_id+'/anm/anm_'+os.path.basename(pdb), heavy)
        
        os.chdir(job_id+'/anm/')
        pdb_splitmodel.run(pdb_splitmodel.check_input(['anm_'+os.path.basename(pdb)]))
        os.remove('anm_'+os.path.basename(pdb))
        os.remove(glob.glob('anm_*_1.pdb')[0]) # remove the first model as this will be a submitted model - maybe we want to keep it?
        os.chdir(home_dir)

if __name__ == "__main__":
    import sys

    path_to_pdb = sys.argv[1]
    home_dir = sys.argv[2]
    job_id = sys.argv[3]
    pdb_id = sys.argv[4]
    conformers = sys.argv[5]
    average_rmsd = sys.argv[6]

    gen_conf(path_to_pdb, home_dir, job_id, pdb_id, conformers, average_rmsd)