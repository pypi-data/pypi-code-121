from os import path
from xml.etree import ElementTree as ET
from pmanager.res import  pinfo, psuccess



def initialize(namespace):
    project_name = namespace.project_name[0]
    

    command = input("IDE/startup command (manual, so it needs the full path of your project etc...)\n--> ")
    
    #escape some characters

    command.replace("&","&amp;")
    command.replace("\"","&quot;")
    command.replace("'","&apos;")
    command.replace("<","&lt;")
    command.replace(">","&gt;")

    if not path.exists(f"config/{project_name}.xml"):
        with open(f"config/{project_name}.xml","w") as f:
            f.write(f'<config>\n<ide>{command}</ide>\n</config>')
            f.close()
    else:
        #get previous content
            with open(f"config/{project_name}.xml","r") as f:
                prev_ctt = f.read()
                f.close()

            #add the command at the end and re-write the file
            with open(f"config/{project_name}.xml","w") as f:
                f.write(prev_ctt.replace("</config>",f"<ide>{command}</ide>\n</config>"))
                f.close()

    psuccess(f"Added project IDE/start command :\n{command}")




#used in open module to get custom start command
def get_default_ide(project_name):

    root = ET.parse(f"config/{project_name}.xml",).getroot()

    commands = [i.text.replace("\n","") for i in root.findall("ide")]
    
    return commands
