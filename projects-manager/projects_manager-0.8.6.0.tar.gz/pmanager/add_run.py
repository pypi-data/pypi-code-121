from os import path
from pmanager.res import *

def initialize(namespace):


    project_name = namespace.project_name[0]
    command = sanitize_for_xml(namespace.command[0])



    if not path.exists("config/default_path.conf"):

        dirpath = get_home_dir_path()+"/projects/"+project_name + "/"

    else:

        with open("config/default_path.conf","r",encoding="utf-8") as f:

            dirpath = f.read()+"/"+ project_name +"/"
            f.close()


    #check if the project exists
    if not path.exists(dirpath):
        perror("This project does not exists")

    else:
        #check if a custom start command is specified for the project
        if path.exists(f"config/{project_name}.xml"):

            #get previous content
            with open(f"config/{project_name}.xml","r") as f:
                prev_ctt = f.read()
                f.close()

            #add the command at the end and re-write the file
            with open(f"config/{project_name}.xml","w") as f:
                f.write(prev_ctt.replace("</config>",f"<run>{command}</run>\n</config>"))
                f.close()            

        else:

            #create and write the file
            with open(f"config/{project_name}.xml","w") as f:
                f.write(f"<config>\n<run>{command}</run>\n</config>")

            
        pinfo(f"added run command :\n{command}\nto project : {project_name}")



