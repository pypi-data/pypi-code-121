import os,sys
import shutil
from IutyLib.file.io import copyTree


def getSitePath():
    pe = os.getenv('path')
    ps = pe.split(';')
    for pi in ps:
        if pi.endswith('site-packages'):
            return pi
    return None

def getTemplatePath():
    templatepath = os.getenv("IutyTemplates")
    return templatepath

def templist(templatepath):
    
    temps = os.listdir(templatepath)
    return temps

def doInit():
    if len(sys.argv) < 3:
        print("init script run as:\r\nChange to project path.\r\nkey on:'pyinit' templatename solutionname")
        return
    
    templatepath = getTemplatePath()
    
    if not templatepath:
        print("can not detect templatepath in environ, process failed")
        return
    
    templatename = sys.argv[1]
    solutionname = sys.argv[1]
    if len(sys.argv) >2:
        solutionname = sys.argv[2]
    
    
    workdir = os.getcwd()
    workdir = os.path.join(workdir,solutionname)
    
    templatelist = templist(templatepath)
    print("get templates:{}".format(templatelist))
    
    if templatename in templatelist:
        templatedir = os.path.join(templatepath,templatename)
        copyTree(templatedir,workdir)
    else:
        print("no such template named '{}'".format(templatename))
    pass

def main():
    doInit()
    pass

if __name__ == "__main__":
    doInit()
    pass