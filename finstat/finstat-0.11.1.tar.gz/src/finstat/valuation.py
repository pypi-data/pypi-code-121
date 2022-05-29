import typing as typ
import numpy as np
import pandas as pd

def cagr(fv, pv, t):
    """
    Computes compound annual growth rate implied by two values over a time, t

    Params
    -------
    fv:     float, future value
    pv:     float, present value
    t:      time between values in years
    """
    return (fv / pv)**(1/t) - 1

def discount_factors(cf, discount, t):
    return (1 + discount)**np.arange(t, cf.shape[0] + t)

def wacc_calc(cost_debt, cost_equity, debt_to_cap):
    return (cost_debt*debt_to_cap) + (cost_equity*(1-debt_to_cap))

def npv(cf, disc=.08):
    """
    Net Present Value calculation for a stream of cash flows
    
    Params
    -------
    cf:    nxm array of cash flow streams
            > n = # of years
            > m = # of different cash flow streams
    disc:  float representing annual discount rate
            > default value per Duff&Phelps recommendation here:
                https://www.duffandphelps.com/-/media/assets/pdfs/publications/articles/dp-erp-rf-table-2020.pd
    
    Returns
    --------
        nxm array representing of each cash inflow discounted to the current day
    """
    return cf.values.reshape(-1,cf.ndim) / (1+disc)**np.arange(0, cf.shape[0]).reshape(-1,1)

def logparams(x1, y1, x2, y2):
    """
    Returns parameters for line of form 
    
    y = a*ln(b*x)
    
    https://math.stackexchange.com/questions/716152/graphing-given-two-points-on-a-graph-find-the-loglarithmic-function-that-passes
    """
    a = (y1 - y2) / np.log(x1 / x2)
    b = np.exp((y2*np.log(x1) - y1*np.log(x2)) / (y1 - y2))
    
    return a, b

def logline(x, a, b):
    xdim = b.shape[0]
    x = x.repeat(xdim).reshape(-1,xdim)
    a = a.reshape(-1,1)
    b = b.reshape(-1,1)

    return a*np.log(b*x.T)

def log_returns(ser):
    if not isinstance(ser, pd.Series):
        ser = pd.Series(ser)
    return np.log(ser / ser.shift(1)).iloc[1:]

class Valuation:
    def __init__(self, cash_flows:typ.Iterable, discount:float, fwd_multiple:float, t=1):
        self.cash_flows = cash_flows
        self.discount = discount
        self.fwd_multiple = fwd_multiple
        self.t = t
        
        idx = self.cash_flows.index
        self.tvidx = pd.period_range(start=idx[0], periods=idx.size + 1, freq=idx.freqstr)
    
    @property
    def discount_factors(self):
        return discount_factors(self.cash_flows_with_tv(), self.discount, self.t)
    
    @property
    def terminal_value(self):
        return self.cash_flows.iloc[-1] * self.fwd_multiple        

    @property
    
    def tv(self):
        return self.terminal_value
    
    @property
    def discounted_tv(self):
        return self.discounted_cash_flows().iloc[-1]

    def cash_flows_with_tv(self):
        ser = pd.concat((self.cash_flows, pd.Series([self.terminal_value])))
        ser.index = self.tvidx
        return ser
    
    def discounted_cash_flows(self):
        return self.cash_flows_with_tv() / self.discount_factors

    def fair_value(self):
        return self.discounted_cash_flows().sum()
    
    def tv_per_fv(self):
        return self.discounted_tv / self.fair_value()
    
    def __call__(self):
        return self.fair_value()
