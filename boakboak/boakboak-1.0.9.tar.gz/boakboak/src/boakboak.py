# src.py
import os, sys
import subprocess
import boakboak.src.settings as sts


def crow(*args, isPackage, executable, appPath, cmds, defaultArgs=None, **kwargs):
    with sts.temp_chdir(appPath):
        if args:
            cmds.extend(args)
        elif defaultArgs is not None:
            for a in defaultArgs:
                cmds.extend(a.strip().split(" ", 1))
        print(f"\nNow running: {appPath}: {' '.join(cmds)} using {executable}")
        out = (
            subprocess.Popen(cmds, stderr=subprocess.PIPE, executable=executable)
            .stderr.read()
            .decode("utf-8")
        )
    return out
