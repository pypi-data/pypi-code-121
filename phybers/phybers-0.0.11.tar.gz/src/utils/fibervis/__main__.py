import shlex
import sys
import os
from subprocess import run

pathname = os.path.dirname(__file__)
cextend_dir = os.path.join(pathname,'Framework','CExtend')
cmd_str2 = os.path.join(pathname,"FiberVis.py")

if not os.path.exists(os.path.join(pathname,'Framework','CExtend','bundleCFunctions.o')):
    print("bundleCFunctions.o does not exist. Creating it...")
    run(shlex.split("make -C " + cextend_dir))
    if not os.path.exists(os.path.join(pathname,'Framework','CExtend','bundleCFunctions.o')):
        print("bundleCFunctions.o still doesn't exist. Exiting...")
        exit()
    else:
        print("Running fibervis...")
        run(["python3", cmd_str2])
else:
    print("Running fibervis...")
    run(["python3", cmd_str2])
