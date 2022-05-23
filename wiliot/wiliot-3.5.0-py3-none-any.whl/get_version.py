import os.path
from setuptools_scm import get_version as scm_get_version
import sys
import re

def get_version(type = "current"):
    git_root = os.path.dirname(os.path.dirname(__file__))
    if os.path.isdir(os.path.join(git_root,".git")):
        version = scm_get_version(root = git_root, git_describe_command = "git describe --long --dirty --tags --match [0-9]*.[0-9]*.[0-9]*")
    elif os.path.isfile(os.path.join(os.path.dirname(__file__),"version.py")):
        from .version import __version__
        version = __version__
    else:
        print("Couldn't get version, retrying setupscm get version")
        #give SCM another shot.. shouldn't get here:
        version = scm_get_version(root = git_root, git_describe_command = "git describe --long --dirty --tags --match [0-9]*.[0-9]*.[0-9]*")

    if type == "current":
        return version
    else:
        ver_arr = re.split("\.", version, 4)
        if len(ver_arr)<3:
            raise ValueError(f"not enough parts at version {version}!!!")
        if type == "next_patch":
            if len(ver_arr) == 3: #we have a valid patch version and we want to progress by 1:
                ver_arr[2] = int(ver_arr[2]) + 1
        elif type == "next_minor":
            ver_arr[2] = 0
            ver_arr[1] = int(ver_arr[1])+1
        elif type == "next_major":
            ver_arr[2] = 0
            ver_arr[1] = 0
            ver_arr[0] = int(ver_arr[0])+1
        return f"{ ver_arr[0]}.{ver_arr[1]}.{ver_arr[2]}"


if __name__ == '__main__':
    num_args = len(sys.argv)
    if num_args == 1:
        type = 'current'
    else:
        type = sys.argv[1]

    __version__ = get_version(type)
    print(__version__)




