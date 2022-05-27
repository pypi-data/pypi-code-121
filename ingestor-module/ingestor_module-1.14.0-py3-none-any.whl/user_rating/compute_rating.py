from datetime import timedelta, date
from math import log
from typing import ClassVar

from graphdb import GraphDbConnection
from graphdb.graph import GraphDb
from pandas import DataFrame, concat, cut, get_dummies

from ingestor.common.constants import VIEW_COUNT, CUSTOMER_ID, CONTENT_ID
from ingestor.user_rating.config import DAYS, weight_duration, weight_top_rating, weight_very_positive, weight_positive, \
    weight_not_sure, SCALING_FACTOR, BIN_RANGE_1, BIN_RANGE_2, NUMBER_OF_BINS
from ingestor.user_rating.constants import BINS, NOT_SURE, POSITIVE, VERY_POSITIVE, TOP_RATING, AGE_OF_EVENT, \
    TIME_DECAY_FACTOR, IMPLICIT_RATING, RECENT_DATE, RECENT_DURATION, COUNT, RATING_DATA_FILE
from ingestor.user_rating.rating_utils import RatingUtils

connection_uri_local = "ws://localhost:8182/gremlin"


class RatingGenerator:

    def __init__(
            self,
            connection_class: GraphDbConnection
    ):
        self.graph = GraphDb.from_connection(connection_class)

    @classmethod
    def from_connection_uri(
            cls,
            connection_uri: str
    ) -> ClassVar:
        """Create new object based on connection uri
        :param connection_uri: string connection uri
        :return: object class
        """
        return cls(GraphDbConnection.from_uri(connection_uri))

    @classmethod
    def from_connection_class(
            cls,
            connection_class: GraphDbConnection
    ) -> ClassVar:
        """Define new class based on object connection
        :param connection_class: object connection class
        :return: object class
        """
        return cls(connection_class)

    def define_rating_events(self) -> DataFrame:
        """
        Define rating events based on view counts:
        TOP RATING : Occurs in top first bin (maximum view counts)
        VERY POSITIVE : Occurs in second top bin
        POSITIVE : third bin
        NOT SURE : last bin (least view counts)
        """
        data = RatingUtils.get_queried_log_data_for_user(self.graph)
        bins = data[VIEW_COUNT].value_counts(bins=NUMBER_OF_BINS, sort=False).rename_axis(BINS).reset_index(name=COUNT)
        bins_list = bins[BINS].to_list()
        data[BINS] = cut(data[VIEW_COUNT],
                         bins=[bins_list[0].left, BIN_RANGE_1, bins_list[1].right, bins_list[3].right - BIN_RANGE_2,
                               bins_list[3].right], labels=[NOT_SURE, POSITIVE, VERY_POSITIVE, TOP_RATING])
        rating_data = get_dummies(data[BINS])
        data = concat([data, rating_data], axis=1)
        return data.reset_index()

    def calculate_time_decay(self
                             ) -> DataFrame:
        """
        Find two rating parameters:
        1. Age of most recent view events (in days) = "created_on" (date) to days conversion
        2. time decay factor = 1/age of view events
        Add all 2 above computed parameters as additional attributes in final dataframe
        """
        data = self.define_rating_events()
        rating_parameters_list = []
        for index, value in data.iterrows():
            rating_parameters_dict = {}
            age = (date.today() - value[RECENT_DATE]) // timedelta(days=DAYS)
            time_decay_factor = 1 / age
            rating_parameters_dict[AGE_OF_EVENT] = age
            rating_parameters_dict[TIME_DECAY_FACTOR] = time_decay_factor
            rating_parameters_list.append(rating_parameters_dict)
        rating_parameters_df = DataFrame(rating_parameters_list)
        data = concat([data, rating_parameters_df], axis=1)
        return data

    def calculate_implicit_rating_with_time_decay_and_inverse_user_frequency(self) -> DataFrame:
        """
        Inverse user frequency = log(N/(1 + n)), where:
                                 N = Total number of users in the catalog
                                 n = total number of top rating events
        """
        data = self.calculate_time_decay()
        implicit_rating_list = []
        max_rating = 0
        for idx, value in data.iterrows():
            implicit_rating_dict = {}
            inverse_user_frequency = log(RatingUtils.get_number_of_users(data) / (1 + data[TOP_RATING].sum()))
            duration_value = weight_duration * value[RECENT_DURATION] * value[
                TIME_DECAY_FACTOR] * inverse_user_frequency
            top_rating_value = weight_top_rating * value[TOP_RATING] * value[VIEW_COUNT] * value[
                TIME_DECAY_FACTOR] * inverse_user_frequency
            very_positive_value = weight_very_positive * value[VERY_POSITIVE] * value[VIEW_COUNT] * value[
                TIME_DECAY_FACTOR] * inverse_user_frequency
            positive_value = weight_positive * value[POSITIVE] * value[VIEW_COUNT] * value[
                TIME_DECAY_FACTOR] * inverse_user_frequency
            not_sure_value = weight_not_sure * value[NOT_SURE] * value[VIEW_COUNT] * value[
                TIME_DECAY_FACTOR] * inverse_user_frequency

            implicit_rating = duration_value + top_rating_value + very_positive_value + positive_value + not_sure_value

            max_rating = max(max_rating, implicit_rating)
            normalised_implicit_rating = implicit_rating / max_rating

            implicit_rating_with_time_decay = SCALING_FACTOR * normalised_implicit_rating

            implicit_rating_dict[IMPLICIT_RATING] = implicit_rating_with_time_decay
            implicit_rating_list.append(implicit_rating_dict)

        rating_df = DataFrame(implicit_rating_list)
        data = concat([data, rating_df], axis=1)
        data = data[[CUSTOMER_ID, CONTENT_ID, IMPLICIT_RATING]]
        data.to_pickle(RATING_DATA_FILE)
        return data
