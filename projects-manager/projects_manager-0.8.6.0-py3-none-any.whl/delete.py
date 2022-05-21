from os import path, remove
from shutil import rmtree
from pmanager.res import *
from xml.etree import ElementTree as ET



def initialize(namespace):

    project_name = namespace.project_name[0]
    modules_name = namespace.modules

    if not path.exists("config/default_path.conf"):
        dirpath = get_home_dir_path()+"/projects/"+project_name
    else:
        with open("config/default_path.conf","r",encoding="utf-8") as f:
            dirpath = f.read()+"/"+ project_name

    if not path.exists(dirpath):
        perror(f"This project does not exist : \n {dirpath}")

    else:

        if modules_name == []:
            pwarn("no modules selected, type \"all\" if you just want to wipe the entire project.")
            exit(1)

        for module in modules_name:
            try:
                if module == "all":
                    pinfo(f"removing project : \n {dirpath}")

                    rmtree(dirpath)
                    #remove the custom startup command if there is one
                    if path.exists(f"config/{project_name}.xml"):
                        remove(f"config/{project_name}.xml")

                    break

                
                else:
                    #get the first folder of the module in his xml file

                    root = ET.parse(f"pmanager/modules/{module}.xml",).getroot()
                
                    for item in root:

                        if item.tag == "folder":
                            module_root_folder = item.attrib['path']
                            break
                    
                    pinfo(f"removing folder : \"{module_root_folder}\" from project")
                                    
                    rmtree(dirpath+"/"+module_root_folder)

                    
            except Exception as e:
                perror("An error occured while removing your files (it may be just that you are not administrator)")
                pwarn("error message :")
                print(e)
                
                exit(1)

        psuccess("Successfully removed your files")
