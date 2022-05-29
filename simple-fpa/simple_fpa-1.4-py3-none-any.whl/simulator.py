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
import numba as nb
    
def cens_Q(Q, x, eps):
    return (Q(eps+x*(1-2*eps))-Q(eps))/(Q(1-eps)-Q(eps))

def cens_q(f, Q, x, eps):
    return (1-2*eps)/(f(Q(eps+x*(1-2*eps)))*(Q(1-eps)-Q(eps)))

class Simulator:
    '''Addition to the package for the "Nonparametric inference on counterfactuals in sealed first-price auctions" paper.'''
    
    def __init__(self, sample_size, smoothing_rate, trim_percent, 
                 frec, rvpdf, rvppf, eps, draws):
        
        self.u_grid = np.linspace(0, 1, sample_size)
        
        self.Q_fun = lambda x: cens_Q(rvppf, x, eps)
        self.q_fun = lambda x: cens_q(rvpdf, rvppf, x, eps)
        
        self.sample_size = sample_size
        self.frec = frec
        
        self.smoothing = -smoothing_rate
        self.u_trim = trim_percent/100
        
        self.draws = draws
        
    def calibrate(self):
        
        self.mc = self.Q_fun(np.sort(np.random.uniform(0, 1, size = self.sample_size)))
        
        self.band_options = calibrate_band(self, self.mc, self.u_trim, self.smoothing)
        self.sample_size, self.band, self.i_band, self.trim = self.band_options
        
        self.kernel, _ = make_kernel(self.u_grid, self.i_band, kernel = tri)
        
        self.part_options = calibrate_part(self, self.u_grid, self.frec)
        self.M, self.A_1, self.A_2, self.A_3, self.A_4, self.a = self.part_options
        
    def simulate(self):
        
        trim = self.trim
        draws = self.draws
        M = self.M
        A_2 = self.A_2
        A_3 = self.A_3
        A_4 = self.A_4
        a = self.a
        u_grid = self.u_grid
        
        true_Q = self.Q_fun(self.u_grid)
        true_q = self.q_fun(self.u_grid)
        
        # eraze boundary
        true_Q[-self.trim:] = 0
        true_q[-self.trim:] = 0
        
        def one_mc(i):
            np.random.seed(i)

            Q_uni = np.sort(np.random.uniform(0, 1, self.sample_size))
            Q_dgp = self.Q_fun(Q_uni)

            q_uni = q_smooth(Q_uni, self.kernel, *self.band_options, is_sorted = True, reflect = False)
            q_dgp = q_smooth(Q_dgp, self.kernel, *self.band_options, is_sorted = True, reflect = False)

            # eraze boundary
            Q_uni[-self.trim:] = 0
            q_uni[-self.trim:] = 0
            Q_dgp[-self.trim:] = 0
            q_dgp[-self.trim:] = 0

            return [Q_uni, q_uni, Q_dgp, q_dgp]
        
        p = Pool(os.cpu_count())
        all_mc = np.array(p.map(one_mc, range(self.draws)))
        p.close()
        p.join()
        
        all_Q_uni  = all_mc[:,0,:].copy()
        all_q_uni  = all_mc[:,1,:].copy()

        all_Q_dgp  = all_mc[:,2,:].copy()
        all_q_dgp  = all_mc[:,3,:].copy()

        del(all_mc)
        
        @nb.jit(nopython = True)
        def d_numba(arr):
            diff = arr - np.roll(arr, 1)
            diff[0] = diff[1]
            return diff*len(diff)

        @nb.jit(nopython = True)
        def int_lowbound_numba(arr):
            return np.flip(np.cumsum(np.flip(arr)))/len(arr)
        
        psi = d_numba(A_2)
        chi = psi - d_numba(A_4*psi)
        
        stats_dgp = np.zeros(shape = (draws, 5), dtype = np.float)
        
        @nb.jit(nopython = True, parallel = True)
        def simulate_all_dgp(stats_dgp):
            for i in nb.prange(draws):
                delta_Q = all_Q_dgp[i]-true_Q
                delta_q = all_q_dgp[i]-true_q

                delta_v = delta_Q + A_4*delta_q
                delta_ts = int_lowbound_numba(delta_v*d_numba(A_2))
                delta_bs = a*int_lowbound_numba(A_3*d_numba(delta_v))
                delta_rev = delta_ts - M*delta_bs

                # this is a better way
                delta_ts = A_4[-1]*psi[-1]*delta_Q[-1]-A_4*psi*delta_Q + int_lowbound_numba(chi*delta_Q)

                stats_dgp[i,0] = np.max(np.abs(delta_q)[trim:-trim])
                stats_dgp[i,1] = np.max(np.abs(delta_v)[trim:-trim])
                stats_dgp[i,2] = np.max(np.abs(delta_bs)[trim:-trim])
                stats_dgp[i,3] = np.max(np.abs(delta_rev)[trim:-trim])
                stats_dgp[i,4] = np.max(np.abs(delta_ts)[trim:-trim])
                
        simulate_all_dgp(stats_dgp)
        self.stats_dgp = stats_dgp
        
        stats_uni = np.zeros(shape = (draws, draws, 5), dtype = np.float)

        @nb.jit(nopython = True, parallel = True)
        def simulate_all_uni(stats_uni):
            for i in nb.prange(draws):
                for j in nb.prange(draws):
                    delta_Q = (all_Q_uni[j]-u_grid)*all_q_dgp[i]
                    delta_q = (all_q_uni[j]-1)*all_q_dgp[i]

                    delta_v = delta_Q + A_4*delta_q
                    delta_ts = int_lowbound_numba(delta_v*d_numba(A_2))
                    delta_bs = a*int_lowbound_numba(A_3*d_numba(delta_v))
                    delta_rev = delta_ts - M*delta_bs

                    # this is a better way
                    delta_ts = A_4[-1]*psi[-1]*delta_Q[-1]-A_4*psi*delta_Q + int_lowbound_numba(chi*delta_Q)

                    stats_uni[i,j,0] = np.max(np.abs(delta_q)[trim:-trim])
                    stats_uni[i,j,1] = np.max(np.abs(delta_v)[trim:-trim])
                    stats_uni[i,j,2] = np.max(np.abs(delta_bs)[trim:-trim])
                    stats_uni[i,j,3] = np.max(np.abs(delta_rev)[trim:-trim])
                    stats_uni[i,j,4] = np.max(np.abs(delta_ts)[trim:-trim])
                    
        simulate_all_uni(stats_uni)
        self.stats_uni = stats_uni
        
    def get_coverage(self, nominal_coverage, digits):
        crit_uni = np.percentile(self.stats_uni.reshape(self.draws, self.draws, 5), nominal_coverage, axis = 1)
        return {i:np.round((np.mean(np.sign(crit_uni[:,j]-self.stats_dgp[:,j]))+1)/2, digits) for i,j in zip(['q','v','bs','rev','ts'],range(5))}
        
        