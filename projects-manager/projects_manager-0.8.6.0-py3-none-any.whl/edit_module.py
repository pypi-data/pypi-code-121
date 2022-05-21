from pmanager.res import *
from subprocess import run
from os import path


def initialize(namespace):

    module_name = namespace.module_name[0]

    # check if module exists
    if not path.exists(f"pmanager/modules/{module_name}.xml"):
        perror("this module doest not exists !")

        if input("Do you want to create it ?[Y/n]\n") in ["N", "n", "no"]:
            return

        #default is yes
        else:
            pre_fill_module_files(module_name)

    with open("config/default_ide.conf", "r") as f:
        cmd = f.read() + \
            f" \"pmanager/modules/{module_name}.xml\" \"pmanager/modules/{module_name}.py\""
        f.close()
        pinfo(f"running :\n{cmd}")
        run(cmd, shell=True)
