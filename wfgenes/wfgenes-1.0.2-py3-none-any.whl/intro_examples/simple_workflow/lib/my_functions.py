import os
import time

def callscript(*args, **kwargs):
    cmd = kwargs['command']
    if 'argument' in kwargs.keys():
        cmd = cmd + " " + kwargs['argument']
    os.system(cmd)
    return 'Done!!! '

def callpython(message):
    print(message)