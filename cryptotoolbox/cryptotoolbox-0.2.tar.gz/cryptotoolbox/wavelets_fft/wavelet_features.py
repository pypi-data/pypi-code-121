import pandas as pd
import numpy as np
import pywt
from numba import njit, jit
from numba.typed import List

@njit()
def signe(a):
    if a>=0:
        return 1
    else:
        return -1
@njit
def upArrow_op(li:List, j:int):
    if j == 0:
        return np.array([np.float64(1)])
    N = len(li)
    li_n = np.zeros(2 ** (j - 1) * (N - 1) + 1)
    for i in range(N):
        li_n[2 ** (j - 1) * i] = li[i]
    return li_n

@njit
def period_list(li:np.ndarray, N:int):
    n = len(li)
    # append [0 0 ...]
    n_app = N - np.mod(n, N)
    li = np.hstack((li, np.zeros(n_app)))
    if len(li) < 2 * N:
        return li
    else:
        l2 = np.reshape(li, (-1, N))
        l3 = np.sum(l2, axis=0)
        return l3
@njit
def circular_convolve_mra(h_j_o:np.ndarray, w_j:np.ndarray):
    ''' calculate the mra D_j'''
    N = len(w_j)
    l = np.arange(N)
    D_j = np.zeros(N)
    for t in range(N):
        index = np.mod(t + l, N)
        w_j_p = np.array([w_j[ind] for ind in index])
        D_j[t] = (h_j_o * w_j_p).sum()
    return D_j

@njit
def circular_convolve_d(h_t:np.ndarray, v_j_1:np.ndarray, j:int):
    N = len(v_j_1)
    L = len(h_t)
    w_j = np.zeros(N)
    l = np.arange(L)
    for t in range(N):
        index = np.mod(t - 2 ** (j - 1) * l, N)
        v_p = np.array([v_j_1[ind] for ind in index])
        w_j[t] = (h_t * v_p).sum()
    return w_j

@njit
def circular_convolve_s(h_t, g_t, w_j, v_j, j):
    '''
    (j-1)th level synthesis from w_j, w_j
    see function circular_convolve_d
    '''
    N = len(v_j)
    L = len(h_t)
    v_j_1 = np.zeros(N)
    l = np.arange(L)
    for t in range(N):
        index = np.mod(t + 2 ** (j - 1) * l, N)
        w_p = np.array([w_j[ind] for ind in index])
        v_p = np.array([v_j[ind] for ind in index])
        v_j_1[t] = (h_t * w_p).sum()
        v_j_1[t] = v_j_1[t] + (g_t * v_p).sum()
    return v_j_1

#@jit(parallel=True)
def wavelet_filters_coeffs(filters:str):
    coeffs = pywt.Wavelet(filters)
    return coeffs

#@jit(parallel=True)
def modwt(x, filters:str, level:int):
    filters_coeffs = wavelet_filters_coeffs(filters)
    untyped_h = filters_coeffs.dec_hi
    untyped_g = filters_coeffs.dec_lo
    # untyped_h = [-1 / np.sqrt(2), 1 / np.sqrt(2)]
    # untyped_g = [1 / np.sqrt(2), 1 / np.sqrt(2)]
    g, h = List(), List()
    [g.append(x) for x in untyped_g]
    [h.append(x) for x in untyped_h]
    h_t = np.array(list(h)) / np.sqrt(2)
    g_t = np.array(list(g)) / np.sqrt(2)
    wavecoeff = []
    v_j_1 = x.astype(np.float64)
    for j in range(level):
        w = circular_convolve_d(h_t, v_j_1, j + 1)
        v_j_1 = circular_convolve_d(g_t, v_j_1, j + 1)
        wavecoeff.append(w)
    wavecoeff.append(v_j_1)
    n = len(wavecoeff)
    m = len(wavecoeff[0])
    # output = np.array([[0 for i in range(m)] for j in range(n)])
    # for i in range(n):
    #     output[i] = wavecoeff[i]
    #     print(output[i], wavecoeff[i])
    # return output
    return np.array(wavecoeff)

# @jit(parallel=True)
def imodwt(w, filters):
    ''' inverse modwt '''

    filters_coeffs = wavelet_filters_coeffs(filters)
    untyped_h = filters_coeffs.dec_hi
    untyped_g = filters_coeffs.dec_lo
    # untyped_h = [-1 / np.sqrt(2), 1 / np.sqrt(2)]
    # untyped_g = [1 / np.sqrt(2), 1 / np.sqrt(2)]
    g, h = List(), List()
    [g.append(x) for x in untyped_g]
    [h.append(x) for x in untyped_h]
    h_t = np.array(h) / np.sqrt(2)
    g_t = np.array(g) / np.sqrt(2)
    level = len(w) - 1
    v_j = w[-1]
    for jp in range(level):
        j = level - jp - 1
        v_j = circular_convolve_s(h_t, g_t, w[j], v_j, j + 1)
    return v_j

#@jit(parallel=True)
def modwtmra(w:np.ndarray, filters:str):
    filters_coeffs = wavelet_filters_coeffs(filters)
    untyped_h = filters_coeffs.dec_hi
    untyped_g = filters_coeffs.dec_lo
    #untyped_h = [-1 / np.sqrt(2), 1 / np.sqrt(2)]
    #untyped_g = [1 / np.sqrt(2), 1 / np.sqrt(2)]
    g, h = List(), List()
    [g.append(x) for x in untyped_g]
    [h.append(x) for x in untyped_h]
    # D
    level, N = w.shape
    level = level - 1
    D = []
    g_j_part = np.array([1]).astype(np.float64)
    for j in range(level):
        # g_j_part
        g_j_up = upArrow_op(g, j)
        g_j_part = np.convolve(g_j_part, g_j_up)
        # h_j_o
        h_j_up = upArrow_op(h, j + 1)
        h_j = np.convolve(g_j_part, h_j_up)
        h_j_t = h_j / (2 ** ((j + 1) / 2.))
        #if j == 0: h_j_t = h / np.sqrt(2)
        if j == 0:
            h_j_t = np.array(list(h)) / np.sqrt(2)
        h_j_t_o = period_list(h_j_t, N)
        D.append(circular_convolve_mra(h_j_t_o, w[j]))
    # S
    j = level - 1
    g_j_up = upArrow_op(g, j + 1)
    g_j = np.convolve(g_j_part, g_j_up)
    g_j_t = g_j / (2 ** ((j + 1) / 2.))
    g_j_t_o = period_list(g_j_t, N)
    S = circular_convolve_mra(g_j_t_o, w[-1])
    D.append(S)
    n = len(D)
    m = len(D[0])
    # output = np.array([[0 for i in range(m)] for j in range(n)])
    # for i in range(n):
    #     output[i] = D[i]
    # return output #np.vstack(D)
    return np.array(D)

class WaveletFeaturesCol:
    def __init__(self, wavelet_filter='haar', dec_level=1, wavelet_look_back=14, details=False):
        self.wavelet_features = pd.DataFrame()
        self.wavelet_filter = wavelet_filter
        self.dec_level = dec_level
        self.wavelet_look_back = wavelet_look_back
        self.details =details


    def waveletDecomposition(self, s):
        wt = modwt(s, self.wavelet_filter, self.dec_level)
        wtmra = modwtmra(wt, self.wavelet_filter)
        if self.details:
            return np.array([np.average(i) for i in wtmra])
        else:
            return np.average(wtmra[-1])

    def rowFeatures(self, X):
        T, N = X.shape
        predictors = np.array([])
        for me_col in range(N):
            col_components = self.waveletDecomposition(X[:, me_col])
            predictors = np.append(predictors, col_components.flatten())
        return predictors


    def assembleFeatures(self, X, display_threshold=0.99):
        X_nd = X.values
        T, N = X_nd.shape
        if self.details:
            new_features_number = N * (self.dec_level + 1)
        else:
            new_features_number = N
        X_wv_col = np.empty((T, new_features_number))
        X_wv_col[:] = np.nan

        for t in range(self.wavelet_look_back, T):
            if np.random.rand() >= display_threshold:
                print(str(t) + ' over ' + str(T))
            X_wv_col[t, :] = self.rowFeatures(X_nd[t - self.wavelet_look_back:t, :])
        output = pd.DataFrame(data=X_wv_col, index=X.index,
                            columns=['wv_' + str(ii) for ii in range(new_features_number)])
        return output


class WaveletFeaturesLine:

    def __init__(self, wavelet_filter='haar', dec_level = 1, details = False):
        self.wavelet_features = pd.DataFrame()
        self.wavelet_filter = wavelet_filter
        self.dec_level = dec_level
        self.details = details

    def createColname(self, X):
        component_name = []
        new_col_names = []
        if self.details:
            for i in range(self.dec_level):
                component_name.append('det_' + str(i + 1))
        component_name.append('approx')
        col_names = list(X)
        for comp_name in component_name:
            for col in col_names:
                new_col_names.append(comp_name + '_' + col)
        return new_col_names


    def multi_wavelet_decomposition(self, X:pd.DataFrame, display_threshold:float = 0.99):
        """ X : DataFrame """
        new_col_names = self.createColname(X)
        X_nd = X.values
        T,N = X_nd.shape
        if self.details:
            new_length = N * (self.dec_level + 1)
        else:
            new_length = N
        X_wv_row = np.zeros((T,new_length))
        for me_row in range(T):
            if np.random.rand()>display_threshold:
                print(str(me_row)+' over '+str(T))
            s = X_nd[me_row, :]
            wt = modwt(s, self.wavelet_filter, self.dec_level)
            wtmra = modwtmra(wt, self.wavelet_filter)
            if self.details:
                X_wv_row[me_row,:]=wtmra.flatten()
            else:
                X_wv_row[me_row, :] = wtmra[-1].flatten()
        return pd.DataFrame(data = X_wv_row, index = X.index, columns=new_col_names)

class WaveletsFeaturesOrtho:

    def __init__(self, wavelet_filter='haar', dec_level=4, wavelet_look_back=100, coeff_index_factor=21):
        self.wavelet_features = pd.DataFrame()
        self.wavelet_filter = wavelet_filter
        self.dec_level = dec_level
        self.wavelet_look_back = wavelet_look_back
        self.coeff_index_factor = coeff_index_factor

    def select_orthogonal_coef(self, wtmra):
        J = self.dec_level
        components = wtmra.copy()
        selected_coeffs = []
        for j in range(len(components)):
            current_array = np.zeros(components[j].shape)

            if j == len(components) - 1:  # Case of the approximation
                for k in range(self.coeff_index_factor):  # range(2):
                    a = len(wtmra[0]) - 2 ** (j) * (k)
                    if -1 * (len(wtmra[0]) + 1) <= a <= len(wtmra[0]):
                        current_array[a - signe(a)] = 1
                        selected_coeffs.append(components[j][a - signe(a)])
            else:
                for k in range(self.coeff_index_factor):  # range(2**(J-(j+1))+1):
                    a = len(wtmra[0]) - 2 ** (j + 1) * (k)
                    if -1 * (len(wtmra[0]) + 1) <= a <= len(wtmra[0]):
                        current_array[a - signe(a)] = 1
                        selected_coeffs.append(components[j][a - signe(a)])

            components[j] = components[j] * current_array
        return np.array(selected_coeffs).reshape(1, len(selected_coeffs))

    def create_orthogonal_features(self, X):
        X_nd = X['close'].values
        T = X_nd.shape[0]
        wt = modwt(X_nd[:self.wavelet_look_back], self.wavelet_filter, self.dec_level)
        wtmra = modwtmra(wt, self.wavelet_filter)
        new_features_number = self.select_orthogonal_coef(wtmra).shape[1]
        X_wv_ortho = np.empty((T, new_features_number))
        for t in range(self.wavelet_look_back, T):
            wt = modwt(X_nd[t - self.wavelet_look_back:t], self.wavelet_filter, self.dec_level)
            wtmra = modwtmra(wt, self.wavelet_filter)
            X_wv_ortho[t, :] = self.select_orthogonal_coef(wtmra)
        output = pd.DataFrame(data=X_wv_ortho, index=X.index,
                              columns=['wv_' + str(ii) for ii in range(new_features_number)])
        return output


# class WaveletFeaturesRecurrent:
#     def __init__(self, wavelet_filter='haar', dec_level=1, wavelet_look_back=14):
#         self.wavelet_features = pd.DataFrame()
#         self.wavelet_filter = wavelet_filter
#         self.dec_level = dec_level
#         self.wavelet_look_back = wavelet_look_back
#
#     def toWavelet(self, s):
#         wt = modwt(s, self.wavelet_filter, self.dec_level)
#         wtmra = modwtmra(wt, self.wavelet_filter)
#         return wtmra
#
#     def assembleFeatures(self, X, display_threshold=0.99):
#         """ 1 column pandas dataframe"""
#         X_nd = X.values
#         T = X_nd.size
#         X_wv_comp = []
#
#         for i in range(self.dec_level + 1):
#             X_wv_comp.append(np.empty((T, self.wavelet_look_back)))
#         for t in range(self.wavelet_look_back, T):
#             if np.random.rand() > display_threshold:
#                 print(str(t) + ' over ' + str(T))
#             res = self.toWavelet(X_nd[t - self.wavelet_look_back:t])
#             for k in range(len(res)):
#                 X_wv_comp[k][t] = res[k]
#
#         output = []
#         for i in range(self.dec_level):
#             detail = pd.DataFrame(data=X_wv_comp[i], index=X.index,
#                                   columns=['det_' + str(i + 1) + '_' + str(j) for j in range(self.wavelet_look_back)])
#             output.append(detail)
#         approx = pd.DataFrame(data=X_wv_comp[-1], index=X.index,
#                               columns=['approx_' + str(self.dec_level + 1) + '_' + str(j) for j in
#                                        range(self.wavelet_look_back)])
#         output.append(approx)
#         return output