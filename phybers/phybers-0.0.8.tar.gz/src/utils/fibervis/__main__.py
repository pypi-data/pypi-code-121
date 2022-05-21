import shlex
import sys
import os
from subprocess import run

pathname = os.path.dirname(__file__)
print("path is: " + pathname)
cmd_str = "python3 " + pathname + "/FiberVis.py"
cmd_str2 = os.path.join(pathname,"FiberVis.py")

print("string: " + cmd_str2)

if not os.path.exists(os.path.join(pathname,'Framework','CExtend','bundleCFunctions.o')):
    print("does not exist")

cextend_dir = os.path.join(pathname,'Framework','CExtend')
print(shlex.split("make -C " + cextend_dir))
#run(["make -C " + os.path.join(pathname,'Framework','CExtend')])
run(shlex.split("make -C " + cextend_dir))
run(["python3", cmd_str2])
#run(shlex.split(cmd_str))
