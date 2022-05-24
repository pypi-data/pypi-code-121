import numpy as np
import pandas as pd
from numpy import fft
from numba import jit
from scipy import signal


@jit(parallel=True)
def computeFourrierTransformCol(x, N):
    # x_freqdom = fft.fft(x)
    # return abs(x_freqdom), np.angle(x_freqdom)
    freq, dsp = signal.periodogram(x, nfft=N)
    return freq[-1], np.average(dsp)


@jit(parallel=True)
def computeFourrierTransformLine(x):
    # t = np.arange(0, N)
    # p = np.polyfit(t, x, 1)  # find linear trend in x
    # x_notrend = x - p[0] * t  # detrended x
    # x_freqdom = fft.fft(x_notrend)
    x_freqdom = fft.fft(x)
    return abs(x_freqdom), np.angle(x_freqdom)


class FourierFeaturesCol:
    def __init__(self, fft_period=21):
        self.fft_period = fft_period

    @jit
    def fourierDecomposition(self, X):
        T, N = X.shape
        predictors = np.array([])
        for me_col in range(N):
            x = X[:, me_col]
            max_freq, avg_dsp = computeFourrierTransformCol(x, T)
            predictors = np.append(predictors, np.hstack([max_freq, avg_dsp]))
        assert len(predictors) == N * 2
        return predictors

    @jit
    def featuresCreation(self, X, display_threshold=0.99):
        X_nd = X.values
        T, N = X_nd.shape
        new_features_length = N * 2
        X_final = np.empty((T, new_features_length))
        X_final[:] = np.nan
        for t in range(self.fft_period, T):
            if np.random.rand() >= display_threshold:
                print(str(t) + ' over ' + str(T))
            X_final[t, :] = self.fourierDecomposition(X_nd[t - self.fft_period:t, :])
        fft_features = pd.DataFrame(data=X_final, index=X.index,
                                    columns=['fff_' + str(i) for i in range(new_features_length)])

        return fft_features


class FourierFeaturesLine:
    def __init__(self):
        self.fft_features = pd.DataFrame()

    @jit
    def featuresCreation(self, X, display_threshold=0.99):
        col_names = list(X)
        amp_col_names = ['amp_lin_' + col for col in col_names]
        phase_col_names = ['phase_lin_' + col for col in col_names]
        new_col_names = amp_col_names + phase_col_names
        X_nd = X.values
        # T, N = X_nd.shape
        T = len(X_nd)
        N = len(X_nd[0])
        X_fft_col = np.zeros((T, 2 * N))
        for me_row in range(T):
            if np.random.rand() >= display_threshold:
                print(str(me_row) + ' over ' + str(T))
            x = X_nd[me_row, :]
            # t = np.arange(0, N)
            # p = np.polyfit(t, x, 1)  # find linear trend in x
            # x_notrend = x - p[0] * t  # detrended x
            # x_freqdom = fft.fft(x_notrend)
            # X_fft_col[me_row,:] = np.concatenate((abs(x_freqdom), np.angle(x_freqdom)))
            X_fft_col[me_row, :] = np.concatenate(computeFourrierTransformLine(x))
        return pd.DataFrame(data=X_fft_col, index=X.index, columns=new_col_names)