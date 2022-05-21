from os import path, listdir, remove
from pmanager.res import perror, pinfo, pwarn, get_home_dir_path
from importlib import  import_module
from xml.etree import ElementTree as ET



def initialize(namespace):

    project_name = namespace.project_name[0]
    selected_modules = namespace.modules

    #get projects path
    if not path.exists("config/default_path.conf"):
        dirpath = get_home_dir_path()+"/projects/"+project_name
    else:
        with open("config/default_path.conf","r",encoding="utf-8") as f:
            dirpath = f.read()+"/"+ project_name


    #get modules list
    modules_list = list(set([path.splitext(x)[0] for x in listdir("pmanager/modules/")]))
    i=1


    for module in selected_modules:
        if module in modules_list:
            try:

                pinfo("initializing " + module)

                
                # get the first folder of the module in his xml file
                root = ET.parse(f"pmanager/modules/{module}.xml",).getroot()

                for item in root:
                    if item.tag == "folder":
                        module_root_folder = item.attrib['path']
                        break
                
                # in case of folder conflict
                if module_root_folder in listdir(dirpath):
                    
                    perror("a folder with the same name as the root folder\
 of the module to add is already in your project")
                    
                    pwarn(f"folder : {module_root_folder}")

                    if input("continue anyway ? [y/N]") in "yY":
                        pinfo(f"removing folder : {module_root_folder}")
                        
                        # handling permission error (and osers if there are)
                        try:

                            remove(f"{dirpath}/{module_root_folder}")

                        except Exception as e:
                            perror("An error occured while removing your files (it may be just that you are not administrator)")
                            pwarn("error message :")
                            print(e)
                    else:
                        return
                
                # end of normal run
                imported_module = import_module(f"pmanager.modules.{module}")
                imported_module.initialize(project_name)


            except Exception as e:
                perror("Error while initializing " + module)
                pwarn("error message :")
                print(e)
            
            i+=1
        else:
            pwarn(f"unexisting module : {module}")
