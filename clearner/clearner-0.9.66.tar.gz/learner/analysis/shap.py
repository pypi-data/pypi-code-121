# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements shap analysis using a trained model and the test data. It handles everything from getting,
sorting, and writing the values as well as creating the narratives and possibly plots. The engines commonly do the
instantiation and invocation of the classes and methods.
"""
import pandas as pd
import numpy as np
import warnings
import logging
import shap
from shap.plots._beeswarm import pl

from learner.analysis.plot import Plot
from learner.utilities.timer import timeit
from learner.configuration.configuration import Configuration
from learner.data_worker.output_handler import OutputHandler
from learner.data_worker.data_processor import DataProcessor, parrallelize_dataframe, parrallelize_dataframes
from learner.utilities.templates import SHAP_PLOT, SHAP_PLOT_ClASS, SHAP_PATH


class Shap:
    def __init__(self, models_dict_item, conf: Configuration, processor):
        self._models_dict_item = models_dict_item
        self._conf = conf
        # once populated, this dictionary will map each column name to its average
        self.mean_dict = None
        # this temporarily holds class_name for multiprocessing purposes where we can't pass an argument to a method
        self.class_name = None
        self._processor = processor
        # the list of columns that will be created after sorting the shap values. These are then used for creating the
        # narratives
        self.value_feature_col_list = self.get_value_feature_col_list()

    @property
    def conf(self):
        return self._conf

    @property
    def models_dict_item(self):
        return self._models_dict_item

    @models_dict_item.setter
    def models_dict_item(self, value):
        self._models_dict_item = value

    @property
    def processor(self):
        return self._processor

    def get_value_feature_col_list(self):
        """Get a list of column names that would be added to shap output file during the calculation of sorted shape
        values and features

        :return: a list of column name
        """
        value_feature_col_list = list()
        for i in range(self.conf.analysis.shap_num_features):
            pos_val_name = f"positive_value_{i}"
            pos_feat_name = f"positive_feature_{i}"
            neg_val_name = f"negative_value_{i}"
            neg_feat_name = f"negative_feature_{i}"
            value_feature_col_list.extend([pos_val_name, pos_feat_name, neg_val_name, neg_feat_name])
        return value_feature_col_list

    @timeit("run shap analysis")
    def run_shap(self, test_data, tag):
        """The main driver method for performing shap analysis calculations. This is the only method that is usually
        called after instantiating the Shap object.

        :param test_data: the test dataset. This data set contains the training data as well as the id columns.
        :param tag: the model tag. This is being used to name the files.
        is not being used.
        :return: None
        """
        try:
            explainer = shap.TreeExplainer(self.models_dict_item["model"])
        except Exception:
            warnings.warn("The {model_type} model is not supported for shap analysis yet. Learner will continue with "
                          "the rest of calculations...".format(model_type=self.models_dict_item["type"]), UserWarning)
            return

        logging.info("Getting the shap values...")
        shap_values = explainer.shap_values(test_data[self.models_dict_item["train_features"]])
        # we handle the plots here because in some situations we need only on item in shap_values list and in
        # some situations we need multiple items. Also, we need to plot things before converting shap_values into
        # numpy arrays
        self.handle_plots(tag, shap_values, test_data)
        shap_values = np.array(shap_values)

        # we need the means to use them for storytelling
        self.calculate_the_mean(data=test_data, cols=self.models_dict_item["train_features"])

        if len(shap_values.shape) == 3:
            logging.info("It looks like a model with multiple output was run. Learner will process shap values for "
                         "each output")
            for i, class_name in enumerate(self.models_dict_item["model"].classes_):
                logging.info(f"Processing shap values for class: {class_name}")
                self.process_shap_data(tag, shap_values[i], test_data, class_name=class_name)
        else:
            self.process_shap_data(tag, shap_values, test_data)

    def handle_plots(self, tag, shap_values, test_data):
        """The main method for using shap library and plotting the data. This method checks if plotting functionality
        was activated or not. If it was activated, it continues with the rest of operations.

        :param tag: the model tag. This is being used to name the files.
        :param shap_values: shap values with the same format that comes out of shap library
        :param test_data: the test dataframe
        :return: None
        """
        if not self.conf.analysis.shap_plot_activate:
            logging.info("The shap plotting was not activated, will not plot the data...")
            return

        logging.info("Plotting the shap values...")

        # get the class names if they exist, otherwise set it to None
        try:
            class_names = self.models_dict_item["model"].classes_
        except AttributeError:
            class_names = None

        # try to make bot bar and dot plots
        for plot_type in ["bar", "dot"]:
            logging.info("Making {plot_type} plot for shap values...".format(plot_type=plot_type))

            filename = SHAP_PLOT.format(
                path=self._conf.model.models_dict[tag]["path"],
                output_name=self.conf.workspace.name,
                tag=str(tag),
                type=plot_type,
                sep_timetag=str(self.conf.sep_timetag))
            try:
                # this can fail for dot plot and multi-class classifications problem. In that case, we still want to make
                # the plots but we need to send the data for each class separately.
                shap.summary_plot(shap_values,
                                  test_data[self.models_dict_item["train_features"]],
                                  show=False,
                                  max_display=self.conf.analysis.shap_num_features,
                                  plot_type=plot_type,
                                  class_names=class_names)
                Plot.savefig(filename, pl)
                pl.clf()
            except AssertionError:
                for i, class_name in enumerate(self.models_dict_item["model"].classes_):
                    logging.info("Plotting shap values for class: {c}".format(c=class_name))
                    filename = SHAP_PLOT_ClASS.format(
                        path=self._conf.model.models_dict[tag]["path"],
                        output_name=self.conf.workspace.name,
                        tag=str(tag),
                        type=plot_type,
                        class_name=class_name,
                        sep_timetag=str(self.conf.sep_timetag))
                    shap.summary_plot(shap_values[i],
                                      test_data[self.models_dict_item["train_features"]],
                                      show=False,
                                      max_display=self.conf.analysis.shap_num_features,
                                      plot_type=plot_type,
                                      class_names=class_names)

                    Plot.savefig(filename, pl)
                    pl.clf()

    @timeit("process the shap data")
    def process_shap_data(self, tag, shap_values, test_data, class_name=None):
        """The main method for processing the shap data. This include converting the shap_values numpy arrays in pandas
        dataframe, calling the narrative method to sort the shap values and create the narratives, and saving the final
        data to disk (by calling the write_shap method)

        :param tag: the model tag. This is being used to name the files.
        :param shap_values: a numpy array that contain shap values
        :param test_data: the test dataframe
        :param class_name: the label of the class for classification problems
        :return: None
        """
        logging.info("Processing the shap data...")

        shap_df = pd.DataFrame(data=shap_values, columns=self.models_dict_item["train_features"])
        if self.conf.analysis.shap_include_sorted_values or self.conf.analysis.shap_narrative_activate:
            logging.info("Obtaining the important features and the corresponding shap values for each data point...")
            shap_df = parrallelize_dataframe(shap_df, self.handle_feature_importance)
            # this is the serial code
            # shap_df = self.handle_feature_importance(shap_df)

        if not self.conf.analysis.shap_narrative_activate:
            logging.info("The shap narrative functionality was not activated, learner will not generate stories")
        else:
            logging.info("Creating narratives for each data point...")
            self.class_name = class_name

            shap_df, test_data = parrallelize_dataframes(shap_df, test_data, self.handle_narrative)
            # this is the serial code
            # self.create_narrative(shap_df, test_data[self.models_dict_item["train_features"]], class_name=class_name if class_name is not None else "target")
        self.write_shap(tag, shap_df, test_data[self.conf.column.id_cols], class_name="_{c}".format(c=class_name) if class_name is not None else '')

    @timeit("compute the mean of the columns")
    def calculate_the_mean(self, data, cols):
        """Accept a dataframe and a list of column. If use_training_mean was set to true, get the mean_dict
        (a dictionary in which the key is the column name and the value is the average value of that column), otherwise
        compute the mean of each column and save them to populate mean_dict.

        :param data: a pandas dataframe
        :param cols: a list of columns to do the calculations
        :return: None
        """
        # we don't need to calculate the mean if narrative is not active
        if not self.conf.analysis.shap_narrative_activate:
            return
        if self.conf.analysis.shap_use_training_mean:
            logging.info("Using the mean of features from the training data to use in narratives.")
            self.mean_dict = self.processor.mean_dict
        else:
            logging.info("Calculating the mean of each feature in test data to use in narratives...")
            processor = DataProcessor(self.conf)
            processor.handle_mean(data[cols])
            self.mean_dict = processor.mean_dict

    def handle_feature_importance(self, shap_df):
        """Use apply method to make a call to _get_important_features method to obtain the important features along with
        their corresponding shap values.

        :param shap_df: the shap dataframe
        :return: updated shap dataframe
        """
        num_features = min(self.conf.analysis.shap_num_features, shap_df.shape[1])
        for i in range(num_features):
            shap_df[f"positive_value_{i}"] = -np.inf
            shap_df[f"positive_feature_{i}"] = -np.inf

            shap_df[f"negative_value_{i}"] = -np.inf
            shap_df[f"negative_feature_{i}"] = -np.inf

        for index, row in shap_df.iterrows():
            sorted_row = row.sort_values(inplace=False, ascending=False)
            for i in range(num_features):
                shap_df.loc[index, f"positive_value_{i}"] = sorted_row.iloc[i] if sorted_row.iloc[i] > 0 else None
                shap_df.loc[index, f"positive_feature_{i}"] = sorted_row.index[i] if sorted_row.iloc[i] > 0 else None

                # 4*num_features is because of the new columns we just created, which will go to the end because of
                # -np.inf
                shap_df.loc[index, f"negative_value_{i}"] = sorted_row.iloc[-1 - i - 4*num_features] if sorted_row.iloc[-1 - i - 4*num_features] < 0 else None
                shap_df.loc[index, f"negative_feature_{i}"] = sorted_row.index[-1 - i - 4*num_features] if sorted_row.iloc[-1 - i - 4*num_features] < 0 else None

        return shap_df

    def handle_narrative(self, shap_df, test_data):
        """Use shap_df and test_data to create the narratives. This method calls create_narrative method to do the work.

        :param shap_df: the shap data frame
        :param test_data: the test dataframe
        :return: updated shap and test_data
        """
        self.create_narrative(shap_df, test_data[self.models_dict_item["train_features"]], class_name=self.class_name if self.class_name is not None else "target")
        return shap_df, test_data

    def create_narrative(self, shap_df, test_df, class_name):
        """The main method that drives generation of the narratives. This method extract the templates and the generic
        messages, and calls narrative_analysis method to add the narrative to the shap data frame.

        :param shap_df: the shap dataframe
        :param test_df: the test dataframe
        :param class_name: the name of the class if we have a multiclass classification problem, or "target" otherwise
        :return: None
        """
        try:
            templates = self.conf.analysis.shap_narrative_stories[class_name]["templates"]
            generic = self.conf.analysis.shap_narrative_stories[class_name]["generic"]
            self._narrative_analysis(shap_df, test_df[self.models_dict_item["train_features"]], templates, generic)
        except KeyError:
            # Note: this warning may not show in the log file due to the mechanism for multiprocessing
            warnings.warn("No narrative parameters for the class {class_name} was provided. Learner will create generic "
                          "narrative for this class. Please update your configuration file if you'd like to create custom "
                          "narratives.".format(class_name=class_name), Warning)
            self._narrative_analysis(shap_df, test_df[self.models_dict_item["train_features"]], [], None)

    def _narrative_analysis(self, shap_df, test_df, templates, generic):
        """Iterate through shap dataframe and test dataframe concurrently and make a call to _get_narrative method to
        get the text for the narrative. Then add that narrative to shap dataframe

        :param shap_df: the shap dataframe with all sorted and unsorted features (we don't use the unsorted columns)
        :param test_df: the test dataframe that include all features. This dataframe is being used to pull the actual numbers
        :param templates: the list of templates. The first matched item will be used from this list
        :param generic: the generic narrative message
        :return: None
        """
        for (i, shap_row), (_, test_row) in zip(shap_df.iterrows(), test_df.iterrows()):
            narrative = self._get_narrative(shap_row, test_row, templates, generic)
            shap_df.loc[i, "narrative"] = narrative

    def _get_narrative(self, shap_row, test_row, templates, generic):
        """Get the narrative text. To do this, we first get the positive and negative features. Knowing the positive and negative features,
        we go through the templates one by one. If that template is a match, we replace the templates with appropriate
        values and return the narrative. If there's no match we return the generic narrative.

        :param shap_row: a row in the shap dataframe
        :param test_row: a row in the test dataset
        :param templates: the list of templates provided in the configuration file
        :param generic: the generic narrative. Currently, we just return it but in the future we may want to get more creative with it.
        :return: the narrative - custom or generic
        """
        # we take care of exclude_cols here
        positive_features = {}
        for i, feature in enumerate(shap_row.index):
            if (str(feature).startswith("positive_feature_") and
                    shap_row.iloc[i] and
                    shap_row.iloc[i] not in self.conf.analysis.shap_exclude_cols and
                    not isinstance(shap_row.iloc[i], float)):

                feature_index = feature.rsplit("_")[-1]
                positive_features[shap_row.iloc[i]] = shap_row["positive_value_{i}".format(i=feature_index)]

        negative_features = {}
        for i, feature in enumerate(shap_row.index):
            if (str(feature).startswith("negative_feature_") and
                    shap_row.iloc[i] and
                    shap_row.iloc[i] not in self.conf.analysis.shap_exclude_cols and
                    not isinstance(shap_row.iloc[i], float)):

                feature_index = feature.rsplit("_")[-1]
                negative_features[shap_row.iloc[i]] = shap_row["negative_value_{i}".format(i=feature_index)]

        # this list will hold all the narratives for the importance method
        importance_narratives = []
        for template in templates:
            if self._is_match(template, positive_features.keys(), negative_features.keys(), test_row):
                if self.conf.analysis.shap_narrative_method == "order":
                    kwargs = self._construct_kwargs(template, test_row)
                    narrative = template["narrative"].format(**kwargs)
                    return narrative
                elif self.conf.analysis.shap_narrative_method == "importance":
                    score = self._get_match_score(template, positive_features, negative_features)
                    importance_narratives.append((template, score))

        # if we found a match for "importance" method
        if importance_narratives:
            template = sorted(importance_narratives, key=lambda x: x[1])[-1][0]
            kwargs = self._construct_kwargs(template, test_row)
            narrative = template["narrative"].format(**kwargs)
            return narrative

        # if no generic provided, we build a generic narrative using data
        if not generic:
            return self._build_generic_narrative_with_data(test_row, positive_features, negative_features)
        # if a generic narrative was provided and we didn't have a match, we return that generic narrative
        return generic

    @staticmethod
    def _get_match_score(template, positive_features, negative_features):
        """For the narratives that there's a match, compute the match score but adding the absolute shap values
        together.

        :param template: an item in the templates list provided in the configuration file.
        :param positive_features: a dictionary in which the keys are features with the highest positive values and the
          values are the shap values for those features
        :param negative_features: a dictionary in which the keys are features with the highest negative values and the
          values are the shap values for those features
        :return: the score of the matched narrative
        """
        score = 0
        for feature, value in template["features"].items():
            try:
                score += abs(positive_features[feature])
            except KeyError:
                score += abs(negative_features[feature])

        return score

    @staticmethod
    def _is_match(template, positive_features, negative_features, test_row):
        """Accept a template item and go through all the features in the template. If all the features, their shap
        category (positive or negative) and their values (if defined) matches the one predicted by the model,
        then return true. If there's any mismatched, return false.

        :param template: an item in the templates list provided in the configuration file.
        :param positive_features: a dictionary in which the keys are features with the highest positive values and the
          values are the shap values for those features
        :param negative_features: a dictionary in which the keys are features with the highest negative values and the
          values are the shap values for those features
        :param test_row: a row in the test dataset
        :return: a boolean indicating if we have a match or not
        """
        while True:
            for feature, value in template["features"].items():
                if value["impact"] == "positive" and feature not in positive_features:
                    return False
                if value["impact"] == "negative" and feature not in negative_features:
                    return False
                # if values are defined but the value for the feature does not exist in the list, return false
                if value["values"] and test_row.loc[feature] not in value["values"]:
                    return False
            return True

    def _construct_kwargs(self, template, test_row):
        """Create a kwargs dictionary to be used for replacing the templates with actual values. Currently, each
        templates accepts templates corresponding to the features in the "features" section of the template item.
        We need to replace each template with their actual values.

        :param template: a template item in templates list
        :param test_row: a row in the test dataframe
        :return: a dictionary of the keyword arguments
        """
        kwargs = {}
        for feature, value in template["features"].items():
            if value["include_mean"]:
                kwargs[feature] = "{value} (avg: {average:.3f})".format(value=test_row.loc[feature], average=self.mean_dict[feature])
            else:
                kwargs[feature] = "{value}".format(value=test_row.loc[feature])
        return kwargs

    def _build_generic_narrative_with_data(self, test_row, positive_features, negative_features):
        """Build a generic narrative based on the sign of the shap values. Basically, the narrative says what features
        are driving the prediction up (with positive shap values) and what features are driving the predictions down
        (with negative shap values). It prints out the name of those features along with their value and the average
        of the cohort, i.e. the test data we are making the predictions for.

        :param test_row: a row in the test dataset
        :param positive_features: a list of features with positive shap values
        :param negative_features: a list of features with negative shap values
        :return: the text of the narrative that says which features driving the predictions up or down
        """
        narrative = []
        if positive_features:
            narrative.append("These features are driving the predictions up:")
            for feature in positive_features:
                narrative.append(feature)
                narrative.append("(val: {value}, avg: {average:.3f}),".format(value=test_row[feature],
                                                                        average=self.mean_dict[feature]))

        if negative_features:
            narrative.append("\nThese features are driving the predictions down:")
            for feature in negative_features:
                narrative.append(feature)
                narrative.append("(val: {value}, avg: {average:.3f}),".format(value=test_row[feature],
                                                                            average=self.mean_dict[feature]))

        return " ".join(narrative)

    @timeit("write the shap output")
    def write_shap(self, tag, shap_df, data, class_name=''):
        """Write the shap dataframe along with any additional columns (typically id columns) to disk. This method also
        makes a call to drop_cols method of the DataProcessor class to drop the unsorted column if not requested.

        :param tag: the model tag defined by user in the configuration file.
        :param shap_df: the shap dataframe
        :param data: the additional data to be concatenated with the shap dataframe. This is typically id columns
        :param class_name: the class name in case of multi-class classification problem.
        :return: None
        """
        logging.info("Writing the shap output data...")
        # we need to drop the unsorted columns if the user hasn't asked for it
        if not self.conf.analysis.shap_include_raw_values:
            DataProcessor.drop_cols(shap_df, list(self.models_dict_item["train_features"]))
        if not self.conf.analysis.shap_include_sorted_values:
            DataProcessor.drop_cols(shap_df, self.value_feature_col_list, errors="ignore")

        data.reset_index(drop=True, inplace=True)
        shap_df.reset_index(drop=True, inplace=True)
        results = pd.concat([data, shap_df], axis=1, ignore_index=False)

        filename = SHAP_PATH.format(
            output_name=self._conf.workspace.name,
            tag=str(tag),
            class_name=class_name,
            sep_timetag=str(self._conf.sep_timetag))

        output = OutputHandler(self._conf)
        output.save_file(self._conf.model.models_dict[tag]["path"], filename, results, add_timetag=False)
        logging.info("Successfully wrote the shap output data")
