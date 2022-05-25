from celery.exceptions import SoftTimeLimitExceeded
import psutil
from celery import task
from billiard import current_process
from jobqueues.util import _getVisibleGPUdevices


visibledevs = _getVisibleGPUdevices()


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


@task
def execute_gpu_job(folder, runsh, sentinel, datadir, copyextensions, jobname=None):
    import subprocess
    import os
    import time

    worker_index = current_process().index
    gpu_index = worker_index
    if visibledevs is not None:
        gpu_index = visibledevs[worker_index % len(visibledevs)]
    print(f"Running job on worker index {worker_index} and GPU device {gpu_index}")

    jobsh = os.path.join(folder, "job.sh")
    stdfile = os.path.join(folder, "celery.out")
    _createJobScript(
        jobsh, folder, runsh, worker_index, sentinel, datadir, copyextensions
    )

    # Sleep for a short bit so that the OS can pick up on the new file before executing it
    time.sleep(0.2)

    process = None
    try:
        with open(stdfile, "a") as fout:
            process = subprocess.Popen(
                ["/bin/sh", jobsh], stdout=fout, stderr=fout, shell=False
            )
            _ = process.communicate()
    except SoftTimeLimitExceeded:
        # The SoftTimeLimitExceeded exception is a hack because SIGTERM doesn't work in Celery. See celeryqueue.py comment.
        if process is not None:
            kill(process.pid)
        print(f"Job {jobname} has been cancelled by the user")
    except Exception as e:
        raise e


@task
def execute_cpu_job(folder, runsh, sentinel, datadir, copyextensions, jobname=None):
    import subprocess
    import os
    import time

    jobsh = os.path.join(folder, "job.sh")
    stdfile = os.path.join(folder, "celery.out")
    _createJobScript(jobsh, folder, runsh, None, sentinel, datadir, copyextensions)

    # Sleep for a short bit so that the OS can pick up on the new file before executing it
    time.sleep(0.2)

    process = None
    try:
        with open(stdfile, "a") as fout:
            process = subprocess.Popen(
                ["/bin/sh", jobsh], stdout=fout, stderr=fout, shell=False
            )
            _ = process.communicate()
    except SoftTimeLimitExceeded:
        # The SoftTimeLimitExceeded exception is a hack because SIGTERM doesn't work in Celery. See celeryqueue.py comment.
        if process is not None:
            kill(process.pid)
        print(f"Job {jobname} has been cancelled by the user")
    except Exception as e:
        raise e


def _createJobScript(
    fname, workdir, runsh, deviceid, sentinel, datadir, copyextensions
):
    import os

    with open(fname, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(
            f'\ntrap "touch {os.path.normpath(os.path.join(workdir, sentinel))}" EXIT SIGTERM SIGINT\n'
        )
        f.write("\n")
        if deviceid is not None:
            f.write(f"export CUDA_VISIBLE_DEVICES={deviceid}\n\n")

        f.write(f"cd {os.path.abspath(workdir)}\n")
        f.write(runsh)

        # Move completed trajectories
        if datadir is not None:
            datadir = os.path.abspath(datadir)
            os.makedirs(datadir, exist_ok=True)
            simname = os.path.basename(os.path.normpath(workdir))
            # create directory for new file
            odir = os.path.join(datadir, simname)
            os.makedirs(odir, exist_ok=True)
            if os.path.abspath(odir) != os.path.abspath(workdir):
                f.write("\nmv {} {}".format(" ".join(copyextensions), odir))

    os.chmod(fname, 0o700)
