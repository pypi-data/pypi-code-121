import shlex
import sys
import os
from subprocess import run

pathname = os.path.dirname(__file__)
#print("path is: " + pathname)
cmd_str = "python3 " + pathname + "/main.py "
aux = 0

for arg in sys.argv[1:]:
    if (aux == 1):
        print("Output path is: " + arg)
        outpath = arg
        aux = 0
    if(arg.startswith('--output-directory')):
        aux = 1
        #print("it does")
    #print(arg)
    cmd_str += arg + " "

run(shlex.split(cmd_str))

#cmd_str2 = "python3 " + pathname + "/UtilsTools2.py " + outpath
#print("cmd_str2 is: " + cmd_str2)
#run(shlex.split(cmd_str2))
