#!/usr/bin/env python3
"""
Ageas Reborn

author: jy, nkmtmsys
"""

import os
import re
import math
import numpy as  np
import pandas as pd
import ageas.tool.json as json
import ageas.database_setup as db_setup
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


class Setup:
    """
    Storage database related setting variables
    """

    def __init__(self,
                database_path = None,
                database_type = 'gem_file',
                class1_path = 'CT1',
                class2_path = 'CT2',
                specie = 'mouse',
                factor_name_type = 'gene_name',
                interaction_db = 'biogrid',
                sliding_window_size = None,
                sliding_window_stride = None):
        super(Setup, self).__init__()
        # Auto GEM folder finder
        if database_path is None:
            assert os.path.exists(class1_path) and os.path.exists(class2_path)
        elif class1_path is None or class2_path is None:
            if len(os.listdir(database_path)) != 2:
                raise DB_Error('Please specify classes for binary clf')
            else:
                class1_path = os.listdir(database_path)[0]
                class2_path = os.listdir(database_path)[1]

        # Initialization
        self.db_path = database_path
        self.type = database_type
        self.specie = specie
        self.factor_name_type = factor_name_type
        self.interaction_db = interaction_db
        self.sliding_window_size = sliding_window_size
        self.sliding_window_stride = sliding_window_stride
        # Get classes'correspond folder paths
        self.class1_path = self.__cast_path(class1_path)
        self.class2_path = self.__cast_path(class2_path)
        # Perform label encoding
        self.label_transformer = Label_Encode(class1_path, class2_path)
        self.label1 = self.label_transformer.get_label1()
        self.label2 = self.label_transformer.get_label2()

    # make path str for the input class based on data path and folder name
    def __cast_path(self, path):
        # no need to concat if path is already completed
        if self.db_path is None:
            return path
        elif path[0] == '/':
            return self.db_path + path
        else:
            return self.db_path + '/' + path



class Label_Encode:
    """
    Transform labels into ints
    """

    def __init__(self, class1_path, class2_path):
        super(Label_Encode, self).__init__()
        # Initialization
        self.encoder = LabelEncoder().fit([class1_path, class2_path])
        self.transformed_labels = self.encoder.transform([class1_path,
                                                        class2_path])

    # Perform inverse_transform
    def getOriginLable(self, query):
        return list(self.encoder.inverse_transform(query))

    # As named
    def get_label1(self): return self.transformed_labels[0]
    def get_label2(self): return self.transformed_labels[1]



class Process(object):
    """
    Seperate sample gene expression data into training sets and testing sets
    by given ratio
    Then prepare sample data to be ready for training and analysis process
    """
    def __init__(self, database_info = None,
                        grnData = None,
                        train_size = 0.7,
                        ramdom_state = None,
                        fullData = None,
                        fullLabel = None,):
        super(Process, self).__init__()
        # Initialization
        self.train_size = train_size
        self.random_state = ramdom_state
        self.all_grp_ids = {}
        # Go through database_info based protocol
        if fullData is None or fullLabel is None:
            self.__init_protocol(database_info, grnData)
        elif fullData is not None and fullLabel is not None:
            self.__iterating_protocool(fullData.to_numpy(), fullLabel)
        else:
            raise db_setup.Error('Preprocessor Error: case not catched')

    # Process in database mode
    def __init_protocol(self, database_info, grnData):
        # class1Result is [dataTrainC1, dataTestC1, lableTrainC1, labelTestC1]
        class1Result = self._splitTrainTest(grnData.class1_pcGRNs,
                                            database_info.label1)
        # similar with class1
        class2Result = self._splitTrainTest(grnData.class2_pcGRNs,
                                            database_info.label2)
        self.labelTrain = np.array(class1Result[2] + class2Result[2])
        self.labelTest = np.array(class1Result[3] + class2Result[3])
        self.dataTrain = []
        self.dataTest = []
        # standardize feature data
        # to make sure all training and testing samples
        # will be in same dimmension
        self.__update_train_test(grnData.class1_pcGRNs,
                                train_set = class1Result[0],
                                test_set = class1Result[1])
        self.__update_train_test(grnData.class2_pcGRNs,
                                train_set = class2Result[0],
                                test_set = class2Result[1])
        # Add zeros for position holding
        self._addZeros(self.dataTrain)
        self._addZeros(self.dataTest)
        # self._allIDsCheck()
        # Clear unnecessary data
        del grnData
        del database_info

    # Update training and testing set based on given expression data
    def __update_train_test(self, grns, train_set, test_set):
        for sample in grns:
            grn = grns[sample]
            grn_copy = {ele:'' for ele in grn}
            features = ''
            for ele in self.all_grp_ids:
                if ele in grn:
                    features += str(grn[ele]['correlation']) + ';'
                    # Update grn_cop if ele already in allIDs
                    del grn_copy[ele]
                else: features += '0.0;'
            for ele in grn_copy:
                self.all_grp_ids[ele] = ''
                features += str(grn[ele]['correlation']) + ';'
            # Change every elements into float type
            features = list(map(float, features.split(';')[:-1]))
            if sample in train_set:
                self.dataTrain.append(features)
            elif sample in test_set:
                self.dataTest.append(features)

    # Makke training/testing data and lable arrays based on given full data
    def __iterating_protocool(self, fullData, fullLabel):
            data = train_test_split(fullData,
                                    fullLabel,
                                    train_size = self.train_size,
                                    random_state = self.random_state)
            self.dataTrain = data[0]
            self.dataTest = data[1]
            self.labelTrain = data[2]
            self.labelTest = data[3]

    # seperate files in given path into training
    # and testing sets based on ratio
    def _splitTrainTest(self, grnData, label):
        data_sample = []
        label_sample = []
        for sample in grnData:
            data_sample.append(sample)
            label_sample.append(label)
        return train_test_split(data_sample,
                                label_sample,
                                train_size = self.train_size,
                                random_state = self.random_state)

    # add zeros to each preprocessed samples
    # to make sure all training and testing samples
    # will be in same dimmension
    def _addZeros(self, dataset):
        for sample in dataset:
            if len(sample) != len(self.all_grp_ids):
                sample += [0] * (len(self.all_grp_ids) - len(sample))
                sample = np.array(sample)
        dataset = np.array(dataset)

    # Check whether allIDs have dupicate IDs or not
    # ToDo: need optimization to get unique ids
    def _allIDsCheck(self):
        # check whether allIDs have duplicate elements
        unique = [x for i, x in enumerate([*self.all_grp_ids])
            if i == [*self.all_grp_ids].index(x)]
        if len(self.all_grp_ids) != len(unique):
            raise db_setup.Error(
                'preprocessor malfunction: duplicate ID in allIDs')
        del unique

    # Calculate a close-to-square matrix size based on allIDs
    # for using 2D-input based machinle learning models (e.g. hybrid_model)
    def auto_inject_fake_grps(self):
        total = len(self.all_grp_ids)
        tar = math.sqrt(total)
        if int(tar) == tar: return
        elif int(tar) < tar:
            aim = int(tar) + 1
            fakeID = 'FAKE'
            fakeID_Num = aim*aim - total
            for i in range(fakeID_Num):
                id = fakeID + str(i)
                self.all_grp_ids[id] = ''
        self._addZeros(self.dataTrain)
        self._addZeros(self.dataTest)
