import datetime,os,sys,requests,json

url = "http://139.9.137.187:7780/api/file/fileserver"


def getArg(args,key):
    if len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        args[key] = arg

def printHelp():
    for ck in __cmd__:
        print("{}\t\t{}".format(ck,__cmd__[ck][0]))
    pass

def printResponse(cmd,json):
    print("receive response cmd = {}".format(cmd))
    print(json)
    pass

def printList():
    data = {"cmd":"list"}
    getArg(data,"index")
    
    json = requests.post(url,data).json()
    print(json)

def pushDirectory(dirname):
    for mdir,sdirs,fs in os.walk("./"):
        if len(fs) > 0:
            for f in fs:
                filepath = os.path.join(mdir,f)
                fi = open(filepath,'rb')
                stream = fi.read()
                file = (f,stream)
                filerelpath = filepath.replace("./","")
                
                filerelpath = filerelpath.replace("\\","/")
                #print(filepath)
                data = {"cmd":"append","dirname":dirname,"filename":filerelpath,"start":True}
                print("上传文件：{}".format(f))
                rtn = requests.post(url,data = data,files = {"file":file})
                print(rtn.json())
                

def push():
    data = {"cmd":"push"}
    getArg(data,"index")
    getArg(data,"tag")
    
    #print(requests.post(url,data).content)
    json = requests.post(url,data).json()
    printResponse("push",json)
    pushDirectory(json["data"])
    pass
    
    

def pull():
    if len(sys.argv) < 2:
        print("tag command argv is less than 2")
        return
    
    data = {"cmd":"pull"}
    
    getArg(data,"index")
    getArg(data,"tag")
    
    json = requests.post(url,data).json()
    printResponse("pull",json)
    
    dirname = json["data"]["dirname"]
    filelist = json["data"]["filelist"]
    
    for file in filelist:
        data = {"cmd":"fetch","dirname":dirname,"filename":file}
        stream = requests.get(url,data).content
        
        fullpath = os.path.join("./",file)
        if os.path.exists(fullpath):
            continue
        pathname = os.path.dirname(fullpath)
        if not os.path.exists(pathname):
            os.makedirs(pathname)
        f = open(fullpath,"wb")
        f.write(stream)
        f.close()
    pass

def tag():
    if len(sys.argv) < 4:
        print("tag command argv is less than 4")
        return
    
    index = sys.argv.pop(1)
    oldtag = sys.argv.pop(1)
    newtag = sys.argv.pop(1)
    
    data = {"cmd":"tag","index":index,"tag":oldtag,"tagname":newtag}
    
    json = requests.post(url,data).json()
    printResponse("tag",json)

__cmd__ = {
    "help":["print help info on cli",printHelp],
    
    "list":["ifs list [index]: show index list or tag list",printList],
    "push":["ifs push index [tag] [-s(kip)/-r(emove) if exist]: push local resource to remote",push],
    
    "pull":["ifs pull index [tag] ",pull],
    "tag":["ifs tag index oldtag newtag:reset a tag name",tag]
    
}

def main():
    
    cmd = "help"
    if len(sys.argv) > 1:
        cmd = sys.argv.pop(1)
    
    if cmd in __cmd__:
        __cmd__[cmd][1]()
    else:
        print("cmd:{} is unrecorgnised".format(cmd))

if __name__ == "__main__":
    main()
    pass