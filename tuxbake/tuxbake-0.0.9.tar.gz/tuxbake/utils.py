import os
import subprocess
from pathlib import Path
from tuxbake.exceptions import TuxbakeRunCmdError


def repo_init(oebuild, src_dir, local_manifest=None, pinned_manifest=None):
    cmd = f"repo init -u {oebuild.repo.url} -b {oebuild.repo.branch} -m {oebuild.repo.manifest}".split()
    run_cmd(cmd, src_dir)
    if pinned_manifest:
        cmd = f"cp {pinned_manifest} .repo/manifests/{oebuild.repo.manifest}".split()
        run_cmd(cmd, src_dir)

    if local_manifest:
        cmd = f"mkdir -p .repo/local_manifests/".split()
        run_cmd(cmd, src_dir)
        cmd = f"cp {local_manifest} .repo/local_manifests/".split()
        run_cmd(cmd, src_dir)
    cmd = "repo sync -j16".split()
    run_cmd(cmd, src_dir)
    cmd = "repo manifest -r -o pinned-manifest.xml".split()
    run_cmd(cmd, src_dir)


def git_init(oebuild, src_dir):
    for git_object in oebuild.git_trees:
        url = git_object.url
        branch = git_object.branch
        ref = git_object.ref
        sha = git_object.sha
        basename = os.path.splitext(os.path.basename(url))[0]
        dir_repo = Path(os.path.join(src_dir, basename))
        if dir_repo.exists() and dir_repo.is_dir():
            cmd = f"git fetch origin".split()
            run_cmd(cmd, os.path.join(src_dir, basename))
            cmd = f"git checkout -B {branch} origin/{branch}".split()
            run_cmd(cmd, os.path.join(src_dir, basename))
        else:
            if branch:
                cmd = f"git clone {url} -b {branch}".split()
            else:
                cmd = f"git clone {url}".split()
            run_cmd(cmd, src_dir)
        if ref:
            cmd = f"git fetch origin {ref}:{ref}-local".split()
            run_cmd(cmd, f"{src_dir}/{basename}")
            cmd = f"git checkout {ref}-local".split()
            run_cmd(cmd, f"{src_dir}/{basename}")
        if sha:
            cmd = f"git checkout {sha}".split()
            run_cmd(cmd, f"{src_dir}/{basename}")


def run_cmd(cmd, src_dir, env=None, fail_ok=False):
    process = subprocess.Popen(cmd, cwd=src_dir, env=env)
    process.communicate()
    if not fail_ok and process.returncode != 0:
        raise TuxbakeRunCmdError(f"Failed to run: {' '.join(cmd)}")
