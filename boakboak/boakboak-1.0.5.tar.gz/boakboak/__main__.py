# __main__.py

import os, sys
import boakboak.src.settings as sts
from boakboak.src.executable import Executable
from boakboak.src.params import Params
import boakboak.src.boakboak as boakboak


def run(*args, params, **kwargs):
    # running the called python module
    for app, pars in params.items():
        pars["executable"], isPackage = Executable(
            *args, **pars
        ).get_executable(app, **pars)
        boakboak.crow(*args[1:], isPackage=isPackage, **pars)


def main(*args, **kwargs):
    # when installed, args have to come via sys.argv not from main(*sys.argv)
    if not args:
        args = sys.argv[1:]
    if not args:
        print(
            f"{sts.sysArgsException}: \n\n\tPath:\t\t\t{sts.os_sep_adj(sts.appsParamsDir)}"
        )
        print(f"\tavailable apps: \t{os.listdir(sts.appsParamsDir)}\n")
        exit()
    p = Params()
    apps = p.get_all_apps(*args)
    params = p.get_params(apps, *args)
    if params:
        run(*args, params=params)


if __name__ == "__main__":
    main(*sys.argv[1:])
