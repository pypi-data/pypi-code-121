import sys
import os
import shutil
import subprocess
import glob 
import re
import json

from importlib import resources

from pdbtools import pdb_mkensemble

natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\\d+)', s)] # used throughout to loop through files in natural order


def refine(home_dir, job_id, pdb, cpu):

    tleap = str(shutil.which("tleap"))
    sander = str(shutil.which("sander"))
    sander_MPI = str(shutil.which("sander.MPI"))
    cpptraj = str(shutil.which("cpptraj"))

    wd = home_dir+'/'+job_id+'/refined/'+os.path.splitext(os.path.basename(pdb))[0] # make dir to run refinement in
    os.makedirs(wd,exist_ok=True)

    with resources.path("nerrds.scripts.AMBER", "leap.in") as f:
        leap_script = f
    with resources.path("nerrds.scripts.AMBER", "min.in") as f:
        min_script = f
    with resources.path("nerrds.scripts.AMBER", "min_solv.in") as f:
        min_solv_script = f
    with resources.path("nerrds.scripts.AMBER", "extract_pdb.cpptraj") as f:
        cpptraj_script = f

    shutil.copyfile(leap_script, wd+"/leap.in") # copy various refinement scripts into wd
    shutil.copyfile(min_script, wd+"/min.in")  
    shutil.copyfile(min_solv_script, wd+"/min_solv.in")
    shutil.copyfile(pdb, wd+'/prot_for_min.pdb') # pdb is renamed to generic name referred to in refinement scripts, will be renamed after

    os.chdir(wd)

    run_tleap = subprocess.run([tleap, "-f", "leap.in"],stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))

    if int(cpu)==1:  
        run_amber = subprocess.run([sander, "-i", "min_solv.in", "-o", "min_solv.out", "-p", "prot_solv.parm7", "-c", "prot_solv.rst7", "-r", "prot_min_solv.rst7", "-x", "prot_min_solv.nc", "-ref", "prot_solv.rst7", "-O"],stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))
        run_amber = subprocess.run([sander, "-i", "min.in", "-o", "min.out", "-p", "prot_solv.parm7", "-c", "prot_min_solv.rst7", "-r", "prot_min.rst7", "-x", "prot_min.nc", "-O"],stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))
    elif int(cpu) > 1:
        run_amber = subprocess.run(["mpirun", "-np", str(cpu), sander_MPI, "-i", "min_solv.in", "-o", "min_solv.out", "-p", "prot_solv.parm7", "-c", "prot_solv.rst7", "-r", "prot_min_solv.rst7", "-x", "prot_min_solv.nc", "-ref", "prot_solv.rst7", "-O"],stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))
        run_amber = subprocess.run(["mpirun", "-np", str(cpu), sander_MPI, "-i", "min.in", "-o", "min.out", "-p", "prot_solv.parm7", "-c", "prot_min_solv.rst7", "-r", "prot_min.rst7", "-x", "prot_min.nc", "-O"],stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))

    if os.path.exists("prot_min.nc"):
        run_cpptraj = subprocess.run([cpptraj, "-i", cpptraj_script],stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))
        shutil.copyfile(wd+'/prot_min.pdb',wd.split('/')[-1]+'_refined.pdb')

    os.chdir(home_dir)


def combine(home_dir, job_id, pdb_id):
    os.chdir(home_dir)

    mkensemble_string = []
    for pdb in sorted(glob.glob(home_dir+'/'+job_id+"/refined/anm_"+pdb_id+"_*/anm_"+pdb_id+"_*_refined.pdb"),key=natsort):
        fail=0
        for i in open(pdb,'r').readlines():  # remove the structures which blew up i.e. have coords with "***"
            if "*" in i:
                fail=1
        if fail == 0:
            mkensemble_string.append(pdb)

    new_pdb = pdb_mkensemble.run(mkensemble_string)

    out = open(home_dir+"/"+job_id+"/refined/anm_"+pdb_id+"_refined.tmp",'w')
    for line in enumerate(new_pdb):
        out.write(line[1])
    out.close()

    # rename HIE, HID to HIS, Amber uses HIE and HID which is not recognised by ANSURR
    out = open(home_dir+"/"+job_id+"/refined/anm_"+pdb_id+"_refined.pdb",'w')   
    for line in open(home_dir+"/"+job_id+"/refined/anm_"+pdb_id+"_refined.tmp",'r'):
        out.write(line.replace('HIE','HIS').replace('HID','HIS'))
    out.close()

    os.remove(home_dir+"/"+job_id+"/refined/anm_"+pdb_id+"_refined.tmp")

    # read REMARKs in combined file to generate dictionary which links model number to the name of the PDB

    model_link = {}
    for line in open(home_dir+"/"+job_id+"/refined/anm_"+pdb_id+"_refined.pdb",'r'):
        line = line.split()
        if line[0] == 'REMARK':
            model_link[str(line[2])] = line[4]
            
    with open(home_dir+"/"+job_id+"/refined/model_link.json", "w") as outfile:
        json.dump(model_link, outfile)


if __name__ == "__main__":
    import sys

    mode = sys.argv[1]
    home_dir = sys.argv[2]
    job_id = sys.argv[3]
    pdb = sys.argv[4]
    cpu = sys.argv[5]
    
    if mode == 'refine':
        refine(home_dir, job_id, pdb, cpu)
    elif mode == 'combine':
        combine(home_dir, job_id, pdb_id)
