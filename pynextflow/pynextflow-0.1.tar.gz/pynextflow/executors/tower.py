from typing import List

import subprocess

import os
import uuid
from datetime import datetime

from pynextflow.entities.workflow import Workflow
from pynextflow.executors import Executor
from pynextflow.workflow import _print_workflow


class Tower(Executor):
    workspace: str
    profile: List[str]

    def __init__(self, workspace: str = None, profile: List[str] = []):
        Executor.__init__(self)

        self.workspace = workspace
        self.profile = profile

    def run(self, work: Workflow, returns=False):
        try:
            from IPython.display import display, Javascript
            display(Javascript('IPython.notebook.save_checkpoint();'))
        except:
            pass

        suffix_date = datetime.now().strftime("%Y%m%d_%H%M%s")
        suffix_rnd = str(uuid.uuid4())[0:8]
        basedir, branch = os.getcwd(), f"pynextflow_{suffix_date}_{suffix_rnd}"
        scriptpath = os.path.join(basedir, f"{branch}.nf")

        _exec("git stash --include-untracked")
        _exec(f"git checkout -b {branch}")
        _exec("git stash apply")
        with open(scriptpath, "w") as fd:
            _print_workflow(work, file=fd)
        _exec(f"git add .")
        _exec(f"git commit -m \"{branch}\"")
        _exec(f"git push --set-upstream origin {branch}")
        _exec("git checkout -")
        _exec("git stash pop")

        repo = _get_repo()
        main_script = f"{branch}.nf"
        profiles = ",".join(self.profile)
        profile = f" --profile={profiles}" if self.profile else ""
        cmd = f"tw launch {repo} -r {branch} --main-script={main_script}{profile}"
        os.system(cmd)


def _get_repo():
    repo = _exec("git config --get remote.origin.url").strip()
    if repo.startswith("git@"):
        repo = repo.replace(":", "/")
        repo = repo.replace("git@", "https://")
        repo = repo.replace(".git", "")

    return repo


def _exec(command: str):
    result = subprocess.run(command.split(" "), capture_output=True, text=True)
    return result.stdout

