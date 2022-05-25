import numpy as np
import os
import datetime
import argparse
from hjn.mkNCHJN import LeftTopCornerPairArr
import time
from dateutil.relativedelta import relativedelta
import hashlib

def degMinSectoDeg(a):
    deg = int(a.split("°")[0])
    sec = int(a.split("'")[-1][:-1])
    min = int(a.replace(f"{deg}°","").replace(f"'{sec}\"",""))
    return deg+min/60+sec/3600

def normal(data, min=None, max=None):
    if max is None:
        max = np.max(data)
    if min is None:
        min = np.min(data)
    rangeLat = max-min
    dataB = (data - min) / rangeLat
    return dataB

def mkDir(path):
    if "." in path:
        os.makedirs(os.path.dirname(path),exist_ok=True)
    else:
        os.makedirs(path, exist_ok=True)

def options():
    parser = argparse.ArgumentParser(description='hjn')
    parser.add_argument('--times', type=str, default='2018060700,2018060700')
    parser.add_argument('--isDebug',action='store_true',default=False)
    config= parser.parse_args()
    config.times = config.times.split(",")
    if len(config.times) == 1:
        config.times = [config.times[0], config.times[0]]
    config.times = [datetime.datetime.strptime(config.times[0], "%Y%m%d%H%M"),
                    datetime.datetime.strptime(config.times[1], "%Y%m%d%H%M")]

    return config


def totalTimes(delta,second):
    return (delta.days*24*3600+delta.seconds)//second

def timeSeq(start,end,secInter,endPoint=True):
    times=totalTimes((end-start),secInter)
    end = 1 if endPoint else 0
    return list(map(lambda x:start+relativedelta(seconds=x*secInter),range(times+end)))

def normalNC(data):
    mx=np.nanmax(data)
    mn = np.nanmin(data)
    rangeV=mx-mn
    scale = rangeV/254
    offset = (mx+mn)/2
    data1=(data - offset)/scale
    data1[np.isnan(data1)] = -128
    return data1,scale,offset


def expend(data,latArr,lonArr,dim=2):
    latOffset = int((LeftTopCornerPairArr[0]["evn"].n - latArr[0]) / 0.01)
    latOffsetDown = int((latArr[-1] - LeftTopCornerPairArr[3]["evn"].s) / 0.01)
    lonOffset = int((lonArr[0] - LeftTopCornerPairArr[6]["evn"].w) / 0.01)
    lonOffsetRight = int((LeftTopCornerPairArr[0]["evn"].e - lonArr[-1]) / 0.01)
    appendLat = np.asarray(list(map(lambda x: latArr[0] + x * 0.01, range(1, latOffset + 2)))[::-1])
    appendLatDown = np.asarray(list(map(lambda x: latArr[-1] - x * 0.01, range(1, latOffsetDown + 2))))
    latArr = np.r_[appendLat, latArr]
    latArr = np.r_[latArr, appendLatDown]
    appendLon = np.asarray(list(map(lambda x: lonArr[0] - x * 0.01, range(1, lonOffset + 2)))[::-1])
    appendLonRight = np.asarray(list(map(lambda x: lonArr[-1] + x * 0.01, range(1, lonOffsetRight + 2))))
    lonArr = np.r_[appendLon, lonArr]
    lonArr = np.r_[lonArr, appendLonRight]

    if latOffset<0:
        latOffset=0
    if latOffsetDown < 0:
        latOffsetDown = 0
    if lonOffset < 0:
        lonOffset = 0
    if lonOffsetRight < 0:
        lonOffsetRight = 0

    if dim==2:
        data = np.pad(data, ((latOffset+1 , latOffsetDown+1 ), (lonOffset+1 , lonOffsetRight+1)),constant_values=np.nan)
    elif dim==3:
        data = np.pad(data, ((0, 0), (latOffset+1, latOffsetDown+1), (lonOffset+1, lonOffsetRight+1)), constant_values=np.nan)
    elif dim==4:
        data = np.pad(data, ((0, 0),(0, 0), (latOffset+1, latOffsetDown+1), (lonOffset+1, lonOffsetRight+1)), constant_values=np.nan)
    return data,latArr,lonArr

def UV2WSWD(U,V):
    ws = np.sqrt(np.square(U) + np.square(V))
    wd = (np.degrees(np.arctan2(-U, -V))+ 360)%360
    return ws,wd

def WSWD2UV(ws,wd):
    u=- ws*np.sin(np.radians(wd))
    v=- ws*np.cos(np.radians(wd))
    return u,v

def findAllIPV4(segment="10."):
    import psutil
    from socket import AddressFamily
    local_addrs = ""
    for name, info in psutil.net_if_addrs().items():
        for addr in info:
            if AddressFamily.AF_INET == addr.family:
                if segment in addr.address:
                    local_addrs = addr.address
    return local_addrs

def sendEmail(message,subject = "fail"):
    import requests
    IP = findAllIPV4()
    response = None
    try:
        response = requests.get("http://10.16.50.218:5004/sendmail?address=408037825@qq.com&subject=%s:%s&message=%s"%(subject,IP,message))
    except Exception as e:
        print(e)
    return response

def seconds2datetime(seconds):
    return datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds)), "%Y-%m-%d %H:%M:%S")

def datetime2seconds(UTC):
    return time.mktime(UTC.timetuple())

def readJulianDateTime(juliandata, hms):
    jd = juliandata + 2440587
    L = jd + 68569
    N = (4 * L) // 146097
    L = L - (146097 * N + 3) // 4
    I = 4000 * (L + 1) // 1461001
    L = L - (1461 * I) // 4 + 31
    J = 80 * L // 2447
    day = L - 2447 * J // 80
    L = int(J // 11)
    month = J + 2 - 12 * L
    year = 100 * (N - 49) + I + L
    seconds = hms // 1000
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds - (60 * h + m) * 60
    return datetime.datetime(year, month, day, h, m, s)

def RGB_to_Hex(tmp):
    rgb = tmp.split(',')  # 将RGB格式划分开来
    strs = '#'
    for i in rgb:
        num = int(i)  # 将str转int
        # 将R、G、B分别转化为16进制拼接转换并大写
        strs += str(hex(num))[-2:].replace('x', '0').upper()

    return strs

def genLatLon(evn,resolution):
    latArr = np.linspace(evn.n,evn.s,int(((evn.n-evn.s)/resolution+1)))
    lonArr = np.linspace(evn.w,evn.e,int(((evn.e-evn.w)/resolution+1)))
    return latArr,lonArr


def calSHA1(path):
    encrypt = hashlib.sha1()
    with open(path,"rb") as f:
        while True:
            b = f.read(128000)
            encrypt.update(b)
            if not b:
                break
    sha1Result = encrypt.hexdigest()
    return sha1Result

