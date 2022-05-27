
from pyspark.sql.functions import split, explode

class TextProcessor:

    def word_count(self, df, col_name='lemm_text'):
        """Creates a DataFrame with word counts.

        Args:
            wordListDF (DataFrame of str): A DataFrame consisting of one string column.

        Returns:
            DataFrame of (str, int): A DataFrame containing 'word' and 'count' columns.
        """
        df = df.select(split(df[col_name], '\s+').alias('split'))
        df_single = df.select(explode(df.split).alias('word'))
        df_single = df_single.where(df_single.word != '')

        return df_single.groupBy('word').count()