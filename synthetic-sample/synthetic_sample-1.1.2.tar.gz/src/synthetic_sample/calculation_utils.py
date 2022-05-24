import numpy as np
import pandas as pd
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.stats import skewnorm

WEIGHT_LABEL = "weight"
MAX_PERCENTAGE_TO_UPDATE = 0.02


def get_annualized_integer(start_date: datetime, end_date: datetime, total_value: int):
    """ Annualized the total_value for the entire period in defined by start_date, end_date

    Args:
        start_date: first date of the period
        end_date: last date of the period
        total_value: integer total for the entire period

    Returns:
        annualized integer value
    """
    number_of_years = (end_date - start_date).days / 365
    annualized_value = int(total_value / number_of_years)

    return annualized_value


def get_sales_ratios(default_packages_per_sale: float, default_quantity_per_package: float, annual_sales: int = None,
                     annual_packages: int = None, annual_quantity: int = None) -> tuple:
    """ Given any combination of annual_sales, annual_packages, and annual_quantity, generates the ratios of packages:sales and quantity:packages

    Args:
        default_packages_per_sale: packages to sales ratio to use as a default
        default_quantity_per_package: quantity to packages ratio to use as a default
        annual_sales: *optional* number of sales for the entire period
        annual_packages: *optional* number of packages for the entire period
        annual_quantity: *optional* quantity for the entire period

    Returns:
        tuple of (annual_sales, packages_per_sale, quantity_per_package)

    Raises:
        ValueError: One of annual_sales, annual_packages, or annual_quantity must be provided
    """
    # We calculate off of annual_sales if possible
    if annual_sales is not None:
        # If annual_packages is provided use it to determine the packages_per_sale
        if annual_packages is not None:
            packages_per_sale = annual_packages / annual_sales
            # If annual_quantity is provided, use it to determine quantity_per_package, otherwise use a default
            if annual_quantity is not None:
                quantity_per_sale = annual_quantity / annual_sales
            else:
                quantity_per_sale = default_quantity_per_package * packages_per_sale
        # If annual_packages is not provided, use a default
        else:
            packages_per_sale = default_packages_per_sale
            # If total quantity is provided, calculate quantity_per_package using the default packages_per_sale
            if annual_quantity is not None:
                quantity_per_sale = annual_quantity / annual_sales
            # Otherwise use a default
            else:
                quantity_per_sale = default_quantity_per_package * packages_per_sale
    # If annual_sales is not provided, base the other metrics off of a default packages_per_sale value
    else:
        packages_per_sale = default_packages_per_sale
        # If annual_packages is given, use it and a default packages_per_sale to determine annual_sales
        if annual_packages is not None:
            annual_sales = int(annual_packages / packages_per_sale)
            # If annual_quantity is given, use it and annual_packages to determine quantity_per_package
            if annual_quantity is not None:
                quantity_per_sale = annual_quantity / annual_sales
            # Otherwise use a default
            else:
                quantity_per_sale = default_quantity_per_package * packages_per_sale
        else:
            # If annual_quantity is given, use default ratios to get packages_per_sale and annual_sales
            if annual_quantity is not None:
                quantity_per_sale = default_quantity_per_package * default_packages_per_sale
                packages_per_sale = default_packages_per_sale
                annual_sales = int((annual_quantity / default_quantity_per_package) / default_packages_per_sale)
            else:
                raise ValueError("One of annual_sales, annual_packages, or annual_quantity must be provided")

    return annual_sales, packages_per_sale, quantity_per_sale


def create_column_from_dist(df: pd.DataFrame, dist_dict: dict, column_name: str) -> None:
    """ Given a dataframe, create a new column `column_name` using the provided distribution

    Args:
        df: dataframe to add the column to
        dist_dict: dictionary of items and their relative weighting
        column_name: name of the updated column
    """
    # Normalize values of relative weights
    dist_dict = normalize_dist_dict(dist_dict)

    # Create columns for random numbers and new values
    df["temp_value"] = np.random.random(df.shape[0])
    df[column_name] = None
    # Check for random values that fall within a probability band defined by the weight
    # For each item check for records that fall between the previous and new probability range limits
    p = 0
    for item in dist_dict:
        mask_lower = df["temp_value"] >= p
        mask_upper = df["temp_value"] <= (p + dist_dict[item])
        # Add the specified item to those records
        df.loc[mask_lower & mask_upper, column_name] = item
        # Add this items probability to the range for the next item
        p += dist_dict[item]
    # Drop temporary column
    df.drop(columns=["temp_value"], inplace=True)


def normalize_dist_dict(raw_dist_dict: dict) -> dict:
    """ Given a dictionary of items and relative weights, modify the weights to normalize to 1

    Args:
        raw_dist_dict:  dictionary of items as keys and their weighting as the value

    Returns: updated dictionary normalized to 1 or an empty dictionary if None is passed
    """
    normalized_dict = {}
    if raw_dist_dict:
        # Get value to normalize
        normalized_value = sum(raw_dist_dict.values())
        # Divide into each value for each key
        normalized_dict = {
            key: raw_dist_dict[key] / normalized_value
            for key in raw_dist_dict
        }

    return normalized_dict


def create_daily_dist_dict_for_month(month_timestamp: pd.Timestamp, weekly_distribution: dict, weekday_distribution: dict) -> dict:
    """ For a given month, provides the percentage distribution across each day of the month

    Args:
        month_timestamp: timestamp in the month of interest
        weekly_distribution: dictionary indicating the probability of sales by week of the month
            -1 indicates last week of the month
        weekday_distribution: dictionary indicating the probability of sales by day of the week

    Returns:
        dictionary with probabilities for every day of the month
    """
    # Get full list of weeks for month
    start_date = month_timestamp.replace(day=1)
    end_date = start_date + relativedelta(months=1) + relativedelta(days=-1)
    date_range = pd.date_range(start=start_date, end=end_date, freq="W-MON")
    # Check if the month includes days from previous ISO weeks and include them if so
    if date_range[0] > start_date:
        week_before_start_date = start_date + relativedelta(days=-7)
        additional_date_range = pd.date_range(week_before_start_date, start_date, freq="W-MON")
        date_range = date_range.union(additional_date_range)

    # Apply distribution, create dict of weeks and their relative weights
    weekly_dist_dict = {}
    # Set probability for each week based on weekly_distribution
    for index in range(0, len(date_range)):
        weekly_dist_dict[date_range[index]] = weekly_distribution.get(index)
        # If -1 is included in the keys, apply it on the last iteration of the loop
        if (-1 in weekly_distribution.keys()) & (index == len(date_range) - 1):
            weekly_dist_dict[date_range[index]] = weekly_distribution[-1]
    # Create a dataframe from the dictionary
    weekly_dist_df = pd.DataFrame.from_dict(weekly_dist_dict, orient='index', columns=[WEIGHT_LABEL])
    # If no values are included, set the distribution to be flat
    if weekly_dist_df[WEIGHT_LABEL].isnull().all():
        weekly_dist_df[WEIGHT_LABEL] = 1
    # Otherwise, set the distribution across non-specified weeks to be flat
    else:
        # Remove probability of all provided weights
        fill_value = 1 - weekly_dist_df[WEIGHT_LABEL].sum()
        # Fill value evenly across other values
        fill_value = fill_value / (len(weekly_dist_df) - 1)
        mask = weekly_dist_df[WEIGHT_LABEL].isnull()
        weekly_dist_df.loc[mask, WEIGHT_LABEL] = fill_value

    # For each week, create a distribution across the individual days
    daily_dist_dict = {}
    for index, row in weekly_dist_df.iterrows():
        # Create a date range for the individual week
        week_end = index + relativedelta(days=6)
        week_dates = pd.date_range(index, week_end)
        # Create a distribution dictionary by multiplying the week's weight with the weekdays weight for each day
        weekday_dist = {
            week_dates[weekday_index].date(): weekday_distribution[weekday_index] * row[WEIGHT_LABEL]
            for weekday_index in weekday_distribution if week_dates[weekday_index].date().month == month_timestamp.month
        }
        daily_dist_dict.update(weekday_dist)

    # Normalize values for the entire month
    normalized_daily_dist_dict = normalize_dist_dict(daily_dist_dict)

    return normalized_daily_dist_dict


def create_daily_dist_dict_for_week(week_start_date: pd.Timestamp, weekday_distribution: dict) -> dict:
    """ For a given month, provides the percentage distribution across each day of the month

    Args:
        week_start_date: timestamp for the start of the week
        weekday_distribution: dictionary indicating the probability of sales by day of the week

    Returns:
        dictionary with probabilities for every day of the week
    """
    week_end = week_start_date + relativedelta(days=6)
    week_dates = pd.date_range(week_start_date, week_end)
    # Create a distribution dictionary by multiplying the week's weight with the weekdays weight for each day
    weekday_dist = {
        week_dates[weekday_index].date(): weekday_distribution[weekday_index]
        for weekday_index in weekday_distribution
    }
    return weekday_dist


def add_int_column_from_distribution(dataframe: pd.DataFrame, column_name: str, mean_value: float, skewness: float,
                                     exponential: float, floor_column: str = None, floor_value: int = None) -> None:
    """ Given a dataframe add a new int column from the distribution defined by mean_value, skewness, and exponential

    Args:
        dataframe: dataframe to add the column to
        column_name: name of column to add
        mean_value: average value for the new column
        skewness: skewness of the distribution for the new column
        exponential: exponential for the new column before fitting to mean
        floor_column: column to indicate the minimum value that the new column can contain
        floor_value: minimum value that the new column can contain
    """
    # Uses https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skewnorm.html to pull from a random distribution
    dataframe[column_name] = skewnorm.rvs(a=skewness, size=len(dataframe))

    # Shifts outputs so the minimum value is 1
    dataframe[column_name] = dataframe[column_name] - dataframe[column_name].min() + 1
    # Apply exponential to curve
    dataframe[column_name] = dataframe[column_name] ** exponential
    # Scale curve to have a mean as provided
    dataframe[column_name] = (dataframe[column_name] * (mean_value / dataframe[column_name].mean()))
    # Convert to discrete integers
    dataframe[column_name] = dataframe[column_name].astype(int)
    # Handle floor cases
    if floor_column:
        mask = dataframe[column_name] < dataframe[floor_column]
        dataframe.loc[mask, column_name] = dataframe.loc[mask, floor_column]
    if floor_value:
        mask = dataframe[column_name] < floor_value
        dataframe.loc[mask, column_name] = floor_value

    # Add 1 to random records to add noise until desired mean is acheived
    dataframe = dataframe.reset_index(drop=True)
    while dataframe[column_name].mean() < mean_value:
        # Determine number of records to update based on the current delta from desired mean
        delta = mean_value - dataframe[column_name].mean()
        number_to_change = int(len(dataframe) * delta/2) + 1
        # Check against a cap on number of records to update at once (to add noise rather than a general shift)
        if number_to_change > len(dataframe) * MAX_PERCENTAGE_TO_UPDATE:
            number_to_change = int(len(dataframe) * MAX_PERCENTAGE_TO_UPDATE)
        # Identify number_to_change records to add 1 to and update them all at once
        records_to_change = set([random.randint(0, len(dataframe)) for x in range(0, number_to_change)])
        mask = dataframe.index.isin(records_to_change)
        dataframe.loc[mask, column_name] = dataframe.loc[mask, column_name] + 1
