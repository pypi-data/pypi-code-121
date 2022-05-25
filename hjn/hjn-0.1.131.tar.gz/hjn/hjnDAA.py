import hashlib
import time
def DAA_example():
    t = time.time()
    para = "serviceNodeId=NMIC_MUSIC_CMADAAS&userId=&interfaceId=getSurfEleByTime&dataCode=SURF_CHN_WSET_FTM&elements=Cnty&times=20200826000000&dataFormat=csv"
    timeStep = "timestamp=%s000"%int(t)
    noncemd5 = hashlib.md5()
    noncemd5.update(timeStep.encode('utf-8'))
    nonce="nonce=%s"%(noncemd5.hexdigest().upper())
    pwd = "pwd="
    paraSK = "&".join([timeStep,nonce,pwd])
    allPara = para+"&"+paraSK
    list= allPara.split("&")
    list.sort()
    paramSort = "&".join(list)
    md5 = hashlib.md5()
    md5.update(paramSort.encode('utf-8'))
    sign ="sign="+md5.hexdigest().upper()
    prefix = "http://10.40.17.54/music-ws/api?"
    url = prefix + para + "&"+"&".join([timeStep,nonce,sign])
    print(url)

if __name__ == '__main__':
    DAA_example()


