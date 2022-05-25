################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2021, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from collections import namedtuple
from sklearn.impute._iterative import _ImputerTriplet

class ExtendedIterativeImputer(IterativeImputer):

    def _forward_conversion(self):
        if len(self.imputation_sequence_) > 0:
            self.new_imputation_sequence_ = [item._asdict() for item in self.imputation_sequence_]

    def _back_to_original(self):
        if len(self.new_imputation_sequence_) > 0:
            self.imputation_sequence_ = [_ImputerTriplet(**item) for item in self.new_imputation_sequence_]

    def fit(self, X, y=None):
        ans = super(ExtendedIterativeImputer, self).fit(X, y)
        self._forward_conversion()
        self.imputation_sequence_ = []
        return ans

    def transform(self, X):
        self._back_to_original()
        self.new_imputation_sequence_ = []
        ans = super(ExtendedIterativeImputer, self).transform(X)
        self._forward_conversion()
        self.imputation_sequence_ = []
        return ans

    def fit_transformform(self, X, y):
        ans = super(ExtendedIterativeImputer, self).fit_transform(X, y)
        self._forward_conversion()
        self.imputation_sequence_ = []
        return ans
