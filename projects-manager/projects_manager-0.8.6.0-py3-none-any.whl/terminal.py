from platform import system
from subprocess import run, check_call, CalledProcessError
from re import split as sep
from os import path, getenv
from pmanager.res import *
from distro import id
from multiprocessing import Process

def run_cmd(cmd):
    """
    :raise: CalledProcessError

    """
    try:
        check_call(cmd,shell=True,close_fds=True)
    except CalledProcessError:
        raise CalledProcessError



def initialize(namespace):


    project_name = namespace.project_name[0]

    if not path.exists("config/default_path.conf"):

        dirpath = get_home_dir_path()+"/projects/"+project_name + "/"

    else:

        with open("config/default_path.conf","r",encoding="utf-8") as f:

            dirpath = f.read()+"/"+ project_name +"/"




    #check if the project exists
    if not path.exists(dirpath):
        perror("This project does not exists")
        exit(0)

    
    pinfo(f"opening project folder in terminal : \n {dirpath}")
    
    
    if path.exists("config/default_term.conf"):
        pinfo("Custom terminal command detected")
        with open("config/default_term.conf","r",encoding="utf-8") as f:
            sTermCmd = f.read()
            pinfo(f"running : {sTermCmd} \"{dirpath}\"")
            Process(run_cmd(f"{sTermCmd} \"{dirpath}\"")).start()
            f.close()

        return

    
    
    DEBIAN_BASED_DISTRO = ["debian","ubuntu","linuxmint","kali","raspbian","deepin","antix","parrot","devuan","av"]


    if system() == "Linux":

        if id() in DEBIAN_BASED_DISTRO:

            try:
            
                Process(run_cmd(f"x-terminal-emulator --working-directory \"{dirpath}\"")).start()
            except:
                perror("The command returned a non-zero status, pmanager is struggling to handle linux terminal emulators so it may be normal. Sorry bro x')")
            
        
        else:
            pwarn("non debiand-based distro, I will die before finishing to handle the amount of terminal emulators here.\n Trying some not really working things...")
        
            term_emulator = sep("-| ",getenv('TERM'))[0].strip("\n")

            pinfo(f"maybe detected default terminal emulator : {term_emulator}")

            try:
                Process(target=run_cmd,args=(f"{term_emulator} --workdir {dirpath}",)).start()

                pwarn(f"running : {term_emulator} --workdir {dirpath}")
            except CalledProcessError:
                try:
                    Process(target=run_cmd,args=(f"{term_emulator} --working-directory {dirpath}",)).start()

                    pwarn(f"running : {term_emulator} --working-directory {dirpath}")
                except CalledProcessError:
                    try:
                        Process(target=run_cmd,args=(f"{term_emulator} --w {dirpath}",)).start()

                        pwarn(f"running : {term_emulator} --w {dirpath}")
                    except CalledProcessError:
                        perror("Sorry, pmanager is not yet able to identify and start an instance of your terminal")

    
    
    elif system() == "Windows":
        run(["start","cmd.exe","/max", f"/k cd /d {dirpath}"],shell=True)