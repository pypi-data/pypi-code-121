import numpy as np
import scipy.stats as st

def to_likelihood(z):
    """convert z_score to likelyhood"""
    try:
        return [to_likelihood(x) for x in z]
    except TypeError:
        return 2*(1-st.norm.cdf(z))

def from_likelihood(p):
    """convert likelyhood to z_score"""
    try:
        return [from_likelihood(x) for x in p]
    except TypeError:
        return st.norm.ppf(1-p/2)


def is_same(a, b):
    """how likely is it that both statistics objects describe the same distribution? Assumes Gaussian distribution and returns the z_score. Use to_likelihood"""
    try:
        ma=a["mean"]
        mb=b["mean"]
        sa=a["std"]
        sb=b["std"]
        na=a["n"]
        nb=b["n"]
    except:
        raise KeyError("a and b must have keys 'mean', 'std', 'n'")

    sa/=np.sqrt(na)
    sb/=np.sqrt(nb)
    s=np.sqrt(sa**2+sb**2)
    if s==0:raise ValueError("std is zero")
    delta=np.abs(ma-mb)
    return delta/s

def similarity_matrix(stats):
    """return a matrix of likelihoods"""
    n=len(stats)
    matrix=np.zeros((n,n))
    
    for i in range(n):
        matrix[i,i]=1
        for j in range(i+1,n):
            matrix[j,i]=matrix[i,j]=is_same(stats[i],stats[j])

    return matrix

if __name__=="__main__":
    print(to_likelihood(0.0))
    print(to_likelihood(1.0))
    print(to_likelihood(2.0))
    print(to_likelihood(3.0))
    print(from_likelihood(to_likelihood(1.234)))










