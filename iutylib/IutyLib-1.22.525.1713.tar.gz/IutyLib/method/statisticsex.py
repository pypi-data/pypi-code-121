

def getAvg(array_data):
    rtn = 0.0
    for i in range(len(array_data)):
        rtn = i/(i+1)*rtn + 1/(i+1)*array_data[i]
    return rtn

def getStd(array_data):
    std = 0.0
    avg = 0.0
    for i in range(len(array_data)):
        
        std = i/(i+1)*std + i/(i+1)**2 * (array_data[i]-avg) **2
        avg = i/(i+1)*avg + 1/(i+1)*array_data[i]
    return std ** 0.5
    
if __name__ == "__main__":
    from statistics import mean,pstdev,stdev
    data = [3.2,2.5,1.4,3.9,5.5]
    avg = getAvg(data)
    std = getStd(data)
    
    mean = mean(data)
    stdev = pstdev(data)
    
    print("avg:{}---std:{}".format(avg,std))
    print("mean:{}---stdev:{}".format(mean,stdev))