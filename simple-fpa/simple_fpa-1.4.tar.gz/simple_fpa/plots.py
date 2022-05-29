import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sb
from pylab import rcParams

def plot_ci(self, ax):
    
    ax.plot(self.data._u, self.data._hat_ts, label = 'ts', color = 'green')
    ax.plot(self.data._u, self.data._hat_ts + self.data._ts_ci, color = 'green', linestyle = '--',linewidth = 1)
    ax.plot(self.data._u, self.data._hat_ts - self.data._ts_ci, color = 'green', linestyle = '--',linewidth = 1)
    
    ax.plot(self.data._u, self.M*self.data._hat_bs, label = 'M*bs', color = 'red', linewidth=1)
    ax.plot(self.data._u, self.M*(self.data._bs_ci+self.data._hat_bs), 
            color = 'red', linestyle = '--', linewidth = 1)
    ax.plot(self.data._u, self.M*(-self.data._bs_ci+self.data._hat_bs), 
            color = 'red', linestyle = '--', linewidth = 1)
    
    ax.plot(self.data._u, self.data._hat_rev, label = 'rev', color = 'blue')
    ax.plot(self.data._u, self.data._rev_ci + self.data._hat_rev, 
            color = 'blue', linestyle = '--',linewidth = 1)
    ax.plot(self.data._u, -self.data._rev_ci + self.data._hat_rev, 
            color = 'blue', linestyle = '--',linewidth = 1)
    
    ax.axvline(self.opt_u, linewidth = 1, color = 'black', label = 'optimal exclusion', linestyle = 'dotted')
    
    ax.legend(loc = 'upper right')
    ax.set_xlabel('confidence intervals')
    
def plot_cb(self, ax):
    
    ax.plot(self.data._u, self.data._hat_ts, label = 'ts', color = 'green')
    ax.plot(self.data._u, self.data._hat_ts + self.data._ts_cb, color = 'green', linestyle = '--',linewidth = 1)
    ax.plot(self.data._u, self.data._hat_ts - self.data._ts_cb, color = 'green', linestyle = '--',linewidth = 1)
    
    ax.plot(self.data._u, self.M*self.data._hat_bs, color = 'red', linewidth=1)
    ax.plot(self.data._u, self.M*(self.data._bs_cb+self.data._hat_bs), 
            color = 'red', linestyle = '--',linewidth = 1)
    ax.plot(self.data._u, self.M*(-self.data._bs_cb+self.data._hat_bs), 
            color = 'red', linestyle = '--',linewidth = 1)
    
    ax.plot(self.data._u, self.data._hat_rev, color = 'blue')
    ax.plot(self.data._u, self.data._rev_cb + self.data._hat_rev, 
            color = 'blue', linestyle = '--',linewidth = 1)
    ax.plot(self.data._u, -self.data._rev_cb + self.data._hat_rev, 
            color = 'blue', linestyle = '--',linewidth = 1)
    
    ax.axvline(self.opt_u, linewidth = 1, color = 'black', linestyle = 'dotted')
    
    ax.set_xlabel('confidence bands')

def plot_counterfactuals(self):
    rcParams['figure.figsize'] = 7, 7/3
    fig, (ax1, ax2) = plt.subplots(1,2, sharey = True)
    
    plot_ci(self, ax1)
    plot_cb(self, ax2)
    
    plt.tight_layout()
    plt.show()

def plot_bidders(self, ax):
    
    sb.countplot(x = self.data.groupby(by = 'auctionid')._bidders.first().astype(int), 
                 facecolor=(0, 0, 0, 0),
                 linewidth=1,
                 edgecolor='black', 
                 ax = ax)
    
    ax.set_xlabel('bidders')
    
def plot_bid_residuals(self, ax):
    
    sb.histplot(data = self.data.loc[self.active_index,'_resid'], 
                stat = 'density', 
                bins = 50, 
                facecolor=(0, 0, 0, 0),
                linewidth=1,
                edgecolor='black', 
                ax = ax);
    
    ax.set_xlabel('bid residuals')
    ax.set_ylabel('density')
    
def plot_aux(self, ax):
    
    ax.plot(self.u_grid, self.A_1, label = '$A_1$')
    ax.plot(self.u_grid, self.A_2, label = '$A_2$')
    ax.plot(self.u_grid, self.A_3, label = '$A_3$')
    ax.plot(self.u_grid, self.A_4, label = '$A_4$')
    ax.set_xlabel('auxilliary functions')
    ax.legend()
    
def plot_densities(self, ax):
    
    ciq = self.ci_two*self.hat_q/np.sqrt(self.sample_size*self.band)
    
    ax.plot(self.u_grid, 
             self.hat_q, 
             label = 'smooth $\hat q(u)$', linewidth = 1, color = 'blue')
    ax.plot(self.u_grid, self.hat_q+ciq, linestyle = '--', linewidth = 1, color = 'blue')
    ax.plot(self.u_grid, self.hat_q-ciq, linestyle = '--', linewidth = 1, color = 'blue')
    
    
    ax.plot(self.u_grid, 
             self.hat_f*self.scale, 
             color = 'red', 
             label = 'smooth $\hat f(b)$ (scale matched)', 
             linewidth=1)
    
    cif = self.ci_two*np.sqrt(self.hat_f)/np.sqrt(self.sample_size*self.band)
    
    ax.plot(self.u_grid, 
             (self.hat_f+cif)*self.scale, 
             color = 'red', 
             linewidth=1, linestyle = '--')
    
    ax.plot(self.u_grid, 
             (self.hat_f-cif)*self.scale, 
             color = 'red', 
             linewidth=1, linestyle = '--')
    
    ax.legend()
    
def plot_quantiles(self, ax):
    
    avg_fitted = 1 #self.data._fitted.mean()

    if self.model_type == 'multiplicative':
        b_qf = self.hat_Q * avg_fitted
        v_qf = self.hat_v * avg_fitted

    if self.model_type == 'additive':
        b_qf = self.hat_Q + avg_fitted
        v_qf = self.hat_v + avg_fitted

    ax.plot(self.u_grid, b_qf, label = 'bid quantile function')
    ax.plot(self.u_grid, v_qf, label = 'value quantile function')
    ax.legend()
    
def plot_val_residuals(self, ax):
    sb.histplot(data = self.data._latent_resid, 
                stat = 'density', 
                bins = 50, 
                facecolor=(0, 0, 0, 0),
                linewidth=1,
                edgecolor='black', 
                ax = ax);
    
    ax.set_xlabel('value residuals')
    ax.set_ylabel('')
    
def plot_stats(self):
    rcParams['figure.figsize'] = 7, 7
    fig, ((ax1, ax3), (ax2, ax6), (ax5, ax4)) = plt.subplots(3,2)

    plot_bidders(self, ax1)
    plot_bid_residuals(self, ax2)
    plot_aux(self, ax3)
    plot_densities(self, ax4)
    plot_quantiles(self, ax5)
    plot_bid_residuals(self, ax6)

    plt.tight_layout()
    plt.show()


