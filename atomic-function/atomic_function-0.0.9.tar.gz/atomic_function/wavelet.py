import numpy as np
from atomic_function import function


class wavelet:

    def __init__(self, waf, coef=2):
        self.coef = coef
        self.waf = waf

    def fi_f(self, w):
        if self.waf == 'ha':
            chi = function.ha(w*3/(self.coef*np.pi)+2/self.coef, self.coef)+function.ha(w*3/(
                self.coef*np.pi), self.coef)+function.ha(w*3/(self.coef*np.pi)-2/self.coef, self.coef)
            return np.sqrt(np.abs(chi*2/self.coef))

        if self.waf == 'up':
            chi = function.up(w*3/(2*np.pi)+1)+function.up(w *
                                                           3/(2*np.pi))+function.up(w*3/(2*np.pi)-1)
            return np.sqrt(np.abs(chi))

        if self.waf == 'upm':
            chi = function.upm(w*3/(2*np.pi)+1, self.coef)+function.upm(
                w*3/(2*np.pi), self.coef)+function.upm(w*3/(2*np.pi)-1, self.coef)
            return np.sqrt(np.abs(chi))

    def frequency_function(self, x):
        n = [-1, 0, 1]
        sum = 0
        for item in n:
            sum += self.fi_f(2*(x-2*np.pi*item))
        return sum

    def H(self, t):
        return self.frequency_function(t)

    def G(self, t):
        return np.exp(1j*t)*np.conj(self.H(t+np.pi))

    def H_(self, t):
        return np.conj(self.H(t))

    def G_(self, t):
        return np.exp(-1j*t)*self.H(t+np.pi)

    def filter(self, N):
        w = np.linspace(-np.pi, np.pi, 1000)

        n = np.arange(-N//2, 1+N//2, 1)

        def fourier_series(f, n):
            h = []
            func = f(w)
            for i in n:
                h.append(np.trapz(func*np.exp(-1j*w*i), x=w)/(2**0.5*np.pi))
            h = np.real(h)
            return h
        h_dec = fourier_series(self.H, n)
        g_dec = fourier_series(self.G, n)
        h_rec = fourier_series(self.H_, n)
        g_rec = fourier_series(self.G_, n)

        return h_dec, g_dec, h_rec, g_rec
