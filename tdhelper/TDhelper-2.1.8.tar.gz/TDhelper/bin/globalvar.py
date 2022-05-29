global _globaldict
_globaldict={}

def setGlobalVariable(key,value):
    _globaldict[key]=value

def deleteGlobalVariable(key):
    del _globaldict[key]

def getGlobalVariable(key,defaultValue=None):
    try:
        return _globaldict[key]
    except Exception as e:
        return defaultValue
        
def hasKey(key):
    if key in _globaldict:
        return True
    return False

'''
    define the system's event cache,if you have't set this param you can call deleteGlobalVariable to delete it;
'''
setGlobalVariable("EventList",{})