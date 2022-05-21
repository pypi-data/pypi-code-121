from os import path
from pmanager.res import perror, get_home_dir_path, psuccess
from subprocess import run

def initialize(namespace):
    project_name = namespace.project_name[0]


    if not path.exists("config/default_path.conf"):

        dirpath = get_home_dir_path()+"/projects/"+project_name + "/"

    else:

        with open("config/default_path.conf","r",encoding="utf-8") as f:

            dirpath = f.read()+"/"+ project_name +"/"
            f.close()




    xml_path = path.abspath(__file__).replace("\\pmanager\\edit_project_conf.py",f"\\config\\{project_name}.xml")

    #check if the project exists
    if not path.exists(dirpath):
        perror("This project does not exists")


    else:
        #check if a custom start command is specified for the project
        if path.exists(f"config/{project_name}.xml"):
            with open("config/default_ide.conf","r") as f:
                run(f"{f.read()} \"{xml_path}\"",shell=True)

        else:
            perror("no special configuration have been specified for this project,\
do you still want to create and edit the file ? [Y/N]")

            r = input("-->")

            if (r == "Y" or r == "y"):
                with open("config/default_ide.conf","r") as f:
                    run(f"{f.read()} \"{xml_path}\"",shell=True)

