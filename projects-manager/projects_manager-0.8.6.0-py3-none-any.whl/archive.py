from os import path, remove
from shutil import move
from pmanager.res import *


def initialize(namespace):
    
    project_name = namespace.project_name[0]

    if not path.exists("config/default_path.conf"):

        dirpath = get_home_dir_path()+"/projects/"+project_name + "/"

    else:

        with open("config/default_path.conf","r",encoding="utf-8") as f:

            dirpath = f.read()+"/"+ project_name +"/"
    

    if not path.exists("config/default_archive_path.conf"):

        archive_dirpath = get_home_dir_path()+"/projects_archive/"+project_name + "/"

    else:

        with open("config/default_archive_path.conf","r",encoding="utf-8") as f:

            archive_dirpath = f.read()+"/"+ project_name +"/"



    #remove the custom startup command if there is one

    if path.exists(f"config/{project_name}.xml"):
        remove(f"config/{project_name}.xml")


    pinfo(f"opening project folder : \n {dirpath}")

    pinfo(f"moving it to : \n {archive_dirpath}")

    try :
        
        move(dirpath,archive_dirpath)    
        psuccess("project archived !")

    except Exception as e:
        perror("An error occured while moving your files (it may be just that you are not administrator)")
        pwarn("error type :")
        print(e)
        exit(1)
