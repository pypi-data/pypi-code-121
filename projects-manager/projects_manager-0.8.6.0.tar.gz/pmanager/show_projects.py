from os import listdir
from pmanager.res import *
from prompt_toolkit.shortcuts import radiolist_dialog
from pmanager.open_project import open_project_str

def show_projects(namespace):

    if not path.exists("config/default_path.conf"):

        dirpath = get_home_dir_path()+"/projects"

    else:

        with open("config/default_path.conf","r",encoding="utf-8") as f:

            dirpath = f.read()

    pwarn("listing folders in your default projects directory :")
    
    projects = []

    for folder in listdir(dirpath):
        projects.append(folder)


    

    result = radiolist_dialog(
        title="Projects List",
        text="Projects list",
        values=[ (i,i) for i in projects]
    ,ok_text="Open",cancel_text="exit").run()


    if result != None :
        open_project_str(result)
    else:
        exit(1)
