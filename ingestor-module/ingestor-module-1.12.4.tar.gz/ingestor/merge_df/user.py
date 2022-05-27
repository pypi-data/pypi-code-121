import pandas as pd
from pandas import DataFrame

from ingestor.common.constants import CUSTOMER_ID
from ingestor.merge_df.common import UserProfileUtils


class FinalDfUserController:

    @staticmethod
    def build_user_profile_final_df(customer=None, df_user_pay_tv=None):
        customer_df = DataFrame()
        result_not_in_df = DataFrame()
        if not pd.isna(customer[CUSTOMER_ID][0]):
            customer_df, result_not_in_df = UserProfileUtils.fetch_prepare_customer_id(
                customer_df, customer, result_not_in_df)
            customer_df, result_not_in_df = UserProfileUtils.fetch_prepare_birthday_id(
                customer_df, customer, result_not_in_df)
            customer_df, result_not_in_df = UserProfileUtils.fetch_prepare_gender(
                customer_df, customer, result_not_in_df)
            customer_df, result_not_in_df = UserProfileUtils.fetch_prepare_created_on(
                customer_df, customer, result_not_in_df)
            customer_df, result_not_in_df = UserProfileUtils.fetch_prepare_modified_on(
                customer_df, customer, result_not_in_df)
            customer_df, result_not_in_df = UserProfileUtils.fetch_prepare_ud_key(
                customer_df, customer, result_not_in_df)
            customer_df, result_not_in_df = UserProfileUtils.fetch_user_pay_tv(
                customer_df, df_user_pay_tv, customer, result_not_in_df)
            customer_df, result_not_in_df = UserProfileUtils.fetch_age(
                customer_df, customer, result_not_in_df)

        return customer_df, result_not_in_df

    '''
    # main entry point for creating user profile final df
    '''

    @staticmethod
    def get_final_df_user_profile(df_customer=None, df_user_pay_tv=None):
        final_df_user_profile = DataFrame()
        result_not_correct_df = DataFrame()

        for row, val in df_customer.iterrows():
            df_new = DataFrame()
            values_to_add = val.to_dict()
            row_to_add = pd.Series(values_to_add)
            print(row, " :: ", "Working on user record: ", row_to_add)
            new_df = pd.concat([df_new, row_to_add], axis=1).T
            result_df, result_not_df = FinalDfUserController.build_user_profile_final_df(
                new_df,
                df_user_pay_tv,
            )

            final_df_user_profile = pd.concat([final_df_user_profile, result_df], axis=0)
            result_not_correct_df = pd.concat([result_not_correct_df, result_not_df], axis=0)

        return final_df_user_profile, result_not_correct_df
