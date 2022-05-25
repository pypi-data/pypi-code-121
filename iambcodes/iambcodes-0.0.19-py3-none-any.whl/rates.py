import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting._matplotlib.style import get_standard_colors
from scipy import stats
from scipy.optimize import curve_fit


def plot_multi(data, cols=None, spacing=.1, **kwargs):
# source:
# https://stackoverflow.com/questions/11640243/pandas-plot-multiple-y-axes

    # Get default color style from pandas - can be changed to any other color list
    if cols is None: cols = data.columns
    if len(cols) == 0: return
    colors = get_standard_colors(num_colors=len(cols))

    fig, ax = plt.subplots()
    # First axis
    ax.plot(data.loc[:, cols[0]].values, data.loc[:, cols[1]].values, **kwargs)
#    ax = data.loc[:, cols[0]].plot(label=cols[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=cols[1])
    lines, labels = ax.get_legend_handles_labels()

    for n in range(2, len(cols)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        data.loc[:, cols[n]].plot(ax=ax_new, label=cols[n], color=colors[n % len(colors)], **kwargs)
        ax_new.set_ylabel(ylabel=cols[n])
        
        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label
        
    ax.legend(lines, labels, loc=0)
    return ax


def SubVector(StartEnd, Vector):
    '''
    Extract a sub-vector based on start and end values. The output are the indices in the input vector.
    '''
    Above = Vector >= StartEnd[0]
    Below = Vector <= StartEnd[1]
    Select = np.logical_and(Above, Below)
    return np.arange(len(Vector))[Select]
    

def FitGrowth(time, ydat, law='lin', inlog=False, p0=None):
    '''
    Curve fitting of a measurement over time to determine rate and standard deviation. Different laws can be chosen.
    See also https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
    
    Arguments:
        time:       np vector, time points
        ydat:       np vector, measurements
        law:        str, 'lin' = linear relation; 'exp' = exponential law; 'log' = logarithmic growth law, Verhulst
        inlog:      Boolean, whether input data should be logarithmized
        p0:         list, initial conditions for the estimator
        
    Returns:
        y_rate:     np vector, rate
        y_sterr:    standard deviation
        y_init:     initial value of y
    
    '''
    
    if law == 'lin':
        if inlog:
            ydat = np.log(ydat)
        y_rate, y_init,_,_, y_sterr = stats.linregress(time, ydat)
        y_lim = None
    elif law == 'exp':
        ExpGrowth = lambda t, r, y0: y0*np.exp(r*t)        
        popt, pcov = curve_fit(ExpGrowth, time, ydat, p0=p0)
        y_rate, y_init = popt[0:2]
        y_sterr = np.sqrt(np.diag(pcov))[0]
        y_lim = None
    elif law == 'log':
        LogGrowth = lambda t, r, y0, K: y0*K / (y0 + (K-y0)*np.exp(-r*t))
        try:
            popt, pcov = curve_fit(LogGrowth, time, ydat, p0=p0)
            y_rate, y_init, y_lim = popt[0:3]
            y_sterr = np.sqrt(np.diag(pcov))[0]
        except RuntimeError:
            return False
    return y_rate, y_sterr, y_init, y_lim

def FitR2(time, ydata, popt, law='lin', inlog=False):
    '''
    Calculated the R2 and sum of squares of a fit.
    https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit

    Parameters
    ----------
    time : np vector
        time points of the experiment.
    ydata : np vector
        measurements.
    popt : np vector, with rate, y_init, and optional y_lim for log func
        DESCRIPTION.
    law : str, optional
        'lin' = linear relation, default; 'exp' = exponential law; 'log' = logarithmic growth law, Verhulst.
    inlog : boolean, optional
        whether input data should be logarithmized. The default is False.

    Returns
    -------
    R2 : np vector.
        correlation coefficient
    SSR : np vector.
        sum of squared residuals

    '''
    if inlog:
        ydata = np.log(ydata)
    if law == 'lin':
        func = lambda time, a, b: a*time+b 
    elif law == 'exp':
        func = lambda t, r, y0: y0*np.exp(r*t)
    elif law == 'log':
        func = lambda t, r, y0, K: y0*K / (y0 + (K-y0)*np.exp(-r*t))

    
    residuals = ydata- func(time, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((ydata-np.mean(ydata))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    return r2, ss_tot

def PlotFit(time, ydat, par, sterr, xyunits, law='lin', inlog=False, export_file=None, kwargs={}):
    '''
    Curve fitting of a measurement over time to determine rate and standard deviation. Different laws can be chosen.

    Arguments:
        time:       np vector, time points
        ydat:       np vector, measurements
        par:        np vector, with rate, y_init, and optional y_lim for log func
        sterr:      np number, standard error of the rate
        xyunits:    list, x and y-axis units
        law:        str, 'lin' = linear relation; 'exp' = exponential law; 'log' = logarithmic growth law, Verhulst
        inlog:      Boolean, whether input data should be logarithmized
        export_file:str, filename of plot
    
    Returns:
        Figure of rate law with data.

    '''
    if inlog:
        ydat = np.log(ydat)
    plt.plot(time, ydat, 'gx', label='data', **kwargs)
    if law == 'lin':
        func = lambda t, a, b: a*t + b
    elif law == 'exp':
        func = lambda t, r, y0: y0*np.exp(r*t)
    elif law == 'log':
        func = lambda t, r, y0, K: y0*K / (y0 + (K-y0)*np.exp(-r*t))
    
    # we sample more points
    ttime = np.linspace(time[0], time[-1], len(time)*10)
    plt.plot(ttime, func(ttime, *par), 'g-', label='fit: rate={:.2f}+/-{:.2f}'.format(par[0], sterr), **kwargs)
    plt.xlabel(xyunits[0])
    plt.ylabel(xyunits[1])
    plt.legend()
    if export_file:
        plt.savefig(export_file)
    # plt.show()

def read_ConfFile(FileAddress:str):
    '''
    Reading JUDAS configuration files. 

    Parameters
    ----------
    FileAddress : str
        Full address of configuration file.

    Returns
    -------
    Par_Dict : dict
        Dictionary with all user defined variables in the respective workflow.

    '''
    Par_Dict = dict()
    with open(FileAddress) as fp:
        mylines = fp.read().splitlines()
        for myline in mylines:
            if not myline.startswith('#'):
                (key, val) = myline.split(':', 1)
                Par_Dict[str(key.strip())] = val.strip()
    return Par_Dict