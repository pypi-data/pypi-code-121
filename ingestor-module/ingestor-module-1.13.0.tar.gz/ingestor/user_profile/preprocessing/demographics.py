from pandas import DataFrame, to_datetime
from datetime import datetime
from ingestor.common.constants import CUSTOMER_ID, BIRTHDAY, GENDER, CUSTOMER_CREATED_ON, CUSTOMER_MODIFIED_ON, \
    PAYTVPROVIDER_ID, DEFAULT_DATE, GENDER_VALUES, AGE, MEDIAN_AGE, AGE_UPPER_BOUND, DEFAULT_NUM, DEFAULT_NAN
from ingestor.common.preprocessing_utils import Utils


class PreprocessDemography:

    def preprocess_customer_id(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        This function type casts customer_id to string.
        :param df: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """
        df[CUSTOMER_ID] = df[CUSTOMER_ID].astype(str)

        return df

    def preprocess_gender(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        This function maps occurrences of male and female to m and f.
        And fills nan values with na

        :param df: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """
        df = Utils.fillna_and_cast_lower(
            data=df,
            feature=GENDER,
            default_val=DEFAULT_NAN
        )
        df[GENDER] = df[GENDER].replace(GENDER_VALUES)

        return df

    def preprocess_birthday(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        This function typecasts birthday column into date object

        :param df: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """
        df[BIRTHDAY] = df[BIRTHDAY].fillna(value=DEFAULT_DATE)
        df[BIRTHDAY] = df[BIRTHDAY].astype(str)
        df[BIRTHDAY] = [datetime.utcnow().strptime(birthday, "%Y-%m-%d").date()
                        for birthday in df[BIRTHDAY]]

        return df

    def calculate_age(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        This function calculates age of the customer from birthday

        :param df: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """
        df[AGE] = [int(birthday.year) for birthday in df[BIRTHDAY]]
        df[AGE] = (df[AGE] - int(datetime.utcnow().strftime('%Y'))) * (-1)
        df.loc[df[AGE] > AGE_UPPER_BOUND, AGE] = MEDIAN_AGE
        df[AGE] = df[AGE].astype(int)

        return df

    def preprocess_paytv_provider(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        This function replaces nan values in paytv_provider column to -1

        :param df: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """
        df[PAYTVPROVIDER_ID] = df[PAYTVPROVIDER_ID].fillna(DEFAULT_NUM)
        df[PAYTVPROVIDER_ID] = df[PAYTVPROVIDER_ID].astype(int)

        return df

    def preprocess_created_modified_on(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        This function typecasts customer_created_on and customer_modified_on into datetime object

        :param df: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """

        df[CUSTOMER_CREATED_ON] = df[CUSTOMER_CREATED_ON].fillna(value=DEFAULT_DATE)
        df[CUSTOMER_MODIFIED_ON] = df[CUSTOMER_MODIFIED_ON].fillna(df[CUSTOMER_CREATED_ON])
        df[CUSTOMER_CREATED_ON] = to_datetime(df[CUSTOMER_CREATED_ON])
        df[CUSTOMER_MODIFIED_ON] = to_datetime(df[CUSTOMER_MODIFIED_ON])

        return df

    def controller(
            self,
            df: DataFrame,
    ) -> DataFrame:
        """
        This is the driver function for user demographics preprocessing

        :param df: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """
        print("Preprocessing Customer_id...")
        data = self.preprocess_customer_id(df)

        print("Preprocessing Gender...")
        data = self.preprocess_gender(data)

        print("Preprocessing Birthday...")
        data = self.preprocess_birthday(data)

        print("Calculating Customer Age...")
        data = self.calculate_age(data)

        #data = self.preprocess_paytv_provider(data)

        print("Preprocessing Customer_created_on and Customer_modified_on...")
        data = self.preprocess_created_modified_on(data)

        print("Finished Preprocessing User Demographics Data...")

        return data
