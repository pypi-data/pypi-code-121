import os
import sys

from os.path import expanduser

import requests
import json

from .timestamp import timestamp

from functools import lru_cache

import numpy as np

hosts=["https://raw.githubusercontent.com/psorus/yanodata/main/{fn}"]

dic_frequency=3600*24


@lru_cache(maxsize=1)
def getbasepth():
    pth=expanduser("~")+"/.yano/data/"
    os.makedirs(pth, exist_ok=True)
    return pth

def calcpath(fn):
    return getbasepth()+fn

def no_file_name(fn):
    if "/" in fn:
        fn=fn[fn.rfind("/")+1:]
    if "." in fn:
        fn=fn[:fn.rfind(".")]
    return fn


def download(fn):
    outp=calcpath(fn)
    for host in hosts:
        url=host.format(fn=fn)
        print(f"Downloading {fn} from {url}")
        r=requests.get(url)
        if r.status_code==200:
            with open(outp, "wb") as f:
                f.write(r.content)
            ages=loadages()
            ages[no_file_name(fn)]=timestamp()
            saveages(ages)
            return
    print(f"Failed to download {fn}")
    exit()

def loadages():
    if os.path.isfile(calcpath("ages.json")):
        return json.load(open(calcpath("ages.json")))
    else:
        return {}

def force_update_dic():
    download("dic.json")

@lru_cache(maxsize=1)
def loaddic():
    assertfile("dic.json",do_check_age=False)
    loct=local_update("dic.json")
    if (loct is None) or (loct<timestamp()-dic_frequency):
        download("dic.json")
    return json.load(open(calcpath("dic.json")))

def fileinfo(fn):
    dic=loaddic()
    fn=no_file_name(fn)
    assert fn in dic.keys(), f"{fn} unknown"
    return dic[fn]

def allfiles():
    dic=loaddic()
    return list(dic.keys())

def countfiles():
    return len(allfiles())

def saveages(ages):
    ages["last"]=timestamp()
    with open(calcpath("ages.json"), "w") as f:
        json.dump(ages, f, indent=2)

def official_update(fn):
    dic=loaddic()
    fn=no_file_name(fn)
    assert fn in dic.keys(), f"{fn} untracked"
    try:
        return dic[fn]["last"]
    except KeyError:
        return 0

def local_update(fn):
    ages=loadages()
    fn=no_file_name(fn)
    if fn in ages.keys():
        return ages[fn]
    else:
        return None


def check_age(fn):
    official=official_update(fn)
    local=local_update(fn)
    if local is None:
        return False
    return local>=official

def assertfile(fn,do_check_age=True):
    if not (os.path.isfile(calcpath(fn)) and (not do_check_age or check_age(fn))):
        download(fn)
    return calcpath(fn)


def loaddata(fn):
    fn=fn+".npz"
    assertfile(fn)
    f=np.load(calcpath(fn))
    return f["x"],f["y"]


if __name__=="__main__":

    #dic=loaddic()

    #print(json.dumps(dic, indent=2))

    x,y=loaddata("cardio")
    print(x.shape,y.shape)






