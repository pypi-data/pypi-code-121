import json



class ModelOption:
    def __init__(self):
        self._configignore = []
        pass
    
    def getOption(cls:type):
        if not "_modeloption" in cls.__dict__:
            cls._modeloption = ModelOption()
        return cls._modeloption
    
    def configignore(cls:type,key:str):
        
        option = ModelOption.getOption(cls)
        option._configignore.append(key)
        return cls




def configignore(key:str):
    def addin(cls):
        ModelOption.configignore(cls,key)
        return cls
    return addin



class A:
    
    def __init__(self):
        self.a = 1
        pass
    pass
    

@configignore("a")
class B:
    
    def __init__(self):
        self.a = A()
        self.b = "B"
        
        pass
    pass

b = B()

def isclass(m):
    return not ((type(m) is int) or (type(m) is str) or (type(m) is bool) or (type(m) is dict))


def getModel(m):
    rtn = m
    if isclass(m):
        rtn = m.__dict__
        ls = list(rtn.keys())
        option = ModelOption.getOption(type(m))
        
        for k in ls:
            
            if k in option._configignore:
                rtn.pop(k)
                continue
            rtn[k] = getModel(rtn[k])
    return rtn

b.a.a = 13


def setModel(source,target):
    if isclass(source):
        source = getModel(source)
    if isclass(target):
        for si in target.__dict__:
            if si in source:
                if isclass(target.__dict__[si]):
                    setModel(source[si],target.__dict__[si])
                else:
                    target.__dict__[si] = source[si]
    pass



b1 = B()
setModel(b,b1)

print(getModel(b1))