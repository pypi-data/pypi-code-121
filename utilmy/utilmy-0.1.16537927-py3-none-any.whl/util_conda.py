# -*- coding: utf-8 -*-
MNAME = "utilmy.util_conda"
""" utils for conda/pip


"""


#############################################################################################
from utilmy import log, log2

def help():
    """function help.
    Doc::
            
            Args:
            Returns:
                
    """
    from utilmy import help_create
    print( help_create(__file__) )





#############################################################################################
def pip_auto_install():
    """ Auto Install pip package.
    Doc::
            
        
    """
    from importlib import util
    import subprocess
    import sys

    class PipFinder:
        @classmethod
        def find_spec(cls, name, path, target=None):
            print(f"Module {name!r} not installed.  Attempting to pip install")
            cmd = f"{sys.executable} -m pip install {name}"
            try:
                subprocess.run(cmd.split(), check=True)
            except subprocess.CalledProcessError:
                return None

            return util.find_spec(name)

    sys.meta_path.append(PipFinder)