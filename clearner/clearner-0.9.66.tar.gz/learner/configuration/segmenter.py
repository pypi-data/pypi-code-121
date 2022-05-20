# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import logging

from learner.data_worker.data_loader import get_value
from learner.configuration.supported_items import *
from learner.validator.input_validator import validate_intersection_cols, validate_subset_list
from learner.configuration.process import ProcessConfiguration
from learner.configuration.column import ColumnConfiguration
from learner.configuration.supported_items import SUPPORTED_DUPLICATES_FOR_SEGMENTERS


class SegmenterConfiguration:
    """Parse all input variables related to segmenter section. Learner currently supports static and
    dynamic segmentation."""

    def __init__(self, json_config, process: ProcessConfiguration, column: ColumnConfiguration):
        self._json_config = json_config
        self._process = process
        self._column = column
        self.activate = get_value(self._json_config, False, "segmenter", "activate")
        self.type = self.get_type()
        self.bin_size = get_value(self._json_config, 1, "segmenter", "params", "bin_size")
        self.max_num_bins = get_value(self._json_config, 100, "segmenter", "params", "max_num_bins")
        self.train_col = self.get_train_col()
        self.train_name = get_value(self._json_config, "train_name", "segmenter", "params", "train_name")
        self.test_col = get_value(self._json_config, self.train_col, "segmenter", "params", "test_col")
        self.test_name = get_value(self._json_config, "test_name", "segmenter", "params", "test_name")
        self.duplicates = self.get_duplicates()
        self.seg_list = get_value(self._json_config, None, "segmenter", "seg_list")

    def get_type(self):
        try:
            seg_type = self._json_config["segmenter"]["type"]
            if seg_type.lower().startswith('s'):
                seg_type = 'static'
            elif seg_type.lower().startswith('d'):
                seg_type = 'dynamic'
            elif seg_type.lower().startswith('v'):
                seg_type = 'value'
            else:
                logging.error("Segmenter type '%s' is not understood. Supported segmenters are %s", seg_type,
                              SUPPORTED_SEGMENTERS)
                sys.exit(1)
            return seg_type
        except KeyError:
            return None

    def get_train_col(self):
        try:
            train_col = self._json_config["segmenter"]["params"]["train_col"]
            # make sure the cat_cols and the train_col do not have an intersection because we process the data first
            # and the train_col won't exist if it gets encoded
            if self._process.dummies_activate:
                validate_intersection_cols(cols1=self._process.dummies_cols,
                                           cols2=[train_col],
                                           cols1_name='cat_cols',
                                           cols2_name='train_col')
            # if train_col is a categorical column, which will be label_encoded, we'd need to backup the column because
            # the data gets to segmenter after it's being processed, i.e. the encoded values will reach to segmenter.
            # Because we only load segment column for making predictions before processing them, we can't use encoded
            # list for loading test data
            if self.type == "value" and self._process.label_encoding_activate and train_col in self._process.label_encoding_cols:
                train_col_name = f"__copy_{train_col}"
                # add train_col to the columns that should be copied
                self._column.copy_cols[train_col] = train_col_name
                # add the column to the list of valid columns
                self._column.valid_cols.append(train_col_name)
                # now add the copied column to the list of column that should be dropped before training
                self._column.drop_from_train.append(train_col_name)
                train_col = train_col_name
            return train_col

        except KeyError:
            return None

    def get_duplicates(self):
        try:
            duplicates = self._json_config["segmenter"]["params"]["duplicates"]
            validate_subset_list(parent_list=SUPPORTED_DUPLICATES_FOR_SEGMENTERS,
                                 parent_name="supported duplicates for segmenters",
                                 subset_list=[duplicates],
                                 subset_name="defined duplicates")
            return duplicates
        except KeyError:
            return "merge"
