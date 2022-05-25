################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2021, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

import unittest
import pandas as pd
from os import path
from autoai_ts_libs.utils.holdout_utils import make_holdout_split


class HoldoutUtilsTest(unittest.TestCase):

    file_path = path.dirname(__file__)
    dataset = pd.read_csv(path.join(file_path, "../data/AirPassengers.csv"))
    dataset_1 = pd.read_csv(path.join(file_path, "../data/Air_Quality.csv"))
    dataset_training = pd.read_csv(path.join(file_path, "../data/AirPassengers_training114.csv"))
    dataset_holdout = pd.read_csv(path.join(file_path, "../data/AirPassengers_holdout30.csv"))

    def test_split_holdout(self):
        X_test, y_test, X_test_indices, y_test_indices = make_holdout_split(self.dataset, target_columns=[2], timestamp_column=1,lookback_window=12,return_only_holdout=True)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        print("X_test_indices: " + str(X_test_indices))
        print("y_test_indices: " + str(y_test_indices))
        self.assertTrue(len(X_test) == 32)
        self.assertTrue(len(y_test) == 20)
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

    def test_split_holdout_ratio_holdout(self):
        X_test, y_test, X_test_indices, y_test_indices = make_holdout_split(self.dataset, test_size=0.2, target_columns=[2], timestamp_column=1,return_only_holdout=True)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        print("X_test_indices: " + str(X_test_indices))
        print("y_test_indices: " + str(y_test_indices))
        self.assertTrue(len(X_test) == 28)
        self.assertTrue(len(y_test) == 28)
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

    def test_split_holdout_integer_holdout(self):
        X_test, y_test, X_test_indices, y_test_indices = make_holdout_split(self.dataset, test_size=18, target_columns=[2], timestamp_column=1,return_only_holdout=True)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        print("X_test_indices: " + str(X_test_indices))
        print("y_test_indices: " + str(y_test_indices))
        self.assertTrue(len(X_test) == 18)
        self.assertTrue(len(y_test) == 18)
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

    def test_split_holdout_float_holdout(self):
        X_test, y_test, X_test_indices, y_test_indices = make_holdout_split(self.dataset, test_size=20.5, target_columns=[2], timestamp_column=1,return_only_holdout=True)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        print("X_test_indices: " + str(X_test_indices))
        print("y_test_indices: " + str(y_test_indices))
        self.assertTrue(len(X_test) == 20)
        self.assertTrue(len(y_test) == 20)
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

    def test_split_holdout_no_timestamp(self):
        X_test, y_test, X_test_indices, y_test_indices = make_holdout_split(self.dataset, target_columns=[2],return_only_holdout=True)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        print("X_test_indices: " + str(X_test_indices))
        print("y_test_indices: " + str(y_test_indices))
        self.assertTrue(len(X_test) == 20)
        self.assertTrue(len(y_test) == 20)
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

    def test_split_holdout_with_training(self):
        X_train, X_test, y_train, y_test, X_train_indices, X_test_indices, y_train_indices, y_test_indices = make_holdout_split(
            self.dataset, target_columns=[2], timestamp_column=1)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        print("X_train_indices: " + str(X_train_indices))
        print("X_test_indices: " + str(X_test_indices))
        print("y_train_indices: " + str(y_train_indices))
        print("y_test_indices: " + str(y_test_indices))
        self.assertTrue(len(X_test) == 20)
        self.assertTrue(len(y_test) == 20)
        self.assertTrue(len(X_train) == len(y_train))
        self.assertTrue(len(X_train) == len(X_train_indices))
        self.assertTrue(len(y_train) == len(y_train_indices))
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

    def test_split_holdout_str_timestamp(self):
        X_test, y_test, X_test_indices, y_test_indices = make_holdout_split(self.dataset_1, target_columns=[1],
                                                                            timestamp_column=0, lookback_window=6,
                                                                            return_only_holdout=True)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        self.assertTrue(len(X_test) == 26)
        self.assertTrue(len(y_test) == 20)
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

    def test_customized_holdout(self):
        X_test, y_test, X_test_indices, y_test_indices = make_holdout_split(self.dataset_training, target_columns=[1],
                                                                            timestamp_column=0, lookback_window=6,
                                                                            return_only_holdout=True,test_dataset=self.dataset_holdout)
        print("X_test: " + str(X_test))
        print("y_test: " + str(y_test))
        self.assertTrue(len(X_test) == 36)
        self.assertTrue(len(y_test) == 30)
        self.assertTrue(len(X_test) == len(X_test_indices))
        self.assertTrue(len(y_test) == len(y_test_indices))

if __name__ == "__main__":
    unittest.main()
