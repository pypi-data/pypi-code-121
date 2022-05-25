import json
def isIns(obj):
    return any([isinstance(obj,int) , isinstance(obj,str) , isinstance(obj,float)])
    
def extract(obj):
    rtn = None
    if isIns(obj):
        rtn = obj
    
    else:
        
        if type(obj) is dict:
            rtn = obj
            its = obj
        elif type(obj) is list:
            rtn = obj
            its = range(len(obj))
        else:
            rtn = obj.__dict__
            its = obj.__dict__
        for it in its:           
            if not isinstance(rtn[it],type):                
                rtn[it] = extract(rtn[it])
    return rtn

def inject(obj,json):
    
    rtn = None
    if isIns(json):
        rtn = json
    else:
        rtn = obj
        if type(obj) is dict:
            
            for it in json:
                obj[it] = inject(None,json[it])
                
            
        elif type(obj) is list:
            for it in range(len(json)):
                v = inject(None,json[it])
                if it < len(obj):
                    obj[it] = v
                else:
                    obj.append(v)
        else:
            for d in json:
                
                obj.__dict__[d] = inject(obj.__dict__[d],json[d])
    return rtn

class Model:

            
    
    def toConfig(self):
        
        return extract(self)
    
    def fromConfig(self,config):
        inject(self,config)


if __name__ == "__main__":
    class B:
        def __init__(self):
            self._B = "my B"
            self.__t__ = {"t1":13}
            self._t_ = [1]

    class A(Model):
        def __init__(self):
            self.A = 10
            
            self.B = B()
            pass
    
    a = A()
    a.B._B = "changed B"
    a.B.__t__["append"] = "vv13"
    a.B._t_.append(10)
    config = a.toConfig()
    print(config)
    a1 = A()
    a1.fromConfig(config)
    print(a1.B._B)
    print(a1.B.__t__)
    print(a1.B._t_)

    