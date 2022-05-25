class SingleTon:
    def __init__(self,cls):
        self._cls = cls()
        
        pass

    def __call__(self):
        return self._cls   
    pass

class Center:
    _tps_ = {}
    def __init__(self,tp):
        
        self._tps_ = Center._tps_
        self._items_ = []
        self._tp = tp
        if not tp in Center._tps_:
            Center._tps_[str(tp)] = self
        pass

    def __call__(self,tp):
        return tp
        
    

    def T(tp): 
        if not tp in Center._tps_:
            Center(tp)      
        return Center._tps_[str(tp)]
    
    def login(self,item):
        
        if issubclass(type(item),self._tp):
            self._items_.append(item)
    
    def logout(self,item):
        if item in self._items_:
            self._items_.remove(item)
    
    def isMatch(skwargs,obj):
        
        pkwargs = obj.__dict__
        for k in skwargs:
            if not k in pkwargs:
                return False
            if str(skwargs[k]) != str(pkwargs[k]):
                return False
        return True

    def findFirst(self,**skwargs):
        rtn = None
        for item in self._items_:
            if Center.isMatch(skwargs,item):
                rtn = item
                break
        return rtn
    

    def findAll(self,**skwargs):
        rtn = []
        for item in self._items_:
            if Center.isMatch(skwargs,item):
                rtn.append(item)
        return rtn
        


if __name__ == "__main__":
    class C:
        pass
    @SingleTon
    class A(C):
        pass

    from IutyLib.coding.asserts import *
    a1 = A()
    a2 = A()

    assertEqual(a1,a2)

    
    @Center(C)
    class B(C):
        def __init__(self):
            self.A = 10
        
        def __str__(self):
            return "class B: A = {}".format(self.A)
        pass

    
    assertTrue(str(C) in Center._tps_)
    ctr = Center.T(C)

    ctr.login(a1)
    #print(ctr)
    b1 = B()
    b2 = B()
    b2.A = 999
    ctr.login(b1)
    ctr.login(b2)

    assertTrue(len(ctr.findAll()) == 3,"items in center is not 3")
    
    assertTrue(ctr.findFirst(A=999) is ctr.findAll(A=999)[0])
    assertTrue(a1 in ctr.findAll(),"a1 can login at C center")
    ctrB = Center.T(B)
    ctrB.login(a1)
    assertFalse(a1 in ctrB.findAll(),"a1 must not login at B center")
    #print(ctrB)

    