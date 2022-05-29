import numpy as np
from scipy.stats import norm
import os
from multiprocess import Pool
#from pathos.multiprocessing import ProcessingPool as Pool

from .estimators import *

def add_column(self, name, values):
    self.data[name] = np.nan
    self.data.loc[self.active_index,name] = values
    
def make_ci_asy(self, confidence, hyp):
    
    one = norm.ppf(confidence/100)
    two = norm.ppf((confidence+(100-confidence)/2)/100)
    
    self.ci_one = np.sqrt(self.intKsq)*one
    self.ci_two = np.sqrt(self.intKsq)*two
    
    if hyp == 'twosided':
        self.ci = self.ci_two
    if hyp == 'onesided':
        self.ci = self.ci_one

    self.core_ci = self.ci*self.hat_q/np.sqrt(self.sample_size*self.band)
        
    add_column(self, '_q_ci_asy', self.core_ci)
    add_column(self, '_v_ci_asy', self.A_4*self.core_ci)
    add_column(self, '_bs_ci_asy', self.a*self.A_3*self.A_4*self.core_ci)
    add_column(self, '_rev_ci_asy', self.M*self.a*self.A_3*self.A_4*self.core_ci)
    
def make_cicb(self, confidence, draws, hyp):

    def simulate_Q(i): 
        np.random.seed(i)
        mc = np.sort(np.random.uniform(0, 1, self.sample_size))
        return self.hat_q*(mc-self.u_grid)
    
    p = Pool(os.cpu_count())
    delta_Qs = np.array(p.map(simulate_Q, range(draws)))
    p.close()
    p.join()
    
    def simulate_q(i): 
        np.random.seed(i)
        mc = np.sort(np.random.uniform(0, 1, self.sample_size))
        mcq = q_smooth(mc, self.kernel, *self.band_options, reflect = True, is_sorted = True)
        return self.hat_q*(mcq-1)

    p = Pool(os.cpu_count())
    delta_qs = np.array(p.map(simulate_q, range(draws)))
    p.close()
    p.join()
        
    if hyp == 'twosided':
        def _sup(x):
            return np.max(np.abs(x)[:,self.trim:-self.trim], axis = 1)
        def _perc(x):
            return np.percentile(x, confidence+(100-confidence)/2, axis = 0)
    if hyp == 'onesided':
        def _sup(x):
            return np.max(x[:,self.trim:-self.trim], axis = 1)
        def _perc(x):
            return np.percentile(x, confidence, axis = 0)
        
    add_column(self, '_q_ci', _perc(delta_qs))
    add_column(self, '_q_cb', _perc(_sup(delta_qs)))
    
    delta_vs = delta_Qs + self.A_4*delta_qs
    
    del(delta_qs)
    
    add_column(self, '_v_ci', _perc(delta_vs))
    add_column(self, '_v_cb', _perc(_sup(delta_vs)))
    
    delta_bs = np.apply_along_axis(lambda x: bidder_surplus(x, *self.part_options), 1, delta_vs)
    
    add_column(self, '_bs_ci', _perc(delta_bs))
    add_column(self, '_bs_cb', _perc(_sup(delta_bs)))
    
    delta_ts = np.apply_along_axis(lambda x: total_surplus(x, *self.part_options), 1, delta_vs)
    delta_rev = delta_ts - self.M*delta_bs
    add_column(self, '_rev_ci', _perc(delta_rev))
    add_column(self, '_rev_cb', _perc(_sup(delta_rev)))
    
    del(delta_vs, delta_rev)

    delta_ts = np.apply_along_axis(lambda x: total_surplus_from_Q(x, *self.part_options), 1, delta_Qs)
    add_column(self, '_ts_ci', _perc(delta_ts))
    add_column(self, '_ts_cb', _perc(_sup(delta_ts)))
    
    del(delta_ts, delta_Qs)
            