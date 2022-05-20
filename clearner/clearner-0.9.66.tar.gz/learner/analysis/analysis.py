# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module to analyze the data as well as the models. This module commonly talks to the plot module to
visualize the results of the analysis
"""
import pandas as pd
import numpy as np
import warnings
import logging

from learner.configuration.configuration import Configuration
from learner.data_worker.output_handler import OutputHandler
from learner.analysis.plot import Plot
from learner.utilities.templates import PREDICTIONS_VS_ACTUALS_PLOT
from learner.model_manager.scoring_manager import RegressorScorer


class Analysis:
    """Implement the methods for analyzing the data and the models. Some of the methods here such as handle_feature_importance
    are being called by the engines."""
    def __init__(self, conf: Configuration):
        """Instantiate an analysis object using the conf object"""
        self._conf = conf

    @property
    def conf(self):
        return self._conf

    def handle_feature_importance(self, mdl, filename):
        """Accept an item in the  models_dict, use the trained model object there to get and save the feature importance.
        If a model does not have the feature_importance_ attribute, issue a warning and return. This method also uses
        the Plot class to plot the results if requested by user.

        :param mdl: an item in the models_dict
        :param filename: the full path to the file that should be used to save the data and plot. This parameter should not
        include the file extension.
        :return: None
        """
        logging.info("Getting feature importance and saving it to the disk...")
        try:
            importances_df = pd.DataFrame(data={"feature": mdl["train_features"],
                                                "importance": mdl["model"].feature_importances_})\
                .sort_values('importance', ascending=False).reset_index(drop=True)

            output = OutputHandler(self._conf)
            full_name = filename + ".csv"
            output.save_file(mdl["path"], full_name, importances_df, add_timetag=False)
            logging.info("The feature importance data was saved in {full_name}".format(full_name=full_name))
        except AttributeError:
            warnings.warn("Feature importance was requested for {model_type} but this model does not provide "
                            "feature importance. Trying to continue...".format(model_type=mdl["type"]), UserWarning)
            return

        if self.conf.analysis.importance_plot_activate:
            logging.info("Plotting the feature importance...")
            # get the top n features
            importances_df = importances_df.iloc[:self.conf.analysis.importance_plot_num_features, :]
            nfeatures = np.arange(importances_df.shape[0])
            plot = Plot(self.conf)
            plot.barh(importances_df["importance"],
                      importances_df["feature"],
                      mdl["path"] + filename+".png",
                      yrange=nfeatures,
                      color=self.conf.analysis.importance_plot_color,
                      width=self.conf.analysis.importance_plot_width or 12,
                      height=self.conf.analysis.importance_plot_height or importances_df.shape[0]/2,
                      xlabel="Feature Importance")

    def handle_missing_values(self, data):
        """Accept a pandas dataframe and compute the count and the ratio of the missing values for all columns in the
        dataframe. Then save the data to disk in csv format and if requested, plot the data using a horizontal bar
        chart.

        :param data: a pandas dataframe
        :return: None
        """
        logging.info("Getting missing values and saving it to the disk...")
        try:
            # get the count of missing values
            missing_df = data.isnull().sum(axis=0).reset_index()
            missing_df.columns = ["feature", "missing_count"]
            missing_df['missing_ratio'] = (missing_df["missing_count"] / data.shape[0])
            missing_df = missing_df.sort_values(by='missing_ratio', ascending=False)
            # save data to disk
            output = OutputHandler(self._conf)
            output.save_file(self.conf.analysis.analysis_directory,
                             self.conf.analysis.missing_filename,
                             missing_df, add_timetag=False)
            logging.info("The missing values data was saved in {filename}".format(filename=self.conf.analysis.missing_filename))
        except Exception as e:
            logging.error("Something went wrong while obtaining the missing values. The error is {error}".format(error=str(e)))
            return

        if self.conf.analysis.missing_plot_activate:
            logging.info("Plotting the missing value data...")
            # get the top n features
            missing_df = missing_df.iloc[:self.conf.analysis.missing_plot_num_features, :]
            nfeatures = np.arange(missing_df.shape[0])
            plot = Plot(self.conf)
            plot.barh(missing_df["missing_ratio"],
                      missing_df["feature"],
                      self.conf.analysis.analysis_directory + self.conf.analysis.missing_plotname,
                      yrange=nfeatures,
                      color=self.conf.analysis.missing_plot_color,
                      width=self.conf.analysis.missing_plot_width or 12,
                      height=self.conf.analysis.missing_plot_height or missing_df.shape[0]/2,
                      xlabel="Missing Ratio")

    def handle_correlation(self, data):
        """Accept a pandas dataframe and compute the correlation coefficient between the features defined in the
        configuration file. Then save the data to disk in csv format and if requested, plot the data using heatmap.

        :param data: a pandas dataframe
        :return: None
        """
        logging.info("Computing the correlation coefficients and saving them to disk...")
        try:
            # compute pearson correlation (the default method when calling corr) coefficient.
            corr = data[self.conf.analysis.correlation_cols].corr()

            # build the mask matrix so that there won't be any duplicates in the plot. We still save everything to disk.
            mask = np.zeros_like(corr)
            mask[np.triu_indices_from(mask, 1)] = True

            # save data to disk
            output = OutputHandler(self._conf)
            output.save_file(self.conf.analysis.analysis_directory,
                             self.conf.analysis.correlation_filename,
                             corr, add_timetag=False, index=True)
            logging.info("The correlation coefficients data was saved in {filename}".format(filename=self.conf.analysis.correlation_filename))
        except Exception as e:
            logging.error("Something went wrong while calculating the correlation coefficients. The error is {error}".format(error=str(e)))
            return

        if self.conf.analysis.correlation_plot_activate:
            logging.info("Plotting the correlation coefficients data...")

            plot = Plot(self.conf)
            plot.correlation_heatmap(corr,
                                     filename=self.conf.analysis.analysis_directory + self.conf.analysis.correlation_plotname,
                                     width=self.conf.analysis.correlation_plot_width or corr.shape[0]/2,
                                     height=self.conf.analysis.correlation_plot_height or corr.shape[0]/2,
                                     x_labelsize=self.conf.analysis.correlation_plot_x_labelsize or corr.shape[0]/2,
                                     y_labelsize=self.conf.analysis.correlation_plot_y_labelsize or corr.shape[0]/2,
                                     annot_size=self.conf.analysis.correlation_plot_annotation_size or corr.shape[0]/2,
                                     vmin=self.conf.analysis.correlation_plot_vmin,
                                     vmax=self.conf.analysis.correlation_plot_vmax,
                                     mask=mask)

    def handle_predictions_vs_actuals_plot(self, tag, mdl):
        """Accept an item of the models_dict (tag and mdl) to handle the predictions vs actuals plot. The mdl dictionary
        and the conf object contain all the necessary information. Because this plot is very identical to scoring the
        predictions (we need y_true and y_pred to do something with them), this method leverages the RegressorScorer
        class to load the necessary data.

        :param tag: a tag (key) in the models_dict item
        :param mdl: a mdl dictionary (the value for the tag) the models_dict
        :return: None
        """
        logging.info("Plotting the predictions vs actuals graph...")
        # the regressor_scorer object will load the actuals and true values for us and apply the log transformation
        # logic if needed
        regressor_scorer = RegressorScorer(self._conf, None)

        pred_filename = mdl["path"] + self._conf.workspace.name + "_validation_" + str(tag) + str(self._conf.sep_timetag) + ".csv"
        regressor_scorer.load_pred(pred_filename)

        plot_filename = PREDICTIONS_VS_ACTUALS_PLOT.format(
            path=mdl["path"],
            output_name=self._conf.workspace.name,
            tag=str(tag),
            sep_timetag=str(self._conf.sep_timetag))

        plot = Plot(self._conf)
        plot.predictions_vs_actuals(regressor_scorer.y_true,
                                    regressor_scorer.pred,
                                    filename=plot_filename,
                                    width=self.conf.analysis.predictions_vs_actuals_width,
                                    height=self.conf.analysis.predictions_vs_actuals_height,
                                    x_label=self.conf.analysis.predictions_vs_actuals_x_label or regressor_scorer.y_true.columns[0],
                                    y_label=self.conf.analysis.predictions_vs_actuals_y_label or regressor_scorer.pred.columns[0],
                                    x_labelsize=self.conf.analysis.predictions_vs_actuals_x_labelsize,
                                    y_labelsize=self.conf.analysis.predictions_vs_actuals_y_labelsize,
                                    color=self.conf.analysis.predictions_vs_actuals_symbol_color,
                                    size=self.conf.analysis.predictions_vs_actuals_symbol_size,
                                    xy_min=self.conf.analysis.predictions_vs_actuals_xy_min,
                                    xy_max=self.conf.analysis.predictions_vs_actuals_xy_max)

    def analyze_data(self, data):
        """The main driver method for calling other methods and running the analysis on data. The method is typically
        called by data_manage module before processing the data. Some methods in this class need to be called after
        model training. As such, this method won't call them.

        :param data: a pandas dataframe (this is usually training data)
        :return: None
        """
        if self.conf.analysis.missing_activate:
            self.handle_missing_values(data)

        if self.conf.analysis.correlation_activate:
            self.handle_correlation(data)
