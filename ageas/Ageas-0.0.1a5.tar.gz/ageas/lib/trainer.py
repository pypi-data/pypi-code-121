#!/usr/bin/env python3
"""
Ageas Reborn
This file contains classes to find best models for further analysis

author: jy, nkmtmsys
"""

import re
import torch
import pickle
import difflib
import numpy as np
import pandas as pd
from warnings import warn
import ageas.lib as lib
import ageas.classifier as clf
import ageas.classifier.gnb as gnb
import ageas.classifier.rfc as rfc
import ageas.classifier.xgb as xgb
import ageas.classifier.svm as svm
import ageas.classifier.rnn as rnn
import ageas.classifier.gru as gru
import ageas.classifier.lstm as lstm
import ageas.classifier.logit as logit
import ageas.classifier.transformer as transformer
import ageas.classifier.cnn_1d as cnn_1d
import ageas.classifier.cnn_hybrid as cnn_hybrid
import ageas.database_setup.binary_class as binary_class



class Train(clf.Make_Template):
    """
    Train out well performing classification models
    """
    def __init__(self,
                pcGRNs = None,
                database_info = None,
                model_config = None,
                random_state = None,
                test_split_set = False,):
        super(Train, self).__init__()
        # Initialization
        self.grns = pcGRNs
        self.models = None
        self.allData = None
        self.allLabel = None
        self.random_state = random_state
        self.model_config = model_config
        self.database_info = database_info
        self.test_split_set = test_split_set

    def general_process(self,
                        train_size = 0.3,
                        clf_keep_ratio = None,
                        clf_accuracy_thread = None):
        """
        Generate training data and testing data iteratively
        Then train out models in model sets
        Only keep top performancing models in each set
        """
        data = binary_class.Process(self.database_info,
                                    self.grns,
                                    train_size,
                                    self.random_state,
                                    self.allData,
                                    self.allLabel)
        data.auto_inject_fake_grps()

        # Update allGRP_IDs, allData, allLabel after first iteration
        # to try to avoid redundant calculation
        if self.allData is None and self.allLabel is None:
            print('Total GRP amount: ', len(data.all_grp_ids))
            self.allData = data.dataTrain + data.dataTest
            self.allLabel = np.concatenate((data.labelTrain, data.labelTest))
            assert len(self.allData) == len(self.allLabel)
            self.allData = pd.DataFrame(self.allData, columns= data.all_grp_ids)

        # Do trainings
        self.models = self.__initialize_classifiers(self.model_config)
        for modelSet in self.models:
            modelSet.train(data, self.test_split_set)
            if self.test_split_set:
                modelSet._filter_models(clf_keep_ratio, clf_accuracy_thread)

        # Concat models together based on performace
        temp = []
        for models in self.models:
            for model in models.models:
                temp.append(model)
        self.models = temp
        # Keep best performancing models in local test
        if self.test_split_set and clf_keep_ratio is not None:
            self._filter_models(clf_keep_ratio, clf_accuracy_thread)

        # Filter based on global test performace
        self.models = self.get_clf_accuracy(clf_list = self.models,
                                            data = self.allData.to_numpy(),
                                            label = self.allLabel)
        self._filter_models(clf_keep_ratio, clf_accuracy_thread)
        print('Keeping ', len(self.models), ' models')


    def successive_halving_process(self,
                                    iteration = 2,
                                    clf_keep_ratio = 0.5,
                                    clf_accuracy_thread = 0.9,
                                    last_train_size = 0.9,):
        """
        Train out models in Successive Halving manner
        Amount of training data is set as limited resouce
        While accuracy is set as evaluation standard
        """
        assert last_train_size < 1.0
        if self.test_split_set:
            warn('Trainer Warning: test_split_set is True! Changing to False.')
            self.test_split_set = False
        # set iteration to 0 if not doing model selection
        if iteration is None: iteration = 0
        # initialize training data set
        init_train_size = float(1 / pow(2, iteration))
        train_size = 0
        for i in range(iteration):
            breaking = False
            train_size = float(init_train_size * pow(2, i))
            # about last round, we set train size to the max resouce
            if train_size >= last_train_size:
                train_size = last_train_size
                breaking = True
            print('Iteration:', i, ' with training size:', train_size)
            keep_ratio = max(1 - train_size, clf_keep_ratio)
            # remove more and more portion as more resource being avaliable
            self.general_process(train_size = train_size,
                                clf_accuracy_thread = clf_accuracy_thread,
                                clf_keep_ratio = keep_ratio)
            self.__prune_model_config(id_keep={x[0].id:''for x in self.models})
            if breaking: break

        if train_size < last_train_size:
            print('Iteration Last: with training size:', last_train_size)
            self.general_process(train_size = last_train_size,
                                clf_accuracy_thread = clf_accuracy_thread)
        else: self._filter_models(clf_accuracy_thread = clf_accuracy_thread)

        self.__prune_model_config(id_keep={x[0].id:''for x in self.models})
        total_model = 0
        for genra in self.model_config:
            total_model += len(self.model_config[genra])
        print('Selecting ', total_model, ' Models after Model Selection')

    # Re-assign accuracy based on all data performance
    def get_clf_accuracy(self, clf_list, data, label):
        i = 0
        for record in clf_list:
            model = record[0]
            i+=1
            # Handel SVM and XGB cases
            # Or maybe any sklearn-style case
            if (model.model_type == 'SVM' or
                model.model_type == 'Logit' or
                model.model_type == 'GNB' or
                model.model_type == 'RFC' or
                model.model_type == 'XGB_GBM'):
                pred_result = model.clf.predict(data)
                pred_accuracy = difflib.SequenceMatcher(None,
                                                        pred_result,
                                                        label).ratio()
            # RNN type handling + CNN cases
            elif (model.model_type == 'RNN' or
                    model.model_type == 'LSTM' or
                    model.model_type == 'GRU' or
                    model.model_type == 'Transformer' or
                    re.search(r'CNN', model.model_type)):
                # Enter eval mode and turn off gradient calculation
                model.eval()
                with torch.no_grad():
                    pred_result = model(clf.reshape_tensor(data))
                pred_accuracy, pred_result = self.__evaluate_torch(pred_result,
                                                                    label)
            else:
                raise lib.Error('Cannot handle classifier: ', model.model_type)
            record[-1] = pred_result
            record.append(pred_accuracy)
            # For debug purpose
            # print('Performined all data test on model', i,
            #         ' type:', model.model_type, '\n',
            #         'test set accuracy:', round(accuracy, 2),
            #         ' all data accuracy: ', round(pred_accuracy, 2), '\n')
        clf_list.sort(key = lambda x:x[-1], reverse = True)
        return clf_list

    # clear stored data
    def clear_data(self):
        self.grns = None
        self.models = None
        self.allData = None
        self.allLabel = None

    # Save result models in given path
    def save_models(self, path):
        with open(path, 'wb') as file:
            pickle.dump(self.models, file)

    # Make model sets based on given config
    def __initialize_classifiers(self, config):
        list = []
        if 'Logit' in config:
            list.append(logit.Make(config = config['Logit']))
        if 'Transformer' in config:
            list.append(transformer.Make(config = config['Transformer']))
        if 'RFC' in config:
            list.append(rfc.Make(config = config['RFC']))
        if 'GNB' in config:
            list.append(gnb.Make(config = config['GNB']))
        if 'GBM' in config:
            list.append(xgb.Make(config = config['GBM']))
        if 'SVM' in config:
            list.append(svm.Make(config = config['SVM']))
        if 'CNN_1D' in config:
            list.append(cnn_1d.Make(config = config['CNN_1D']))
        if 'CNN_Hybrid' in config:
            list.append(cnn_hybrid.Make(config = config['CNN_Hybrid'],
                                        grp_amount = len(self.allData.columns)))
        if 'RNN' in config:
            list.append(rnn.Make(config = config['RNN']))
        if 'LSTM' in config:
            list.append(lstm.Make(config = config['LSTM']))
        if 'GRU' in config:
            list.append(gru.Make(config = config['GRU']))
        return list

    # delete model configs not on while list(dict)
    def __prune_model_config(self, id_keep):
        result = {}
        for genra in self.model_config:
            temp = {}
            for id in self.model_config[genra]:
                if id in id_keep:
                    temp[id] = self.model_config[genra][id]
                else:
                    print('     Pruning:', id)
            if len(temp) > 0: result[genra] = temp
        self.model_config = result

    # Evaluate pytorch based methods'accuracies
    def __evaluate_torch(self, result, label):
        modifiedResult = []
        correct = 0
        for i in range(len(result)):
            if result[i][0] > result[i][1]: predict = 0
            else: predict = 1
            if predict == label[i]: correct += 1
            modifiedResult.append(predict)
        accuracy = correct / len(label)
        return accuracy, modifiedResult
