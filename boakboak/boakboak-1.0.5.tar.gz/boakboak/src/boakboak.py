# src.py
import os, sys
import subprocess


def crow(
    *args, isPackage, executable, appPath, cmds, defaultArgs=None, **kwargs
):
    os.chdir(appPath)
    if args:
        cmds.extend(args)
    elif defaultArgs is not None:
        for a in defaultArgs:
            cmds.extend(a.strip().split(" ", 1))
    print(f"\nNow running: {appPath}: {' '.join(cmds)} using {executable}")
    out = str(
        subprocess.Popen(
            cmds, shell=False, executable=executable, stdout=subprocess.PIPE
        )
        .stdout.read()
        .decode("utf-8")
    )
