from IutyLib.stock.files import QualifyFile, HourFile,QuarterFile, DailyFile, WeeklyFile, CqcxDailyFile,StackFile

'''
Qualify Method
'''
def getIndexOfSerial(Serial,date):
    for data in Serial:
        if data[0] == date:
            return Serial.index(data)
    return -1

def SMA(Pre,Cur,N,M):
#N:Cycle Count
#M:Right Value
    if (M>N):
        return None
    
    v = ((N-M)*Pre + M * Cur)/N
    return v

def EMA(Pre,Cur,N):
    v = (Cur*2 + Pre*(N-1))/(N+1)
    return v

def REF(serial,base,interval):
    index = serial.index(base)
    if index < interval:
        return None
    return serial[index-interval]

def MUL(serial,index):
    default = None
    if index < 4:
        return default
    for i in range(index-4,0,-1):
        if serial[i][6]/serial[i-1][6] > 2.0:
            lev = serial[i-1][4]
            v = 3*(serial[i][4] - lev)/4
            if serial[i][4]<lev:
                return default
            if serial[i+1][4] < lev+v:
                return default
            if serial[i+2][4] < lev+v:
                return default
            if serial[i+3][4] < lev+v:
                return default
            return i
    return default

def WAV(serial,index):
    default = None
    if index < 20:
        return default
    vl2 = VLV(serial,index,5,3)
    if vl2[0] == index:
        return default
    b2 = serial[vl2[0]][4]
    
    vh1 = VHV(serial,vl2[0],5,3)
    if vh1[0] == vl2[0]:
        return default
    a1 = serial[vh1[0]][4]
    
    vl1 = VLV(serial,vh1[0],5,3)
    if vl1[0] == vh1[0]:
        return default
    b1 = serial[vl1[0]][4]
    
    return[(vl1[0],b1),(vh1[0],a1),(vl2[0],b2)]

def TSH(serial,index,threshold):
    h = serial[index][4]
    l = serial[index][4]
    c = serial[index][4]
    delta = 1
    for i in range(index,-1,-1):
        h = max(h,serial[i][2])
        l = min(h,serial[i][3])
        deltah = h - c
        deltal = c - l
        if deltal != 0:
            delta = deltah/deltal
        if (delta > (1 + threshold)) | (delta < (1 - threshold)):
            break
    return (index,delta)

def AMVL(mvl_data,date,lastclose = None,bound = 1.045):
    if len(mvl_data) == 0:
        return []
    m_index = 0
    for data in mvl_data:
        if data[0] > date:
            m_index = mvl_data.index(data)-1
            break
        m_index = len(mvl_data) -1
    serial = mvl_data[:m_index]
    vols = sorted(serial, key = lambda serial:serial[2])
    
    rtn = [mvl_data[m_index]]

def SMVL(mvl_data,date,lastclose = None,bound = 1.045):
    
    if len(mvl_data) == 0:
        return []
    m_index = 0
    for data in mvl_data:
        if data[0] > date:
            m_index = mvl_data.index(data)-1
            break
        m_index = len(mvl_data) -1
    if m_index == 0:
        return []
    
    rtn = [mvl_data[m_index]]
    for i in range(m_index-1,0,-1):
        insert_index = len(rtn)
        b_insert = True
        for data in rtn:
            if data[1] > mvl_data[i][1]:
                if mvl_data[i][1] > data[1]/bound:
                    b_insert = False
                    break
            if data[1] < mvl_data[i][1]:
                if mvl_data[i][1] < data[1]*bound:
                    b_insert = False
                    break
            if data[1] == mvl_data[i][1]:
                b_insert = False
                break
            if data[1] > mvl_data[i][1]:
                if insert_index == len(rtn):
                    insert_index = rtn.index(data)
                    continue
                if data[1] < rtn[insert_index][1]:
                    insert_index = rtn.index(data)
        if b_insert:
            rtn.insert(insert_index,mvl_data[i])
    if not lastclose is None:
        tul = []
        for i in range(1,len(rtn)):
            if rtn[i][1] > lastclose:
                tul.append(rtn[i-1])
                tul.append(rtn[i])
                break
        return tul
    return rtn
    

def LK(serial,index,item):
    default = None
    if index < 20:
        return default
    if len(serial) < index:
        return default
    k = -10000
    for i in range(index-1,0,-1):
        k1 = (serial[index][item] - serial[i][item])/(index-i)
        
        if k1 > k:
            k = k1
            continue
        if k1 <= k:
            #print('k={0},k1={1}'.format(k,k1))
            return (i+1,k)
    return default
    
def HK(serial,index,item):
    default = None
    if index < 20:
        return default
    if len(serial) < index:
        return default
    k = 10000
    for i in range(index-1,0,-1):
        k1 = (serial[index][item] - serial[i][item])/(index-i)
        
        if k1 < k:
            k = k1
            continue
        if k1 >= k:
            #print('k={0},k1={1}'.format(k,k1))
            
            return (i,k)
    return default

def VHV(serial,index,item,length = 7):
    default = (index,serial[index][item])
    source = []
    for i in range(index,0,-1):
        source.append(serial[i][item])
        if len(source) < length:
            continue
        i_rtn = length//2
        if source[i_rtn] == max(source):
            return (i+i_rtn,serial[i+i_rtn][item])
        source.pop(0)
    return default

def VLV(serial,index,item,length = 7):
    default = (index,serial[index][item])
    source = []
    for i in range(index,0,-1):
        source.append(serial[i][item])
        if len(source) < length:
            continue
        i_rtn = length//2
        if source[i_rtn] == min(source):
            return (i+i_rtn,serial[i+i_rtn][item])
        source.pop(0)
    return default

def LH(serial,index,item):
    default = (index,serial[index][item])
    for i in range(index-1,0,-1):
        if (serial[i][item] > serial[i-1][item]) & (serial[i][item] > serial[i+1][item]):
            #if serial[i][item] > serial[index][item]:
            return (i,serial[i][item])
            #else:
            #    return default
    return default

def LL(serial,index,item):
    default = (index,serial[index][item])
    for i in range(index-1,0,-1):
        if (serial[i][item] < serial[i-1][item]) & (serial[i][item] < serial[i+1][item]):
            #if serial[i][item] > serial[index][item]:
            return (i,serial[i][item])
            #else:
            #    return default
    return default

def VL(serial,index,item):
    default = (index,serial[index][item])
    ll1 = LL(serial,index,item)
    if (ll1[0] == index):
        
        return default
    m_index = ll1[0]-1
    while 1:
        ll2 = LL(serial,m_index,item)
        
        if ll2[0] == m_index:
            
            return default
        if ll2[1] > ll1[1]:
            return ll1
        
        ll1 = ll2
        m_index = ll1[0] - 1
    return default
    
def VH(serial,index,item):
    default = (index,serial[index][item])
    
    lh1 = LH(serial,index,item)
    if (lh1[0] == index):
        return default
    m_index = lh1[0]-1
    while 1:
        lh2 = LH(serial,m_index,item)
        if lh2[0] == m_index:
            return default
        if lh2[1] > lh1[1]:
            return lh1
        lh1 = lh2
        m_index = lh1[0] - 1
    return default

def VLs(serial,index,item,level = 1):
    default = []
    m_index = index
    source = serial
    for i in range(level):
        target = []
        while 1:
            ll = LL(source,m_index,item)
            if ll[0] == m_index:
                break
            if ll[1][item] > source[m_index][item]:
                target.insert(0,source[ll[0]])
            m_index =  ll[0]
        
        if len(target) > 0:
            #print('s:{0}----t:{1}'.format(len(source),len(target)))
            source = target
            continue
        else:
            return default
    return target

def VHs(serial,index,item,level = 1):
    default = []
    m_index = index
    source = serial
    for i in range(level):
        target = []
        while 1:
            lh = LH(source,m_index,item)
            #print('{0}\t{1}'.format(m_index,ll[0]))
            if lh[0] == m_index:
                
                break
            if lh[1][item] < source[m_index][item]:
                target.insert(0,source[lh[0]])
            m_index =  lh[0]
        if len(target) > 0:
            #print('s:{0}----t:{1}'.format(len(source),len(target)))
            
            source = target
            continue
        else:
            return default
    return target

def TUL(serial,index,itemh,iteml):
    m_index = index-1
    m_max = serial[index][itemh]
    m_min = serial[index][iteml]
    default = (m_min,m_max,m_index)
    while 1:
        vlv = VLV(serial,m_index,iteml)
        vhv = VHV(serial,m_index,itemh)
        if vlv[0] == m_index:
            return default
        if vhv[0] == m_index:
            return default
        
        if vlv[0] > vhv[0]:
            if vlv[1] < m_max * 0.8:
                return default
            else:
                m_min = min(vlv[1],m_min)
                m_index = vlv[0]
                default = (m_min,m_max,m_index)
        else:
            if vhv[1] > m_min * 1.2:
                return default
            else:
                m_max = max(vhv[1],m_max)
                m_index = vhv[0]
                default = (m_min,m_max,m_index)
    pass


def VDC(serial,index,interval):
    default = None
    if index < interval:
        return default
    vol = 0
    stack = 0.0
    for i in range(index-interval,index+1):
        vol += serial[i][5]
        stack += serial[i][6]
    return (index,stack/vol)

def LTH(serial,index):
    default = None
    for i in range(index-1,0,-1):
        if serial[i][4] > serial[i+1][4]:
            if serial[i][4] >= serial[i-1][4]:
                return serial[i]
    return default

def CMA(serial,index,level=100):
    rtn = 0
    sum_acc = 0.0
    sum_vol = 0
    sum_turn = 0.0
    for i in range(index-1,0,-1):
        sum_turn += float(serial[i][7])
        sum_vol += float(serial[i][6])
        sum_acc += float(serial[i][5])
        if sum_turn > level:
            rtn = sum_acc/sum_vol
            break
    return rtn

def CMI(serial,index,level=100):
    rtn = 0
    sum_acc = 0.0
    sum_vol = 0
    sum_turn = 0.0
    for i in range(index-1,0,-1):
        sum_turn += float(serial[i][7])
        sum_vol += float(serial[i][6])
        sum_acc += float(serial[i][5])
        if sum_turn > level:
            rtn = index-i
            break
    return rtn

def HHV(serial,index,period):
    rtn = serial[indx][2]
    for i in range(index-1,index-period-1,-1):
        if rtn < serial[i][2]:
            rtn = serial[i][2]
    return rtn

def LLV(serial,index,period):
    rtn = serial[indx][3]
    for i in range(index-1,index-period-1,-1):
        if rtn < serial[i][3]:
            rtn = serial[i][3]
    return rtn

class Qualification:
    from abc  import abstractmethod
    def __init__(self,code,type,cqcx = False):
        self.qfile = QualifyFile(code,type,cqcx)
        if cqcx:
            self.dfile = CqcxDailyFile(code)
        else:
            self.dfile = DailyFile(code)
        self.q_data = self.qfile.getData()
        self.d_data = self.dfile.getData()
        
        self.type = type
        self.code = code
        
    def getNextIndex(self):
        if self.q_data == []:
            return 0
        for i in range(0,len(self.d_data)):
            if self.q_data[-1][0] < self.d_data[i][0]:
                return i
        return -1
    
    def calcAppends(self):
        last = self.getNextIndex()
        
        if last == -1:
            return None
        d_data = self.d_data
        self.appends = []
        for i in range(last,len(d_data)):
            
            filter = False
            append = self.calcValue(i)
            self.q_data.append(append)
            for appenditem in append:
                if type(appenditem) == type(None):
                    filter = True
                    continue
            if filter:
                continue
            
            self.appends.append(append)
            
        return self.appends
    
    def writeAppends(self):
        appends = self.calcAppends()
        if appends == None:
            return
        if len(appends) == 0:
            return

        self.qfile.appendData(appends)
        #for append in appends:
            #self.q_data.append(append)
        pass
    
    @abstractmethod
    def calcValue(self,input_index,d_data = None,q_data = None):
        '''计算技术值'''
        pass
    
    def getCurrent(self,cur,mid=False):
        default = None
        if len(self.d_data) == 0:
            return default
        if len(self.q_data) == 0:
            return default
        
        d_data = self.d_data
        q_data = self.q_data
        index = (len(self.d_data)-1)
        if mid:
            for d in self.d_data:
                if d[0] == cur[0]:
                    index = (self.d_data.index(d))
                    d_data = self.d_data[:index]
                    break
            for q in self.q_data:
                if q[0] == cur[0]:
                    q_data = self.q_data[:self.q_data.index(q)]
                    break
        d_data.append(cur)
        rtn = self.calcValue(index,d_data,q_data)
        return rtn
    
    def getValues(self):
        self.q_data = self.qfile.getData()
        return self.q_data
    
    def getValue(self,date):
        for v in self.getValues():
            if v[0] == date:
                return v
        pass

class RNG(Qualification):
    def __init__(self,code,cycle='D'):
        Qualification.__init__(self,code,'Rng'+'_'+cycle,cqcx=False)
        self.cycle = cycle
        if cycle == 'W':
            self.dfile = WeeklyFile(code,cqcx=False)
            self.d_data = self.dfile.getData()
        kdjfile = KDJ(code,cycle)
        self.kdjdata = kdjfile.getValues()
        pass

    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        d_date = d_data[index][0]
        d_close = d_data[index][4]
        value = [d_date,d_close]
        kdjindex = getIndexOfSerial(self.kdjdata,d_date)
        if kdjindex == -1:
            return (None,)
        rl0 = None
        rh0 = None
        rl1 = None
        rh1 = None
        findl = True
        findkdjindex0 = kdjindex
        if self.kdjdata[kdjindex][2] < self.kdjdata[kdjindex][3]:
            findl = False
        for i in range(40):
            if findl:
                findkdjindex1 = VLV(self.kdjdata,findkdjindex0,4,3)[0]
            else:
                findkdjindex1 = VHV(self.kdjdata,findkdjindex0,4,3)[0]
            if findkdjindex0 == findkdjindex1:
                return (None,)
            findkdjindex0 = findkdjindex1
            findkdj = self.kdjdata[findkdjindex0]
            finddaily = self.d_data[getIndexOfSerial(self.d_data,findkdj[0])]
            #print(finddaily)
            
            if findl:
                if findkdj[2]>findkdj[3]:
                    continue
                findl = False
                if(d_close > finddaily[4]):#(d_close / 1.05 < finddaily[4]) & 
                    if (rl0 == None):
                        rl0 = finddaily[4]
                    elif (rl1 == None):
                        rl1 = finddaily[4]
            else:
                if findkdj[2]<findkdj[3]:
                    continue
                findl = True
                if(d_close < finddaily[4]):# (d_close * 1.05 > finddaily[4]) & 
                    if (rh0 == None):
                        rh0 = finddaily[4]
                    elif (rh1 == None):
                        rh1 = finddaily[4]
            if (not (rh1 == None)) & (not (rl1 == None)):
                break
        
        if (rh1 == None) | (rl1 == None):
            return (None,)
        
        value.append(rl0)
        value.append(rh0)
        value.append(rl1)
        value.append(rh1)
        
        return tuple(value)    

class DTMA(Qualification):
    def __init__(self,code,cycle='D'):
        Qualification.__init__(self,code,'dmt'+'_'+cycle,cqcx=False)
        self.cycle = cycle
        if cycle == 'W':
            self.dfile = WeeklyFile(code,cqcx=False)
            self.d_data = self.dfile.getData()
        mafile = MA(code,cycle)
        self.madata = mafile.getValues()
        pass

    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        d_date = d_data[index][0]
        d_close = d_data[index][4]
        value = [d_date,d_close]
        maindex = getIndexOfSerial(self.madata,d_date)
        if maindex == -1:
            return (None,)
        ma = self.madata[maindex]
        r1 = 1/(1/5)*((1/5*ma[1]))
        r2 = 1/(1/5+1/10)*((1/5*ma[1])+(1/10*ma[2]))
        r3 = 1/(1/5+1/10+1/30)*((1/5*ma[1])+(1/10*ma[2])+(1/30*ma[3]))
        r4 = 1/(1/5+1/10+1/30+1/60)*((1/5*ma[1])+(1/10*ma[2])+(1/30*ma[3])+(1/60*ma[4]))
        
        value.append(r1)
        value.append(r2)
        value.append(r3)
        value.append(r4)
        
        return tuple(value)    

class BLC(Qualification):
    
    def __init__(self,code,cycle='D'):
        Qualification.__init__(self,code,'Blc'+'_'+cycle,cqcx=False)
        self.cycle = cycle
        if cycle == 'W':
            self.dfile = WeeklyFile(code,cqcx=False)
            self.d_data = self.dfile.getData()

    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        value = [d_data[index][0],]
        v0 = VLV(d_data,index,5,3)
        if v0[0] == index:
            return (None,)
        v1 = VLV(d_data,v0[0],5,3)
        if v1[0] == v0[0]:
            return (None,)
        value.append(d_data[v1[0]][4])
        mi = min([l for d,o,h,l,c,a,v in d_data[v1[0]:v0[0]+1]])
        ma = max([h for d,o,h,l,c,a,v in d_data[v1[0]:v0[0]+1]])
        value.append(ma)
        value.append(mi)
        value.append(d_data[v0[0]][4])
        vol = 0
        amount = 0.0
        for dta in d_data[v1[0]:v0[0]+1]:
            vol += dta[6]
            amount += dta[5]
        value.append(amount)
        value.append(vol)
        #print(value)
        value.append(v0[0])

        return tuple(value)    

class DLT(Qualification):
    
    def __init__(self,code,cycle='D'):
        Qualification.__init__(self,code,'Dlt'+'_'+cycle,cqcx=False)
        self.cycle = cycle
        if cycle == 'W':
            self.dfile = WeeklyFile(code,cqcx=False)
            self.d_data = self.dfile.getData()

    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        level = [5,10,30,60]
        value = [d_data[index][0],]
        for li in range(0,len(level)):
            if 2*level[li] <= index:
                v = 0.0
                for ii in range(0,level[li]):
                    v +=(d_data[index-ii][4] - d_data[index-ii-level[li]][4])/level[li]
                av = v/level[li]
                value.append(av)
            else:
                value.append(None)
        return tuple(value)

class MA(Qualification):
    
    def __init__(self,code,cycle='D'):
        Qualification.__init__(self,code,'Ma'+'_'+cycle,cqcx=False)
        self.cycle = cycle
        if cycle == 'W':
            self.dfile = WeeklyFile(code,cqcx=False)
            self.d_data = self.dfile.getData()

    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        level = [5,18,30,60]
        value = [d_data[index][0],]
        for li in range(0,len(level)):
            if level[li] <= index:
                sum = 0.0
                for i in range(index-level[li]+1,index+1):
                    sum = sum + d_data[i][4]
                value.append(round((sum/level[li]),2))
            else:
                value.append(None)
        return tuple(value)

class STMA(Qualification):
    def __init__(self,code,cycle='D'):
        Qualification.__init__(self,code,'STMa',cqcx=False)
        self.cycle = cycle
        self.dfile = StackFile(code)
        self.d_data = self.dfile.getData()
    
    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        level = [5,18,30,60]
        value = [d_data[index][0],]
        for li in range(0,len(level)):
            if level[li] <= index:
                sum = 0.0
                for i in range(index-level[li]+1,index+1):
                    sum = sum + d_data[i][1]
                value.append(round((sum/level[li]),2))
            else:
                value.append(None)
        return tuple(value)

    
class KDJ(Qualification):
    
    def __init__(self,code,cycle = 'D',cqcx = False):
        Qualification.__init__(self,code,'KDJ'+'_'+cycle,cqcx)
        self.cycle = cycle
        if cycle == 'W':
            self.dfile = WeeklyFile(code,cqcx)
            self.d_data = self.dfile.getData()
        if cycle == 'H':
            self.dfile = HourFile(code)
            self.d_data = self.dfile.getData()
        if cycle == 'Q':
            self.dfile = QuarterFile(code)
            self.d_data = self.dfile.getData()

        
    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        if self.cycle == 'W':
            temp_d = []
            temp_d.append(d_data[index])
            for i in range(index-1,-1,-1):
                if d_data[0][0].strftime('%W') != d_data[i][0].strftime('%W'):
                    temp_d.insert(0,d_data[i])
                    if len(temp_d) > 81:
                        break
        else:
            temp_d = []
            for i in range(index,-1,-1):
                temp_d.insert(0,d_data[i])
                if len(temp_d)>81:
                    break
        #q_data = q_data + self.appends
        if len(temp_d) < 81:
            return (d_data[-1][0],None,None,None,None)

        hhv = temp_d[-1][2]
        llv = temp_d[-1][3]
        for i in range(len(temp_d)-81,len(temp_d)):
            if temp_d[i][2]>hhv:
                hhv = temp_d[i][2]
            if temp_d[i][3]<llv:
                llv = temp_d[i][3]
        
        if hhv == llv:
            return (d_data[-1][0],None,None,None,None)
        
        rsv = 100.0*(d_data[-1][4]-llv)/(hhv-llv)

        pre_k = 0
        pre_d = 0
        if self.cycle == 'W':
            for i in range(len(q_data)-1,-1,-1):
                if q_data[i][0].strftime('%W') != d_data[-1][0].strftime('%W'):
                    pre_k = q_data[i][2]
                    pre_d = q_data[i][3]
                    break
            
        elif self.cycle == 'M':
            for i in range(len(q_data)-1,-1,-1):
                if q_data[i][0].strftime('%M') != d_data[-1][0].strftime('%M'):
                    pre_k = q_data[i][2]
                    pre_d = q_data[i][3]
                    break
        else:
            if len(q_data) > 0:
                pre_rsv = q_data[-1][1]
                pre_k = q_data[-1][2]
                pre_d = q_data[-1][3]
        
        k = SMA(pre_k,rsv,18,1)
        
        d = SMA(pre_d,k,18,1)
        j = 3*k-2*d
        #print((d_data[-1][0],rsv,k,d,j))
        return (d_data[-1][0],rsv,k,d,j)

class MACD(Qualification):
    
    def __init__(self,code,cycle = 'D',cqcx = False):
        Qualification.__init__(self,code,'MACD'+'_'+cycle,cqcx)
        self.cycle = cycle
        if cycle == 'W':
            self.dfile = WeeklyFile(code,cqcx)
            self.d_data = self.dfile.getData()

        
    def calcValue(self,index,d_data=None,q_data=None):
        #q_data = self.q_data + self.appends
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        c = d_data[index][4]

        pre_ema12 = 0
        pre_ema26 = 0
        pre_dea = 0
        if self.cycle == 'W':
            for i in range(len(q_data)-1,-1,-1):
                if q_data[i][0].strftime('%W') != d_data[index][0].strftime('%W'):
                    pre_ema12 = q_data[i][1]
                    pre_ema26 = q_data[i][2]
                    pre_dif = q_data[i][3]
                    break
            
        elif self.cycle == 'M':
            for i in range(len(q_data)-1,-1,-1):
                if q_data[i][0].strftime('%M') != d_data[index][0].strftime('%M'):
                    pre_ema12 = q_data[i][1]
                    pre_ema26 = q_data[i][2]
                    pre_dea = q_data[i][4]
                    break
        else:
            if len(q_data) > 1:
                pre_ema12 = q_data[-1][1]
                pre_ema26 = q_data[-1][2]
                pre_dif = q_data[-1][3]
                pre_dea = q_data[-1][4]
        ema12 = EMA(pre_ema12,c,12)
        ema26 = EMA(pre_ema26,c,26)
        dif = ema12 - ema26
        #print(pre_dea)
        dea = EMA(pre_dea,dif,9)
        
        macd = (dif-dea)*2.0
        #print((d_data[-1][0],rsv,k,d,j))
        return (d_data[index][0],ema12,ema26,dif,dea,macd)
    
class LVL(Qualification):
    def __init__(self,code,cqcx = False):
        Qualification.__init__(self,code,'LVL',cqcx)
        
    def calcValue(self,index,d_data=None,q_data=None):
        if d_data == None:
            d_data = self.d_data
        if q_data == None:
            q_data = self.q_data
        if index < 10:
            return (d_data[index][0],None,None,None)
            
        kt1 = self.getKValue(index)
        if kt1 != None:
            kt2 = self.getKValue(kt1[3])
            if kt2 != None:
                kv = self.checkKValue(kt2,index)
                if kv != None:
                    #data
                    return (d_data[index][0],kv,index-kt2[3],kt2[1])
        return (d_data[index][0],None,None,None)
        
    def getKValue(self,index):
        k = 0
        rtn = None
        for ix in range(index-1,-1,-1):
            k1 = (self.d_data[index][3]-self.d_data[ix][3])/(index-ix)/self.d_data[ix][3]
            if(k1>=k):
                k = k1
                rtn = (index,k,self.d_data[index][3],ix,self.d_data[ix][3])
        return rtn
        
    def checkKValue(self,kv,index):
        if(len(kv)==0):
            return None
        return (kv[1] * kv[4] * (index-kv[3])+kv[4])
        
        
class HVH(Qualification):
    def __init__(self,code,cqcx = False):
        Qualification.__init__(self,code,'HVH',cqcx)
    
    def calcValue(self,index):
        if index < 10:
            return (self.d_data[index][0],None,None,None)
            
        kt1 = self.getKValue(index)
        if kt1 != None:
            kt2 = self.getKValue(kt1[3])
            if kt2 != None:
                kv = self.checkKValue(kt2,index)
                if kv != None:
                    return (self.d_data[index][0],kv,index-kt2[3],kt2[1])
        return (self.d_data[index][0],None,None,None)
        
    def getKValue(self,index):
        k = 0
        rtn = None
        for ix in range(index-1,-1,-1):
            k1 = (self.d_data[index][2]-self.d_data[ix][2])/(index-ix)/self.d_data[ix][2]
            if(k1<=k):
                k = k1
                rtn = (index,k,self.d_data[index][2],ix,self.d_data[ix][2])
        return rtn
    
    def checkKValue(self,kv,index):
        if(len(kv)==0):
            return None
        return (kv[1] * kv[4] * (index-kv[3])+kv[4])

class MVL(Qualification):
    def __init__(self,code,cqcx = False):
        Qualification.__init__(self,code,'MVL',cqcx)
    
    def calcValue(self,index):
        default = (self.d_data[index][0],None,None)
        if index < 1:
            return default
        if index > len(self.d_data)-4:
            return default
        if self.d_data[index][5] > self.d_data[index-1][5]*1.2:
            #if ((self.d_data[index][4] > self.d_data[index-1][4]) & (self.d_data[index+1][4] > self.d_data[index-1][4]) & (self.d_data[index+2][4] > self.d_data[index-1][4]) & (self.d_data[index+3][4] > self.d_data[index-1][4])):
            return (self.d_data[index][0],self.d_data[index-1][4],self.d_data[index][4],self.d_data[index][5])
            #return default
        else:
            return default
        