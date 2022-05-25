import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sb
from scipy.stats import norm
import pkg_resources

from .kernels import *
from .estimators import *
from .plots import *
from .calibrate import *
from .inference import *

from multiprocess import Pool    
    
def cens_Q(Q, x, eps):
    return (Q(eps+x*(1-2*eps))-Q(eps))/(Q(1-eps)-Q(eps))

def cens_fQ(f, Q, x, eps):
    return f(Q(eps+x*(1-2*eps)))*(Q(1-eps)-Q(eps))/(1-2*eps)

def cens_q(f, Q, x, eps):
    return (1-2*eps)/(f(Q(eps+x*(1-2*eps)))*(Q(1-eps)-Q(eps)))

class Simulator:
    '''Addition to the package for the "Nonparametric inference on counterfactuals in sealed first-price auctions" paper.'''
    
    def __init__(self, sample_size, smoothing_rate, trim_percent, 
                 frec, rvpdf, rvppf, eps, reflect = True):
        
        self.u_grid = np.linspace(0, 1, sample_size)
        
        self.Q_fun = lambda x: cens_Q(rvppf, x, eps)
        self.fQ_fun = lambda x: cens_fQ(rvpdf, rvppf, x, eps)
        self.q_fun = lambda x: cens_q(rvpdf, rvppf, x, eps)
        
        self.sample_size = sample_size
        self.frec = frec
        
        self.smoothing = -smoothing_rate
        self.u_trim = trim_percent/100
        self.reflect = reflect
        
    def calibrate(self):
        
        self.mc = self.Q_fun(np.sort(np.random.uniform(0, 1, size = self.sample_size)))
        
        self.band_options = calibrate_band(self, self.mc, self.u_trim, self.smoothing)
        self.sample_size, self.band, self.i_band, self.trim = self.band_options
        
        self.kernel, _ = make_kernel(self.u_grid, self.i_band, kernel = tri)
        
        self.part_options = calibrate_part(self, self.u_grid, self.frec)
        self.M, self.A_1, self.A_2, self.A_3, self.A_4, self.a = self.part_options
        
    def make_true(self):
        
        self.true_Q = self.Q_fun(self.u_grid)
        self.true_fQ = self.fQ_fun(self.u_grid)
        self.true_q = self.q_fun(self.u_grid)
        
        self.true_v = self.true_Q + self.A_4*self.true_q        
        self.true_ts = total_surplus(self.true_v, *self.part_options)
        self.true_bs = bidder_surplus(self.true_v, *self.part_options)
        self.true_rev = self.true_ts - self.M*self.true_bs
        
        # this is the correct way
        self.true_ts = total_surplus_from_Q(self.true_Q, *self.part_options)
        
    def make_true_uni(self):
        
        self.true_Q_uni = self.u_grid
        self.true_fQ_uni = np.ones(self.sample_size)
        self.true_q_uni = np.ones(self.sample_size)
  
        # for smooth functionals
        self.true_Q_uni *= self.true_q
        # for non-smooth functionals
        self.true_q_uni *= self.true_q
        
        self.true_v_uni = self.true_Q_uni + self.A_4*self.true_q_uni
        self.true_ts_uni = total_surplus(self.true_v_uni, *self.part_options)
        self.true_bs_uni = bidder_surplus(self.true_v_uni, *self.part_options)
        self.true_rev_uni = self.true_ts_uni - self.M*self.true_bs_uni
        
        # this is the correct way
        self.true_ts_uni = total_surplus_from_Q(self.true_Q_uni, *self.part_options)
        
    def simulate_uni(self, draws = 1000, nominal_coverage = 95): 
        
        def simulate_one_uni(i, smooth_Q = False): 
            np.random.seed(i)
            mc = np.sort(np.random.uniform(0, 1, self.sample_size))
            hat_Q = mc
            hat_q = q_smooth(hat_Q, self.kernel, *self.band_options, is_sorted = True, reflect = self.reflect)
            
            if smooth_Q == True:
                hat_Q = np.cumsum(hat_q)/len(hat_q)
            
            # for smooth functionals
            hat_Q *= self.true_q
            # for non-smooth functionals
            hat_q *= self.true_q
            
            hat_v = hat_Q + self.A_4*hat_q
            hat_bs = bidder_surplus(hat_v, *self.part_options)
            hat_ts = total_surplus(hat_v, *self.part_options)
            hat_rev = hat_ts - self.M*hat_bs
            
            # this is the correct way
            hat_ts = total_surplus_from_Q(hat_Q, *self.part_options)
            
            left = [hat_q, hat_v, hat_bs, hat_rev, hat_ts]
            right = [self.true_q_uni, self.true_v_uni, self.true_bs_uni, self.true_rev_uni, self.true_ts_uni]
            
            return [np.max(np.abs(x-y)[self.trim:-self.trim]) for x,y in zip(left,right)]
            
        p = Pool(os.cpu_count())
        hats_uni = np.array(p.map(simulate_one_uni, range(draws)))
        p.close()
        p.join()
        
        self.crit_qs_uni = np.percentile(hats_uni, nominal_coverage, axis = 0)
        
    def simulate_dgp(self, draws = 1000, nominal_coverage = 95): 
        
        def simulate_one_dgp(i, smooth_Q = False): 
            np.random.seed(i)
            mc = np.sort(np.random.uniform(0, 1, self.sample_size))
            hat_Q = self.Q_fun(mc)
            hat_q = q_smooth(hat_Q, self.kernel, *self.band_options, is_sorted = True, reflect = self.reflect)
            
            if smooth_Q == True:
                hat_Q = np.cumsum(hat_q)/len(hat_q)
            
            hat_v = hat_Q + self.A_4*hat_q
            hat_bs = bidder_surplus(hat_v, *self.part_options)
            hat_ts = total_surplus(hat_v, *self.part_options)
            hat_rev = hat_ts - self.M*hat_bs
            
            # this is the correct way
            hat_ts = total_surplus_from_Q(hat_Q, *self.part_options)
            
            left = [hat_q, hat_v, hat_bs, hat_rev, hat_ts]
            right = [self.true_q, self.true_v, self.true_bs, self.true_rev, self.true_ts]
            
            return [np.max(np.abs(x-y)[self.trim:-self.trim]) for x,y in zip(left,right)]
            
        p = Pool(os.cpu_count())
        hats_dgp = np.array(p.map(simulate_one_dgp, range(draws)))
        p.close()
        p.join()
        
        self.cov = np.round((1+np.mean(np.sign(self.crit_qs_uni-hats_dgp), axis = 0))/2, 3)
        
    def simulate_dgp_nested(self, inner_loop = 1000, outer_loop = 1000, nominal_coverage = 95): 
        
        def simulate_one(i, smooth_Q = False): 
            np.random.seed(i)
            mc = np.sort(np.random.uniform(0, 1, self.sample_size))
            hat_Q = self.Q_fun(mc)
            hat_q = q_smooth(hat_Q, self.kernel, *self.band_options, 
                             is_sorted = True, reflect = self.reflect)
            
            if smooth_Q == True:
                hat_Q = np.cumsum(hat_q)/len(hat_q)
            
            hat_v = hat_Q + self.A_4*hat_q
            hat_ts = total_surplus(hat_v, *self.part_options)
            hat_bs = bidder_surplus(hat_v, *self.part_options)
            hat_rev = hat_ts - self.M*hat_bs
            
            # this is the correct way
            hat_ts = total_surplus_from_Q(hat_Q, *self.part_options)
            
            left = [hat_q, hat_v, hat_bs, 
                    hat_rev, hat_ts]
            right = [self.true_q, self.true_v, self.true_bs, 
                     self.true_rev, self.true_ts]
            
            stat_dgp = [np.max(np.abs(x-y)[self.trim:-self.trim]) for x,y in zip(left,right)]
            
            stats_uni = []
            for j in range(inner_loop):
                np.random.seed(j)
                hat_Q_uni = np.sort(np.random.uniform(0, 1, self.sample_size))
                hat_q_uni = q_smooth(hat_Q_uni, self.kernel, *self.band_options, 
                             is_sorted = True, reflect = self.reflect)
                
                if smooth_Q == True:
                    hat_Q_uni = np.cumsum(hat_q_uni)/len(hat_q_uni)
            
                # here comes the pivotization
                # for smooth functionals
                hat_Q_uni *= self.true_q
                # for non-smooth functionals
                hat_q_uni *= self.true_q
            
                hat_v_uni = hat_Q_uni + self.A_4*hat_q_uni                
                hat_ts_uni = total_surplus(hat_v_uni, *self.part_options)
                hat_bs_uni = bidder_surplus(hat_v_uni, *self.part_options)
                hat_rev_uni = hat_ts_uni - self.M*hat_bs_uni
                
                # this is the correct way
                hat_ts_uni = total_surplus_from_Q(hat_Q_uni, *self.part_options)
                
                left = [hat_q_uni, hat_v_uni, 
                        hat_bs_uni, hat_rev_uni, hat_ts_uni]
                right = [self.true_q_uni, self.true_v_uni, 
                         self.true_bs_uni, self.true_rev_uni, self.true_ts_uni]

                stat_uni = [np.max(np.abs(x-y)[self.trim:-self.trim]) for x,y in zip(left,right)]
                stats_uni.append(stat_uni)
                
            crit_uni = np.percentile(np.array(stats_uni), nominal_coverage, axis = 0)
            return (np.sign(crit_uni - stat_dgp)+1)/2
            
        p = Pool(os.cpu_count())
        rejections = np.array(p.map(simulate_one, range(outer_loop)))
        p.close()
        p.join()
        
        self.cov = np.mean(rejections, axis = 0)
        
        
        
    
        