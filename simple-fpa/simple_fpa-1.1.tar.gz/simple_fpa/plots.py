import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sb
from pylab import rcParams

def plot_counterfactuals(self):
    rcParams['figure.figsize'] = 7, 7/3
    fig, (ax1, ax2) = plt.subplots(1,2, sharey = True)
    
    ax1.plot(self.u_grid, self.ts, label = 'ts', color = 'green')
    #ax1.plot(self.u_grid, self.ts2, color = 'yellow', linestyle = '--',linewidth = 1)
    ax1.plot(self.u_grid, self.ts + self.ci_ts, color = 'green', linestyle = '--',linewidth = 1)
    ax1.plot(self.u_grid, self.ts - self.ci_ts, color = 'green', linestyle = '--',linewidth = 1)
    
    ax1.plot(self.u_grid, self.M*self.bs, label = 'M*bs', 
             color = 'red', linewidth=1)
    ax1.plot(self.data._u, self.M*(self.data._bs_ci+self.data._hat_bs), 
             color = 'red', linestyle = '--', linewidth = 1)
    ax1.plot(self.data._u, self.M*(-self.data._bs_ci+self.data._hat_bs), 
             color = 'red', linestyle = '--', linewidth = 1)
    
    ax1.plot(self.u_grid, self.rev, label = 'rev', color = 'blue')
    ax1.plot(self.data._u, self.data._rev_ci + self.data._hat_rev, 
             color = 'blue', linestyle = '--',linewidth = 1)
    ax1.plot(self.data._u, -self.data._rev_ci + self.data._hat_rev, 
             color = 'blue', linestyle = '--',linewidth = 1)
    
    ax1.axvline(self.opt_u, linewidth = 1, color = 'black', label = 'optimal exclusion', linestyle = 'dotted')
    
    ax1.legend(loc = 'upper right')
    #ax1.set_ylabel('in terms of residuals')
    ax1.set_xlabel('confidence intervals')
    
    ax2.plot(self.u_grid, self.ts, label = 'TS', color = 'green')
    #ax2.plot(self.u_grid, self.ts2, color = 'yellow', linestyle = '--',linewidth = 1)
    ax2.plot(self.u_grid, self.ts + self.cb_ts, color = 'green', linestyle = '--',linewidth = 1)
    ax2.plot(self.u_grid, self.ts - self.cb_ts, color = 'green', linestyle = '--',linewidth = 1)
    
    ax2.plot(self.u_grid, self.M*self.bs, color = 'red', linewidth=1)
    ax2.plot(self.data._u, self.M*(self.data._bs_cb+self.data._hat_bs), 
             color = 'red', linestyle = '--',linewidth = 1)
    ax2.plot(self.data._u, self.M*(-self.data._bs_cb+self.data._hat_bs), 
             color = 'red', linestyle = '--',linewidth = 1)
    
    ax2.plot(self.u_grid, self.rev, color = 'blue')
    ax2.plot(self.data._u, self.data._rev_cb + self.data._hat_rev, 
             color = 'blue', linestyle = '--',linewidth = 1)
    ax2.plot(self.data._u, -self.data._rev_cb + self.data._hat_rev, 
             color = 'blue', linestyle = '--',linewidth = 1)
    
    ax2.axvline(self.opt_u, linewidth = 1, color = 'black', linestyle = 'dotted')
    
    ax2.set_xlabel('confidence bands')
    
    plt.tight_layout()
    plt.show()

def plot_stats(self):
    rcParams['figure.figsize'] = 7, 7
    fig, ((ax1, ax3), (ax2, ax6), (ax5, ax4)) = plt.subplots(3,2)
    sb.countplot(x = self.data.groupby(by = 'auctionid')._bidders.first().astype(int), 
                 facecolor=(0, 0, 0, 0),
                 linewidth=1,
                 edgecolor='black', 
                 ax = ax1)
    
    ax1.set_xlabel('bidders')
    
    sb.histplot(data = self.data.loc[self.active_index,'_resid'], 
                stat = 'density', 
                bins = 50, 
                facecolor=(0, 0, 0, 0),
                linewidth=1,
                edgecolor='black', 
                ax = ax2);
    
    ax2.set_xlabel('bid residuals')
    ax2.set_ylabel('density')
    
    ax3.plot(self.u_grid, self.A_1, label = '$A_1$')
    ax3.plot(self.u_grid, self.A_2, label = '$A_2$')
    ax3.plot(self.u_grid, self.A_3, label = '$A_3$')
    ax3.plot(self.u_grid, self.A_4, label = '$A_4$')
    ax3.set_xlabel('auxilliary functions')
    ax3.legend()
        
    ciq = self.ci_two*self.hat_q/np.sqrt(self.sample_size*self.band)
    
    ax4.plot(self.u_grid, 
             self.hat_q, 
             label = 'smooth $\hat q(u)$', linewidth = 1, color = 'blue')
    ax4.plot(self.u_grid, self.hat_q+ciq, linestyle = '--', linewidth = 1, color = 'blue')
    ax4.plot(self.u_grid, self.hat_q-ciq, linestyle = '--', linewidth = 1, color = 'blue')
    
    
    ax4.plot(self.u_grid, 
             self.hat_f*self.scale, 
             color = 'red', 
             label = 'smooth $\hat f(b)$ (scale matched)', 
             linewidth=1)
    
    cif = self.ci_two*np.sqrt(self.hat_f)/np.sqrt(self.sample_size*self.band)
    
    ax4.plot(self.u_grid, 
             (self.hat_f+cif)*self.scale, 
             color = 'red', 
             linewidth=1, linestyle = '--')
    
    ax4.plot(self.u_grid, 
             (self.hat_f-cif)*self.scale, 
             color = 'red', 
             linewidth=1, linestyle = '--')
    
    ax4.legend()

    avg_fitted = self.data._fitted.mean()

    if self.model_type == 'multiplicative':
        b_qf = self.hat_Q * avg_fitted
        v_qf = self.hat_v * avg_fitted

    if self.model_type == 'additive':
        b_qf = self.hat_Q + avg_fitted
        v_qf = self.hat_v + avg_fitted

    ax5.plot(self.u_grid, b_qf, label = 'bid quantile function')
    ax5.plot(self.u_grid, v_qf, label = 'value quantile function')
    ax5.legend()
    
    sb.histplot(data = self.data._latent_resid, 
                stat = 'density', 
                bins = 50, 
                facecolor=(0, 0, 0, 0),
                linewidth=1,
                edgecolor='black', 
                ax = ax6);
    
    ax6.set_xlabel('value residuals')
    ax6.set_ylabel('')
    
    plt.tight_layout()
    plt.show()






