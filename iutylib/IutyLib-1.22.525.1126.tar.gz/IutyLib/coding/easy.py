


def singleton(cls):
    """
    单例装饰，在类上
    """
    def getins(*args,**kwargs):
        if not getins.ins:
            getins.ins = cls(*args,**kwargs)
        return getins.ins
    getins.ins = None
    return getins

__cents__ = {}
def center(cls):
    def login(obj):
        obj.__class__._center_.append(obj)
        pass
    
    def logout(obj):
        if obj in obj.__class__._center_:
            obj.__class__._center_.remove(obj)
            print(111)
        pass 
    
    if not cls in __cents__:
        __cents__[cls] = []
        cls._center_ = __cents__[cls]
        cls.login = login
        cls.logout = logout
        cls.__del__ = logout
    
    return cls
        

@center
class A:
    def __init__(self):
        self.a = 1
        pass


if __name__ == "__main__":
    for i in range(5):
        a = A()
    
        a.login()
        a.__del__()
        
        print(__cents__[A])