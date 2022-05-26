from datetime import date
from zeno_etl_libs.utils.fcst_performance import metric_calc
import pandas as pd


def cal_fields_store_drug_level(df_ss, df_inv, df_sales, df_pr_loss, df_3m_sales):
    """
    Calculate all the fields for store-drug level forecast performance assessment
    Parameters:
            df_ss: (pd.DataFrame) safety stock data IPC or Non-IPC
            df_inv: (pd.DataFrame) current inventory data
            df_sales: (pd.DataFrame) 28 days sales data
            df_pr_loss: (pd.DataFrame) 28 days pr loss data
            df_3m_sales: (pd.DataFrame) 3 month sales before reset (for NPI)
    Returns:
            df_sdl: (pd-DataFrame) of store-drug level performance metrics
    """
    # Merge Inventory and NPI dataframe
    df_inv_npi = pd.merge(df_inv, df_3m_sales, on="drug_id", how="left")
    df_inv_npi.net_sales_3m.fillna(0, inplace=True)
    df_inv_npi['is_npi'] = (df_inv_npi['net_sales_3m'] == 0)

    # Merge sales and PR loss dataframe
    df_sales_pr = pd.merge(df_sales, df_pr_loss, on="drug_id", how="left")
    df_sales_pr.pr_loss.fillna(0, inplace=True)

    # Merge inventory, NPI, sales and PR loss dataframes
    df_merged = pd.merge(df_inv_npi, df_sales_pr, on="drug_id", how="left")
    df_merged.net_sales.fillna(0, inplace=True)
    df_merged.pr_loss.fillna(0, inplace=True)
    df_merged = df_merged[["drug_id", "current_inventory", "is_npi",
                           "net_sales", "pr_loss"]]
    df_merged.rename(columns={"net_sales": "net_sales_28days",
                              "pr_loss": "pr_loss_28days"}, inplace=True)

    # Merge all collected data with SS table
    df_all_combined = pd.merge(df_ss, df_merged, on="drug_id", how="left")
    df_all_combined = df_all_combined[df_all_combined['drug_name'].notna()]
    df_all_combined.current_inventory.fillna(0, inplace=True)
    df_all_combined.net_sales_28days.fillna(0, inplace=True)
    df_all_combined.pr_loss_28days.fillna(0, inplace=True)
    df_all_combined.is_npi.fillna(True, inplace=True)

    # Creating dataframe of required format
    df_all_combined.rename(columns={"curr_inventory": "inventory_at_reset",
                                    "std": "fcst_std", "type": "drug_type",
                                    "current_inventory": "inventory_at_measurement"},
                           inplace=True)
    df_all_combined["is_npi"] = df_all_combined["is_npi"].apply(
        lambda x: 'Y' if x == True else 'N')
    df_sdl = df_all_combined[["store_id", "store_type", "drug_id", "drug_name",
                              "drug_type", "drug_grade", "reset_date", "bucket",
                              "is_npi", "model", "percentile", "fcst", "fcst_std",
                              "safety_stock", "reorder_point", "order_upto_point",
                              "inventory_at_reset", "fptr", "inventory_at_measurement",
                              "net_sales_28days", "pr_loss_28days"]].copy()
    df_sdl["demand_28days"] = df_sdl["net_sales_28days"] + df_sdl["pr_loss_28days"]
    df_sdl["fcst_error"] = df_sdl["fcst"] - df_sdl["demand_28days"]

    for index, row in df_sdl.iterrows():
        forecast = row["fcst"]
        actual = row["demand_28days"]
        df_sdl.loc[index, "perc_error"] = metric_calc.pe(forecast, actual)

    df_sdl["measurement_date"] = date.today()
    return df_sdl

