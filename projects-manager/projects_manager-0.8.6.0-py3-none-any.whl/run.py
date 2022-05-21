from os import path, chdir
from subprocess import Popen, PIPE
from xml.etree import ElementTree as ET
from pmanager.res import *

def get_run_commands(project_name):
    """
    parsing the xml and return run commands

    """
    root = ET.parse(f"config/{project_name}.xml",).getroot()

    command = [ i.text.replace("\n","") for i in root.findall("run")]

    return command




def initialize(namespace):
    """
    called by argparse

    """

    project_name = namespace.project_name[0]

    
    if not path.exists("config/default_path.conf"):

        dirpath = get_home_dir_path()+"/projects/"+project_name + "/"

    else:

        with open("config/default_path.conf","r",encoding="utf-8") as f:

            dirpath = f.read()+"/"+ project_name +"/"
            f.close()


    #check if a custom start command is specified for the project
    if path.exists(f"config/{project_name}.xml"):
        
        for command in get_run_commands(project_name):
            chdir(dirpath)
            pinfo(f"running : {command}")

            p = Popen(command,shell=True,stdout=PIPE)
            for line in p.stdout:
                print(line.decode('utf-8',errors="ignore"),end="")

    else:
        perror("no run command(s) specified for this project,\
\n run \"python -m pmanager <project name> add_run <command>\" to add a\
run command\n (you can add as many commands as you want !)")

    