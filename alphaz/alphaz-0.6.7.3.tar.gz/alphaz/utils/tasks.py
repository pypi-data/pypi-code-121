import shlex
import subprocess

def start_celery(worker=True,beat=False):
    from core import core

    config = core.api.conf
    """worker  = config.get("celery/worker")
    beat    = config.get("celery/beat")"""

    if beat or worker:
        cmd = 'pkill celery'
        subprocess.call(shlex.split(cmd))

    if worker:
        log_file = config.get('celery/log')
        cmd = "celery -A tasks.configuration worker --loglevel=info --logfile="+log_file
        print(f"   > starting celery worker {cmd}")
        subprocess.Popen(cmd.split(), shell=False)

    if beat:
        cmd = "celery -A tasks.configuration beat --loglevel=info --logfile="+log_file
        print(f"   > starting celery beat {cmd}")
        subprocess.Popen(cmd.split(), shell=False)