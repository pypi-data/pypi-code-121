from pandas import DataFrame, concat
from ingestor.common.constants import CUSTOMER_ID, DUMMY_ATTRIBUTE_SPLIT_ON


class RelationshipExtractor:

    def __init__(
            self,
            data: DataFrame
    ):
        """
        Accept the dataframe object with
        dummy attributes
        :param data: dataframe object
        """
        self.data = data

        #initializing feature name for the result
        self.original_title = ''

    def get_original_feature_title(
            self
    ):
        """
        Finding the feature name for result dataframe
        from one of the current dummy attributes
        :return: None, simply updates the instance
        member of the class
        """
        for feature in self.data.columns:

            if feature == CUSTOMER_ID:
                continue

            self.original_title = feature.rsplit(
                DUMMY_ATTRIBUTE_SPLIT_ON, 1)[0]

            # all dummy features will return the
            # same value, therefore no need to iterate for
            # more than one attribute
            break

    def get_original_feature_values(
            self
    ):
        """
        Obtain the relation nodes to which the customer
        node will be connected to. This will be found by
        choosing all the dummy features with a
        value = 1 for a given customer_id
        :return:None, simply updates the instance
        member of the class
        """
        for feature in self.data.columns:

            if feature == CUSTOMER_ID:
                continue

            feature_val = feature.rsplit(
                DUMMY_ATTRIBUTE_SPLIT_ON, 1
            )

            self.data.rename(
                columns={feature: feature_val[1]},
                inplace=True
            )

    def add_relation(
            self,
            df: DataFrame,
            customer_id: str,
            original_feature_val: str
    ):
        """
        Create a new record in the result df
        :param df: result dataframe object
        :param customer_id: customer id in
        result df record
        :param original_feature_val: connect
        customer_id to this node
        :return:
        """
        record_count = len(df)

        df.loc[record_count,
               CUSTOMER_ID] = customer_id

        df.loc[record_count,
               self.original_title] = original_feature_val

    def get_preference_explode_df(
            self,
            customer_id: str,
            record_df: DataFrame
    ):
        """
        Expand the record df so as to explode the list of
        preferences into individual records in a
        dataframe object
        :param customer_id: value string
        :param record_df: dataframe object pandas
        :return: dataframe object pandas
        """
        explode_df = DataFrame(columns=[CUSTOMER_ID, self.original_title])
        explode_df.loc[0, CUSTOMER_ID] = customer_id
        explode_df.at[0, self.original_title] = list(record_df.columns)
        explode_df = explode_df.explode(column=self.original_title)
        explode_df = explode_df.iloc[:-1, :]
        return explode_df

    def get_preference_record_df(
            self,
            index: int
    ):
        """
        Retrieve the currently considered df
        as a separate dataframe object
        :param index: dataframe index to extract as a
        separate dataframe object
        :return: customer_id value string, dataframe
        object pandas
        """
        # extract the current record as an individual
        # dataframe object
        record_df = self.data.iloc[[index]].reset_index(drop=True)
        customer_id = record_df.loc[0, CUSTOMER_ID]
        record_df = record_df.loc[:, record_df.iloc[0] == 1]
        return customer_id, record_df

    def get_preference_relationships(
            self
    ):
        """
        Find all the relationships from dummy
        attribute dataframe
        :return: non-dummified dataframe with
        customer id and records with its preferences
        for the specific feature values
        """

        result = DataFrame(
            columns=[CUSTOMER_ID,
                     self.original_title]
        )

        size = len(self.data)
        for index in range(size):
            print("---Working on index ", index, " of ", size)

            customer_id, record_df = \
                self.get_preference_record_df(index)

            explode_df = self.get_preference_explode_df(
                customer_id=customer_id,
                record_df=record_df
            )
            # append the exploded df to the result
            # dataframe object pandas
            result = concat(
                [result, explode_df], axis=0
            ).reset_index(drop=True)

        return result

    def controller(
            self
    ):
        """
        Driver function
        :return: non-dummified dataframe with
        customer id and records with its preferences
        for the feature values
        """
        self.get_original_feature_title()
        self.get_original_feature_values()
        return self.get_preference_relationships()
