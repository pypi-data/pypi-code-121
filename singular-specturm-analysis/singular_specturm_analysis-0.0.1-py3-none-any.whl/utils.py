import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from scipy.signal import periodogram
import multiprocessing
import time
import sys


def check_groups_strategy(groups_strategy, num):
    #! 检查分组策略是否基本正确
    s = []
    for g in groups_strategy:
        s += g
    if len(s) == num:
        return True
    else:
        False


#!--------------------------------------------------------------------------------------  embedding
def embedding(x, L, stride, tao):
    '''
    :param x: 时间序列
    :param L:
    :param stride:
    :param tao:
    :return: 时间序列长度，轨迹点个数，轨迹点维度，相空间（轨迹矩阵），相空间索引（用于重构时间序列）
    '''
    L_span = (L - 1) * (tao - 1) + L
    if len(x) < L_span:
        assert "The length of time series is too short to embedding."
    length = len(x)
    x_index = np.arange(0, len(x), 1)
    cols, rows = (len(x) - L_span) // stride + 1, L
    K = cols
    dim = rows
    phase_space = np.zeros((rows, cols))
    phase_space_index = np.zeros_like(phase_space)
    for r in range(cols):
        index = [i for i in range(r * stride, r * stride + L_span, tao)]
        phase_space[:, r] = x[index]
        phase_space_index[:, r] = x_index[index]
    return length, K, dim, phase_space, phase_space_index


#!--------------------------------------------------------------------------------
def convert_array_to_series(array, length, array_index):
    '''
    :param array: 轨迹矩阵或者相空间矩阵
    :param length: 原时间序列长度
    :param array_index: 轨迹矩阵对应的下标，用于重构时间序列
    :return:
    '''
    # * 将矩阵转换回时间序列
    series = np.zeros((length,))
    for i in range(length):
        index = np.where(array_index == i)
        if len(index[0]) == 0:
            print("Warning! some values were left when embedding")
            series[i] = 0
        else:
            series[i] = np.mean(array[index])
    return series


def diagnal_average(array):
    '''
    :param array: 轨迹矩阵
    :return: 反对角线平均
    '''
    if len(array.shape) != 2:
        assert "Input array is not a matrix."
    L, K = array.shape
    y = np.zeros((K+L-1, ))
    array_flip = np.fliplr(array)
    for i in range(K+L-1):
        y[i] = np.mean(np.diag(array_flip, k=K-1-i))
    return y

#!--------------------------------------------------------------------------------周期图
def periodogram(x, verify=False):
    N = len(x)
    N = N if N%2 == 0 else N + 1
    fourier = np.abs(np.fft.fft(x, n=N))
    p = fourier[0:N//2+1]
    p[1:N//2] = np.sqrt((p[1:N//2]**2 + fourier[N//2+1:][::-1]**2))
    if verify:
        time_energy = np.linalg.norm(x, ord=2) ** 2 / len(x)
        freq_energy = np.sum((p / np.sqrt(N*len(x)))**2)
        if np.abs(time_energy - freq_energy) <= 1e-10:
            print("Satisfy Parseval Principle.")
        else:
            print("Warning: Do Not Satisfy Parseval Principle.")
    return (p / np.sqrt(N*len(x)))**2       #! 为了与公式2.11保持一致



#!--------------------------------------------------------------------------------------
def convert_labels_to_groupstrategy(labels):
    label = np.unique(labels)
    groupstrategy = []
    for i in label:
        index = np.where(labels==i)[0]
        groupstrategy.append(list(index))
    return groupstrategy


#!-------------------------------------------------------------------------------------- 频率估计
def polar_angle(v1, v2):
    #! 二维坐标下的极角，v1为横坐标，v2为纵坐标，两个都是列向量
    angle = np.zeros((v1.shape[0]))
    for i in range(v1.shape[0]):
        angle[i] = np.arccos(v1[i] / np.linalg.norm([v1[i], v2[i]], ord=2))
        if v2[i] < 0:
            angle[i] = 2*np.pi - angle[i]
    return angle


def freq_estimation(v1, v2):
    #!  v1, v2为两个特征向量，都是列向量
    angle = polar_angle(v1, v2)
    if np.pi > (angle[0] - angle[1]) > 0:       # 顺时针旋转
        delta_angle = angle[0:-1] - angle[1:]  # 由于旋转方向不一定是逆时针，因此需要特殊处理
    else:                       # 逆时针旋转
        delta_angle = angle[1:] - angle[0:-1]  # 由于旋转方向不一定是逆时针，因此需要特殊处理
    index = np.where(delta_angle < 0)[0]            # 由于角度会出现7-337的情况，需要进行处理
    delta_angle[index] += 2*np.pi
    return np.mean(delta_angle) / (2*np.pi)         #* 注意估计结果是数字频率，需要乘上采样频率才是最终的估计频率
#!--------------------------------------------------------------------------------------


#!-------------------------------------------------------------------------------------- 计算相关图
def inner_product(weights, x1, x2):
        #* 计算两个信号的内积
        #* x1,x2为一维矩阵
        if len(x1) != len(weights):
            assert "The length of x1 do not consist with original length."
        if len(x2) != len(weights):
            assert "The length of x2 do not consist with original length."
        product = weights * x1 * x2
        return np.sum(product)


def w_correlation(weights, x1, x2):
    return inner_product(weights, x1, x2) / (np.sqrt(inner_product(weights, x1, x1)) * np.sqrt(inner_product(weights, x2, x2)))


def w_correlation_matrix(weights, series_array):
    n_series, dim = series_array.shape
    if dim != len(weights):
        assert "The length of series do not consist with original length."
    w_matrix = np.zeros((n_series, n_series))
    for i in range(n_series):
        for j in range(i, n_series):
            w_matrix[i,j] = w_correlation(weights, series_array[i], series_array[j])
            w_matrix[j,i] = w_matrix[i,j]
    return w_matrix
#!--------------------------------------------------------------------------------------


def spectral_energy(x, w0, w1):
    '''
    :param x: 时间序列
    :param [w0, w1]: 频率范围，这是都是数字频率
    :return:
    '''
    if w0 > 0.5 or w1 > 0.5:
        assert "Freq beyond the scope of periodogram"
    periodogram_x = periodogram(x)
    M = len(x)
    w0 = int(w0 / 0.5 * (M // 2))
    w1 = int(w1 / 0.5 * (M // 2))
    return M * np.sum(periodogram_x[w0:w1+1]) / (np.linalg.norm(x, ord=2)**2)


def harmonics_energy(V1, V2):
    '''
    :param v1,v2: 两个特征向量，都是一维向量
    :param thres: 门限
    :return:
    '''
    v1 = V1
    v2 = V2
    periodogram_v1 = periodogram(v1)
    periodogram_v2 = periodogram(v2)
    gamma = 0.5 * (len(v1) * periodogram_v1 / (np.linalg.norm(v1, ord=2)**2) + \
                   len(v2) * periodogram_v2 / (np.linalg.norm(v2, ord=2)**2))
    rho = np.max(gamma)
    return rho


def recurrent_forcast(x, eigenvectors, m):
    '''
    :param x: 时间序列
    :param eigenvectors: 特征矩阵；每一列为一个特征向量
    :param m: 要预测的点数
    :return:
    '''
    if len(eigenvectors.shape) != 2:
        assert "Input eigenvectors is not a matrix."
    if len(x) < eigenvectors.shape[0]-1:
        assert "Input series is too short to make prediction."
    M = m
    L = eigenvectors.shape[0]
    n = L-1
    x = x[len(x)-n:]
    pi = eigenvectors[-1, :]
    v2 = np.sum(pi**2)
    R = np.sum(pi * eigenvectors[0:-1, :], axis=1).reshape([-1, 1]) / (1 - v2)      # 列向量
    predictions = np.zeros((L+M-1))
    predictions[0:L-1] = np.array(x)
    for i in range(M):
        predict = predictions[i:i+L-1].reshape([1, -1]) @ R
        predictions[L-1+i] = predict[0][0]
    return np.array(predictions[n:])


def vector_predict(array, eigenvectors, m):
    '''
    :param array: 分组后的矩阵项
    :param eigenvectors: 特征矩阵；每一列为一个特征向量
    :param m: 要预测的点数
    :return:
    '''
    if len(eigenvectors.shape) != 2:
        assert "Input eigenvectors is not a matrix."
    if len(array) != 2:
        assert "Input array is not a matrix."
    pi = eigenvectors[-1, :]
    v2 = np.sum(pi ** 2)
    R = np.sum(pi * eigenvectors[0:-1, :], axis=1).reshape([-1, 1]) / (1 - v2)  # 列向量
    V = eigenvectors[0:-1, :]
    PI = V @ V.T + (1 - v2) * R @ R.T
    M = m
    L, K = array.shape
    Z = np.zeros((L, K+M+L-1))
    Z[:, 0:K] = array
    for i in range(K, K+M+L-1):
        Z[:, i:i+1] = np.concatenate([PI @ Z[1:, i-1:i], R.T @ Z[1:, i-1:i]], axis=0)
    y = diagnal_average(Z)
    return y[K+L-1:M+K+L-1]



###############* plot
class ScrollableWindow(QtWidgets.QWidget):
    stop_analyz_signal = QtCore.pyqtSignal()

    def __init__(self, fig):
        app = QtWidgets.QApplication([])
        QtWidgets.QWidget.__init__(self)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidget(self.canvas)
        self.nav = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.nav)
        self.layout().addWidget(self.scroll)
        self.show()
        app.exec()


def plot_series(x, series, xticks=None, path=None, title=None):
    plt.figure()
    ax=plt.gca()
    plt.plot(x)
    plt.plot(series)
    if title:
        plt.legend([title])
    if xticks:
        ax.xaxis.set_major_locator(MultipleLocator(10))
        plt.tick_params(labelsize=5)
        plt.xticks(rotation=90)
    if path:
        plt.savefig(path)
    plt.show()



def plot_series_array(x, series_array, path=None, mode='default'):
    fig, axes = plt.subplots(ncols=1, nrows=series_array.shape[0], figsize=(8, 2*series_array.shape[0]))
    for i, ax in enumerate(axes.flatten()):
        if i==0: ax.plot(x)
        ax.plot(series_array[i])
        ax.set_title(str(i))
    fig.tight_layout()
    if mode == "qt":
        window = ScrollableWindow(fig)
    else:
        plt.show()
        plt.figure()
        plt.plot(x)
        for s in series_array:
            plt.plot(s)
        plt.legend(["origin series"])
        plt.show()


def plot_wmatrix(w_matrix):
    plt.figure()
    ax = plt.gca()
    im = ax.matshow(w_matrix, cmap=plt.cm.Blues)     # 画混淆矩阵，配色风格使用cm.Blues
    plt.colorbar(im, fraction=0.03, pad=0.05)
    plt.tight_layout()
    plt.show()


def plot_scatter_eigenvector(model, index):
    if index is None:
        N = model.eigenvector_left.shape[1]
    else:
        N = len(index)
    fig, axes = plt.subplots(ncols=4, nrows=int(np.ceil(N / 4)), dpi=150)
    for i, ax in enumerate(axes.flatten()):
        if i == N-2:
            break
        ax.plot(model.eigenvector_left[:, index[i]], model.eigenvector_left[:, index[i+1]])
        ax.set_title("%d(%.3f%%)-%d(%.3f%%)" % (i, model.components_contrib[i]/100, i+1, model.components_contrib[i+1]/100), fontsize=5)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    plt.show()

