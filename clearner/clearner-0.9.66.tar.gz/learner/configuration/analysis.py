# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import os
import re
import warnings
import logging

from learner.data_worker.data_loader import get_value
from learner.configuration.workspace import WorkspaceConfiguration
from learner.configuration.data import DataConfiguration
from learner.configuration.column import ColumnConfiguration
from learner.validator.input_validator import validate_subset_list, validate_intersection_cols
from learner.configuration.supported_items import SUPPORTED_NARRATIVE_METHODS, SUPPORTED_ENGINE_FOR_PREDICTIONS_VS_ACTUALS_PLOT


class AnalysisConfiguration:
    def __init__(self, json_config, column: ColumnConfiguration, workspace: WorkspaceConfiguration,
                 data: DataConfiguration, sep_timetag, engine):
        self._json_config = json_config
        self._column = column
        self._workspace = workspace
        self._data = data
        self._sep_timetag = sep_timetag
        self._engine = engine

        self.importance_activate = get_value(self._json_config, False, "analysis", "feature_importance_params", "activate")
        self.importance_plot_activate = get_value(self._json_config, False, "analysis", "feature_importance_params", "plot_params", "activate")
        self.importance_plot_num_features = get_value(self._json_config, 10, "analysis", "feature_importance_params", "plot_params", "num_features")
        self.importance_plot_color = get_value(self._json_config, "blue", "analysis", "feature_importance_params", "plot_params", "options", "color")
        self.importance_plot_width = get_value(self._json_config, None, "analysis", "feature_importance_params", "plot_params", "options", "width")
        self.importance_plot_height = get_value(self._json_config, None, "analysis", "feature_importance_params", "plot_params", "options", "height")

        self.analysis_directory = self.get_analysis_directory()

        self.missing_activate = get_value(self._json_config, False, "analysis", "missing_values_params", "activate")
        self.missing_plot_activate = get_value(self._json_config, False, "analysis", "missing_values_params", "plot_params", "activate")
        self.missing_plot_num_features = get_value(self._json_config, 10, "analysis", "missing_values_params", "plot_params", "num_features")
        self.missing_plot_color = get_value(self._json_config, "blue", "analysis", "missing_values_params", "plot_params", "options", "color")
        self.missing_plot_width = get_value(self._json_config, None, "analysis", "missing_values_params", "plot_params", "options", "width")
        self.missing_plot_height = get_value(self._json_config, None, "analysis", "missing_values_params", "plot_params", "options", "height")
        self.missing_filename = "missing_values{sep_timetag}.csv".format(sep_timetag=self.sep_timetag)
        self.missing_plotname = "missing_values{sep_timetag}.png".format(sep_timetag=self.sep_timetag)

        self.correlation_activate = get_value(self._json_config, False, "analysis", "correlation_params", "activate")
        self.correlation_plot_activate = get_value(self._json_config, False, "analysis", "correlation_params", "plot_params", "activate")
        self.correlation_cols = self.get_correlation_cols()
        self.correlation_plot_width = get_value(self._json_config, None, "analysis", "correlation_params", "plot_params", "options", "width")
        self.correlation_plot_height = get_value(self._json_config, None, "analysis", "correlation_params", "plot_params", "options", "height")
        self.correlation_plot_vmin = get_value(self._json_config, None, "analysis", "correlation_params", "plot_params", "options", "vmin")
        self.correlation_plot_vmax = get_value(self._json_config, None, "analysis", "correlation_params", "plot_params", "options", "vmax")
        self.correlation_plot_x_labelsize = get_value(self._json_config, None, "analysis", "correlation_params", "plot_params", "options", "x_labelsize")
        self.correlation_plot_y_labelsize = get_value(self._json_config, None, "analysis", "correlation_params", "plot_params", "options", "y_labelsize")
        self.correlation_plot_annotation_size = get_value(self._json_config, None, "analysis", "correlation_params", "plot_params", "options", "annotation_size")
        self.correlation_filename = "correlation{sep_timetag}.csv".format(sep_timetag=self.sep_timetag)
        self.correlation_plotname = "correlation{sep_timetag}.png".format(sep_timetag=self.sep_timetag)

        self.shap_activate = self.get_shap_activate()
        self.shap_num_features = get_value(self._json_config, 10, "analysis", "shap_params", "num_features")
        self.shap_narrative_activate = get_value(self._json_config, False, "analysis", "shap_params", "narrative_params", "activate")
        self.shap_include_raw_values = get_value(self._json_config, False, "analysis", "shap_params", "include_raw_values")
        self.shap_plot_activate = get_value(self._json_config, False, "analysis", "shap_params", "plot_params", "activate")
        self.shap_include_sorted_values = self.get_shap_include_sorted_values()
        self.shap_exclude_cols = self.get_shap_exclude_cols()
        self.shap_use_training_mean = get_value(self._json_config, False, "analysis", "shap_params", "use_training_mean")
        self.shap_narrative_stories = self.get_shape_narrative_stories()
        self.shap_narrative_method = self.get_shape_narrative_method()

        self.predictions_vs_actuals_activate = self.get_predictions_vs_actuals_activate()
        self.predictions_vs_actuals_width = get_value(self._json_config, 10, "analysis", "predictions_vs_actuals_params", "width")
        self.predictions_vs_actuals_height = get_value(self._json_config, 10, "analysis", "predictions_vs_actuals_params", "height")
        self.predictions_vs_actuals_x_labelsize = get_value(self._json_config, 10, "analysis", "predictions_vs_actuals_params", "x_labelsize")
        self.predictions_vs_actuals_y_labelsize = get_value(self._json_config, 10, "analysis", "predictions_vs_actuals_params", "y_labelsize")
        self.predictions_vs_actuals_x_label = get_value(self._json_config, None, "analysis", "predictions_vs_actuals_params", "x_label")
        self.predictions_vs_actuals_y_label = get_value(self._json_config, None, "analysis", "predictions_vs_actuals_params", "y_label")
        self.predictions_vs_actuals_xy_min = get_value(self._json_config, None, "analysis", "predictions_vs_actuals_params", "xy_min")
        self.predictions_vs_actuals_xy_max = get_value(self._json_config, None, "analysis", "predictions_vs_actuals_params", "xy_max")
        self.predictions_vs_actuals_symbol_size = get_value(self._json_config, 1, "analysis", "predictions_vs_actuals_params", "symbol_size")
        self.predictions_vs_actuals_symbol_color = get_value(self._json_config, "blue", "analysis", "predictions_vs_actuals_params", "symbol_color")

    @property
    def json_config(self):  # pragma: no cover
        return self._json_config

    @property
    def output(self):
        return self._workspace

    @property
    def sep_timetag(self):
        return self._sep_timetag

    def get_analysis_directory(self):  # pragma: no cover
        # create a directory called "analysis" under output.path to save the analysis data and plots. Note that feature
        # importance does not stay in this directory because it is specific to each model.
        analysis_directory = self.output.path + "analysis/"
        if not os.path.exists(analysis_directory):
            os.makedirs(analysis_directory)
        return analysis_directory

    def get_correlation_cols(self):
        try:
            correlation_cols = self._json_config["analysis"]["correlation_params"]["cols"]
            return correlation_cols
        except KeyError:
            return self._column.use_cols

    def get_shap_activate(self):
        try:
            activate = self._json_config["analysis"]["shap_params"]["activate"]
            if activate:
                warnings.warn("shap analysis was activated. Learner will attempt to load the entire test dataset. "
                              "Please ensure you have enough resources available", Warning)
                # setting the chunksize to a big number so that the entire test data will be loaded
                self._data.test_chunksize = 9000000000
            return activate
        except KeyError:
            return False

    def get_shap_include_sorted_values(self):
        include_sorted_values = get_value(self._json_config, False, "analysis", "shap_params", "include_sorted_values")
        if self.shap_activate and not (include_sorted_values or self.shap_include_raw_values or
                                       self.shap_narrative_activate or self.shap_plot_activate):
            logging.critical("shape feature was activated but include_sorted_values and include_raw_values were "
                             "set to false and narrative was not activated. Please set one of these to true or "
                             "deactivate shap feature. Exiting...")
            sys.exit(1)
        return include_sorted_values

    def get_shap_exclude_cols(self):
        try:
            exclude_cols = self._json_config["analysis"]["shap_params"]["exclude_cols"]
            return exclude_cols
        except KeyError:
            return []

    def get_shape_narrative_stories(self):
        if not self.shap_narrative_activate:
            return None
        # this is the pattern for finding the values between curly braces
        pattern = re.compile("{(.*?)}")
        try:
            shap_narrative_stories = self._json_config["analysis"]["shap_params"]["narrative_params"]["stories"]
            # if there's only one item, make sure the key is called "target"
            if len(shap_narrative_stories) == 1:
                shap_narrative_stories["target"] = shap_narrative_stories.pop(next(iter(shap_narrative_stories)))
            # make sure each item has "templates" and "generic" keys
            for class_name, stories in shap_narrative_stories.items():
                validate_subset_list(parent_list=["templates", "generic"], parent_name="required items in stories",
                                     subset_list=stories.keys(), subset_name="provided items")
                # these two lines make generic and template keys optional
                stories["generic"] = stories.get("generic", None)
                stories["templates"] = stories.get("templates", [])
                # make sure there's no template in the generic text
                results = re.findall(pattern, stories["generic"]) if stories["generic"] else None
                if results:
                    logging.error("Learner does not accept template in generic text. These items were found: {items}".
                                  format(items=results))
                    sys.exit(1)
                # make sure the templates are lists
                if not isinstance(stories["templates"], list):
                    logging.error("The templates in stories section must be lists not {type}. Exiting...".
                                  format(type=type(stories["templates"])))
                    sys.exit(1)
                # validate the templates
                self._validate_shap_templates(stories, pattern)
            return shap_narrative_stories
        except KeyError:
            return {'target': {'generic': None, 'templates': []}}

    def _validate_shap_templates(self, stories, pattern):
        for item in stories["templates"]:
            # make sure "features" and "narrative" exist in all dictionaries in the templates list
            validate_subset_list(parent_list=["features", "narrative"], parent_name="required items in templates",
                                 subset_list=item.keys(), subset_name="provided items")
            # make sure the exclude_cols and features columns don't have an intersection
            validate_intersection_cols(cols1=item["features"].keys(), cols2=self.shap_exclude_cols,
                                       cols1_name="features columns", cols2_name="exclude_cols")
            # make sure if the features are defined, the narrative is not missing
            if len(item["features"]) > 0 and "narrative" not in item:
                logging.error('The "features" are defined in an item in the templates but "narrative" is missing. '
                              'Please update the configuration file. Exiting...')
                sys.exit(1)
            # make sure the values for each column in features in positive or negative
            acceptable_values = {"p": "positive", "n": "negative"}
            for feature, value in item["features"].items():
                if isinstance(value, str):
                    feature_value = value.lower()
                    if feature_value in acceptable_values.values():
                        item["features"][feature] = {"impact": feature_value, "include_mean": True, "values": []}
                    else:
                        try:
                            item["features"][feature] = {"impact": acceptable_values[feature_value[0]], "include_mean": True, "values": []}
                        except KeyError:
                            logging.error('The value for feature {feature} should be ("positive" or "negative"). '
                                          'The value "{value}" is not understood'.format(feature=feature, value=value))
                            sys.exit(1)

                elif isinstance(value, dict):
                    validate_subset_list(parent_list=["impact", "include_mean", "values"],
                                         parent_name="required items in templates features",
                                         subset_list=value.keys(), subset_name="provided items")

                    # get the values for values, include_mean, and shap or use the defaults
                    item["features"][feature]["values"] = value.get("values", [])
                    item["features"][feature]["include_mean"] = value.get("include_mean", True)
                    item["features"][feature]["impact"] = value.get("impact", None)
                    # make sure the provided values have the correct type
                    assert isinstance(value["values"], list), "the values field for feature {feature} must be a list".format(feature=feature)
                    assert isinstance(value["include_mean"], bool), "the include_mean for feature {feature} must be boolean".format(feature=feature)
                    assert isinstance(value["impact"], str), "the shap field for feature {feature} must be string".format(feature=feature)
                    # try to infer the value for the shap field if the provided value is not acceptable
                    if value["impact"].lower() not in acceptable_values.values():
                        try:
                            item["features"][feature]["impact"] = acceptable_values[value["impact"][0]]
                        except KeyError:
                            logging.error('The impact field for feature {feature} should be ("positive" or "negative"). '
                                          '"{value}" is not understood'.format(feature=feature, value=value["impact"]))
                            sys.exit(1)

                else:
                    logging.error("The value for features items {feature} should be a string or a dictionary, "
                                  "found {type}".format(feature=feature, type=type(value)))
                    sys.exit(1)

    def get_shape_narrative_method(self):
        try:
            method = self._json_config["analysis"]["shap_params"]["narrative_params"]["method"]
            validate_subset_list(parent_list=SUPPORTED_NARRATIVE_METHODS, parent_name="valid narrative methods",
                                 subset_list=[method], subset_name="provided narrative method")
            return method
        except KeyError:
            return "order"

    def get_predictions_vs_actuals_activate(self):
        try:
            activate = self._json_config["analysis"]["predictions_vs_actuals_params"]["activate"]
            if activate:
                validate_subset_list(parent_list=SUPPORTED_ENGINE_FOR_PREDICTIONS_VS_ACTUALS_PLOT,
                                     parent_name="acceptable engines for plotting predictions vs actuals",
                                     subset_list=[self._engine],
                                     subset_name="defined engine")
                if not self._data.validation_score_activate:
                    logging.critical("scoring_params in validation_params was not activated. Learner will not make "
                                     "predictions and therefore cannot plot predictions vs actuals. Please update "
                                     "your configuration file and try again. Exiting...")
                    sys.exit(1)
            return activate
        except KeyError:
            return False
