from ast import literal_eval
from datetime import datetime
from math import log
from operator import itemgetter

from pandas import DataFrame, concat

from ingestor.common.constants import CUSTOMER_ID, VIEW_COUNT, VIEW_HISTORY, CONTENT_ID, CREATED_ON, DURATION
from ingestor.user_rating.constants import TOP_RATING, VERY_POSITIVE, POSITIVE, NOT_SURE, YYMMDD, RECENT_DATE, \
    RECENT_DURATION
from ingestor.user_rating.query_utils import RatingQueryUtils


class RatingUtils:

    @staticmethod
    def get_queried_log_data_for_user(graph):
        user_content_network = RatingQueryUtils.get_user_content_network(graph)
        user_content_df = DataFrame()
        for view in user_content_network:
            for history in view:
                user_object_data = history[0][CUSTOMER_ID]
                content_object_data = history[2][CONTENT_ID]
                recent_viewed_date_data = RatingUtils.get_recent_viewed_date(history)
                recent_duration_data = RatingUtils.get_recent_duration(history)
                view_count_data = history[1][VIEW_COUNT]
                user_content_data = DataFrame([{CUSTOMER_ID: user_object_data,
                                                CONTENT_ID: content_object_data,
                                                RECENT_DATE: recent_viewed_date_data,
                                                VIEW_COUNT: view_count_data,
                                                RECENT_DURATION: recent_duration_data}])
                user_content_df = concat([user_content_df, user_content_data], axis=0)
                user_content_df = user_content_df.sort_values(by=[RECENT_DATE, VIEW_COUNT], ascending=False)

        return user_content_df

    @staticmethod
    def get_recent_viewed_date(history):
        history_data = history[1][VIEW_HISTORY]
        list_history_data = literal_eval(history_data)
        list_history_data = sorted(list_history_data, key=itemgetter(CREATED_ON), reverse=True)
        recent_date = list_history_data[0][CREATED_ON]
        recent_date = datetime.strptime(recent_date, YYMMDD).date()
        return recent_date

    @staticmethod
    def get_recent_duration(history):
        history_data = history[1][VIEW_HISTORY]
        list_history_data = literal_eval(history_data)
        list_history_data = sorted(list_history_data, key=itemgetter(DURATION), reverse=True)
        recent_duration = list_history_data[0][DURATION]
        return recent_duration

    @staticmethod
    def get_number_of_users(data) -> int:
        number_of_users = len(set(data[CUSTOMER_ID]))
        return number_of_users

