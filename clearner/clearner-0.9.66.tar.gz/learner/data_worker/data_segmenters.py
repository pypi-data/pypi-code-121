# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Handle segmenting a dataset based on the values of a specific column"""
import sys
import abc
import warnings
import logging
import numpy as np
import pandas as pd

from learner.configuration.configuration import Configuration


class AbstractSegmenter:
    """A template class for other segmenter classes."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, conf: Configuration):  # pragma: no cover
        self._conf = conf
        self._seg_list = conf.segmenter.seg_list
        self._max_num_bins = conf.segmenter.max_num_bins
        self.seg_dict = None

    @property
    def conf(self):
        return self._conf

    @property
    def seg_list(self):
        return self._seg_list

    @property
    def max_num_bins(self):
        return self._max_num_bins

    @staticmethod
    def fit(data, train_col):  # pragma: no cover
        pass

    @staticmethod
    def transform(data, col, name):  # pragma: no cover
        pass

    @staticmethod
    def fit_transform(data, train_col, train_name):  # pragma: no cover
        pass

    def create_seg_dict(self):
        """Create a dictionary of the segments from seg_list where the key is the segment border and the value is the
        segment id. This dictionary is used to update the model_dict and enable custom parameters/model for each
        segment.

        :return: None
        """
        self.seg_dict = {seg_border: seg_id for seg_id, seg_border in enumerate(self.seg_list)}

    def update_models_dict(self):
        """Make some updates to the models_dict by finding the seg_id and seg_name for each segment. Then reformat the
        models_dict in a way that the value of each tag will be a dictionary of dictionaries. The key of each item of
        the parent dictionary is the seg_id, and the value is a dictionary that contain all the parameters. Here's an
        example:
            {'rf1': {0: {'params': {'min_samples_leaf': 1,
                                    'min_samples_split': 4,
                                    'n_estimators': 100,
                                    'n_jobs': -1},
                         'seg_id': 0,
                         'type': 'RandomForestClassifier'},
                     1: {'params': {'min_samples_leaf': 1,
                                    'min_samples_split': 4,
                                    'n_estimators': 100,
                                    'n_jobs': -1},
                         'path': '/home/ramezani/dev/output/classifier/classifier_rf1_2019-06-20-22-14/',
                         'seg_id': 1,
                         'type': 'XGBClassifier'}}
        :return: None
        """
        self.create_seg_dict()
        self._convert_dict_to_list()
        self._set_seg_ids()
        self._reformat_models_dict()
        self._ensure_all_segs_have_params()

    def _convert_dict_to_list(self):
        """The user has the option to pass a dictionary or a list of dictionaries in the models_dict field. If a
        dictionary is provided, it indicates that all segments will use similar parameters (no custom parameter).
        In that case, we need to set seg_id to -1 and seg_name to "any" and then convert the dictionary to a list
        for consistency.

        :return:  None
        """
        # loop through all items in models_dict, find the ones that are dictionaries and make necessary updates.
        for tag, mdls in self.conf.model.models_dict.items():
            if isinstance(mdls, dict):
                self.conf.model.models_dict[tag]["seg_name"] = "any"
                self.conf.model.models_dict[tag]["seg_id"] = -1
                self.conf.model.models_dict[tag] = [mdls]

    def _set_seg_ids(self):
        """Find and set seg_id for all items in the models_dict. Also, make sure seg_name and seg_id are consistent in
        case both of them are provided.

        :return: None
        """
        for tag, mdls in self.conf.model.models_dict.items():
            for i, mdl in enumerate(mdls):
                # if seg_id is not defined, try to figure things out using seg_name
                if "seg_id" not in mdl:
                    try:
                        seg_name = mdl["seg_name"]
                        mdl["seg_id"] = self.seg_dict[seg_name] if seg_name != "any" else -1
                    except KeyError:
                        mdl["seg_id"] = -1
                        mdl["seg_name"] = "any"
                elif mdl["seg_id"] == -1:
                    mdl["seg_name"] = "any"
                # if both seg_id and seg_name are defined, make sure they both are correct
                elif "seg_id" in mdl and "seg_name" in mdl:
                    try:
                        if mdl["seg_id"] != self.seg_dict[mdl["seg_name"]]:
                            logging.error("The seg_id '{seg_id}' and seg_name '{seg_name}' in {tag} are not consistent."
                                          " Please update the configuration file and try again. Exiting...".
                                          format(seg_id=mdl["seg_id"],
                                                 seg_name=mdl["seg_name"],
                                                 tag=tag))
                            sys.exit(1)
                    except KeyError:
                        logging.error("The seg_name '{seg_name}' is defined under {tag} but does not contain "
                                      "in the data. There could be a typo there. Please update the configuration file "
                                      "and try again. Exiting..."
                                      .format(seg_id=mdl["seg_id"],
                                              seg_name=mdl["seg_name"],
                                              tag=tag))

                        sys.exit(1)

    def _reformat_models_dict(self):
        """Reformat the models_dict and create a dictionary of dictionaries. Please see the documentation of
        update_models_dict method for more details.

        :return: None
        """
        for tag, mdls in self.conf.model.models_dict.items():
            # check if default parameters exist
            default_exist = any(is_default for is_default in [(mdl.get("seg_id", None) == -1 or mdl.get("seg_name", None) == "any") for mdl in mdls])
            # if there are default parameters, inform the user that learner will use them
            if len(mdls) < len(self.seg_list) and default_exist:
                logging.info("The default parameters have been provided. Learner will use them for segments without "
                             "customized parameters")
            if len(mdls) < len(self.seg_list) and not default_exist:
                logging.error("The number of segments are {num_segments} but {num_params} parameters was provided "
                              "without providing a default parameter. Please update the configuration file. Exiting".
                              format(num_segments=len(self.seg_list), num_params=len(mdls)))
                sys.exit(1)
            self.conf.model.models_dict[tag] = {mdl["seg_id"]: mdl for mdl in mdls}

    def _ensure_all_segs_have_params(self):
        """We need to make sure the number of items in models_dict matches the number of segments. If the number of
        parameters do not match, we need to use default values for the segments that we don't have a custom parameter
        for. This method takes care of that. It will raise an error if we need a default parameter but it hasn't been
        provided or there are other inconsistencies. This is the last step in updating the models_dict.

        :return: None
        """
        for seg_id, seg_border in enumerate(self.seg_list):
            for tag, mdls in self.conf.model.models_dict.items():
                if seg_id not in self.conf.model.models_dict[tag]:
                    try:
                        self.conf.model.models_dict[tag][seg_id] = self.conf.model.models_dict[tag][-1]
                    except KeyError:
                        logging.error("The parameters set for different segments are incorrect. There are probably "
                                      "overlaps between seg_name and seg_id with no default parameters")
                        sys.exit(1)


class SegmenterHandler:
    """SegmenterHandler is the workflow class that is responsible for instantiation and running segmentation."""

    def __init__(self, conf, data_type="train"):
        """Initialize a SegmenterHandler object using a conf object and initialize the instance variables.

        :param conf: a conf object
        """
        self._conf = conf
        self._data_type = data_type

    @property
    def conf(self):
        return self._conf

    def handle_segmenter(self, data):
        """Execution method for controlling the creation and transformation of data with a segmenter

        :param data: a pandas dataframe
        :return: None
        """
        # if segmenter is not activated immediately return, otherwise continue
        if not self._conf.segmenter.activate:
            return
        segmenter = None
        seg_type = self._conf.segmenter.type
        # find the segmenter type and instantiate the corresponding object
        if seg_type == 'static':
            segmenter = StaticSegmenter(self._conf)
        elif seg_type == 'dynamic' and self.conf.segmenter.duplicates == "merge":
            segmenter = DynamicSegmenter(self._conf)
        elif seg_type == 'dynamic' and self.conf.segmenter.duplicates == "drop":
            segmenter = QCutSegmenter(self._conf)
        elif seg_type == 'value':
            segmenter = ValueSegmenter(self._conf)
        # if seg_list hasn't been populated (commonly during training phase) go through the entire process of fitting,
        # transforming, and populating it.
        if not self._conf.segmenter.seg_list:

            segmenter.fit_transform(data,
                                    self._conf.segmenter.train_col,
                                    self._conf.segmenter.train_name)

            segmenter.transform(data,
                                self._conf.segmenter.test_col,
                                self._conf.segmenter.test_name)

            self._conf.segmenter.seg_list = segmenter.seg_list
        # if the seg_list has already been populated, then just do the transform
        else:
            # we need to do this because the test_col might be precessed, i.e. label encoding, etc
            if seg_type == "value" and self._data_type == "validation":
                segmenter.transform(data,
                                    self._conf.segmenter.train_col,
                                    self._conf.segmenter.test_name)
            else:
                segmenter.transform(data,
                                    self._conf.segmenter.test_col,
                                    self._conf.segmenter.test_name)


class ValueSegmenter(AbstractSegmenter):
    """Segment a column by finding the unique value in that column. This is suitable for categorical columns or columns
     with limited number of unique values. This is a pretty straightforward segmenter. We just get a list of unique
     values to create the seg_list, and then copy the columns. The processor and configuration classes perform some
     operations to enable an easy implementation here. For example, if a column is a categorical column and gets
     label-encoded, the pre-encoded column needs to be used while processing the training data because the test data
     get's loaded before processing. The processor makes a backup and configuration updates the column names"""

    def __init__(self, conf):
        """Initialize a segmenter object using a conf object.

        :param conf: an instance of the Configuration class
        """
        super().__init__(conf)

    def fit(self, data, train_col):
        """Get a list that contain all the unique values in the train_col. train_col is an existing column in the data.

        :param data: pandas DataFrame
        :param train_col: the column to use for segmentation
        :return: a list containing the upper boundary of the segments
        """
        # we first try to sort the list, if we give up and continue with unsorted list if we fail. This can happen when
        # there are missing values in segment column and the get imputed with a number.
        try:
            self._seg_list = sorted(data[train_col].unique().tolist())
        except Exception:
            self._seg_list = data[train_col].unique().tolist()
        self.update_models_dict()

    def transform(self, data, col, name):
        """Transform a column with a trained segment list. This function copies the column names "col" into a new
        column named "name"

        :param data: pandas DataFrame
        :param col: column to use
        :param name: name of the new column
        """
        data[name] = data[col]

    def fit_transform(self, data, train_col, train_name):
        """Create a segment list and transform the same column.

         :param data: pandas DataFrame
         :param train_col: the columns to be used for segmentation
         :param train_name: name of column to assign transformed column
         :return: None
         """
        self.fit(data, train_col)
        self.transform(data, train_col, train_name)


class StaticSegmenter(AbstractSegmenter):
    """Segment a column by the bin size and max number of bins specified."""

    def __init__(self, conf):
        """Initialize a segmenter object using a conf object.

        :param conf: an instance of the Configuration class
        """
        super().__init__(conf)
        self._bin_size = conf.segmenter.bin_size

    @property
    def bin_size(self):
        return self._bin_size

    def _get_segment_id(self, value):
        """Given a value, return the segment id for that value.

        :param value: a numeric value
        :return: an integer corresponding to segment id
        """
        return int(min(value // self._bin_size, self._max_num_bins - 1))

    def _get_seg_border(self, value):
        """Compute the upper boundary of a segment using bin_size and segment id

        :param value: a number to find the segment border for
        :return: upper boundary of a segment for the value
        """
        seg_id = self._get_segment_id(value)
        return (seg_id + 1) * self._bin_size

    def fit(self, data, train_col):
        """Create a column with label name that contains the segment border for each entry. Use an existing column in
        the data set (train_col) for calculations.

        :param data: pandas DataFrame
        :param train_col: the column to use for segmentation
        :return: a list containing the upper boundary of the segments
        """
        segment = data[train_col].apply(lambda x: self._get_seg_border(x))
        self._seg_list = sorted(segment.unique().tolist())
        self.update_models_dict()

    def transform(self, data, col, name):
        """Transform a column with a trained segment list. This function creates a new column in the dataset (called name),
         which contain the upper boundary of the segment corresponding the the values in col.

        :param data: pandas DataFrame
        :param col: column to use for finding the segments
        :param name: name of column to assign transformed column
        """
        data[name] = data[col].apply(lambda x: self._get_seg_border(x))

    def fit_transform(self, data, train_col, train_name):
        """Create a segment list and transform the same column.

         :param data: pandas DataFrame
         :param train_col: the columns to be used for segmentation
         :param train_name: name of column to assign transformed column
         :return: None
         """
        self.fit(data, train_col)
        self.transform(data, train_col, train_name)


class DynamicSegmenter(AbstractSegmenter):
    """Creates segments that are dynamic in width based on the number of items in each segment."""

    def __init__(self, conf):
        """Initialize a DynamicSegmenter instance using a conf object.

        :param conf: a instance of the Configuration class
        """
        super().__init__(conf)

    def _get_seg_borders(self, data, train_col):
        """Obtain the segment borders (both upper and lower boundaries) for train_col in the data

        :param data: a pandas DataFrame
        :param train_col: the column in the dataset to use for finding the segment borders
        :return: a list of lists containing the lower and upper boundaries of the segments
        """
        seg_borders = []
        delta = int(data.shape[0]/self._max_num_bins)
        lower = 0
        upper = delta - 1
        sorted_train_col = np.sort(data[train_col])
        for i in range(self._max_num_bins):
            seg_borders.append([sorted_train_col[lower], sorted_train_col[upper]])
            lower = upper + 1
            upper = lower + delta - 1
        # the last border should be the maximum value in the column
        seg_borders[-1][1] = sorted_train_col[-1]
        return seg_borders

    @staticmethod
    def _merge_seg_borders(seg_borders):
        """If upper boundary of a segment is the same as the lower boundary of the next segment, merge those intervals.

        :param seg_borders: a list of lists containing the lower and upper boundaries of the segments
        :return: a list of lists containing the merged segment borders
        """
        merged_seg_borders = []
        for border in seg_borders:
            if not merged_seg_borders or merged_seg_borders[-1][1] < border[0]:
                merged_seg_borders.append(border)
            else:
                merged_seg_borders[-1][1] = max(merged_seg_borders[-1][1], border[1])
        return merged_seg_borders

    def fit(self, data, train_col):
        """Create and store the upper boundaries for segments

        :param data: pandas DataFrame
        :param train_col: the column to be used for segmentation fitting
        """
        logging.info("Attempting to split the training dataset into %i segment(s)", self._max_num_bins)
        seg_borders = self._get_seg_borders(data, train_col)
        merged_seg_borders = self._merge_seg_borders(seg_borders)
        self._seg_list = [border[1] for border in merged_seg_borders]

        if len(self._seg_list) < self._max_num_bins:
            warnings.warn("The training dataset was split into {0} segments due to overlaps in the boundaries"
                          .format(len(self._seg_list)), Warning)
        else:
            logging.info("The training dataset was successfully split into %i segment(s)", self._max_num_bins)
        self.update_models_dict()

    def transform(self, data, col, name):
        """Transform a column with a trained segment list.

        :param data: pandas DataFrame
        :param col: column to be used for segmentation transformation
        :param name: column name for the output of segmentation transformation
        :return: None
        """
        seg_list = self._seg_list

        # This is done so that the edges take into account lower and higher values in a prediction dataset than were
        # seen in the training dataset.
        seg_list = [-np.inf] + seg_list

        if data[col].max() > max(self._seg_list):
            max_value = data[col].max()
            seg_list[-1] = max_value

        data[name] = pd.cut(data[col], seg_list, labels=self._seg_list, right=True)

    def fit_transform(self, data, train_col, train_name):
        """Create a segment list and transform the same column.

        :param data: pandas DataFrame
        :param train_col: the column to be used for segmentation fitting
        :param train_name: the column name for the output of segmentation transformation
        :return: None
        """
        self.fit(data, train_col)
        self.transform(data, train_col, train_name)


class QCutSegmenter(AbstractSegmenter):
    """Creates segments that are dynamic in width based on the number of items in each segment. The difference between
    the DynamicSegment and the QCutSegmenter is how the boundaries are defined. Here we use pandas's qcut."""

    def __init__(self, conf):
        """Initialize a QCutSegmenter instance using a conf object.

        :param conf: a instance of the Configuration class
        """
        super().__init__(conf)

    def _get_seg_borders(self, data, train_col):
        """Obtain the segment borders for train_col in the data. Here, we get a single list that contains the borders
        instead of list of lists. This is provided by pandas' qcut method. For more information, see
        https://pandas.pydata.org/docs/reference/api/pandas.qcut.html

        :param data: a pandas DataFrame
        :param train_col: the column in the dataset to use for finding the segment borders
        :return: a list containing the lower and upper boundaries of the segments
        """
        _, seg_borders = pd.qcut(data[train_col], self._max_num_bins, duplicates="drop", retbins=True)

        # we ignore the first one to later replace it with -inf
        return list(seg_borders[1:]) if len(seg_borders) != 1 else list(seg_borders)

    def fit(self, data, train_col):
        """Create and store the upper boundaries for segments

        :param data: pandas DataFrame
        :param train_col: the column to be used for segmentation fitting
        """
        logging.info("Attempting to split the training dataset into %i segment(s)", self._max_num_bins)
        self._seg_list = self._get_seg_borders(data, train_col)

        if len(self._seg_list) < self._max_num_bins:
            warnings.warn("The training dataset was split into {0} segments due to overlaps in the boundaries"
                          .format(len(self._seg_list)), Warning)
        else:
            logging.info("The training dataset was successfully split into %i segment(s)", self._max_num_bins)
        self.update_models_dict()

    def transform(self, data, col, name):
        """Transform a column with a trained segment list.

        :param data: pandas DataFrame
        :param col: column to be used for segmentation transformation
        :param name: column name for the output of segmentation transformation
        :return: None
        """
        seg_list = self._seg_list.copy()

        # This is done so that the edges take into account lower and higher values in a prediction dataset than were
        # seen in the training dataset.
        seg_list = [-np.inf] + seg_list

        if data[col].max() > max(self._seg_list):
            max_value = data[col].max()
            seg_list[-1] = max_value

        data[name] = pd.cut(data[col], seg_list, labels=self._seg_list, right=True)

    def fit_transform(self, data, train_col, train_name):
        """Create a segment list and transform the same column.

        :param data: pandas DataFrame
        :param train_col: the column to be used for segmentation fitting
        :param train_name: the column name for the output of segmentation transformation
        :return: None
        """
        self.fit(data, train_col)
        self.transform(data, train_col, train_name)
