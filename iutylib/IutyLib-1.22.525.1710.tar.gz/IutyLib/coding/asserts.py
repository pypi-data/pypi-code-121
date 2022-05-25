import importlib

def assertImport(module):
    try:
        m = importlib.import_module(module)
        return m
    except Exception as err:
        #print(r"引入模块[{}]异常！".format(module))
        raise AssertionError(r"import [{}] failed！because:{}".format(module,str(err)))
    pass

def assertWorks(func,*args,**kwargs):
    try:
        func.__call__(*args,**kwargs)
    except Exception as err:
        raise AssertionError("function can not worked, "+str(err))
    pass

def assertEqual(arg1,arg2,msg = None):
    assertmsg = r"{} is not equal to {}".format(arg1,arg2)
    if msg:
        assertmsg += " ({})".format(msg)
    assert arg1 == arg2,assertmsg

def assertTrue(expr,msg = None):
    if not msg:
        msg = "assert"
    assertmsg = r"{} is not a true expression".format(msg)
    
    assert expr,assertmsg

def assertFalse(expr,msg = None):
    if not msg:
        msg = "assert"
    assertmsg = r"{} is not a false expression".format(msg)
    
    assert not expr,assertmsg

