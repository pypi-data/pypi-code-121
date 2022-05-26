#!/Users/jacky/tools/venv/bin/python3.9

# This app is developed for creating a new client/project with necessary structure, folders, and files. 

import os,argparse,json,shutil
from datetime import date
from config.system import ROOT_DIR

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def main():
    parser=argparse.ArgumentParser(description="For createing client/project with necessary structure, folders, and files")
    
    parser.add_argument("-cc", "--client", help="create a client working directory")
    parser.add_argument("-cp", "--project", help="create a project working directory ")

    args = parser.parse_args()

    if args.client:
        clientName=args.client
        if os.path.isdir(clientName):
            print(f'{clientName} is existing... ')
            return 
        else:
            os.makedirs(clientName)

        source=os.path.join(ROOT_DIR,"templates/client")
        copytree(source,clientName,symlinks=False,ignore=None)
        print(f'A working directory for client {clientName} is ready...')
        return 
    
    if args.project:
        # make project name, exp: 20211001-lmia
        today=date.today()
        project=(str)(today.year)+str(today.month).zfill(2)+str(today.day).zfill(2)+"-"+args.project

        # create project folder
        if os.path.isdir(project):
            print(f'The project {project} is existing...')
            return 
        else:
            os.makedirs(project)
        
        # get template folder
        jsonDir=os.path.join(ROOT_DIR,"templates/templates.json")
        with open(jsonDir) as jf:
            dirs=json.load(jf)
        source=os.path.join(ROOT_DIR,dirs[args.project])

        # copy template contents to working project
        copytree(source,project,symlinks=False,ignore=None)
        print(f'A working directory for project {project} is ready...')
        return 

if __name__=="__main__":
    main()

