import pandas as pd
from pandas import DataFrame

from ingestor.common.constants import CUSTOMER_ID
from ingestor.merge_df.common import UserBehaviourUtils


class FinalDfUBDController:

    @staticmethod
    def build_user_behaviour_final_df(video_measure_data=None,
                                      df_content_having_tags=None,
                                      df_content_having_director=None,
                                      df_content_having_actor=None) -> DataFrame:
        video_measure_df = DataFrame()
        result_not_in_df = DataFrame()
        if not pd.isna(video_measure_data[CUSTOMER_ID][0]):
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_customer_id(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_created_on(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_country_id(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_region_name(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_devops(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_attribute(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_video_id(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_category1(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_category2(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_duration(
                video_measure_df, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_tags_df(
                video_measure_df, df_content_having_tags, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_actor_df(
                video_measure_df, df_content_having_actor, video_measure_data, result_not_in_df)
            video_measure_df, result_not_in_df = UserBehaviourUtils.fetch_prepare_director_df(
                video_measure_df, df_content_having_director, video_measure_data, result_not_in_df)

        return video_measure_df, result_not_in_df

    '''
    # main entry point for updating user profile final df
    '''

    @staticmethod
    def get_final_df_user_behaviour(df_video_measure_data=None,
                                    df_content_having_tags=None,
                                    df_content_having_director=None,
                                    df_content_having_actor=None):
        final_df_user_behaviour = DataFrame()
        result_not_correct_df = DataFrame()

        for row, val in df_video_measure_data.iterrows():
            df_new = DataFrame()
            values_to_add = val.to_dict()
            row_to_add = pd.Series(values_to_add)
            new_df = pd.concat([df_new, row_to_add], axis=1).T
            print(row, " :: ", "Working on ubd record: ", row_to_add)
            result_df, result_not_df = FinalDfUBDController.build_user_behaviour_final_df(
                new_df,
                df_content_having_tags,
                df_content_having_director,
                df_content_having_actor)

            final_df_user_behaviour = pd.concat([final_df_user_behaviour, result_df], axis=0)
            result_not_correct_df = pd.concat([result_not_correct_df, result_not_df], axis=0)

        return final_df_user_behaviour, result_not_correct_df
