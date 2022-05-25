class MontecarloCore:
    def __init__(self):
        self._vl_ = []
        self.mt = 0
        self.at = 0
        pass
    
    def add(self,v,r=1):
        self.at += r
        if len(self._vl_) == 0:
            self._vl_.append(0.0)
        if self._vl_[0] > 50000:
            self._vl_.insert(0,0.0)
        self._vl_[0] += v
        pass
    
    def mul(self,v,r=1):
        self.mt += r
        if len(self._vl_) == 0:
            self._vl_.append(1.0)
        if self._vl_[0] > 50000 or self._vl_[0] < 0.0005:
            self._vl_.insert(0,1.0)
        self._vl_[0] *= v
        pass
    
    def getValue(self):
        if (self.at > 0) and (self.mt) == 0:
            rtn = 0.0
            for v in self._vl_:
                rtn += v/self.at
            return rtn
        if (self.mt) > 0 and (self.at) == 0:
            rtn = 1.0
            for v in self._vl_:
                rtn *= v**(1/self.mt)
            return rtn
        return 0.0
    
    pass
    
if __name__ == "__main__":
    import random
    mc = MontecarloCore()
    for i in range(10000000+1):
        x = random.random()
        y = random.random()
        r2=x**2+y**2
        if r2 > 1:
            mc.add(1)
        else:
            mc.add(4)
        
        if i == 100 or i == 1000 or i == 100000 or i == 1000000 or i == 10000000:
            print("step:{}, pi={}".format(i,mc.getValue()))
    pass