import shlex
import sys
import os
from subprocess import run

pathname = os.path.dirname(__file__)
cmd_str = "python3 " + os.path.join(pathname, "main.py ")
print("cmd_str is: " + cmd_str)
aux = 0

for arg in sys.argv[1:]:
    if (aux == 1):
        print("Output path is: " + arg)
        outpath = arg
        aux = 0
    if(arg.startswith('--output-directory')):
        aux = 1)

    cmd_str += arg + " "

run(shlex.split(cmd_str))

