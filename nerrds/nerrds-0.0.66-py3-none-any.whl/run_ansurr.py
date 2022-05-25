import os

from ansurr import ansurr


def run_ansurr(home_dir, job_id, pdb_id, path_to_shifts):

    ansurr_dir = home_dir+"/"+job_id+"/ansurr/"
    os.makedirs(ansurr_dir,exist_ok=True)
    os.chdir(ansurr_dir)
    ansurr.main("-p "+home_dir+"/"+job_id+"/refined/anm_"+pdb_id+"_refined.pdb"+" -s "+path_to_shifts+" -r")


if __name__ == "__main__":
    import sys
    home_dir = sys.argv[1]
    job_id = sys.argv[2]
    pdb_id = sys.argv[3]
    path_to_shifts = sys.argv[4]
    run_ansurr(home_dir, job_id, pdb_id, path_to_shifts)

