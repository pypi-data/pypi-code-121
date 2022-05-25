from IutyLib.commonutil.config import Config
from IutyLib.coding.compile import compile_list
import datetime,os,sys
import git
import re
from twine.cli import dispatch

from twine.commands.check import main as check
from twine.commands.register import main as register
from twine.commands.upload import main as upload

import json

def setVersion(cfg):
    dt = datetime.datetime.now()
    yy = dt.strftime("%y")
    mmdd = dt.strftime("%m%d")
    HHMM = dt.strftime("%H%M")
    
    cfg.set("Version","subver","{}.{}.{}".format(yy,mmdd,HHMM))
    pass

def setCompile(cfg):
    tdir = cfg.get("Path","release")
    sdir = r"./source"
    compile_list(sdir,tdir)
    pass

def setVersionOnPythonPackage(root = "./",major = 1):
    pattern = "__version__ = .*$"
    filename = "__init__.py"
    now = datetime.datetime.now()
    for r,ds,fs in os.walk(root):
        if filename in fs:
            print("set __init__ Version at path {}".format(r))
            file = open(os.path.join(r,filename),"r")
            info = file.read()
            file.close()
            
            
            ver = "__version__ = '{}.{}'".format(major,datetime.datetime.strftime(now,'%y.%m%d.%H%M'))
            info = re.sub(pattern,ver,info)
            
            file = open(os.path.join(r,filename),"w")
            file.write(info)
            file.close()


def setVersionOnpy():
    if not os.path.exists(r"./setup.py"):
        print("setup.py is not in current directory")
        return
    f = open("./setup.py","r")
    lines = f.readlines()
    f.close()
    for fi in range(len(lines)):
        fl = lines[fi]
        splits = fl.split('=')
        if splits[0] == "version ":
            now =datetime.datetime.now()
            lines[fi] = "version = '1.{}'\n".format(datetime.datetime.strftime(now,'%y.%m%d.%H%M'))
            print("set {}".format(lines[fi]))
            f = open("./setup.py","w")
            f.writelines(lines)
            f.close()
            print("set version complete")
            break

def setCSharpVersion(root = "./",major = 1):
    pattern = "([1-9])(.\d{2})(.\d{4}){2}"
    pattern0 = "([1-9])(.[0-9])(.[0-9])(.[0-9])"
    filename = "AssemblyInfo.cs"
    now = datetime.datetime.now()
    for r,ds,fs in os.walk(root):
        if filename in fs:
            print("setC#Version at path {}".format(r))
            file = open(os.path.join(r,filename),"r")
            info = file.read()
            file.close()
            
            fbak = open(os.path.join(r,filename+".old"),"w")
            fbak.write(info)
            fbak.close()
            
            ver = "{}.{}".format(major,datetime.datetime.strftime(now,'%y.%m%d.%H%M'))
            info = re.sub(pattern,ver,info)
            info = re.sub(pattern0,ver,info)
            file = open(os.path.join(r,filename),"w")
            file.write(info)
            file.close()
    

def getRepo():
    try:
        repo = git.Repo("./")
        return repo
    except:
        return None

def commit(repo):
    if repo.is_dirty():
        ufs = repo.untracked_files
        for uf in ufs:
            print(repo.git.add(uf))
        print("start commit")
        print(repo.git.commit("-am","regular commit",author="iuty"))
    pass

def push(repo,remote="gitee",branch="master"):
    print("start push code to gitee")
    print(repo.git.push(remote,branch))
    pass

def push2git():
    #config = Config("./Config.conf")
    #setCompile(config)
    print("start set config process")
    #setVersion(config)
    setVersionOnpy()
    setVersionOnPythonPackage()
    setCSharpVersion()
    repo = getRepo()
    commit(repo)
    push(repo)
    print("publish to git process ok...")
    pass

def compileDist():
    sys.argv.append("sdist")
    sys.path.append(r"./")
    print(sys.path)
    import setup
    pass

def clearDir(path):
    for mdir,ds,fs in os.walk(path):
        for f in fs:
            fp = os.path.join(mdir,f)
            print("remove file {}".format(fp))
            os.remove(fp)
            

def upload2pip():
    try:
        
        dispatch(["upload","dist/*"])
    except Exception as err:
        print("upload to pipy error")
        print(err)

def setNpmVersion():
    path = r"./package.json"
    if not os.path.exists(path):
        print("package.json is not exists in the current directory")
        return
    try:
        with open(path,'r') as f:
            obj_json = json.load(f)
        now =datetime.datetime.now()
        version = "1.{}".format(datetime.datetime.strftime(now,'%y.%m%d.%H%M'))
        print("set npm version to {}",format(version))
        obj_json["version"] = version
        
        with open(path,'w') as f:
            json.dump(obj_json,f,indent=4)
    except Exception as err:
        print("set npm version error")
        print(err)
    
    pass
    

def main():
    
    cmd = "git"
    if len(sys.argv) > 1:
        cmd = sys.argv.pop(1)
    
    if cmd == "git":
        push2git()
    elif cmd == "pip":
        clearDir(r"./dist")
        compileDist()
        upload2pip()
    elif cmd == "npm":
        setNpmVersion()
    else:
        print("cmd is not recorgnized")

def test():
    setCSharpVersion()

if __name__ == "__main__":
    main()
    pass