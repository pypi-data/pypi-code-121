from os import rename
from pmanager.res import *

def initialize(namespace):


    project_name = namespace.old_project_name[0]
    new_project_name = namespace.new_project_name[0]


    if not path.exists("config/default_path.conf"):
        dirpath = get_home_dir_path()+"/projects/"+project_name
    else:
        with open("config/default_path.conf","r",encoding="utf-8") as f:
            dirpath = f.read()+"/"+ project_name

    if not path.exists(dirpath):
        perror(f"This project does not exist : \n {dirpath}")

    else:
        rename(dirpath,dirpath.replace(project_name,new_project_name))

        psuccess(f"renamed {dirpath} to {dirpath.replace(project_name,new_project_name)}")