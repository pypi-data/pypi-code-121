import numpy as np
from scipy.stats import norm
import os
from multiprocess import Pool
#from pathos.multiprocessing import ProcessingPool as Pool

from .estimators import *

def make_ci(self, confidence, hyp):
    
    one = norm.ppf(confidence/100)
    two = norm.ppf((confidence+(100-confidence)/2)/100)
    
    self.ci_one = np.sqrt(self.intKsq)*one
    self.ci_two = np.sqrt(self.intKsq)*two
    
    if hyp == 'twosided':
        self.ci = self.ci_two

    self.core_ci = self.ci*self.hat_q/np.sqrt(self.sample_size*self.band)
        
    self.data['_q_ci'] = np.nan
    self.data.loc[self.active_index,'_q_ci'] = self.core_ci

    self.data['_v_ci'] = np.nan
    self.data.loc[self.active_index,'_v_ci'] = self.A_4*self.core_ci
    
    self.data['_bs_ci'] = np.nan
    self.data.loc[self.active_index,'_bs_ci'] = self.a*self.A_3*self.A_4*self.core_ci
    
    self.data['_rev_ci'] = np.nan
    self.data.loc[self.active_index,'_rev_ci'] = self.M*self.a*self.A_3*self.A_4*self.core_ci
    
def make_cb(self, confidence, draws, hyp):

    def simulate_q(i): 
        np.random.seed(i)
        mc = np.sort(np.random.uniform(0, 1, self.sample_size))
        return q_smooth(mc, self.kernel, *self.band_options, reflect = True, is_sorted = True)

    p = Pool(os.cpu_count())
    hat_qs = np.array(p.map(simulate_q, range(draws)))
    p.close()
    p.join()
    
    sup = np.max((hat_qs-1)[:,self.trim:-self.trim], axis = 1)
    supabs = np.max(np.abs(hat_qs-1)[:,self.trim:-self.trim], axis = 1)

    self.cb_one = np.percentile(sup, confidence)
    self.cb_two = np.percentile(supabs, confidence+(100-confidence)/2)
        
    if hyp == 'twosided':
        self.cb = self.cb_two
        
    self.core_cb = self.cb*self.hat_q
        
    self.data['_q_cb'] = np.nan
    self.data.loc[self.active_index,'_q_cb'] = self.core_cb

    self.data['_v_cb'] = np.nan
    self.data.loc[self.active_index,'_v_cb'] = self.A_4*self.core_cb
    
    self.data['_bs_cb'] = np.nan
    self.data.loc[self.active_index,'_bs_cb'] = self.a*self.A_3*self.A_4*self.core_cb
    
    self.data['_rev_cb'] = np.nan
    self.data.loc[self.active_index,'_rev_cb'] = self.M*self.a*self.A_3*self.A_4*self.core_cb
    
def make_cicb_for_ts(self, confidence, draws, hyp):
    
    def simulate_ts(i): 
        np.random.seed(i)
        hat_F = np.sort(np.random.uniform(0, 1, self.sample_size))
        return total_surplus_from_Q(self.hat_q*hat_F, *self.part_options)
    
    p = Pool(os.cpu_count())
    hat_TSs = np.array(p.map(simulate_ts, range(draws)))
    p.close()
    p.join()
    
    right = total_surplus_from_Q(self.hat_q*self.u_grid, *self.part_options)
    
    sup_ts = np.max((hat_TSs-right)[:,self.trim:-self.trim], axis = 1)
    abs_ts = np.abs(hat_TSs-right)
    supabs_ts = np.max(abs_ts[:,self.trim:-self.trim], axis = 1)
    
    self.ci_two_ts = np.percentile(abs_ts, confidence+(100-confidence)/2, axis = 0)
    
    self.cb_one_ts = np.percentile(sup_ts, confidence)
    self.cb_two_ts = np.percentile(supabs_ts, confidence+(100-confidence)/2)
    
    if hyp == 'twosided':
        self.cb_ts = self.cb_two_ts
        self.ci_ts = self.ci_two_ts

    self.data['_ts_ci'] = np.nan
    self.data.loc[self.active_index,'_ts_ci'] = self.ci_ts
        
    self.data['_ts_cb'] = np.nan
    self.data.loc[self.active_index,'_ts_cb'] = self.cb_ts
    
