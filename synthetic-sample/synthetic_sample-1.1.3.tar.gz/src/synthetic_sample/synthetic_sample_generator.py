import pandas as pd
from dateutil.relativedelta import relativedelta
from pathlib import Path

from synthetic_sample import (
    calculation_utils,
    generate_synthetic_curves,
    generate_synthetic_records,
    sample_curve,
    defaults
)
# import calculation_utils, generate_synthetic_curves, generate_synthetic_records, sample_curve, defaults


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
        packages_per_sale,
        quantity_per_sale,
        modifiers_list)
    return_dict = {"curve": sample_curves_df}

    # If indicated that records should be created, run create_records_dataset()
    if create_records_dataset:
        sample_records_df = generate_synthetic_records.generate_synthetic_records(sample_curves_df, packages_per_sale,
                                                                                  quantity_per_sale,
                                                                                  week_distribution,
                                                                                  weekday_distribution,
                                                                                  product_distribution)
        if type(period_definition) == tuple:
            # If specific dates are requested, drop sample outside of bounds
            mask = sample_records_df["date"] < request_end_date
            mask = mask & (sample_records_df["date"] >= request_start_date)
            sample_records_df = sample_records_df[mask]
        return_dict["records"] = sample_records_df

    return return_dict
