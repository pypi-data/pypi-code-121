# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Given a similarity matrix, and predictions of a classifier, this module extends the prediction to a certain number
defined by the user"""

from operator import itemgetter
import warnings
import logging
import pandas as pd
import numpy as np


class Extenders:

    def __init__(self, mdl, conf):
        """This classes receives a MultilabelBinarizer object, a trained classifier, and a similarity matrix to
        extend the predictions of the classifier."""

        self._mdl = mdl
        self._conf = conf

    @property
    def mdl(self):
        return self._mdl

    @property
    def conf(self):
        return self._conf

    def extend(self, column_name):
        """The main function for extending the predictions.

        :return: An updated Learner classifier, which holds the extended predictions
        """
        logging.info("Extending the predictions")

        # use the previously trained mlb object to binarize the predictions of the model
        prediction_mlb = pd.DataFrame(self._mdl["mlb_obj"].transform(self._mdl["prediction"]), columns=self._mdl["mlb_obj"].classes_)
        # use the similarity matrix to compute the similarity scores for all items in the model and each row in the
        # prediction array
        sim_scores = self.get_similarity_scores(prediction_mlb, self._mdl["sim_matrix"], columns=self._mdl["mlb_obj"].classes_)

        # check whether the number of basket extension in config is larger than the predicted number of baskets
        if self._conf.recommender.num_recs > sim_scores.shape[1]:
            warnings.warn("The number of recommendations provided in the json config exceeds the maximum number of "
                          "recommendations provided by Learner, which is equals to {0}".format(sim_scores.shape[1]), Warning)

        # use the columns of the mlb object, the similarity scores, and the binarized rows to make a tuple
        # note: the sorted_sim_scores does not contain the sorted value yet. It gets sorted in the next step
        sorted_sim_scores = self.tuplize_scores_predictions_for_sorting(prediction_mlb, sim_scores)

        # get the extended predictions
        self._mdl["extended_prediction"] = self.get_extended_prediction(sorted_sim_scores,
                                                                        self._mdl["prediction"],
                                                                        self._conf.recommender.num_recs,
                                                                        column_name=column_name)

        logging.info("Successfully extended the predictions")
        return self._mdl

    @staticmethod
    def get_similarity_scores(mlb_data, similarity_matrix, columns=None):
        """Do a matrix multiplication to get the similarity score for each prediction.

        :param mlb_data: dataframe that contains the binarized predictions
        :param similarity_matrix: the similarity matrix
        :param columns: the columns to use for creating the dataframe
        :return: a pandas dataframe that

        Note: the number of columns of the mlb_data should be equal to the number of rows of the similarity matrix to
        perform the matrix multiplication
        """
        return pd.DataFrame(mlb_data.values.dot(similarity_matrix.values), columns=columns)

    @staticmethod
    def tuplize_scores_predictions_for_sorting(mlb_data, similarity_scores):
        """Use the columns of the mlb object, the similarity scores, and the binarized rows to make a tuple

        :param mlb_data: the pandas dataframe containing binarized predictions
        :param similarity_scores: the pandas dataframe containing similarity scores
        :return: a pandas dataframe in which each element contains a tupe of column name (service code for example),
                 similarity score, and binarized data
        """
        sorted_sim_scores = pd.DataFrame()
        for col in mlb_data.columns:
            col_name = np.full(mlb_data.shape[0], col)
            sorted_sim_scores[col] = list(zip(col_name, similarity_scores[col], mlb_data[col]))
        return sorted_sim_scores

    def get_extended_prediction(self, tupled_similarity_scores, predictions, num_recs, column_name):
        """Sort the predictions and extend them based on the similarity scores

        :param tupled_similarity_scores: pandas dataframe containing the tupled similarity score
        :param predictions: the tupled predictions (the classification results)
        :param num_recs: the target number of recommendations set by the user
        :return: the extended predictions in pandas series format

        Note: to speed up the calculations, extension should only be done on unique baskets
        """
        # a temporary dictionary to hold the rows that are extended and their corresponding extension
        # this helps speed up the extension process by not sorting the predictions that have already been extended
        temp_dict = {}
        extended_prediction = []
        temp_df = pd.DataFrame()

        for i in range(tupled_similarity_scores.shape[0]):
            if predictions[i] in temp_dict:
                extended_prediction.append(temp_dict[predictions[i]])
            else:
                # first sort the recommendation from the classification model, break the tie on similarity score
                row = sorted(tupled_similarity_scores.iloc[i], key=lambda x: x[::-1], reverse=True)

                # now sort the rest according to the similarity score
                row[len(predictions[i]):] = sorted(row[len(predictions[i]):], key=itemgetter(1), reverse=True)

                temp_df = temp_df.append(row)

                # extract the service codes from the tuples
                temp_ext_pred = []
                for item in row[:num_recs]:
                    temp_ext_pred.append(item[0])

                # add the extended predictions in tuple
                extended_prediction.append(tuple(temp_ext_pred))

                # add the prediction and the extension to the temp_dict to avoid redoing things
                temp_dict[predictions[i]] = tuple(temp_ext_pred)

        return pd.Series(extended_prediction, name=column_name)

