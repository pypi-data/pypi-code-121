import random

def getValue(v):
    if isinstance(v,list):
        return v[random.randint(0,(lambda v:len(v)-1)(v))]
    else:
        return v