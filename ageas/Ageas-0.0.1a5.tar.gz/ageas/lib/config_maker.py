#!/usr/bin/env python3
"""
This file contains classes to build model config file

author: jy, nkmtmsys
"""


import itertools
import ageas.lib as lib
from collections import deque
import ageas.tool.json as json


# Paternize default list_config
def List_Config_Reader(path):
    config_list = json.decode(path)
    result = {}
    if 'Transformer' in config_list:
        result['Transformer'] = Pytorch_Transformer(
                                    header = 'pytorch_transformer_',
                                    config = config_list['Transformer']).configs
    if 'CNN_1D' in config_list:
        result['CNN_1D'] = Pytorch_CNN_1D(
                                    header = 'pytorch_cnn_1d_',
                                    config = config_list['CNN_1D']).configs
    if 'CNN_Hybrid' in config_list:
        result['CNN_Hybrid'] = Pytorch_CNN_Hybrid(
                                    header = 'pytorch_cnn_hybrid_',
                                    config = config_list['CNN_Hybrid']).configs
    if 'RNN' in config_list:
        result['RNN'] = Pytorch_RNN(header = 'pytorch_rnn_',
                                    config = config_list['RNN']).configs
    if 'GRU' in config_list:
        result['GRU'] = Pytorch_GRU(header = 'pytorch_gru_',
                                    config = config_list['GRU']).configs
    if 'LSTM' in config_list:
        result['LSTM'] = Pytorch_LSTM(header = 'pytorch_lstm_',
                                    config = config_list['LSTM']).configs
    if 'SVM' in config_list:
        result['SVM'] = Sklearn_SVM(header = 'pytorch_svc_',
                                    config = config_list['SVM']).configs
    if 'RFC' in config_list:
        result['RFC'] = Sklearn_RFC(header = 'pytorch_rfc_',
                                    config = config_list['RFC']).configs
    if 'GNB' in config_list:
        result['GNB'] = Sklearn_GNB(header = 'pytorch_gnb_',
                                    config = config_list['GNB']).configs
    if 'Logit' in config_list:
        result['Logit'] = Sklearn_Logit(header = 'pytorch_logit_',
                                    config = config_list['Logit']).configs
    if 'GBM' in config_list:
        result['GBM'] = XGBoost_GBM(header = 'xgboost_gbm_',
                                    config = config_list['GBM']).configs
    return result



class Sklearn_SVM(lib.Config_Maker_Template):
    """
    config maker for sklearn based SVMs
    """
    def __init__(self, header = None, config = None):
        self.header = header
        deq = deque()
        combs = list(itertools.product(*config.values()))
        for ele in combs:
            assert len(config.keys()) == len(ele)
            temp = {}
            for i in range(len(ele)):
                key = list(config.keys())[i]
                value = ele[i]
                temp[key] = value
            temp = self.__verify_config(temp)
            if temp is not None:
                record = {'config':temp}
                if record not in deq: deq.appendleft(record)
        self.configs = {self.header + str(i) : deq[i] for i in range(len(deq))}

    # verify a SVC config before adding it to set
    def __verify_config(self, query):
        if 'kernel' in query and query['kernel'] != 'poly':
            if 'degree' in query:
                query['degree'] = 0
        return query



class Sklearn_Logit(lib.Config_Maker_Template):
    """
    config maker for sklearn based Logistic Regressions
    Note:
    https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html?highlight=logistic%20regression#sklearn.linear_model.LogisticRegression
    """
    def __init__(self, header = None, config = None):
        self.header = header
        deq = deque()
        combs = list(itertools.product(*config.values()))
        for ele in combs:
            assert len(config.keys()) == len(ele)
            temp = {}
            for i in range(len(ele)):
                key = list(config.keys())[i]
                value = ele[i]
                temp[key] = value
            temp = self.__verify_config(temp)
            if temp is not None:
                record = {'config':temp}
                if record not in deq: deq.appendleft(record)
        self.configs = {self.header + str(i) : deq[i] for i in range(len(deq))}

    def __verify_config(self, query):
        if 'solver' in query and 'penalty' in query:
            if query['solver'] == 'newton-cg':
                if query['penalty'] != 'l2' and query['penalty'] != 'none':
                    return None
            elif query['solver'] == 'lbfgs':
                if query['penalty'] != 'l2' and query['penalty'] != 'none':
                    return None
            elif query['solver'] == 'liblinear':
                if query['penalty'] != 'l2' and query['penalty'] != 'l1':
                    return None
            elif query['solver'] == 'sag':
                if query['penalty'] != 'l2' and query['penalty'] != 'none':
                    return None
        return query



class Sklearn_GNB(lib.Config_Maker_Template):
    """
    config maker for sklearn based GNBs
    """
    def __init__(self, header = None, config = None):
        self.header = header
        deq = deque()
        combs = list(itertools.product(*config.values()))
        for ele in combs:
            assert len(config.keys()) == len(ele)
            temp = {}
            for i in range(len(ele)):
                key = list(config.keys())[i]
                value = ele[i]
                temp[key] = value
            if temp is not None:
                record = {'config':temp}
                if record not in deq: deq.appendleft(record)
        self.configs = {self.header + str(i) : deq[i] for i in range(len(deq))}



class Sklearn_RFC(Sklearn_GNB):
    """
    config maker for sklearn based RFs
    """
    def __verify_config(self, query):
        return query



class XGBoost_GBM(lib.Config_Maker_Template):
    """
    config maker for XGBoost based GBMs
    """
    def __init__(self, header = None, config = None):
        self.header = header
        deq = deque()
        combs = list(itertools.product(*config.values()))
        for ele in combs:
            assert len(config.keys()) == len(ele)
            temp = {}
            for i in range(len(ele)):
                key = list(config.keys())[i]
                value = ele[i]
                temp[key] = value
            temp = self.__verify_config(temp)
            if temp is not None:
                record = {'config':temp}
                if record not in deq: deq.appendleft(record)
        self.configs = {self.header + str(i) : deq[i] for i in range(len(deq))}

    # verify a GBM config before adding it to set
    def __verify_config(self, query):
        if 'objective' in query and query['objective'] == 'multi:softmax':
            query['num_class'] = 2
        return query



class Pytorch_CNN_Hybrid(lib.Config_Maker_Template):
    """
    config maker for Pytorch based Hybrid-CNN
    """
    def __init__(self, header = None, config = None):
        self.epoch = 1
        self.batch_size = None
        self.header = header
        config = self.__resize_config(config)
        self.configs = self.__get_configs(config)

    # Generate all possible hyperparameter combination
    # Check model config file for orders of parameters
    def __get_configs(self, config):
        deq = deque()
        combs = list(itertools.product(*config.values()))
        for ele in combs:
            assert len(config.keys()) == len(ele)
            temp = {}
            for i in range(len(ele)):
                key = list(config.keys())[i]
                value = ele[i]
                temp[key] = value
            temp = self.__verify_config(temp)
            if temp is not None:
                # add up epoch and batch_size
                for epoch in self.epoch:
                    for batch_size in self.batch_size:
                        record = {
                            'config':temp,
                            'epoch':epoch,
                            'batch_size':batch_size
                        }
                        if record not in deq: deq.appendleft(record)
        return {self.header + str(i) : deq[i] for i in range(len(deq))}

    # this should vary with different classes
    def __resize_config(self, query):
        try:
            self.epoch = query['epoch']
            self.batch_size = query['batch_size']
            del query['epoch']
            del query['batch_size']
        except Exception as CNN_Config_Maker_Error:
            raise
        return query

    # verify a hybrid CNN config before adding it to set
    def __verify_config(self, query):
        return query


class Pytorch_CNN_1D(Pytorch_CNN_Hybrid):
    """
    config maker for Pytorch based 1D-CNN
    """
    # verify a 1D CNN config before adding it to set
    def __verify_config(self, query):
        return query



class Pytorch_RNN(Pytorch_CNN_Hybrid):
    """
    config maker for Pytorch based RNN
    """
    def __verify_config(self, query):
        return query



class Pytorch_LSTM(Pytorch_CNN_Hybrid):
    """
    config maker for Pytorch based RNN
    """
    def __verify_config(self, query):
        return query


class Pytorch_GRU(Pytorch_CNN_Hybrid):
    """
    config maker for Pytorch based RNN
    """
    def __verify_config(self, query):
        return query



class Pytorch_Transformer(Pytorch_CNN_Hybrid):
    """
    config maker for Pytorch based Transformer
    """
    def __verify_config(self, query):
        return query



""" For test """
if __name__ == "__main__":
    path = "../data/config/list_config.js"
    result = List_Config_Reader(path)
    json.encode(result, 'sample_config.js')
