# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the ColumnValidator class to validate the column names defined in different section of the
configuration file.
"""
import re
import warnings
import logging

from learner.validator.input_validator import validate_subset_cols, validate_intersection_cols


class ColumnValidator:
    def __init__(self, conf):
        self.conf = conf

    def validate_columns(self):
        """The main method that communicates with other methods to validate the columns defined in different sections
        of the configuration file. The name of each validator method ends with the section name.

        :return: None
        """
        self.validate_analysis()
        self.validate_column()
        self.validate_data()
        self.validate_feature_engineering()
        self.validate_outlier()
        self.validate_process()
        self.validate_sample()

    def validate_analysis(self):
        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.analysis.correlation_cols,
                             subset_cols_name="correlation columns")

        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.analysis.shap_exclude_cols,
                             subset_cols_name="shap exclude columns")

        # this is the pattern for finding the values between curly braces
        pattern = re.compile("{(.*?)}")
        if self.conf.analysis.shap_narrative_stories:
            for class_name, stories in self.conf.analysis.shap_narrative_stories.items():
                for item in stories["templates"]:
                    # validate the columns in the "features" section
                    validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=item["features"].keys(),
                                         subset_cols_name="features columns")

                    # now validate the template columns to make sure they exist in use columns
                    results = re.findall(pattern, item["narrative"])
                    validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=results,
                                         subset_cols_name="columns in narrative text")

    def validate_column(self):
        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.column.copy_cols.keys(),
                             subset_cols_name="copy_cols")

        if self.conf.column.dtype_activate and self.conf.column.col_dtypes:
            validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.column.col_dtypes.keys(),
                                 subset_cols_name="cols_dtypes")

        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=[self.conf.column.target_col], subset_cols_name="target_col")

        # one can request the items of date column to show up in the prediction output
        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.column.id_cols, subset_cols_name="id_cols")

        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.column.drop_cols, subset_cols_name="drop_cols")

        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.column.drop_from_train, subset_cols_name="drop_from_train")

    def validate_data(self):
        # make sure join_cols are included in id_cols
        diff = set(self.conf.data.validation_join_cols) - set(self.conf.column.id_cols)
        if diff and self.conf.data.validation_score_activate:
            self.conf.column.id_cols = set(self.conf.column.id_cols).union(diff)
            self.conf.column.id_cols = list(self.conf.column.id_cols)

            warnings.warn(f"The columns {diff} were included in scoring_params join_cols but not column id_cols. "
                          "Updating the column id_cols to include this...", UserWarning)

        # make sure if segmenter is activated we have join_cols defined
        if not self.conf.data.validation_join_cols and self.conf.segmenter.activate and self.conf.data.validation_score_activate:
            warnings.warn("Segmentation's been activated but join_cols are not defined in the scoring_params "
                          "section. Learner will try to use id_cols defined in column section. This could fail if "
                          "those columns have been processed or changed after loading them", UserWarning)
            self.conf.data.validation_join_cols = self.conf.column.id_cols

        validate_subset_cols(use_cols=self.conf.column.valid_cols, subset_cols=self.conf.data.validation_join_cols,
                             subset_cols_name="scoring join_cols")

    def validate_feature_engineering(self):
        if self.conf.feature_engineering.basic_operations_params:
            for item in self.conf.feature_engineering.basic_operations_params:
                # validate only if the item is activated
                if item["activate"]:
                    validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                         subset_cols=item["cols"],
                                         subset_cols_name="basic_operations_cols")

        if self.conf.feature_engineering.log_transform_params:
            for item in self.conf.feature_engineering.log_transform_params:
                # validate only if the item is activated
                if item["activate"]:
                    validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                         subset_cols=[item["col"]],
                                         subset_cols_name="log transform cols")

        if self.conf.feature_engineering.groupby_params:
            for param in self.conf.feature_engineering.groupby_params:
                # validate only if the item is activated
                if param["activate"]:
                    validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                         subset_cols=[param["col"]],
                                         subset_cols_name="groupby cols")
                    for agg in param["aggregation"]:
                        validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                             subset_cols=[agg["col"]],
                                             subset_cols_name="groupby aggregation cols")

    def validate_outlier(self):
        validate_subset_cols(use_cols=self.conf.column.valid_cols,
                             subset_cols=self.conf.outlier.min_max_dict,
                             subset_cols_name="min_max_params")

        validate_subset_cols(use_cols=self.conf.column.valid_cols,
                             subset_cols=self.conf.outlier.quantile_dict,
                             subset_cols_name="quantile_params")

        validate_subset_cols(use_cols=self.conf.column.valid_cols,
                             subset_cols=self.conf.outlier.sd_dict,
                             subset_cols_name="sd_params")

        validate_subset_cols(use_cols=self.conf.column.valid_cols,
                             subset_cols=self.conf.outlier.value_cols.keys(),
                             subset_cols_name="cols_params in value_params")

    def validate_process(self):
        if self.conf.process.fillnan_activate and self.conf.process.fillnan_value_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.fillnan_value_cols.keys(),
                                 subset_cols_name="fillnan cols")

        if self.conf.process.fillnan_activate and self.conf.process.fillnan_mean_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.fillnan_mean_cols,
                                 subset_cols_name="fillnan mean cols")

        if self.conf.process.fillnan_activate and self.conf.process.fillnan_median_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.fillnan_median_cols,
                                 subset_cols_name="fillnan median cols")

        if self.conf.process.fillnan_activate and self.conf.process.fillnan_mode_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.fillnan_mode_cols,
                                 subset_cols_name="fillnan mode cols")

        if self.conf.process.dummies_activate and self.conf.process.dummies_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.dummies_cols,
                                 subset_cols_name="dummies cols")
            # we don't want to process categorical columns for deep learning engines
            if self.conf.process.dummies_activate is True and self.conf.engine in ("DeepClassifier", "DeepRegressor"):
                self.conf.process.dummies_activate = False

        if self.conf.process.to_numeric_activate and self.conf.process.to_numeric_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.to_numeric_cols,
                                 subset_cols_name="to_numeric cols")

        if self.conf.process.label_encoding_activate and self.conf.process.label_encoding_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.label_encoding_cols,
                                 subset_cols_name="label_encoding cols")

        if self.conf.process.tuplize_activate and self.conf.process.tuplize_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.tuplize_cols,
                                 subset_cols_name="tuplize cols")

        if self.conf.process.date_cols_activate and self.conf.process.date_cols_params:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.date_cols_params.keys(),
                                 subset_cols_name="date cols")

        if self.conf.process.standard_scaler_activate and self.conf.process.standard_scaler_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.standard_scaler_cols,
                                 subset_cols_name="standard scaler cols")

        if self.conf.process.min_max_scaler_activate and self.conf.process.min_max_scaler_cols:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=self.conf.process.min_max_scaler_cols,
                                 subset_cols_name="min_max scaler cols")

        count_vectorize_cols = []
        if self.conf.process.count_vectorize_activate:
            for col_param in self.conf.process.count_vectorize_cols_params:
                count_vectorize_cols.append(col_param["name"])
                validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                     subset_cols=[col_param["name"]],
                                     subset_cols_name="count vectorize cols")

        tfidf_cols = []
        if self.conf.process.tfidf_activate:
            for col_param in self.conf.process.tfidf_cols_params:
                tfidf_cols.append(col_param["name"])
                validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                     subset_cols=[col_param["name"]],
                                     subset_cols_name="tfidf cols")

        # make sure count_vectorize and tfidf_cols don't have an intersection
        if self.conf.process.count_vectorize_activate and self.conf.process.tfidf_activate:
            validate_intersection_cols(cols1=count_vectorize_cols,
                                       cols1_name="count_vectorize cols",
                                       cols2=tfidf_cols,
                                       cols2_name="tfidf cols")

    def validate_sample(self):
        if self.conf.sample.split_activate and self.conf.sample.split_method == "sort" and self.conf.sample.split_sort_col:
            validate_subset_cols(use_cols=self.conf.column.valid_cols,
                                 subset_cols=[self.conf.sample.split_sort_col],
                                 subset_cols_name="col in options of train_test_split_params")
