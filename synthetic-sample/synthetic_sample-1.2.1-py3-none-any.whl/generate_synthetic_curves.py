import pandas as pd
from datetime import datetime, timedelta
from typing import Union

# from synthetic_sample import calculation_utils
# from synthetic_sample.sample_curve import SampleCurve, CustomSampleCurve, PeriodType
import calculation_utils
from sample_curve import SampleCurve, CustomSampleCurve, PeriodType


def create_yearly_metadata_dict(period_definition: Union[tuple, list], total_sales: int, annual_growth_rate: float) -> dict:
    """ Creates dictionary containing each year and the total number of sales to attribute

    Args:
        period_definition: defines the time period to use
            if a tuple, expected to contain (start_date, end_date)
            if a list, expected to contain each requested year as an integer

    Returns:
        dictionary with metadata around the sales for each year. Keys are:
            start_date: first day to include for the year
            end_date: last day to include for the year
            sales: total number of sales for the year
    """
    if type(period_definition) == list:
        year_metadata_dict = {
            year: {}
            for year in period_definition
        }
    elif type(period_definition) == tuple:
        start_date = period_definition[0]
        end_date = period_definition[1]
        year_metadata_dict = {
            year: {
                "start_date": datetime(year, 1, 1),
                "end_date": datetime(year, 12, 31)
            }
            for year in range(start_date.year, end_date.year + 1)
        }
        year_metadata_dict[start_date.year]["start_date"] = pd.to_datetime(start_date)
        year_metadata_dict[end_date.year]["end_date"] = pd.to_datetime(end_date)
    else:
        raise NotImplementedError()

    growth_multiplier = 1
    sales_weight_total = 0
    for year in year_metadata_dict:
        year_dict = year_metadata_dict.get(year)
        if year_dict.get("start_date") is not None:
            start_date = year_dict["start_date"]
            end_date = year_dict["end_date"]
        else:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
        days_of_year = (end_date - start_date)
        fractional_year_multiplier = days_of_year / (datetime(year, 12, 31) - datetime(year, 1, 1))
        year_dict["sales_weight"] = growth_multiplier * fractional_year_multiplier
        sales_weight_total += year_dict["sales_weight"]
        growth_multiplier *= annual_growth_rate

    for year in year_metadata_dict:
        year_dict = year_metadata_dict.get(year)
        year_dict["sales"] = (year_dict["sales_weight"] / sales_weight_total) * total_sales

    return year_metadata_dict


def apply_curve_to_time_period(curve: CustomSampleCurve, period_definition: Union[tuple, list],
                               seasonal_distribution: dict, annual_sales: int, annual_growth_rate: float, curve_modifiers: list) -> pd.DataFrame:
    """ Given a curve and input parameters, apply the curve to the period to create the aggregated synthetic data

    Args:
        curve: CustomSampleCurve object to apply to the year
        period_definition: defines the tim eperiod to use
            if a tuple, expected to contain (start_date, end_date)
            if a list, expected to contain each requested year as an integer
        seasonal_distribution: dictionary indicating redistribution of output according to seasonal trends
        annual_sales: annual sales for the period
        annual_growth_rate: average annual growth rate (10% growth being 1.1)

    Returns:
        dataframe with the total number of sales for each period in the requested time period
    """
    yearly_metadata_dict = create_yearly_metadata_dict(period_definition, annual_sales, annual_growth_rate)
    sales_df = curve.apply(yearly_metadata_dict, seasonal_distribution, curve_modifiers)

    return sales_df.reset_index(drop=True)


def generate_synthetic_curves(
        period_type: PeriodType,
        period_definition: Union[tuple, list],
        annual_growth_factor: float,
        curve_definition: dict,
        seasonal_distribution: dict,
        total_sales: int,
        total_packages: int,
        total_quantity: int,
        curve_modifiers: list) -> pd.DataFrame:
    """ Generates synthetic sales data for given json input

    Args:
        period_type: type of period to create aggregated data for
        period_definition: definition for the period, either a list of years or a tuple of (start_date, end_date)
        annual_growth_factor: average annual growth rate (10% growth being 1.1)
        curve_definition: dictionary to define the sales curve in terms of the cumulative percentage at the end of each period
        seasonal_distribution: dictionary indicating redistribution of output according to seasonal trends
        total_sales: total sales for the period
        total_packages: total number of packages
        total_quantity: total quantity sold

    Returns:
        dataframe with the total number of sales, packages, and quantity for each period in the requested time period
    """
    # Create synthetic sales curve
    custom_curve = CustomSampleCurve(period_type, curve_definition)
    sales_time_series_df = apply_curve_to_time_period(custom_curve, period_definition, seasonal_distribution,
                                                      total_sales, annual_growth_factor, curve_modifiers)
    sales_time_series_df.rename(columns={SampleCurve.value_column_name: "sales"}, inplace=True)

    # Add derived values based on ratio
    sales_time_series_df["packages"] = (sales_time_series_df["sales"] * (total_packages / total_sales)).apply(int)
    sales_time_series_df["quantity"] = (sales_time_series_df["sales"] * (total_quantity / total_sales)).apply(int)

    # If outputs are not exact matches to requested totals, fill in
    sales_time_series_df = calculation_utils.realign_with_totals(sales_time_series_df, "sales", total_sales)
    sales_time_series_df = calculation_utils.realign_with_totals(sales_time_series_df, "packages", total_packages)
    sales_time_series_df = calculation_utils.realign_with_totals(sales_time_series_df, "quantity", total_quantity)

    return sales_time_series_df
