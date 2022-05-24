import numpy as np
from model.utils import *
from sklearn.cluster import affinity_propagation, spectral_clustering, AgglomerativeClustering


class SSA:
    def __init__(self, L, stride=1, tao=1):
        #* L：相空间的维度
        #* stride：窗口移动步长
        #* tao：延时长度
        #* 默认stride=1, tao=1，相空间为轨迹矩阵
        self.L, self.stride, self.tao = L, stride, tao
        self.dim = 0                #! 相空间维度
        self.K = 0                  #! 延时向量的个数
        self.length = 0             #! 时间序列长度
        self.phase_space = np.array([]) 
        self.phase_space_index = np.array([])           #! 用于记录时间序列下标的位置，用于将矩阵转换回时间序列
        self.components_array = np.array([])            #! 存放矩阵分量
        self.components_series = np.array([])           #! 存放序列分量
        self.components_contrib = np.array([])          #! 存放矩阵分量在原始时间序列中所占的比重
        self.components_array_grouped = np.array([])           #! 分组结果
        self.components_series_grouped = np.array([])           #! 存放序列分量
        self.groups_strategy = []                       #! 存放分组策略
        self.weights = 0                                #! 用于计算w-correlation的权重
        self.w_matrix = 0                               #! w-相关矩阵
        self.periodogram = np.array([])


    def embedding(self, x):
        #! 构造相空间，特殊情况为轨迹矩阵
        self.length, self.K, self.dim, self.phase_space, self.phase_space_index = embedding(x, self.L, self.stride, self.tao)
        print("\033[1;31m 相空间维度：\033[0m", self.dim)
        print("\033[1;31m 相空间轨迹点个数：\033[0m", self.K)
        #! 初始化用于计算w-相关的权重
        self.weights = np.arange(1, self.length+1, 1)
        l = min(self.dim, self.K)
        k = max(self.dim, self.K)
        self.weights[l:k+1] = l
        self.weights[k+1:] = np.arange(self.length-k-1, 0, -1)
        #! 求解周期图
        self.periodogram = periodogram(x)



    def decomposition(self):
        #* 对相空间矩阵进行SVD分解并获取子成份
        if len(self.phase_space) == 0:
            assert "Please take embedding first."
        S = self.phase_space @ self.phase_space.T
        Lambda, U = np.linalg.eig(S)
        #! 排序
        sorted_index = np.argsort(Lambda)[::-1]
        Lambda = Lambda[sorted_index]
        U = U[:, sorted_index]          #* 矩阵的列表示特征向量
        #!
        V = self.phase_space.T @ U / np.sqrt(Lambda)
        self.eigenvalue = Lambda
        self.eigenvector_left = U
        self.eigenvector_right = V      
        self.components_array = np.zeros((len(Lambda), self.L, self.K))
        self.components_contrib = np.zeros((len(Lambda), ))
        self.rank = np.linalg.matrix_rank(self.phase_space)
        print("\033[1;31m 轨迹矩阵的秩：\033[0m", self.rank)
        #* 重构
        sum_of_eigenvalue = np.linalg.norm(self.phase_space, ord='fro')
        for i in range(len(Lambda)):
            self.components_array[i] = np.sqrt(Lambda[i]) * (U[0:,i:i+1] @ V[0:, i:i+1].T)
            self.components_contrib[i] = np.linalg.norm(self.components_array[i], ord='fro') ** 2 / sum_of_eigenvalue

    
    def decomposition_safe(self):
        #! 相比于普通的def decomposition，该函数首先计算秩，然后只保留秩以内数目的特征值和特征向量，避免复数参与运算。
        #! 该函数不会有警告，但是如果处理的序列本身就是复数序列，请不要使用该函数。
        #* 对相空间矩阵进行SVD分解并获取子成份
        if len(self.phase_space) == 0:
            assert "Please take embedding first."
        S = self.phase_space @ self.phase_space.T
        Lambda, U = np.linalg.eig(S)
        Lambda, U = np.real(Lambda), np.real(U)     #! 只保留实部
        #! 计算秩
        self.rank = np.linalg.matrix_rank(self.phase_space)
        print("\033[1;31m 轨迹矩阵的秩：\033[0m", self.rank)
        #! 排序
        sorted_index = np.argsort(Lambda)[::-1]
        Lambda = Lambda[sorted_index]
        U = U[:, sorted_index]          #* 矩阵的列表示特征向量
        #!
        Lambda = Lambda[0:self.rank]
        U = U[:, 0:self.rank]
        #!
        V = self.phase_space.T @ U / np.sqrt(Lambda)
        self.eigenvalue = Lambda
        self.eigenvector_left = U
        self.eigenvector_right = V      
        self.components_array = np.zeros((len(Lambda), self.L, self.K))
        self.components_contrib = np.zeros((len(Lambda), ))
        #* 重构
        sum_of_eigenvalue = np.linalg.norm(self.phase_space, ord='fro')
        for i in range(self.rank):
            self.components_array[i] = np.sqrt(Lambda[i]) * (U[0:,i:i+1] @ V[0:, i:i+1].T)
            self.components_contrib[i] = np.linalg.norm(self.components_array[i], ord='fro') ** 2 / sum_of_eigenvalue


    def grouping(self, option='default', params=None):
        #* 对分解结果进行分组
        if option == "default":
            self.groups_strategy = [[i] for i in range(len(self.components_array))]
        else:
            self.w_matrix = w_correlation_matrix(self.weights, self.components_series)  # ! 计算w相关矩阵
            if params is None:
                n_clusters = 3
            else:
                n_clusters = params["n_clusters"]
            if option == "AP":
                cluster_centers_indices, labels, n_ite = affinity_propagation(1 - self.w_matrix, copy=True, damping=0.5,
                                                                              preference=None, return_n_iter=True)
                if n_ite >= 200:
                    assert "Affinity Ppropagation is something wrong."
            elif option == "SC":
                labels = spectral_clustering(self.w_matrix, n_clusters=n_clusters, assign_labels='discretize')
            elif option == "AC":
                labels = AgglomerativeClustering(n_clusters=n_clusters, linkage='complete', affinity='precomputed') \
                    .fit_predict(1 - self.w_matrix)
            self.groups_strategy = convert_labels_to_groupstrategy(labels)
        if not check_groups_strategy(self.groups_strategy, self.L):
            assert "Grouping strategies are wrong."

        #! 分组以后把信号分量相加
        self.components_array_grouped = np.zeros((len(self.groups_strategy), self.dim, self.K))
        self.components_series_grouped = np.zeros((len(self.groups_strategy), self.length))
        for i in range(len(self.groups_strategy)):
            self.components_array_grouped[i] = np.sum(self.components_array[self.groups_strategy[i]], axis=0)
            self.components_series_grouped[i] = np.sum(self.components_series[self.groups_strategy[i]], axis=0)


    def reconstruction(self):
        #* 根据分组结果，经分组后的子成分还原回时间序列。
        self.components_series = np.zeros((len(self.eigenvalue), self.length))
        for i in range(len(self.eigenvalue)):
            if self.components_array[i].shape != self.phase_space_index.shape:
                assert "Something Wrong when embedding or decomposition."
            self.components_series[i] = convert_array_to_series(self.components_array[i], self.length, self.phase_space_index)          #! 从矩阵转换回时间序列


    def extract_trend(self, omega=1/24, thres=0.9):
        #* 提取趋势成分
        #! 这里的omega是数字频率
        trend_component_index = []
        for i in range(len(self.components_series)):
            se = spectral_energy(self.components_series[i], 0, omega)
            # print(se)
            if se >= thres:
                trend_component_index.append(i)
        trend_component = np.sum(self.components_series[trend_component_index], axis=0)
        return trend_component_index, trend_component


    def extract_harmonics(self, thres=0.9):
        #! 这个函数对于窗口长度十分敏感，如果窗口长度不是周期的整倍数，很难提取出正确的周期分量
        harmonics_component_index = []
        harmonics_component = []
        for i in range(self.eigenvector_left.shape[1]-1):
            v1 = self.eigenvector_left[:, i]
            v2 = self.eigenvector_left[:, i+1]
            rho = harmonics_energy(v1, v2)
            if rho > thres:
                harmonics_component_index.append(i)
                harmonics_component.append(self.components_series[i] + self.components_series[i+1])
        return harmonics_component_index, np.array(harmonics_component)


    def predict(self, m, grouped=True, method='r'):
        '''
        :param m: 要预测的点数
        :param grouped: 是否对分组后的分量进行预测，或者是直接对原时间序列进行预测
        :param method: 有'r'和'v'两种选项；'r'表示循环预测方法，'v'表示向量预测方法
        :return: 如果grouped==True，就返回每个分量的预测结果；如果为False，就直接返回预测结果。
        '''
        if grouped:
            predictions = np.zeros((len(self.groups_strategy), m))
            if method == 'r':
                for i in range(len(self.groups_strategy)):
                    predictions[i] = recurrent_forcast(self.components_series_grouped[i],
                                                       self.eigenvector_left[:, self.groups_strategy[i]],
                                                       m)
            elif method == 'v':
                for i in range(len(self.groups_strategy)):
                    predictions[i] = vector_predict(self.components_array_grouped[i],
                                                    self.eigenvector_left[:, self.groups_strategy[i]],
                                                    m)
            else:
                assert "Argument: method is not included."

        else:
            if method == 'r':
                predictions = recurrent_forcast(np.sum(self.components_series, axis=0),
                                                self.eigenvector_left,
                                                m)
            elif method == 'v':
                predictions = vector_predict(self.phase_space,
                                             self.eigenvector_left,
                                             m)
            else:
                assert "Argument: method is not included."
        return predictions

