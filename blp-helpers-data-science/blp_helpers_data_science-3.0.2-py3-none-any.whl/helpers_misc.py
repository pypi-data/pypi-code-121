import pandas as pd


def get_value_counts_as_df(data_frame, column_name_grouping, column_name_count='count'):
    """Return a data frame containing counts of unique values
    :param data_frame: Pandas data frame to process
    :param column_name_grouping: the column for which the unique values are counted
    :param column_name_count: the name of the column that contains the counts for column_grouping
    :return: grouped_values: data frame with column_grouping and column_count as headers

    Example:

    column_name_grouping = 'verified_purchase'
    column_name_count = 'count'
    grouped_values =
        verified_purchase	count
    0	Y	                371539
    1	N	                256810
    """
    grouped_values = data_frame[column_name_grouping].value_counts().rename_axis(column_name_grouping).reset_index(
        name=column_name_count)
    grouped_values.sort_values(by=[column_name_count], inplace=True, ascending=False)
    grouped_values.reset_index(drop=True, inplace=True)

    return grouped_values
