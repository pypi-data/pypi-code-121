import numpy as np


class TSCyclic(object):
    #этот вариант работает по отсечке таймстампа, окно берется с запасом
    def __init__(self, maxlen=1000000):
        self.maxlen = maxlen
        self.shift = 0        
        self.ts = np.zeros(maxlen)
        self.vals = np.zeros(maxlen)  
        
    def add(self, timestamp, val):
        self.vals[self.shift], self.ts[self.shift] = val, timestamp
        self.shift = (self.shift + 1) % self.maxlen
        
    def get_older_then(self, timestamp):
        return self.vals[np.flatnonzero(self.ts >= timestamp)]

    def get_quantiles(self, timestamp, quantiles=[0.33, 0.66, 1]):
        vals = self.get_older_then(timestamp)
        return np.quantile(vals, quantiles, interpolation='nearest')   
    
    def get_quant_counts(self, timestamp, quantiles=[0.2, 0.4, 0.6, 0.8, 1]):
        vals = self.get_older_then(timestamp)
        return np.quantile(vals, quantiles, interpolation='nearest')*len(vals)
    
    def get_hist_counts(self, timestamp, bins, rng=None):
        vals = self.get_older_then(timestamp)
        if rng:
            return np.histogram(vals, bins=bins, range=rng)[0]
        else:
            return np.histogram(vals, bins=bins)[0]
    
class Cyclic(object):
    #этот вариант работает по всему буферу, размер которого задается заранее
    def __init__(self, win=300):
        self.win = win
        self.shift = 0
        self.vals = np.full(win, np.nan) 
        
    def add(self, val):
        self.vals[self.shift] = val
        self.shift = (self.shift + 1) % self.win
        
    def get_valid_vals(self):
        return self.vals[~np.isnan(self.vals)]
        
    def get_quantiles(self, quantiles=[0.33, 0.66, 1]):
        vals = np.nanquantile(self.vals, quantiles, interpolation='nearest')
        return vals
    
    def get_quant_counts(self, quantiles=[0.2, 0.4, 0.6, 0.8, 1]):
        vals = np.nanquantile(self.vals, quantiles, interpolation='nearest')
        return vals * np.count_nonzero(~np.isnan(vals))
    
class PSITS(object):
    #http://ucanalytics.com/blogs/population-stability-index-psi-banking-case-study/
    #этот вариант работает по отсечке таймстампа, окно берется с запасом
    def __init__(self, expected_distribution_vector, bins=10, maxlen=1000000):        
        self.n_const = np.full(bins, 0.5)
        self.hist = lambda x: np.histogram(x, bins=bins, range=(0.0, 1.0))[0] + self.n_const

        self.buf = TSCyclic(maxlen)
        self.add = self.buf.add
        
        expected = self.hist(np.array(expected_distribution_vector))
        self.expected = expected/expected.sum()
        
    def compute(self, timestamp):
        raw_hist = self.hist(self.buf.get_older_then(timestamp))
        actual = raw_hist/raw_hist.sum()
        terms = (actual - self.expected)*np.log(actual/self.expected)
        return terms.sum() #percents
        
class PSI(object):
    #http://ucanalytics.com/blogs/population-stability-index-psi-banking-case-study/
    #этот вариант работает по всему буферу, размер которого задается заранее
    def __init__(self, expected_distribution_vector, bins=10, win=1000):        
        self.n_const = np.full(bins, 0.5)
        self.hist = lambda x: np.histogram(x, bins=bins, range=(0.0, 1.0))[0] + self.n_const

        self.buf = Cyclic(win)
        self.add = self.buf.add
        
        expected = self.hist(np.array(expected_distribution_vector))
        self.expected = expected/expected.sum()
        
    def compute(self):
        raw_hist = self.hist(self.buf.get_valid_vals())
        actual = raw_hist/raw_hist.sum()
        terms = (actual - self.expected)*np.log(actual/self.expected)
        return terms.sum() #percents    

class KS(object):
#https://www.encyclopediaofmath.org/index.php/Kolmogorov-Smirnov_test
#http://matstats.ru/smirnov.html
#http://bjlkeng.github.io/posts/the-empirical-distribution-function/
#https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test#Two-sample_Kolmogorov%E2%80%93Smirnov_test
    def __init__(self, expected_distribution_vector, bins=10, win=1000):        
        self.buf = Cyclic(win)
        
        self.add = self.buf.add
        self.expected_vec = np.array(expected_distribution_vector)
        self.expected_len = len(self.expected_vec)
        #self.win = win
        
        self.F_ref, self.bin_edges = self._ecdf(self.expected_vec, bins)
        
        
    def _ecdf(self, X, bins=10):
        hist, bin_egdes = np.histogram(X, bins=bins)
        csum = np.cumsum(hist)
        return csum/csum[-1], bin_egdes        
        
    def compute(self):

        def c2alpha(c):
            return np.exp(-2*np.power(c, 2))


        #buflen = self.win #длина буфера в потоке данных       
        cur_vals = self.buf.get_valid_vals()
        
        len_ref = self.expected_len
        len_cur = len(cur_vals)

        #поправочный коэффициент для Two-sample Kolmogorov–Smirnov test
        coeff = np.sqrt((len_ref*len_cur)/(len_ref+len_cur))

        #сначала считаем два cdf распределения 
        F_ref = self.F_ref
        F_cur, _ = self._ecdf(cur_vals, bins=self.bin_edges) #bin_egdes гарантирует, что совпадут бакеты
        #теперь супремум
        D_max = (np.abs(F_cur-F_ref)).max()
        #теперь поправочный коэф-т
        lambda_emph = D_max*coeff
        #теперь p-val
        p = c2alpha(lambda_emph) #чем меньше разница распределений, тем больше число 
        return p

