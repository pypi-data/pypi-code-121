import sys
import os
import argparse
import shutil
import glob
import re
import subprocess

from importlib import resources
from datetime import datetime

from nerrds import gen_conf
from nerrds import refine
from nerrds import run_ansurr
from nerrds import reweight_bme
from nerrds.functions import check_quiet_print

nerrds_version = "0.0.83"

def main():

    #------------------------------------------------------ check if AMBERtools is available and quit if not ------------------------------------------------
     
    tleap = shutil.which("tleap")
    sander = shutil.which("sander")
    sander_MPI = shutil.which("sander.MPI")
    cpptraj = shutil.which("cpptraj")

    if sander is None and sander_MPI is None:
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
    parser.add_argument("-e", "--env", help="path to virtual environment on NMRbox, needed to run refinement in parallel via HTCondor")
    parser.add_argument("-q", "--quiet", help="suppress output to the terminal", action="store_true")
    parser.add_argument("-v", "--version", help="NERRDS | NMR Ensemble Refinement using RigiDity anf Shifts v"+nerrds_version)

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
        if sander_MPI is None:
            if sander is not None:
                print("WARNING cannot find sander.MPI to run refinement with multiple cpus, continuing with sander and ncpu=1")
                cpu = 1
        else:
            cpu = int(args.ncpu)
            if cpu == 1 and sander is None:
                print("ERROR cannot find sander to run refinement with 1 cpu, quitting")
                sys.exit(0)
    else:
        if sander is None:
            print("ERROR cannot find sander to run refinement with 1 cpu, quitting")
            sys.exit(0)
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

    now = datetime.now()
    check_quiet_print(args.quiet,"\nNERRDS v"+nerrds_version+" "+now.strftime("%d/%m/%Y %H:%M:%S"))
    check_quiet_print(args.quiet," -> pdb: "+path_to_pdb)
    check_quiet_print(args.quiet," -> shifts: "+path_to_shifts)
    
    if args.env is not None: # check if job to be run on HT condor

        gen_conf.gen_conf(path_to_pdb, home_dir, job_id, pdb_id, conformers, average_rmsd)

        os.makedirs("logs",exist_ok=True)

        with resources.path("nerrds", "refine.py") as f:
        	refine_script = f

        with resources.path("nerrds", "run_ansurr.py") as f:
            ansurr_script = f

        with resources.path("nerrds", "reweight_bme.py") as f:
            bme_script = f

        shutil.copy(refine_script, home_dir+'/'+job_id+"/") #copy local version as permission being denied?
        shutil.copy(ansurr_script, home_dir+'/'+job_id+"/") #copy local version as permission being denied?
        shutil.copy(bme_script, home_dir+'/'+job_id+"/") #copy local version as permission being denied?

        refine_script = home_dir+'/'+job_id+"/refine.py"
        ansurr_script = home_dir+'/'+job_id+"/run_ansurr.py"
        bme_script = home_dir+'/'+job_id+"/reweight_bme.py"

        out = open("refine.tmp","w")
        out.write("#!"+str(os.path.abspath(args.env))+'/bin/python3\n') # append specific version of python needed
        for line in open(refine_script,"r"):
            out.write(line)
        out.close()
        shutil.move("refine.tmp",refine_script) 
        os.chmod(refine_script , 0o777)

        out = open("run_ansurr.tmp","w")
        out.write("#!"+str(os.path.abspath(args.env))+'/bin/python3\n') # append specific version of python needed
        for line in open(ansurr_script,"r"):
            out.write(line)
        out.close()
        shutil.move("run_ansurr.tmp",ansurr_script) 
        os.chmod(ansurr_script , 0o777)

        out = open("reweight_bme.tmp","w")
        out.write("#!"+str(os.path.abspath(args.env))+'/bin/python3\n') # append specific version of python needed
        for line in open(bme_script,"r"):
            out.write(line)
        out.close()
        shutil.move("reweight_bme.tmp",bme_script) 
        os.chmod(bme_script , 0o777)
        
        condor_refine = open(job_id+"_run_refine.sub","w")  ###  scripts dir will need to read from package install
        condor_refine.write("executable = "+job_id+"_run_refine.sh\nrequest_memory = 4G\nrequest_cpus = "+str(cpu)+"\nrequest_gpus = 0\noutput = logs/$(JobName).stdout\nerror = logs/$(JobName).stderr\nlog = logs/run.log\n")
        condor_refine.write("transfer_executable = FALSE\nshould_transfer_files = NO\nJobName = run_refine\nrequirements = (Target.Production == True)\n+Production = True\n")
        for pdb in sorted(glob.glob(home_dir+'/'+job_id+"/anm/anm_"+pdb_id+"_*.pdb"),key=natsort):
            p = os.path.splitext(os.path.basename(pdb))[0]
            condor_refine.write("JobName = "+p+'\n')
            condor_refine.write("arguments = refine "+home_dir+" "+job_id+" "+pdb+" "+str(cpu)+" "+str(tleap)+" "+str(sander)+" "+str(sander_MPI)+" "+str(cpptraj)+" "+'\n')
            condor_refine.write("queue"+'\n\n')
        condor_refine.close()

        condor_combine = open(job_id+"_run_combine.sub","w")  ###  scripts dir will need to read from package install
        condor_combine.write("executable = "+job_id+"_run_refine.sh\nrequest_memory = 4G\nrequest_cpus = 1\nrequest_gpus = 0\noutput = logs/$(JobName).stdout\nerror = logs/$(JobName).stderr\nlog = logs/run.log\n")
        condor_combine.write("transfer_executable = FALSE\nshould_transfer_files = NO\nJobName = run_combine\nrequirements = (Target.Production == True)\n+Production = True\n")
        condor_combine.write("JobName = combine\n")
        condor_combine.write("arguments = combine "+home_dir+" "+job_id+" "+pdb_id+'\n')
        condor_combine.write("queue"+'\n\n')           
        condor_combine.close()

        condor_ansurr = open(job_id+"_run_ansurr.sub","w")  ###  scripts dir will need to read from package install
        condor_ansurr.write("executable = "+job_id+"_run_ansurr.sh\nrequest_memory = 4G\nrequest_cpus = 1\nrequest_gpus = 0\noutput = logs/$(JobName).stdout\nerror = logs/$(JobName).stderr\nlog = logs/run.log\n")
        condor_ansurr.write("transfer_executable = FALSE\nshould_transfer_files = NO\nJobName = run_combine\nrequirements = (Target.Production == True)\n+Production = True\n")
        condor_ansurr.write("JobName = ansurr\n")
        condor_ansurr.write("arguments = "+home_dir+" "+job_id+" "+pdb_id+" "+path_to_shifts+'\n')
        condor_ansurr.write("queue"+'\n\n')
        condor_ansurr.close()

        condor_bme = open(job_id+"_run_bme.sub","w")  ###  scripts dir will need to read from package install
        condor_bme.write("executable = "+job_id+"_run_bme.sh\nrequest_memory = 4G\nrequest_cpus = 1\nrequest_gpus = 0\noutput = logs/$(JobName).stdout\nerror = logs/$(JobName).stderr\nlog = logs/run.log\n")
        condor_bme.write("transfer_executable = FALSE\nshould_transfer_files = NO\nJobName = run_bme\nrequirements = (Target.Production == True)\n+Production = True\n")
        condor_bme.write("JobName = bme\n")
        condor_bme.write("arguments = "+home_dir+" "+job_id+" "+pdb_id+" "+shifts_id+'\n')
        condor_bme.write("queue"+'\n\n')
        condor_bme.close()

        bash_refine = open(job_id+"_run_refine.sh","w")
        bash_refine.write("#!/bin/bash\n")
        bash_refine.write("source "+str(os.path.abspath(args.env))+"/bin/activate\n")  
        bash_refine.write("python3 "+str(refine_script)+" $1 $2 $3 $4 $5 $6 $7 $8 $9"+'\n')
        bash_refine.close()
        os.chmod(job_id+"_run_refine.sh" , 0o777)

        bash_ansurr = open(job_id+"_run_ansurr.sh","w")
        bash_ansurr.write("#!/bin/bash\n")
        bash_ansurr.write("source "+str(os.path.abspath(args.env))+"/bin/activate\n")  
        bash_ansurr.write("python3 "+str(ansurr_script)+" $1 $2 $3 $4"+'\n')
        bash_ansurr.close()
        os.chmod(job_id+"_run_ansurr.sh" , 0o777)

        bash_bme = open(job_id+"_run_bme.sh","w")
        bash_bme.write("#!/bin/bash\n")
        bash_bme.write("source "+str(os.path.abspath(args.env))+"/bin/activate\n")  
        bash_bme.write("python3 "+str(bme_script)+" $1 $2 $3 $4"+'\n')
        bash_bme.close()
        os.chmod(job_id+"_run_bme.sh" , 0o777)

        dag = open(job_id+".dag","w")
        dag.write("JOB A "+job_id+"_run_refine.sub\n")
        dag.write("JOB B "+job_id+"_run_combine.sub\n")
        dag.write("JOB C "+job_id+"_run_ansurr.sub\n")
        dag.write("JOB D "+job_id+"_run_bme.sub\n")
        dag.write("PARENT A CHILD B\n")
        dag.write("PARENT B CHILD C\n")
        dag.write("PARENT C CHILD D\n")
        dag.close()

        check_quiet_print(quiet,"submitted subsequent processing to the job queue, check NERRDS.log for progress")

        run_refine = subprocess.run(["condor_submit_dag", "-f", job_id+".dag"],stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))

    else: # run on this machine in serial 

        # generate conformers
        gen_conf.gen_conf(path_to_pdb, home_dir, job_id, pdb_id, conformers, average_rmsd)

        # refine conformers in serial
        for pdb in sorted(glob.glob(home_dir+'/'+job_id+"/anm/anm_"+pdb_id+"_*.pdb"),key=natsort):
            refine.refine(home_dir, job_id, pdb, cpu, str(tleap), str(sander), str(sander_MPI), str(cpptraj))

        # combine succesfully refined conformers into single ensemble
        refine.combine(home_dir, job_id, pdb_id)

        # run ansurr
        run_ansurr.run_ansurr(home_dir,job_id,pdb_id,path_to_shifts)

        # run BME
        reweight_bme.reweight_ensemble(home_dir,job_id,pdb_id,shifts_id)

if __name__ == "__main__":
    main()
