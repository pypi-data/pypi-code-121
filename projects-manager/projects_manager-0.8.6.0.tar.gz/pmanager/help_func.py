from os import  listdir,path
from pmanager.res import *


help_message = """
======================HELP======================

- pmanager new <project name> [module]
Create a new project with de desired module configurations
(default archives folder is <user home directory>/projects)

- pmanager <project name> add [module]
Add a module to an existing project

- pmanager delete all/[module] <project name>
Delete all project or only a module

- pmanager share <project name> 
Open a tiny webserver to share your project source code over
the network

- pmanager config
Start pmanager configuration script

- pmanager add [module] <project name>
add a module to an existing project

- pmanager open <project name>
open a project

- pmanager modlist
get a list of all available modules

- pmanager projects
get a list of all projects

- pmanager archive <project name>
archive a specific project 
(default archives folder is <user home directory>/projects_archive)

- pmanager terminal <project name>
open your default terminal at the specified project folder

- pmanager import
start the assistant to import a custom project module

example :
./pmanager.py new test python flask

======================HELP======================

"""

def display_help_message(namespace=""):
    pwarn(help_message)


def print_modules_list(namespace):
    modules_list = list(set([path.splitext(x)[0] for x in listdir("pmanager/modules/")]))
    for module in modules_list:
        if((not module.startswith("__")) and (not module.endswith("__"))):
            pinfo(module)