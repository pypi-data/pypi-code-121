import configparser,json,os
def getPickleData(path,isDictionary = False):
    """
    help pass
    """
    import os,pickle
    if os.path.exists(path):
        file = open(path,'rb')
        rtn = pickle.load(file)
        file.close()
        return rtn
    if isDictionary:
        return {}
    return []

def savePickleData(path,memery):
    """
    help pass
    """
    import os,pickle
    f = open(path,'wb')
    pickle.dump(memery,f)
    f.close()
    
class Config:
    def __init__(self,path="./Config/Config.conf"):
        self._path = path
        self._config = configparser.ConfigParser()
        self._config.read(self._path)
        pass
        
    def get(self,session,key):
        rtn = None
        try:
            rtn = self._config.get(session,key)
        except Exception as err:
            a = 1
        return rtn
    
    def set(self,session,key,val):
        if not self._config.has_section(session):
            self._config.add_section(session)
        self._config.set(session,key,val)
        
        self.save()
        pass
    
    def save(self):
        with open(self._path,'w') as f:
            self._config.write(f)
        self._config.read(self._path)
        pass
    
    def getSections(self):
        
        rtn = []
        try:
            rtn = self._config.sections()
        except Exception as err:
            print(str(err)+"in Config getSections")
        return rtn
    
    def getOptions(self,section):
        rtn = []
        try:
            rtn = self._config.options(section)
        except Exception as err:
            print(str(err)+"in Config getOption")
        return rtn
    
    def rmSection(self,section):
        self._config.remove_section(section)
        self.save()
        pass
    
    def rmOption(self,section,option):
        self._config.remove_option(section,option)
        self.save()
        pass
    
    def copy(self,target,section,key,defaultvalue):
        v = self._config.get(section,key)
        if not v:
            v = defaultvalue
        try:
            target.set(section,key,v)
        except Exception as err:
            print(err+"in Config copy")
        pass

class JConfig:
    """
    path:[string] config path
    default:[dict] default value for config
    reset:[bool] delete local config file before load
    """
    def __init__(self,path="./Config/Config.json",default = {},reset=False):
        self._path = path
        self._config = default
        if reset:
            os.remove(self._path)
        self.load()
        pass
    
    def load(self):
        try:
            if os.path.exists(self._path):
                with open(self._path,'r') as f:
                    self._config = json.load(f)
        except:
            print("load json error")
        pass
    
    def save(self):
        with open(self._path,'w') as f:
            json.dump(self._config,f,indent=4)
        self.load()
        pass
    
    def get(self):
        return self._config
    
    pass
    
if __name__ == "__main__":
    cfg = JConfig(default={'app':"test app"})
    #cfgvalue = cfg.get()
    #cfgvalue["app"] = "appname name"
    #cfgvalue["setting"] = {'port':3378,'ip':"127.0.0.1"}
    cfg.save()