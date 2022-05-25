import os

errmsg=[
    "copy src is not exists",
    "copy tgt parent is not exists",
]

def removeFile(path):
    if os.path.exists(path):
        os.remove(path)
    pass

def copyFile(src,tgt):
    if os.path.isfile(src):
        if os.path.exists(os.path.dirname(tgt)):
            open(tgt,'wb').write(open(src,'rb').read())
        else:
            raise IOError(errmsg[1])
    pass

def copyTree(src,tgt,instead = False):
    src = os.path.abspath(src)
    tgt = os.path.abspath(tgt)
    
    if not os.path.exists(src):
        raise IOError(errmsg[0])
    
    if not os.path.exists(os.path.dirname(tgt)):
        raise IOError(errmsg[1])
    
    if not os.path.exists(tgt):
        os.mkdir(tgt)
    
    for p,d,f in os.walk(src):
        for di in d:
            spath = os.path.join(p,di)
            tpath = spath.replace(src,tgt)
            if not os.path.exists(tpath):
                os.mkdir(tpath)
        for fi in f:
            spath = os.path.join(p,fi)
            tpath = spath.replace(src,tgt)
            if os.path.exists(tpath):
                if instead:
                    copyFile(spath,tpath)
            else:
                copyFile(spath,tpath)
    pass