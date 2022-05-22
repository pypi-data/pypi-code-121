import json
import numpy as np


from .methods import sign_test

from ..const import significance

class Stats(object):
    def __init__(self,q):
        self.q = q

    def __str__(self):
        if len(self.q)==0:
            return "No data"
        elif len(self.q)==1:
            return str(self.q[0])
        else:
            return f"{np.mean(self.q)} +- {np.std(self.q)} [{np.min(self.q)}, {np.max(self.q)}] * "+"{"+str(len(self.q))+"}"

    def __repr__(self):
        return str(self)

    def __float__(self):
        if len(self.q)==0:
            raise ValueError("No data")
        return np.mean(self.q)

    def __add__(self,other):
        assert isinstance(other,Stats)
        return Stats(self.q+other.q)

    def __eq__(self,other):
        assert isinstance(other,Stats)
        return sign_test(self.q,other.q)

    def __ne__(self,other):
        return 1-(self==other)

    def isnan(self):
        return np.any(np.isnan(self.q))

    def shortstr(self):
        return str(round(np.mean(self.q),4))

    def mediumstr(self):
        std=self.std()
        if std<0.0001:
            return str(round(self.mean(),4))
        return f"{self.mean():.4f}+-{self.std():.4f}"

    def to_list(self):
        return [float(x) for x in self.q]

    def mean(self):
        return np.mean(self.q)

    def std(self):
        return np.std(self.q)

    def __len__(self):
        return len(self.q)



if __name__=="__main__":
    q=Stats([1,2,3,4,5])
    print(q)


    exit()

def negative_infinity(n=10):
    return Stats([-2**30]*n)


def combine_stats(*args):
    assert len(args)>0
    assert all(isinstance(x,Stats) for x in args)

    ret=args[0]
    for x in args[1:]:
        ret=ret+x
    return ret

def average_stats(*args):
    """This is a simplistic averaging function. You could do better"""
    assert len(args)>0
    if len(args)==1:
        if type(args[0])==list:
            return average_stats(*args[0])
    assert all(isinstance(x,Stats) for x in args)

    ret=[]
    for x in args:
        ret.append(x.mean())
    return Stats(ret)

def maximum_stats(*args):
    """from a list of stats, which are the bests in them? (returns also a list, as in later versions we could implement statistical significance here. But currently only returns max(mean)"""

    assert len(args)>0
    if len(args)==1:
        if type(args[0])==list:
            return maximum_stats(*args[0])
    assert all(isinstance(x,Stats) for x in args)


    maxv=-2**30-1
    maxi=0
    for i,arg in enumerate(args):
        if arg.mean()>maxv:
            maxv=arg.mean()
            maxi=i
    maxo=args[maxi]
    return [arg for arg in args if len(maxo)==len(arg) and (maxo==arg)>significance]
    return [args[maxi]]



