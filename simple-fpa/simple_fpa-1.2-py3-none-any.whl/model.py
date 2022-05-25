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

def load_haile():
    stream = pkg_resources.resource_stream(__name__, 'data/haile_data.csv')
    return pd.read_csv(stream, index_col=0)

class Model:
    '''A package for the "Nonparametric inference on counterfactuals in sealed first-price auctions" paper.'''
    
    def __init__(self, data, auctionid_columns, bid_column):
        self.data = data
        self.auctionid_columns = auctionid_columns
        self.bid_column = bid_column
        
        self.count_bidders_by_auctionid()
        
    def count_bidders_by_auctionid(self):
        self.data.sort_values(by = self.auctionid_columns, inplace = True)
        
        self.data['__ones'] = 1
        self.data['_bidders'] = self.data.groupby(by = self.auctionid_columns)['__ones'].transform(sum)
        self.data.drop(columns = ['__ones'], inplace = True)
        
        frec = self.data.groupby(by = 'auctionid')._bidders.first().value_counts().values
        frec = frec/np.sum(frec)
        n_bids = self.data.groupby(by = 'auctionid')._bidders.first().value_counts().index.values
        self.frec = {int(i):j for i,j in zip(n_bids, frec)}
        
    def residualize(self, cont_covs_columns, disc_covs_columns, model_type = 'multiplicative'):
        
        self.cont_covs_columns = cont_covs_columns
        self.disc_covs_columns = disc_covs_columns
        self.model_type = model_type
        
        if self.model_type == 'multiplicative':
            self.formula = 'np.log(' + self.bid_column + ') ~ '
            for c in self.cont_covs_columns:
                self.formula += 'np.log(' + c + ') + '
            for c in self.disc_covs_columns:
                self.formula += 'C(' + c + ') + '
            self.formula = self.formula[:-2]
            
        if self.model_type == 'additive':
            self.formula = self.bid_column + ' ~ '
            for c in self.cont_covs_columns:
                self.formula += c + ' + '
            for c in self.disc_covs_columns:
                self.formula += 'C(' + c + ') + '
            self.formula = self.formula[:-2]
            
        self.ols = smf.ols(formula=self.formula, data=self.data).fit()
        
        if self.model_type == 'multiplicative':
            self.data['_resid'] = np.exp(self.ols.resid)
            self.data['_fitted'] = np.exp(self.ols.fittedvalues)
            
        if self.model_type == 'additive':
            self.data['_resid'] = self.ols.resid
            self.data['_fitted'] = self.ols.fittedvalues
            
        self.data.sort_values(by = '_resid', inplace = True) # here comes the sorting
            
    def summary(self, show_dummies = False):
        for row in self.ols.summary().as_text().split('\n'):
            if row[:2] != 'C(' or show_dummies == True:
                print(row)
                
    def trim_residuals(self, trim_percent = 5):
        left = np.percentile(self.data._resid.values, trim_percent)
        right = np.percentile(self.data._resid.values, 100-trim_percent)
        self.data['_trimmed'] = 0
        self.data.loc[(self.data._resid < left) | (self.data._resid > right), '_trimmed'] = 1
    
    def fit(self, smoothing_rate = 0.2, trim_percent = 5, reflect = True):
        
        self.observations = self.data[self.data._trimmed == 0]._resid.values.copy()
        
        self.intercept = self.observations.min()
        self.observations -= self.intercept
        self.scale = self.observations.max()
        self.observations /= self.observations.max()
        
        self.smoothing = -smoothing_rate
        self.u_trim = trim_percent/100
        self.reflect = reflect
        
        self.band_options = calibrate_band(self, self.observations, self.u_trim, self.smoothing)
        self.sample_size, self.band, self.i_band, self.trim = self.band_options
        
        self.u_grid = np.linspace(0, 1, self.sample_size)
        self.kernel, self.intKsq = make_kernel(self.u_grid, self.i_band, kernel = tri)
        
        self.part_options = calibrate_part(self, self.u_grid, self.frec)
        self.M, self.A_1, self.A_2, self.A_3, self.A_4, self.a = self.part_options
         
        self.hat_Q = self.intercept + self.scale*self.observations # they are sorted with the dataset
        
        self.hat_f = f_smooth(self.observations, self.kernel, *self.band_options, 
                              paste_ends = False, reflect = reflect)/self.scale # might be unnecessary
        
        self.hat_q = self.scale*q_smooth(self.observations, self.kernel, *self.band_options, 
                                         is_sorted = True, reflect = reflect)
        
        self.hat_v = v_smooth(self.hat_Q, self.hat_q, self.A_4)
        
        self.ts = total_surplus(self.hat_v, *self.part_options)
        self.ts2 = total_surplus_from_Q(self.hat_Q, *self.part_options)
        
        self.bs = bidder_surplus(self.hat_v, *self.part_options)
        self.rev = revenue(self.hat_v, *self.part_options)
        
    def predict(self):
        self.active_index = self.data._trimmed.isin([0])
        
        self.data['_u'] = np.nan
        self.data.loc[self.active_index,'_u'] = self.u_grid
        
        self.data['_hat_q'] = np.nan
        self.data.loc[self.active_index,'_hat_q'] = self.hat_q
        
        self.data['_hat_v'] = np.nan
        self.data['_latent_resid'] = np.nan
        self.data.loc[self.active_index,'_hat_v'] = self.hat_v
        self.data.loc[self.active_index,'_latent_resid'] = self.hat_v
        
        self.data['_hat_ts'] = np.nan
        self.data.loc[self.active_index,'_hat_ts'] = self.ts
        
        self.data['_hat_bs'] = np.nan
        self.data.loc[self.active_index,'_hat_bs'] = self.bs
        
        self.data['_hat_rev'] = np.nan
        self.data.loc[self.active_index,'_hat_rev'] = self.rev
        
        self.data['_latent_'+self.bid_column] = np.nan
        if self.model_type == 'multiplicative':
            self.data['_latent_'+self.bid_column] = self.data['_latent_resid']*self.data._fitted
        if self.model_type == 'additive':
            self.data['_latent_'+self.bid_column] = self.data['_latent_resid']+self.data._fitted
            
    def plot_stats(self):
        plot_stats(self)
        
    def plot_counterfactuals(self):
        plot_counterfactuals(self)
        
    def make_ci(self, confidence, hyp = 'twosided'):
        make_ci(self, confidence, hyp)
    
    def make_cb(self, confidence, draws = 10000, hyp = 'twosided'):
        make_cb(self, confidence, draws, hyp)
        
    def make_cicb_for_ts(self, confidence, draws = 10000, hyp = 'twosided'):
        make_cicb_for_ts(self, confidence, draws, hyp)
        
    def find_optimal_u(self):
        self.opt_u = self.data._u[self.data._hat_rev.idxmax()]
        print('optimal exclusion:', np.round(self.opt_u,5))
        
        
        
        
    
        
        