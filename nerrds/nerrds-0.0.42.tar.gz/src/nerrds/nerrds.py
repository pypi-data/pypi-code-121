import sys
import os
import argparse
import shutil
import glob
import re

from importlib import resources
from datetime import datetime

from nerrds import gen_conf
from nerrds import refine
from nerrds import reweight_bme

from ansurr import ansurr


def is_tool(name):
    return shutil.which(name) is not None

def main():


    #ansurr.main()    # does this work? where would the args go?


    #------------------------------------------------------ check if AMBERtools is available and quit if not ------------------------------------------------

    sander_MPI = 1 if is_tool("sander.MPI") else 0
    sander = 1 if is_tool("sander") else 0
    tleap = 1 if is_tool("tleap") else 0
    cpptraj = 1 if is_tool("cpptraj") else 0
     
    if sander_MPI + sander == 0:
        print("ERROR could not find sander or sander.MPI (needed to refine models), quitting")
        sys.exit(0)

    elif tleap == 0:
        print("ERROR could not find tleap (needed to refine models), quitting")
        sys.exit(0)

    elif cpptraj == 0:
        print("ERROR could not find cpptraj (needed to refine models), quitting")
        sys.exit(0)

    #-------------------------------------------------------------- args ----------------------------------------------------------------------------

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pdb", type=str, help="input PDB file",required=True)
    parser.add_argument("-s", "--shifts", type=str, help="input shifts file in NMR-STAR v3 or NEF format",required=True)

    parser.add_argument("-c", "--conf", help="number of conformers to generate per model in input ensemble (default 50)")
    parser.add_argument("-r", "--avrmsd", help="average RMSD of conformers generated per model in input ensemble (default 2A)")
    parser.add_argument("-n", "--ncpu", help="number of CPUs used to refine models in AMBER (default 1)")

    parser.add_argument("-e", "--env", help="virtual environment on NMRbox to run via HTCondor")
    parser.add_argument("-j", "--job", help="job ID")

    args = parser.parse_args()

    #-------------------------------------------------------------- parameters ----------------------------------------------------------------------------

    # number of conformers to generate per model in input ensemble
    if args.conf:
        conformers = args.conf
    else:
        conformers = 50 

    # average RMSD of confomers generated
    if args.avrmsd:
        average_rmsd = args.avrmsd
    else:
        average_rmsd = 2    

    # number of CPUs used to refine models in AMBER
    if args.ncpu:
        if sander_MPI == 1:
            cpu = int(args.ncpu)
        else:
            print("WARNING cannot find sander.MPI to run refinement with multiple cpus, continuing with ncpu=1")
            cpu = 1
    else:
        cpu = 1

    #-------------------------------------------------------------- variables ----------------------------------------------------------------------------

    home_dir = os.getcwd()

    # shifts and PDB ensemble required as input
    path_to_pdb = home_dir+"/"+args.pdb
    path_to_shifts = home_dir+"/"+args.shifts

    # useful for later when running ansurr
    pdb_id = os.path.splitext(os.path.basename(path_to_pdb))[0]    
    shifts_id = os.path.splitext(os.path.basename(path_to_shifts))[0]

    # unique jobID based on time - could append pdb_id?
    job_id = datetime.now().strftime("%Y"+"%m"+"%d"+"_"+"%H"+"%M"+"%S"+"%f"+"_"+pdb_id+"_"+shifts_id)

    natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\\d+)', s)] # used throughout to loop through files in natural order


    #------------------------------------------------------ check if job to be run on HT condor --------------------------------------------------------------

    if args.env is not None:

        gen_conf.gen_conf(path_to_pdb, home_dir, job_id, pdb_id, conformers, average_rmsd)


        with resources.path("nerrds", "refine.py") as f:
        	refine_script = f

        shutil.copy(refine_script, home_dir+'/'+job_id+"/") #copy local version as permission being denied?
        refine_script = home_dir+'/'+job_id+"/refine.py"
  
        condor_refine = open("run_refine.sub","w")  ###  scripts dir will need to read from package install
        condor_refine.write("executable = "+str(refine_script)+"\nrequest_memory = 4G\nrequest_cpus = "+str(cpu)+"\nrequest_gpus = 0\noutput = logs/$(JobName).stdout\nerror = logs/$(JobName).stderr\nlog = logs/run.log\n")
        condor_refine.write("notification = Error   \ntransfer_executable = FALSE\nshould_transfer_files = NO\nJobName = run_refine\nrequirements = (Target.Production == True)\n+Production = True\n")

        for pdb in sorted(glob.glob(home_dir+'/'+job_id+"/anm/anm_"+pdb_id+"_*.pdb"),key=natsort):
            p = os.path.splitext(os.path.basename(pdb))[0]
            condor_refine.write("JobName = "+p+'\n')
            condor_refine.write("arguments = refine "+home_dir+" "+job_id+" "+pdb+" "+str(cpu)+'\n')
            condor_refine.write("queue"+'\n\n')
           
        condor_refine.close()


        bash_refine = open("run_refine.sh","w")
        bash_refine.write("#!/bin/bash\n")
        bash_refine.write("source "+str(os.path.abspath(args.env))+"\n")  
        bash_refine.write("python3 "+str(refine_script)+" $1 $2 $3 $4 $5"+'\n')
        bash_refine.close()

        os.chmod("run_refine.sh" , 0o777)




        

    else:

        # generate conformers
        gen_conf.gen_conf(path_to_pdb, home_dir, job_id, pdb_id, conformers, average_rmsd)

        ### check generate conf worked

        # refine conformers in serial
        for pdb in sorted(glob.glob(home_dir+'/'+job_id+"/anm/anm_"+pdb_id+"_*.pdb"),key=natsort):
            refine.refine(home_dir, job_id, pdb, cpu)

        ##### check refinement worked

        # combine succesfully refined conformers into single ensemble
        refine.combine(home_dir, job_id, pdb_id)

        # run ansurr
        ansurr_dir = home_dir+"/"+job_id+"/ansurr/"
        os.makedirs(ansurr_dir,exist_ok=True)
        os.chdir(ansurr_dir)
        ansurr.main("-p "+home_dir+"/"+job_id+"/refined/anm_"+pdb_id+"_refined.pdb"+" -s "+path_to_shifts+" -r")


        #### check ansurr worked

        # run BME
        reweight_bme.reweight_ensemble(home_dir,job_id,pdb_id,shifts_id)



if __name__ == "__main__":
    main()
