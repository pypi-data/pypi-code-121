


_unittest_ = []

def unittest(testfunc):
    d = {"func":testfunc,"skip":False}
    _unittest_.append(d)
    
    return testfunc


def skip(testfunc):
    for d in _unittest_:
        if testfunc == d["func"]:
            d["skip"] = True
            break


class Event:
    def __init__(self,func):
        self.name = func.__name__
        self.cls = func.__class__
        self._deles_ = []
    
    
    
    def __iadd__(self,delegate):
        self._deles_.append(delegate)
        return self
    
    def __isub__(self,delegate):
        while delegate in self._deles_:
            self._deles_.remove(delegate)
        return self
    
    def __call__(self,*args):
        for d in self._deles_:
            d(self.name,*args)
        pass

def eve(func):
    e = Event(func)
    return e


class A:
    def __init__(self):
        self.e = []
    
    @eve
    def OnMsg(sender,*args):
        pass
        

def handle(sender,*args):
    print(sender)


if __name__ == "__main__":
    a = A()
    a.OnMsg += handle
    
    
    a1 = A()
    a1.OnMsg += handle
    a.OnMsg()