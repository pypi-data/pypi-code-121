#from task.tasks import TaskProxy,Task
from flask import request
import requests
import json
import os
from file.info import FileInfo,DirInfo
from commonutil.config import Config
from task.tasks import TaskItem,TaskProxy
import base64

class FileServer:
    """
    client download from server
    """
    
    def getFullPath(namespace,path):
        if namespace == None:
            #root is None => path is full path
            return os.path.join("./" ,path)
        else:
            #root not None => path is rel path,find root at os.path
            realdir = Config.get("FileServer",namespace)
            
            if realdir is None:
                raise Exception("{} not in system path".format(namespace))
            return os.path.join(realdir,path)

    def getDir(namespace,path,filter = [],choise = []):
        dpath = FileServer.getFullPath(namespace,path)
        dir = DirInfo(dpath)
        return dir.getFilesName()
        '''
        
        '''

    def getFileStream(namespace,path,filename,start,slice = 128000):
        rtn = {"exists":False}
        dirpath = FileServer.getFullPath(namespace,path)
        fi = FileInfo(dirpath,filename)
        if not fi.Exists:
            return rtn
        rtn = fi.getFileStream(start,slice)
        
        return rtn

    """
    client upload to server
    """
    def setFileStream(namespace,path,filename,start,data):
        rtn = {"success":False}
        dirpath = FileServer.getFullPath(namespace,path)
        
        fi = FileInfo(dirpath,filename)
        #if not fi.Exists:
            #return rtn
        rtn = fi.setFileStream(start,data)
        return rtn
    
    def catchFileApi():
        namespace = request.json.get("namespace")
        path = request.json.get("path")
        filename = request.json.get("filename")
        start = request.json.get("start")
        data = request.json.get("data")
        #print(bytes(data,"utf-8"))
        rtn = FileServer.setFileStream(namespace,path,filename,int(start),base64.b64decode(bytes(data,"utf-8")))
        return json.dumps(rtn)
        pass
    
    def fetchFileApi():
        namespace = request.json.get("namespace")
        path = request.json.get("path")
        filename = request.json.get("filename")
        start = request.json.get("start")
        batch = request.json.get("batch")
        
        rtn = FileServer.getFileStream(namespace,path,filename,int(start))
        #print(rtn["data"])
        rtn["data"] = str(base64.b64encode(rtn["data"]),"utf-8")
        return json.dumps(rtn)
        pass
    pass

class TransFileTask(TaskItem):
    def __init__(self,namespace,local,path,fname,type):
        self._namespace = namespace
        self._local = local
        self._path = path
        self._filename = fname
        TaskItem.__init__(self,os.path.join(local,path,fname),type)
        pass
    
    @property
    def NameSpace(self):
        return self._namespace
    
    @property
    def Local(self):
        return self._local
    
    @property
    def Path(self):
        return self._path
    
    @property
    def FileName(self):
        return self._filename
    pass

class TransDirTask(TaskItem):
    def __init__(self,namespace,local,path,type):
        self._namespace = namespace
        self._local = local
        self._path = path
        TaskItem.__init__(self,os.path.join(local,path),type)
        pass
    
    @property
    def NameSpace(self):
        return self._namespace
    
    @property
    def Local(self):
        return self._local
    
    @property
    def Path(self):
        return self._path
    
    pass

class Client(TaskProxy):
    def __init__(self,url = "http://127.0.0.1:7001/download"):
        self._url = url
        self._task = None
        
        TaskProxy.__init__(self)
        
        pass
    
    def uploadFileStream(self,namespace,local,path,fname,start=0,batch = 128000):
            
        fi = FileInfo(local,fname)
        fs = fi.getFileStream(start,batch)
        fsdata = base64.b64encode(fs["data"])
        data = {'cmd':"updateFileStream",'namespace':namespace,'path':path,'local':local,'filename':fname,'start':start,'data':str(fsdata,"utf-8")}
        
        headers = {'Content-Type':'application/json'}
        response = requests.post(url=self._url,headers = headers, data = json.dumps(data))
        result = json.loads(response.text)
        result["surplus"] = fs["surplus"]
        return result

    def downloadFileStream(self,namespace,local,path,fname,start=0,batch = 128000):
        
        data = {'cmd':"downloadFileStream",'namespace':namespace,'path':path,'local':local,'filename':fname,'start':start}
        headers = {'Content-Type':'application/json'}
        response = requests.post(url=self._url,headers = headers, data = json.dumps(data))
        
        fi = FileInfo(local,fname)
        
        result = json.loads(response.text)
        
        if result["success"]:
            dt = base64.b64decode(bytes(result.pop("data"),"utf-8"))
            rst = fi.setFileStream(start,dt)
            result["size"] = rst["size"]
        return result
    
    def uploadFile(self,namespace,local,path,filename):
        self.addTask(TransFileTask(namespace,local,path,filename,"upload"))
        pass
    
    def downloadFile(self,namespace,local,path,filename):
        self.addTask(TransFileTask(namespace,local,path,filename,"download"))
        pass

    def runTask(self):
        if self._task == None:
            self._task = self.getTask()
            
        if self._task != None:
            tsk = self._task
            if tsk.Type == "upload":
                rst = self.uploadFileStream(tsk.NameSpace,tsk.Local,tsk.Path,tsk.FileName,tsk.Start)
                if rst["success"]:
                    tsk.Start = rst["size"]
                    tsk.To = rst["surplus"]
                    
                    if tsk.Process == 1:
                        self.finTask(tsk)
                        self._task = None
                else:
                    self._task = None
            elif tsk.Type == "download":
                rst = self.downloadFileStream(tsk.NameSpace,tsk.Local,tsk.Path,tsk.FileName,tsk.Start)
                if rst["success"]:
                    tsk.Start = rst["size"]
                    tsk.To = rst["surplus"]
                    
                    if tsk.Process == 1:
                        self.finTask(tsk)
                        self._task = None
                else:
                    self._task = None
                pass
                
            return
        
        pass

if __name__ == "__main__":
    uc = Client()
    #print(uc.uploadFileStream("test",r"d:/back/local","","123.txt",0))
    #print(uc.downloadFileStream("test",r"d:/back/local","","123.txt"))
    uc.downloadFile("test",r"d:/back/local","","1-160521014039.pdf")
    uc.runTask()
    while (uc._task != None):
        
        uc.runTask()
        print(100.0*uc.Process)
