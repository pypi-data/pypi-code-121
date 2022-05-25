"""
import below
---------------------------
"""
import os,sys

debug = False
if os.path.exists("./debug"):
    sys.path.insert(os.path.abspath("../"))
    debug = True

from IutyScripts.file.fileclient import main as client
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

"""
class below(if need)
---------------------------
"""



"""
main below
---------------------------
"""

def main():
    client()
    pass

if __name__ == "__main__":
    main()
