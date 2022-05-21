from pmanager.res import *
from os import mkdir,path
from xml.etree import ElementTree as ET


def recursive(root,path):
    for item in root:

        if item.tag == "folder":
            sub_path = item.attrib['path']
            print(f"folder : {path}{sub_path}")
            mkdir(f"{path}{sub_path}")
            recursive(item,f"{path}{sub_path}/")

            
        elif item.tag == "file":
            fname = item.attrib['name']
            print(f"file : {path}{fname}")
            with open((path+fname),"w") as f:
                f.write(item.text)
                f.close()


def initialize(project_name):
    if not path.exists("config/default_path.conf"):
        dirpath = get_home_dir_path()+"/projects/"+project_name
    else:
        with open("config/default_path.conf","r",encoding="utf-8") as f:
            dirpath = f.read()+"/"+ project_name

    if not path.exists(dirpath):
            mkdir(dirpath)
        
    module_name = path.basename(__file__).replace(".py","")

    root = ET.parse(f"pmanager/modules/{module_name}.xml",).getroot()

    recursive(root,dirpath+"/")
    



