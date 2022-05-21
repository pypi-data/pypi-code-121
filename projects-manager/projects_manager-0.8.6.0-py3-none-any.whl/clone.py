try:
    from git import Repo
except ImportError:
    pass
    
from pmanager.res import *

def initialize(namespace):

    project_name = namespace.project_name[0]
    git_url = namespace.git_url[0]

    if not path.exists("config/default_path.conf"):
        dirpath = get_home_dir_path()+"/projects/"+project_name
    else:
        with open("config/default_path.conf","r",encoding="utf-8") as f:
            dirpath = f.read()+"/"+ project_name

    if path.exists(dirpath):
        perror(f"This project does not exist : \n {dirpath}")
        exit(1)

    try:
        pinfo(f"cloning into {git_url}...")

        Repo.clone_from(git_url,dirpath)

        psuccess(f"cloned repo to a new project : {project_name}\n({dirpath})")
    
    except Exception as e:
        perror(f"an error occured while cloning repo : \n{e}")

