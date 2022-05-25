
def getMA(serial,index,period,p=4):
    if period > index:
        return None
    if index >= len(serial):
        return None
    total = 0.0
    for i in range(index-period+1,index+1):
        total += serial[i][p]
    return total/period


def getHHI(serial,index,period=20,p=2):
    if period > index:
        return None
    if index >= len(serial):
        return None
    
    ri = index - period + 1
    for i in range(index-period+1,index+1):
        if serial[i][p] > serial[ri][p]:
            ri = i
    return ri

def getLLI(serial,index,period=20,p=3):
    if period > index:
        return None
    if index >= len(serial):
        return None
    
    ri = index - period + 1
    for i in range(index-period+1,index+1):
        if serial[i][p] < serial[ri][p]:
            ri = i
    return ri

def getSum(serial,index,period,p=4):
    if period > index:
        return None
    if index >= len(serial):
        return None
    total = 0.0
    for i in range(index-period+1,index+1):
        total += serial[i][p]
    return total

def getStd(serial,index,period = 20,p=4):
    ma = getMa(s,period,index,p)
    std2 = 0.0
    for i in range(index-period+1,index+1):
        
        std2 += (s[i][p]-ma) ** 2
    std = std2 ** 0.5
    return std/period

