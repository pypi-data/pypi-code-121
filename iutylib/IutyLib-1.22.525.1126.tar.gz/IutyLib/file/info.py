from encription.encription import getfilemd5,des_descrypt,des_encrypt
import os
import random


class FileInfo:
    def __init__(self,path,name):
        self._name = name
        self._dir = DirInfo(path)
        pass
    
    @property
    def FullPath(self):
        return os.path.join(self._dir.Path,self._name)
    
    @property
    def Directory(self):
        return self._dir
    
    @property
    def Name(self):
        return self._name
    
    @property
    def Exists(self):
        return True if os.path.exists(self.FullPath) else False
        
    def getMd5(self):
        rtn = ""
        
        if self.Exists():
            rtn = getfilemd5(self.FullPath)
        return rtn
    
    @property
    def Size(self):
        rtn = 0
        if self.Exists:
            rtn = os.path.getsize(self.FullPath)
        return rtn
    
    def creat(self):
        f = open(self.FullPath,"ab")
        f.close()
        pass
    
    def getFileStream(self,start,batch = 1000):
        rtn = {'success':False}
        if not self.Exists:
            return rtn
        file = open(self.FullPath,'rb')
        
        file.read(start)
        data = file.read(batch)
        
        surplus = len(file.read())
        
        rtn['data'] = data
        rtn['surplus'] = surplus
        
        rtn['success'] = True
        file.close()
        return rtn
    
    def setFileStream(self,start,bs):
        rtn = {'success':False}
        if not self.Directory.Exists:
            self.Directory.creat()
        
        if not self.Exists:
            self.creat()
        
        file = open(self.FullPath,"rb+")
        cur = len(file.read())
        if start != cur:
            
            rtn['err'] = "file size not match with start"
        else:
            batch = file.write(bs)
            rtn['success'] = True
        file.close()
        size = self.Size
        rtn['size'] = size
        return rtn

class DirInfo:
    def __init__(self,path):
        self._path = path
    
    @property
    def Path(self):
        return self._path
    
    @property
    def Exists(self):
        return True if os.path.exists(self._path) else False
    
    def getFilesName(self):
        rtn = {'exists':False}
        if self.Exists:
            files = os.listdir(self._path)
            fs = [file for file in files if os.path.isfile(self._path+file)]
            rtn['exists'] = True
            rtn['files'] = fs
        return rtn
        
    def getInfo(self,file = True,dir = True,belong = True,choise = [],filter = []):
        rtn = {"exists":False}
        
        if os.path.exists(self._path):
            rtn["exists"] = True
            rtn["dirs"] = []
            rtn["files"] = []
            for root,dirs,files in os.walk(self._path):
                for dir in dirs:
                    if root != self._path:
                        continue
                    rtn["dirs"].append(dir)
                for file in files:
                    if root != self._path:
                        continue
                    ext = file.split('.')[-1]
                    if len(filter) > 0:
                        if ext in filter:
                            continue
                    if len(choise) > 0:
                        if not (ext in choise):
                            continue
                    rtn["files"].append(file)
        return rtn
    
    def getFilesInfo(self,start=0,**kwargs):
        batch = 200
        if 'Size' in kwargs:
            batch = batch//2
        if 'Md5' in kwargs:
            batch = batch//4

        rtn = {'start':start}
        
        files = self.getFilesName()
        rtn['filecount'] = len(files)
        if start > len(files)-1:
            return rtn
        end = start + batch
        
        if (start + batch) >= len(files):
            end = len(files)

        fs = []
        rtn['files'] = fs

        for filename in files[start:end]:
            finfo = {'Name':filename}
            fi = FileInfo(self._path,filename)
            if 'Size' in kwargs:
                finfo['Size'] = fi.getSize()
            if 'Md5' in kwargs:
                finfo['Md5'] = fi.getMd5()
            finfo = {'Name':filename,'Md5':md5,'Size':size}
            fs.append(finfo)
        
        return rtn
    
    def creat(self):
        if not self.Exists:
            os.mkdir(self._path)