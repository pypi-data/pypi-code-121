import sys,os,importlib
from IutyLib.coding.tdd import ins_MethodTest, test_process
ins_MethodTest._testmode  = True

def getArgv():
    if len(sys.argv) == 0:
        return None
    return sys.argv.pop(0)


def main():
    getArgv()
    path = getArgv()
    
    if not path:
        print("Path is nesserary at the 1st parameter place")
        return
    """
    if not os.path.exists(path):
        print("{} is not exists".format(path))
    """
    if path[-3:] == ".py":
        path = path[:-3]
    try:
        
        importlib.__import__(path)
    except:
        print("import module error")
        return
    
    test_process()

if __name__ == "__main__":
    main()
    pass