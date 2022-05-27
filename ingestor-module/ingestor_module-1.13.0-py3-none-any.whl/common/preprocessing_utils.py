from pandas import DataFrame

from ingestor.common.constants import WHITESPACE_REGEX, SINGLE_SPACE, ABSURD_VALUE


class Utils:

    @staticmethod
    def fillna_and_cast_lower(
            data: DataFrame,
            feature: str,
            default_val: str
    ) -> DataFrame:
        """
        This function is used to fillna with the default value specified
        on the feature specified.

        :param data: dataframe object pandas
        :param feature: feature name for preprocessing
        :param default_val: default value to be used for replacing nan
        :return:
        """
        data[feature] = data[feature].fillna(default_val)
        data[feature] = data[feature].replace(WHITESPACE_REGEX, SINGLE_SPACE, regex=True)
        data[feature] = data[feature].replace({ABSURD_VALUE: default_val})
        data[feature] = data[feature].str.strip()
        data[feature] = data[feature].str.lower()
        return data
