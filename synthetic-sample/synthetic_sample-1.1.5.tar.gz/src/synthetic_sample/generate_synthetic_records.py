import pandas as pd

from synthetic_sample import calculation_utils
# import calculation_utils

# Internal config vars for distribution definitions
quantity_skewness = 10
package_skewness = 50
quantity_exponential = 1.5
package_exponential = 3

VALUE_COLUMN = "value"
PERIOD_COLUMN = "period"

# TODO Add limit to number of records
def generate_synthetic_records(sales_curve_df: pd.DataFrame, packages_per_sale: float, quantity_per_sale: float,
                               week_distribution: dict, weekday_distribution: dict, product_distribution: dict) -> object:
    """ Generates individual sales records from an aggregated curve

    Args:
        sales_curve_df: dataframe with the aggregate sales values for each period
        packages_per_sale: average number of packages per sale
        quantity_per_sale: average quantity sold per sale
        week_distribution: dictionary indicating how sales are distributed across each weekday, only relevant for monthly curves
        weekday_distribution: dictionary indicating how sales are distributed across each weekday
        product_distribution: dictionary indicating how sales are distributed across each SKU

    Returns:
        dataframe with each sale as a record with the date and categories determined by provided distributions
    """
    # Preprocessing
    quantity_per_package = quantity_per_sale / packages_per_sale
    weekday_distribution = {int(key): weekday_distribution[key] for key in weekday_distribution}
    if "week_number" in sales_curve_df.columns:
        period_type = 'weekly'
    else:
        period_type = "monthly"

    # Generate individual sales records from aggregated sales_time_series_df
    df_list = []
    for index, row in sales_curve_df.iterrows():
        # Create single record for each sale
        if period_type == "weekly":
            raw_data = [{PERIOD_COLUMN: row[PERIOD_COLUMN], "week_number": row["week_number"]}] * row["sales"]
        else:
            raw_data = [{PERIOD_COLUMN: row[PERIOD_COLUMN]}] * row["sales"]
        temp_df = pd.DataFrame(raw_data).rename(columns={0: "date"})
        if period_type == "monthly":
            # Create month specific distribution
            daily_dist_dict = calculation_utils.create_daily_dist_dict_for_month(row[PERIOD_COLUMN], week_distribution, weekday_distribution)
        elif period_type == "weekly":
            daily_dist_dict = calculation_utils.create_daily_dist_dict_for_week(row[PERIOD_COLUMN], weekday_distribution)
        else:
            raise ValueError("Period Type must be 'weekly' or 'monthly'")

        # Apply SKU distributions
        calculation_utils.create_column_from_dist(temp_df, product_distribution, "item_sku")
        calculation_utils.create_column_from_dist(temp_df, daily_dist_dict, "date")
        df_list.append(temp_df)

    # Combine each of the periods dataframes and set the sales amount for each one to 1
    sales_df = pd.concat(df_list)

    # Add packages and quantity based on the statistical curve
    calculation_utils.add_int_column_from_distribution(sales_df, "packages", packages_per_sale, package_skewness, package_exponential, None, 1)
    calculation_utils.add_int_column_from_distribution(sales_df, "quantity", quantity_per_sale, quantity_skewness, quantity_exponential, "packages", 1)

    # Reset index and use to determine the order_id
    sales_df = sales_df.reset_index(drop=True).reset_index()
    sales_df.rename(columns={"index": "order_id"}, inplace=True)
    # Number of digits in ID determined by total number of sales
    digits = len(str(len(sales_df)))
    sales_df["order_id"] = (sales_df["order_id"] + 10**digits).astype(str).str.zfill(digits)

    # Split out records that exceed the provided ratio into separate sales lines
    count = 1
    sales_df["line_id"] = count
    continue_flag = True
    additional_sales_df = pd.DataFrame(columns=sales_df.columns)
    while continue_flag == True:
        count += 1
        # ID records to duplicate and keep a full copy to adjust the same rows on both dataframes
        mask = sales_df["packages"] > packages_per_sale
        duplicate_df = sales_df.copy()
        # If none exist, exit
        if sum(mask) == 0:
            continue_flag = False
        else:
            duplicate_df["line_id"] = count
            # If the record has more packages than the average and has more quantity than the average,
            # a full set with the provided ratio can be extracted
            mask_enough_quantity = ((duplicate_df["quantity"] - int(quantity_per_package)) > (duplicate_df["packages"] - int(packages_per_sale)))
            duplicate_df.loc[mask & mask_enough_quantity, "quantity"] = int(quantity_per_package)
            duplicate_df.loc[mask & mask_enough_quantity, "packages"] = int(packages_per_sale)
            sales_df.loc[mask & mask_enough_quantity, "quantity"] = sales_df.loc[mask & mask_enough_quantity, "quantity"] - int(quantity_per_package)
            sales_df.loc[mask & mask_enough_quantity, "packages"] = sales_df.loc[mask & mask_enough_quantity, "packages"] - int(packages_per_sale)

            # Otherwise, split out a package with a single quantity
            duplicate_df.loc[mask & ~mask_enough_quantity, "quantity"] = 1
            duplicate_df.loc[mask & ~mask_enough_quantity, "packages"] = 1
            sales_df.loc[mask & ~mask_enough_quantity, "quantity"] = sales_df.loc[mask & ~mask_enough_quantity, "quantity"] - 1
            sales_df.loc[mask & ~mask_enough_quantity, "packages"] = sales_df.loc[mask & ~mask_enough_quantity, "packages"] - 1

            additional_sales_df = pd.concat([additional_sales_df, duplicate_df[mask]])

    sales_df = pd.concat([sales_df, additional_sales_df])
    sales_df = sales_df.sort_values(by="order_id").reset_index(drop=True)

    return sales_df
