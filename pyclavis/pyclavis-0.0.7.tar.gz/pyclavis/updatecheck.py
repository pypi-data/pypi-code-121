import os
import json
from functools import cmp_to_key
import string
import semver

from .logging import log, print_t, print_e

from .bgtask import BackgroundTask


def _run_cmd(cmd_line, callb=None):
    resp = []
    p = os.popen(cmd_line)
    try:
        while True:
            rc = p.readline()
            if len(rc) == 0:
                break
            resp.append(rc)
            if callb:
                callb(rc)
    except:
        pass
    p.close()
    return resp


def do_pip_install(pypi_project, python_bin=None, callb=None):
    if python_bin == None:
        python_bin = "python3"
    lines = _run_cmd(f"{python_bin} -m pip install -U {pypi_project}", callb=callb)
    cont = "".join(lines)
    return cont


def getversions(repo, opts=None, python_bin=None, callb=None):
    if opts == None:
        opts = ""
    if python_bin == None:
        python_bin = "python3"

    lines = _run_cmd(f"{python_bin} -m pygitgrab {opts} -itags {repo}", callb=callb)

    cont = "".join(lines)
    print_t("download version info", cont)

    o = json.loads(cont)

    ref = map(lambda x: x["ref"], o)
    ref_strip = map(lambda x: x[x.rfind("/") + 1 :], ref)

    return ref_strip


def stripversion(x):
    for i, c in enumerate(x):
        if c in string.digits:
            return x[i:]
    return x


def check_download_version(
    repo_url, thisversion, opts=None, callb=None, python_bin=None
):

    thisversion = stripversion(thisversion)
    thisversion = semver.parse_version_info(thisversion)

    ver = getversions(repo_url, opts=opts, callb=callb, python_bin=python_bin)
    ver = map(stripversion, ver)
    ver = map(lambda x: semver.parse_version_info(x), ver)
    ver = sorted(ver)

    ver = list(ver)

    ver_s = list(map(lambda x: str(x), ver))
    print_t("all versions", ver_s)

    # last version
    ver = ver[-1]

    update = ver > thisversion

    return update, ver, thisversion


class BackgroundCheckDownload(BackgroundTask):
    def set_remote(self, repo_url, thisversion, opts=None, python_bin=None):
        self.repo_url = repo_url
        self.thisversion = thisversion
        self.opts = opts
        self.python_bin = python_bin
        return self

    def run(self):
        super().run()
        self.rc = check_download_version(
            self.repo_url,
            self.thisversion,
            opts=self.opts,
            callb=self._append_rc,
            python_bin=self.python_bin,
        )


def get_check_download_task(repo_url, thisversion, opts=None, python_bin=None):
    return BackgroundCheckDownload().set_remote(
        repo_url, thisversion, opts=opts, python_bin=python_bin
    )
