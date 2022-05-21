from os import mkdir,path
from pmanager.res import *

def initialize():
    mkdir("config")
    with open("config/default_ide.conf","w") as f:
        f.write("code")
        f.close()
    try:
        mkdir(get_home_dir_path()+"/projects_archive")
    except:
        pinfo("projects archives folder is already existing")


def change_default_editor(reset=False):
    if reset:
        ide_command = "code"
    else:
        ide_command = input("please put the path/command to open your favorite IDE :\n--> ")

    with open("config/default_ide.conf","w") as f:
        f.write(ide_command)
        f.close()

    psuccess("default IDE updated")

def change_default_path():
    path = input("new path --> ")

    if(path.endswith("/") or path.endswith("\\")):
        path = path[:-1]

    with open("config/default_path.conf","w",encoding="utf-8") as f:
        f.write(path)
        f.close()

    psuccess("default projects path updated")


def change_default_archive_path():
    path = input("new path --> ")

    if(path.endswith("/") or path.endswith("\\")):
        path = path[:-1]

    with open("config/default_archive_path.conf","w",encoding="utf-8") as f:
        f.write(path)
        f.close()

    psuccess("default projects archive path updated")



def change_terminal_command():

    with open("config/default_term.conf","w",encoding="utf-8") as f:
        f.write(input("terminal command (take care to put the working dir option at last) :\n-->"))
        f.close()

    psuccess("default terminal has been updated")


def delete_settings():
    """delete all superficial settings (all except folders settings)
    """
    pwarn("returning all settings except projects/archiving path to default settings")
    if path.exists("config/default_term.conf"):
        remove("config/default_term.conf")
        psuccess("removed custom terminal command")

    change_default_editor(reset = True)



def config_menu(namespace):
    print("""
    =====================CONFIGURATION====================

    [1] Select default editor
    [2] Change default projects path
    [3] Change default projects archiving path
    [4] Change default terminal command
    [5] Delete all settings (except projects and archiving path)

    =====================CONFIGURATION====================
    
    """)
    while True:
        choice = input("-->")
        
        if choice == "1":
            change_default_editor()
            break
        elif choice =="2":
            change_default_path()
            break
        elif choice =="3":
            change_default_archive_path()
            break
        elif choice == "4":
            change_terminal_command()
            break
        elif choice == "5":
            delete_settings()
            break
        else:
            print("Unknown option")
    
