import gpustat as gp # TODO: add to requirements
import time, os
import subprocess as sp
import sys
import importlib.util

def monitor():
    c = gp.new_query()
    processes_per_gpu = [ len(x['processes']) for x in  c.jsonify()['gpus']]
    return processes_per_gpu

def submit(job_text):
    '''
    Submits a job and keeps it in Q until GPUs have no processes:

    job_text:   e.g. `python train.py --lr 0.1`

    TODO: add shutdown as an option.
    TODO: add some indication of what runs where.
    '''
    tar_file = [ f for f in job_text.split(' ') if '.py' in f]
    torch = importlib.util.find_spec('torch') is not None
    assert len(tar_file)==1

    while True:
        ppgpu = monitor()
        if sum(ppgpu)>1:
            print(f'Still busy. File {tar_file[0]} is in local: {tar_file[0] in os.listdir()}. \
            Torch present {torch}.')
        else:
            print('Done, submitting a new job!')
            # my_env = os.environ.copy()
            sp.run(job_text, shell=True)
            time.sleep(120)
            sys.exit(0)
        time.sleep(1)

