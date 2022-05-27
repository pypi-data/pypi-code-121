from scipy.stats import median_abs_deviation
import numpy as np
import pandas

def estimate_typing(snidresult,  weight_by="rlap",
                    topn=30, rlap_range=[5,1000], 
                    grad="good", default=None):
    """ """
    
def estimate_redshift(snidresult, weight_by="rlap",
                              topn=30, typing=None, rlap_range=[5,1000], 
                              grad="good", default=[np.NaN, np.NaN]):
    """ """
    
    d = snidresult.copy()
    if topn is not None:
        d = d[d["no."].astype("int")<30]
    if typing is not None:
        d = d[d["type"].isin(np.atleast_1d(typing))]
    if rlap_range is not None:
        d = d[d["rlap"].between(*rlap_range)]
        
    if len(d) == 0:
        return default
    if len(d) == 1:
        return d["z"][0], np.NaN
    
    redshift = np.average(d["z"], weights=d[weight_by])
    dredshift = median_abs_deviation(d["z"])
    return redshift, dredshift
