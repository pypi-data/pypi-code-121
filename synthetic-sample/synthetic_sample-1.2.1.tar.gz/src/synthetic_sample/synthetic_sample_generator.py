import pandas as pd
from dateutil.relativedelta import relativedelta
from pathlib import Path

# from synthetic_sample import (
#     calculation_utils,
#     generate_synthetic_curves,
#     generate_synthetic_records,
#     sample_curve,
#     defaults
# )
#
import calculation_utils, generate_synthetic_curves, generate_synthetic_records, sample_curve, defaults

module_path = Path(__file__).parent


def synthetic_sample(input_dict: dict, create_records_dataset: bool = False) -> dict:
    """ Main executable to create synthetic sales data based on annual curves

    Args:
        input_dict: filepath of the request parameters in JSON format
        create_records_dataset: indicates if the individual sales records should also be created

    """
    # Unpack request dictionary to initialize variable
    default_type = input_dict.get("default_type")
    year_list = input_dict.get("year_list")
    start_date = input_dict.get("start_date")
    end_date = input_dict.get("end_date")
    total_sales = input_dict.get("total_sales")
    total_packages = input_dict.get("total_packages")
    total_quantity = input_dict.get("total_quantity")
    annual_sales = input_dict.get("annual_sales")
    annual_packages = input_dict.get("annual_packages")
    annual_quantity = input_dict.get("annual_quantity")
    annual_growth_factor = input_dict.get("annual_growth_factor")
    period_type = input_dict.get("period_type")
    curve_definition = input_dict.get("curve_definition")
    product_distribution = input_dict.get("product_distribution")
    week_distribution = input_dict.get("week_distribution")
    weekday_distribution = input_dict.get("weekday_distribution")
    seasonal_distribution = input_dict.get("seasonal_distribution")
    modifiers_list = input_dict.get("modifiers")

    # Initialize defaults and apply to inputs if necessary
    default_dict = defaults.CONFIGS.get("standard")
    if default_type is not None:
        default_dict.update(defaults.CONFIGS.get(default_type))

    if year_list is None:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        # If start_date is Jan 1, ensure the full ISO weeks are included
        if (start_date.month == 1) & (start_date.day == 1):
            start_date = start_date - relativedelta(days=start_date.weekday())
            end_date = end_date + relativedelta(days=(7 - end_date.weekday()))
            request_start_date = start_date if start_date.isocalendar()[1] == 1 else start_date + relativedelta(days=7)
        else:
            request_start_date = start_date
        request_end_date = end_date
        period_definition = (start_date, end_date)
    else:
        period_definition = year_list
    if annual_growth_factor is None:
        annual_growth_factor = default_dict.get("annual_growth_factor")
    if annual_sales is None:
        annual_sales = calculation_utils.get_annualized_integer(start_date, end_date, total_sales)
    if annual_packages is None:
        annual_packages = calculation_utils.get_annualized_integer(start_date, end_date, total_packages)
    if annual_quantity is None:
        annual_quantity = calculation_utils.get_annualized_integer(start_date, end_date, total_quantity)
    if product_distribution is None:
        product_distribution = default_dict.get("sku_distribution")
    if week_distribution is None:
        week_distribution = default_dict.get("week_distribution")
    if weekday_distribution is None:
        weekday_distribution = default_dict.get("weekday_distribution")
    if type(curve_definition) == str:
        curve_definition = defaults.CURVES.get(period_type).get(curve_definition)
    if modifiers_list is None:
        modifiers_list = []

    # Preprocessing of variables
    period_type = sample_curve.PeriodType(period_type)
    # Create required ratios based on whatever inputs are provided
    annual_sales, packages_per_sale, quantity_per_sale = calculation_utils.get_sales_ratios(
        default_dict.get("packages_per_sale"),
        default_dict.get("quantity_per_package"),
        annual_sales,
        annual_packages,
        annual_quantity)
    # Distributions must be normalized to add up to a total of 1.0
    product_distribution = calculation_utils.normalize_dist_dict(product_distribution)
    weekday_distribution = calculation_utils.normalize_dist_dict(weekday_distribution)
    seasonal_distribution = calculation_utils.normalize_dist_dict(seasonal_distribution)

    # Generate a dataframe with sample curves
    sample_curves_df = generate_synthetic_curves.generate_synthetic_curves(
        period_type,
        period_definition,
        annual_growth_factor,
        curve_definition,
        seasonal_distribution,
        total_sales,
        total_packages,
        total_quantity,
        modifiers_list)
    return_dict = {"curve": sample_curves_df}

    # If indicated that records should be created, run create_records_dataset()
    if create_records_dataset:
        sample_records_df = generate_synthetic_records.generate_synthetic_records(
            sample_curves_df,
            week_distribution,
            weekday_distribution,
            product_distribution)
        if type(period_definition) == tuple:
            # # If specific dates are requested, reallocate out of bounds orders randomly to other dates
            replace_mask = sample_records_df["date"] < request_start_date
            replace_mask = replace_mask | (sample_records_df["date"] >= request_end_date)
            valid_dates = pd.Series(sample_records_df.loc[~replace_mask, "date"].unique())
            replace_order_ids = sample_records_df[replace_mask].order_id.unique()
            replacement_dates = list(valid_dates.sample(n=len(replace_order_ids), replace=True))
            remapping_dict = dict(zip(replace_order_ids, replacement_dates))
            sample_records_df.loc[replace_mask, "date"] = sample_records_df.loc[replace_mask, "order_id"].apply(lambda x: remapping_dict[x])

            # Reallocate data from ISO years to calendar years for start and end of dataset
            input_start_date = pd.to_datetime(input_dict.get("start_date")).date()
            input_end_date = pd.to_datetime(input_dict.get("end_date")).date()
            mask = sample_records_df["date"] < input_start_date
            sample_records_df.loc[mask, "date"] = input_start_date

            last_week_start = input_end_date - relativedelta(days=input_end_date.weekday())
            mask = sample_records_df["date"] > input_end_date
            sample_records_df.loc[mask, "date"] = last_week_start

        return_dict["records"] = sample_records_df.copy()

    return return_dict


dd = {
    'datestamp': 'May 26, 2022 2:15 PM', 'user_id': 15, 'request_type': 'Sample', 'sales_total': 685000,
    'distribution_total': 710000, 'product_total': 1495000, 'start_date': '1/1/2020', 'end_date': '12/31/2021',
    'annual_growth': 10.0, 'trend_period': 'Weekly', 'product_id': ['1', '2', '3', '4', '5', '6'],
    'product_sku': ["Summa' Js", "Summa' Buds", "Summa' Chews", "Summa' Rubs", 'Smoky Honey Pot', 'Smoky Train Wreck'],
    'product_quantity': [19.0, 23.0, 11.0, 8.0, 22.0, 17.0],
    'brand': ["Summa' Sensi", "Summa' Sensi", "Summa' Sensi", "Summa' Sensi", 'Big Bear', 'Big Bear'],
    'product_category': ['Pre-Roll', 'Flower', 'Edible', 'Topical', 'Flower', 'Flower'], 'forecast_optin': 'Yes',
    'categorical_data': 'Custom', 'trend_curve': 'Standard Trends', 'ca_region': 'Cities', 'custom_jan': '',
    'custom_feb': '', 'custom_mar': '', 'custom_apr': '', 'custom_may': '', 'custom_jun': '', 'custom_jul': '',
    'custom_aug': '', 'custom_sep': '', 'custom_oct': '', 'custom_nov': '', 'custom_dec': '', 'age_1': '45.00',
    'age_2': '35.00', 'age_3': '20.00', 'ethnic_1': '44.00', 'ethnic_2': '16.00', 'ethnic_3': '21.00',
    'ethnic_4': '6.00', 'ethnic_5': '9.00', 'ethnic_6': '4.00', 'gender_1': '55.00', 'gender_2': '45.00',
    'channel_1': '36.00', 'channel_2': '50.00', 'channel_3': '12.00', 'channel_4': '2.00', 'sales_region': 'California',
    'sales_subregion': ['Ukiah', 'Healdsburg', 'Santa Rosa', 'Sonoma', 'Napa', 'San Rafael', 'Mill Valley',
        'San Francisco'], 'total_sales': 685000, 'total_packages': 710000, 'total_quantity': 1495000,
    'curve_definition': 'kv_standard', 'annual_growth_factor': 1.1, 'product_distribution': {
        "Summa' Js": 19.0, "Summa' Buds": 23.0, "Summa' Chews": 11.0, "Summa' Rubs": 8.0, 'Smoky Honey Pot': 22.0,
        'Smoky Train Wreck': 17.0
    }, 'period_type': 'week'
}
synthetic_sample(dd, True)
