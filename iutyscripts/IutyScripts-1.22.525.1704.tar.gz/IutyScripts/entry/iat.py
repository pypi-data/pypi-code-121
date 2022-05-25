"""
import below
---------------------------
"""
import os,sys
import sys,os,importlib
from IutyLib.coding.tdd import ins_MethodTest, test_process
ins_MethodTest._testmode  = True


debug = False
if os.path.exists("./debug"):
    sys.path.insert(os.path.abspath("../"))
    debug = True

"""
function below
--------------------------
"""
def getArg():
    arg = None
    if len(sys.argv) > 1:
        arg = sys.argv.pop(1)
    return arg

def getKwargs():
    """
    get kwargs by formatter["key=value"]
    call before getArg
    """
    kwargs = {}
    for i in range(1,len(sys.argv)):
        arg = sys.argv[i]
        arg_split = arg.split('=')
        if len(arg_split) > 1:
            kwargs[arg_split[0].strip()] = kwargs[arg_split[1].strip()]
            sys.argv.pop(i)
    return kwargs

def getIntergrate():
    path = "./entry/intergrate.py"
    if os.path.exists(path):
        try:
            module = importlib.__import__(path[:-3])
            return module
        except Exception as err:
            print(err)
        
    return None

"""
class below(if need)
---------------------------
"""



"""
main below
---------------------------
"""

def main():
    intergrate = getIntergrate()
    if intergrate:
        test_process

if __name__ == "__main__":
    main()
