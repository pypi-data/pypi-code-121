import sys


#sargs:源参数，一般是函数传参
#targs:目标参数，一般是缺省参数
def setArgs(sargs,targs):
    if type(sargs) == list:
        for i in range(len(sargs)):
            targs[str(i)] = sargs[i]
    
    if type(sargs) == dict:
        for k in sargs:
            targs[k] = sargs[k]
    pass

#命令行参数转传参
def parseArgs(cli = None):
    if not cli:
        cli = sys.argv
    args = []
    kwargs = {}

    key = None
    for arg in cli.split(' '):
        if key:
            kwargs[key] = arg
            key = None
            
        elif arg.startswith('-'):
            key = arg.split('-')[-1]
        
        else:
            args.append(arg)
    
    return args,kwargs

if __name__ == "__main__":
    from IutyLib.coding.asserts import *
    cli = "cliname command -p1 363 --ver 1.0.254"
    print("cli:"+cli)
    print("-"*10)
    args,kwargs = parseArgs(cli)

    print("parse res:")
    print("-"*10)
    for arg in args:
        print(arg)
    for k in kwargs:
        print("{}-{}".format(k,kwargs[k]))
    assertEqual(args[1], "command")
    
    print("set defaults:")
    print("-"*10)
    dkwargs = {"d1":"init","p1":"53505"}
    setArgs(args,dkwargs)
    setArgs(kwargs,dkwargs)

    for k in dkwargs:
        print("{}-{}".format(k,dkwargs[k]))