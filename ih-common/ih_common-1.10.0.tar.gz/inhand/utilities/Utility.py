#coding=utf-8
import json

import time
from datetime import date,datetime,timedelta
# coding=utf-8
import re
import math
import socket


# 工具类
class Utility:
    @staticmethod
    def getTheDayFrom(theDay=None,days=0):
        tdelta = timedelta(days=days)
        current=theDay
        if current is None:
            current = date.today()
        theDay = current +tdelta
        #theTime = datetime.time(0,0,0)
        last = datetime(theDay.year,theDay.month,theDay.day,0,0,0)
        return last

    @staticmethod
    def getTheTimeFrom(theTime=None,days=0,hours=0,minutes=0,seconds=0,ms=0):
        tdelta = timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds,milliseconds=ms)
        current = theTime
        if current is None:
            current = datetime.now()
        theTime = current +tdelta
        return theTime

    @staticmethod
    def getEndTimeFromCurrentDay(theTime=None,hours=0,minutes=0,seconds=59):
        tdelta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        current = theTime
        if current is None:
            current = datetime.now()
        theTime = current + tdelta
        tdelta = timedelta(hours=hours, minutes=minutes, seconds=seconds+1)
        next = current+tdelta
        if current.day < theTime.day:
            theTime = datetime(current.year,current.month,current.day,23,59,59,0)
            next = Utility.getTheDayFrom(1)
        return (theTime,next)

    # 序列化
    @staticmethod
    def serialize_instance(obj):
        d = {'__classname__': obj.__class__.__name__}
        d.update(vars(obj))
        return d

    # 反序列化
    @staticmethod
    def unserialize_object(d, classes={}):
        clsname = d.pop('__classname__', None)
        if clsname:
            cls = classes[clsname]
            obj = cls()  # Make instance without calling __init__
            dict = d.items()
            for key in dict.keys():
                setattr(obj, key, dict[key])
            return obj
        else:
            return d


    @staticmethod
    def ieee754Int2Float(a, p):
        f = ((-1) ** ((a & 0x80000000) >> 31)) * (2 ** (((a & 0x7f800000) >> 23) - 127)) * (1 + (
                    (a & 0x7fffff) * 1.0 / (
                        2 ** 23)))  # (1 + (math.log((a & 0x7fffff),2)))#((-1)**((a & 0x80000000)>>31))*(2**(((a &0x7f800000)>>23)-127))*(1+((a&0x7fffff)/(2**23*1.0)))
        return round(f, p)

    # ieee754转换
    @staticmethod
    def Float2ieee754Words(f, byte_order):

        words = []
        if (f == 0):
            words.append(0)
            words.append(0)
            return words

        signedBit = 0 if f > 0 else 1

        stepBits = int(math.floor(math.log(abs(f), 2)))
        tailBits = int(((abs(f) / (2 ** stepBits)) - 1) * (2 ** 23)) if stepBits > 0 else int(
            (abs(f) / (2 ** stepBits)) * (2 ** 23))  # int(((f/(2**stepBits))-1) * (2**23))

        dw = ((signedBit << 31) & 0x80000000) | (((stepBits + 127) << 23) & 0x7f800000) | (tailBits & 0x7fffff)
        wh = (dw & 0xffff0000) >> 16
        wl = dw & 0xffff
        if re.search(r'(^cdab$)', byte_order) != None:
            words.append(wl)
            words.append(wh)
        elif re.search(r'(^abcd$)', byte_order) != None:
            words.append(wh)
            words.append(wl)
        elif re.search(r'(^badc$)', byte_order) != None:
            words.append(((wh & 0xff) << 8) | ((wh & 0xff00) >> 8))
            words.append(((wl & 0xff) << 8) | ((wl & 0xff00) >> 8))
        else:  # r'(^dcba$)'
            words.append(((wl & 0xff) << 8) | ((wl & 0xff00) >> 8))
            words.append(((wh & 0xff) << 8) | ((wh & 0xff00) >> 8))
        return words

    @staticmethod
    def ieee754Words2Float(wl, wh, p):
        a = wh << 16 | wl
        # f = ((-1) ** ((a & 0x80000000) >> 31)) * (2 ** (((a & 0x7f800000) >> 23) - 127)) * (1 + ((a & 0x7fffff) / (2 ** 23 * 1.0)))
        # f = ((-1) ** ((a & 0x80000000) >> 31)) * (2 ** (((a & 0x7f800000) >> 23) - 127)) * (1 + (math.log((a & 0x7fffff),2)))
        return Utility.ieee754Int2Float(a, p)

    # int -> words[2]
    @staticmethod
    def toWords(d, byte_order):
        wh = (abs(d) & 0xffff0000) >> 16
        wl = abs(d) & 0xffff
        words = []
        if d < 0:
            wh = wh | 0x8000
        if re.search(r'(^cdab$)', byte_order) != None:
            words.append(wl)
            words.append(wh)
        elif re.search(r'(^abcd$)', byte_order) != None:
            words.append(wh)
            words.append(wl)
        elif re.search(r'(^badc$)', byte_order) != None:
            words.append(((wh & 0xff) << 8) | ((wh & 0xff00) >> 8))
            words.append(((wl & 0xff) << 8) | ((wl & 0xff00) >> 8))
        else:  # r'(^dcba$)'
            words.append(((wl & 0xff) << 8) | ((wl & 0xff00) >> 8))
            words.append(((wh & 0xff) << 8) | ((wh & 0xff00) >> 8))
        return words

    # 		if re.search(r'(^dcba$)|(^cdba$)', byte_order) != None:
    # 			words.append(wh)
    # 			words.append(wl)
    # 		else:
    # 			words.append(wl)
    # 			words.append(wh)
    # 		return words

    # bytes[2] -> word
    @staticmethod
    def toWord(l, h, byte_order, vtype):
        if re.search(r'(^ba($|cd$))|(^dcba$)', byte_order) != None:
            if (re.search('^unsigned ', vtype)):
                t = (((l & 0x7f) << 8) & (((l & 0x8) << 8) & 0xff00) | h)
                return t
            else:
                t = ((l << 8) & 0xff00) | h
                return t
        else:
            if (re.search('^unsigned ', vtype)):
                t = (((h & 0x7f) << 8) & (((h & 0x8) << 8) & 0xff00) | l)
                return t
            else:
                t = ((h << 8) & 0xff00) | l
                return t

    # words[2] -> double words (int)
    @staticmethod
    def toDWord(l0, h0, l1, h1, byte_order, vtype):
        if re.search(r'^dcba$', byte_order) != None:
            if (re.search('^signed ', vtype)):
                s = (((l1 & 0x7f) << 24) & 0xff000000) | ((h1 << 16) & 0xff0000) | ((l0 << 8) & 0xff00) | (h0 & 0xff)
                t = s if (l1 & 0x80) == 0 else (0 - s)
            else:
                t = ((l1 & 0xff) << 24) | (h1 << 16) | (l0 << 8) | h0

        elif re.search(r'^cdab$', byte_order) != None:
            if (re.search('^signed ', vtype)):
                s = (((h1 & 0x7f) << 24) & 0xff000000) | ((l1 << 16) & 0xff0000) | ((h0 << 8) & 0xff00) | (l0 & 0xff)
                t = s if (h1 & 0x80) == 0 else (0 - s)
            else:
                t = ((h1 & 0xff) << 24) | (l1 << 16) | (h0 << 8) | l0

        elif re.search(r'^badc$', byte_order) != None:
            if (re.search('^signed ', vtype)):
                s = (((l0 & 0x7f) << 24) & 0xff000000) | ((h0 << 16) & 0xff0000) | ((l1 << 8) & 0xff00) | (h1 & 0xff)
                t = s if (l0 & 0x80) == 0 else (0 - s)
            else:
                t = ((l0 & 0xff) << 24) | (h0 << 16) | (l1 << 8) | h1

        else:
            if (re.search('^signed ', vtype)):
                s = (((h0 & 0x7f) << 24) & 0xff000000) | ((l0 << 16) & 0xff0000) | ((h1 << 8) & 0xff00) | (l1 & 0xff)
                t = s if (h0 & 0x80) == 0 else (0 - s)
            else:
                t = ((h0 & 0xff) << 24) | (l0 << 16) | (h1 << 8) | l1
        return t

    # ieee754 , byte[4] -> float
    @staticmethod
    def toFloat(l0, h0, l1, h1, byte_order, vtype):
        t = Utility.toDWord(l0, h0, l1, h1, byte_order, vtype)
        return Utility.ieee754Int2Float(t, 2)  # ieee754 converting, precision: default 2


    @staticmethod
    def getLocalIP(host='8.8.8.8',port=808):
        # h=socket.gethostname()
        # ip=socket.gethostbyname(h)
        # return ip
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((host, port))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip


#统计型变量类
class StatisticsVar:
    #id : 变量id
    #current： 当前统计值
    #value： 当前值，通过此值，经过计算，汇总到current
    #timestamp： 本次数据的时间戳
    #last： 上次统计的时间错
    def __init__(self,id=None,current=0,value=None,timestamp=0,last=0):
        self.id = id
        self.current = current
        self.value = value
        self.timestamp = int(timestamp/3600)*3600
        self.endTime = timestamp + 3600 #hourly
        self.last = last

    #json反序列化
    def unwrap(self,str):
        #u = Utilities.utilities()
        s = json.loads(str)
        self.current = s['current']
        self.value = s['value']
        self.timestamp = s['timestamp']
        self.endTime = s['endTime']
        if 'last' in s.keys():
            self.last = s['last']

    #序列化成json
    def wrap(self):
        return json.dumps(self,default=Utility.serialize_instance)

    #统计
    def calc(self,current,value,last):
        self.current = current
        self.count = self.cout +1
        self.last = last
        self.value = value
        #self.timestamp = timestamp

    #清零
    def reset(self,timestamp):
        self.value = 0
        self.timestamp = timestamp
        # 'current' and 'last' could not reset

if __name__ == '__main__':
    ts = int(time.time())
    sv = StatisticsVar()
    sv.current = 1
    sv.value = 232
    sv.timestamp = ts
    str = sv.wrap()
    print(str)
    sv1 = StatisticsVar()
    sv1.unwrap(str)
    print(sv1.value)
    sv.value = 128
    print(str)
    str = sv.wrap()
    print(str)
    sv1 = StatisticsVar()
    sv1.unwrap(str)
    print(sv1.value)
    value ='128'
    v = float("2.2")
    print(v)
    (wl, wh) = Utility.Float2ieee754Words(v, "abcd")
    dw = ((wh & 0xffff) << 16) | (wl & 0xffff)
    bhh = (wh & 0xff00) >> 8
    bhl = wh & 0x00ff
    blh = (wl & 0xff00) >> 8
    bll = wl & 0xff
    print("" + str(bhh) + "-" + str(bhl) + "-" + str(blh) + "-" + str(bll))
    f = Utility.ieee754Int2Float(dw, 2)
    print(str(f))
    s = Utility.ieee754Int2Float(0x42c88000, 3)
    print(str(s))
