#!/usr/bin/env python3

"""
This script is a template for a prefect script. This can be
scheduled in a supervisor.

[program:REPO_THISSCRIPT]
command = /home/ubuntu/enrich/manage/bin/run_prefect_cmd.sh /home/ubuntu/enrich/customers/REPO/USECASE/workflows/prefect/THISSCRIPT.py ; Command to start app
user = ubuntu                                                         ; User to run as
group = ubuntu 
stdout_logfile = /home/ubuntu/enrich/logs/prefect/REPO_THISSCRIPT.log   ; Where to write log messages
redirect_stderr = true                                                ; Save stderr in the same log
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8                       ; Set UTF-8 as default encoding
autostart=false
stopasgroup=true



"""
import os
import sys
import subprocess
import platform
import time
from datetime import date, timedelta
from prefect.engine.executors import LocalDaskExecutor

import prefect
from prefect import Flow, task
from prefect.schedules import CronSchedule
from prefect.tasks.github import GetRepoInfo
from prefect.triggers import any_failed
from prefect.utilities.logging import get_logger


def get_dates():
    daybefore = (date.today() + timedelta(days=-2)).isoformat()
    yesterday = (date.today() + timedelta(days=-1)).isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    today = date.today().isoformat()
    return {
        "today": today,
        "yesterday": yesterday,
        "daybefore": daybefore,
        "tomorrow": tomorrow,
    }


@task
def run_pipeline(delay=0):
    logger = prefect.context.get("logger")
    logger.debug("Starting: Run Pipeline")

    dates = get_dates()
    if delay > 0:
        time.sleep(delay)

    cmd = [
        "/bin/bash",
        os.path.expandvars("$ENRICH_MANAGE/bin/run_enrichcli.sh"),
        "run-pipeline",
        "--scheduled",
        "--conf",
        os.path.expandvars(
            "$ENRICH_CUSTOMERS/acme/Marketing/pipelines/conf/PIPELINENAME.py"
        ),
        # Add required parameters
        # "TransformName:Variable=Value",
        # "SortEvents:backend=hs",
        "user=" + os.getlogin(),
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    logger.debug("Output: {}".format(out))
    logger.debug("Error: {}".format(err))
    logger.debug("Completed: Run pipeline")


if __name__ == "__main__":
    with Flow("Running Enrich Pipeline", schedule=None) as flow:
        data = run_pipeline(delay=0)
        # A way to force the dependencies
        # data = run_another_pipeline(data)

    executor = LocalDaskExecutor(scheduler="processes")
    flow.run(executor=executor)
