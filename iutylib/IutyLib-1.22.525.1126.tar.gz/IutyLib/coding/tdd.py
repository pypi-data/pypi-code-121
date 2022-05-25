"""
import os,sys,time,json,datetime
from IutyLib.coding.asserts import assertImport

passed = "passed"
skiped = "skiped"
failed = "failed"

class BaseTest:
    _testmode = False
    
    #_modules_ = []
    
    _cases_ = []
    msg = ""
    mustpass = []
    pass

def setup(module,reload=True):
    #if modulepath ins_MethodTest._modules_
    abspath = os.path.abspath(module)
    """
    if abspath in ins_MethodTest._modules_:
        if reload:
            importlib.reload(module)
            print(r"reload [{}] successed!".format(module))
        return
    """
    try:
        m = assertImport(module)
        print(r"import [{}] successed！".format(module))
        #ins_MethodTest._modules_.append(abspath)
        return m
    except AssertionError as err:
        print(err)
    
    #print(ins_MethodTest._modules_)
    pass

def case(msg = "have not set message yet",mustpass=[]):
    ins_MethodTest.msg = msg
    ins_MethodTest.mustpass = mustpass
    return testfuncwrapper
    
def testfuncwrapper(func):
    if ins_MethodTest._testmode:
        ins_MethodTest._cases_.append(
        {
            'file':func.__globals__['__file__'],
            'name':func.__name__,
            'func':func,
            'msg':ins_MethodTest.msg,
            "mustpass":ins_MethodTest.mustpass
        })
    
    return func

def test_method(result,testcase):
    
    file = testcase["file"]
    name = testcase["name"]
    func = testcase["func"]
    mustpass = testcase["mustpass"]
    if not (file in result["cases"]):
        result["cases"][file] = {}
    
    if name in result["cases"][file]:
        return True
    
    for item in mustpass:
        #不可跨文件增加约束
        if not (item in result["cases"][file]):
            print("detect mustpass case [{}] when test in {}".format(item,name))
            return False
        else:
            if result["cases"][file][item]["result"] != "passed":
                result["cases"][file][name] = {}
                report = result["cases"][file][name]
                report["result"] = skiped
                report["message"] = "skiped because dependence {} is not pass the test".format(item)
                return True
    print('-'*20)
    
    result["cases"][file][name] = {}
    report = result["cases"][file][name]
    cs = time.time()
    try:
        func()
        print("{} test passed".format(name))
        report["result"] = "passed"
            
    except AssertionError as err:
        
        print("[line:{}] {} test failed! ({})".format(err.__traceback__.tb_next.tb_lineno,name,str(err)))
        report["result"] = "failed"
        report["message"] = "[line:{}]:{}".format(err.__traceback__.tb_next.tb_lineno,str(err))
    ce = time.time()
    report["spend"] = round(ce-cs,3)
    return True



def test_process(resultpath=r"./",testlimit = 10,post = None):
    rtn = {"spend":0.0,"cases":{}}
    gs = time.time()
    
    
    for i in range(testlimit):
        alltested = True
        for testcase in ins_MethodTest._cases_:
            result = test_method(rtn,testcase)
            alltested &= result
        if alltested:
            break
    
    ge = time.time()
    rtn["spend"] = round(ge-gs,3)
    
    now = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(now,"%y%m%d_%H%M%S")
    
    if resultpath:
        try:
            resultfile = os.path.join(resultpath,timestamp+".json")
            with open(resultfile,'w') as f:
                json.dump(rtn,f,indent = 4)
        except Exception as err:
            print("Save test result failed")
            print(err)
        
    if post:
        raise Exception("No post func here")
    pass
    
    



class MethodTest(BaseTest):
    
    pass


    
ins_MethodTest = MethodTest()

"""

_testlist_ = {}

class TestOption:
    def __init__(self):
        self.skip = False
        self.mustpass = False
        pass



def unittest(func):
    if not func in _testlist_:
        _testlist_[func] = TestOption()
    return func


def skip(func):
    if func in _testlist_:
        _testlist_[func].skip = True
    pass

def mustpass(func):
    if func in _testlist_:
        _testlist_[func].mustpass = True
    pass

def businesstest(func):
    if not func in _testlist_:
        _testlist_[func] = TestOption()
    return func
