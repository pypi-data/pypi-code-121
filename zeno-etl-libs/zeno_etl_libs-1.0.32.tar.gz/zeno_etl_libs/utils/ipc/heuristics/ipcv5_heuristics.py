"""
IPC V5 Corrections:
* Calculates STD Patient-Drug Qty for past 3 months
* Only for repeatable drugs
* If IPC Set ROP < STD Qty (drug-level), then set ROP = STD Qty
* Adjust SS & OUP accordingly
author: vivek.revi@zeno.health
"""

import pandas as pd
import numpy as np
import datetime as dt


def v5_corrections(store_id, safety_stock_df, db, schema, logger):
    """
        Main function to perform V5 corrections
    """
    # Get Drug STD Qty and list of repeatable drug_ids
    df_3m_drugs, unique_drugs_3m = get_3m_drug_std_qty(store_id, db, schema, logger)

    # Locate drugs to perform correction check
    df_std_check = safety_stock_df.loc[safety_stock_df["drug_id"].isin(
        unique_drugs_3m)][["drug_id", "fcst", "safety_stock", "reorder_point", "order_upto_point"]]

    # Drugs not forecasted by IPC
    drugs_3m_not_set = list(set(unique_drugs_3m) ^ set(df_std_check["drug_id"].unique()))
    logger.info(f"Number of drugs not forecasted: {len(drugs_3m_not_set)}")

    # Merge STD Qty with SS table and find drugs correction areas
    df_std_check = df_3m_drugs.merge(df_std_check, on="drug_id", how="left")
    df_std_check = df_std_check.dropna()
    df_std_check["rop>=std_qty"] = np.where(
        df_std_check["reorder_point"] >= df_std_check["std_qty"], "Y", "N")

    tot_rep_drugs = df_std_check.shape[0]
    corr_req = df_std_check.loc[df_std_check['rop>=std_qty'] == 'N'].shape[0]
    corr_not_req = df_std_check.loc[df_std_check['rop>=std_qty'] == 'Y'].shape[0]
    logger.info(f"Number of repeatable drugs: {tot_rep_drugs}")
    logger.info(f"Number of repeatable drugs corrections required: {corr_req}")
    logger.info(f"Number of repeatable drugs corrections not required: {corr_not_req}")

    # CORRECTION STARTS
    order_freq = 4
    column_order = list(df_std_check.columns)
    column_order += ["corr_ss", "corr_rop", "corr_oup"]

    # CASE1: No changes required
    df_no_change = df_std_check.loc[df_std_check["rop>=std_qty"] == "Y"].copy()
    df_no_change["corr_ss"] = df_no_change["safety_stock"].astype(int)
    df_no_change["corr_rop"] = df_no_change["reorder_point"].astype(int)
    df_no_change["corr_oup"] = df_no_change["order_upto_point"].astype(int)

    # CASE2: SS & ROP & OUP is Non Zero
    df_change1 = df_std_check.loc[(df_std_check["rop>=std_qty"] == "N") &
                                  (df_std_check["safety_stock"] != 0) &
                                  (df_std_check["reorder_point"] != 0) &
                                  (df_std_check["order_upto_point"] != 0)].copy()
    df_change1["mul_1"] = df_change1["reorder_point"] / df_change1["safety_stock"]
    df_change1["mul_2"] = df_change1["order_upto_point"] / df_change1["reorder_point"]
    df_change1["corr_rop"] = df_change1["std_qty"]
    df_change1["corr_ss"] = np.ceil(df_change1["corr_rop"] / df_change1["mul_1"]).astype(int)
    # If ROP >= OUP, then in those cases, increase OUP.
    df_change11 = df_change1.loc[
        df_change1["corr_rop"] >= df_change1["order_upto_point"]].copy()
    df_change12 = df_change1.loc[
        df_change1["corr_rop"] < df_change1["order_upto_point"]].copy()
    df_change11["corr_oup"] = np.ceil(df_change11["corr_rop"] + (
                df_change11["fcst"] * order_freq / 28)).astype(int)
    df_change12["corr_oup"] = np.ceil(df_change12["corr_rop"] + (
                df_change12["fcst"] * order_freq / 28)).astype(int)
    df_change1 = df_change11.append(df_change12)
    df_change1 = df_change1[column_order]

    # CASE3: Any of SS & ROP & OUP is Zero
    df_change2 = df_std_check.loc[(df_std_check["rop>=std_qty"] == "N")].copy()
    df_change2 = df_change2.loc[~((df_change2["safety_stock"] != 0) &
                                  (df_change2["reorder_point"] != 0) &
                                  (df_change2["order_upto_point"] != 0))].copy()
    df_change2["corr_rop"] = df_change2["std_qty"].astype(int)
    df_change2["corr_ss"] = np.floor(df_change2["corr_rop"] / 2).astype(int)
    # If ROP >= OUP, then in those cases, increase OUP.
    df_change21 = df_change2.loc[
        df_change2["corr_rop"] >= df_change2["order_upto_point"]].copy()
    df_change22 = df_change2.loc[
        df_change2["corr_rop"] < df_change2["order_upto_point"]].copy()
    df_change21["corr_oup"] = np.ceil(df_change21["corr_rop"] + (
                df_change21["fcst"] * order_freq / 28)).astype(int)
    df_change22["corr_oup"] = np.ceil(df_change22["corr_rop"] + (
                df_change22["fcst"] * order_freq / 28)).astype(int)
    df_change2 = df_change21.append(df_change22)
    df_change2 = df_change2[column_order]

    # Combine all 3 cases
    df_corrected = df_no_change.append(df_change1)
    df_corrected = df_corrected.append(df_change2)
    df_corrected = df_corrected.sort_index(ascending=True)

    # Get DF of corrected drugs and merge with input DF
    df_corrected_to_merge = df_corrected.loc[df_corrected["rop>=std_qty"] == "N"][
                                ["drug_id", "corr_ss", "corr_rop", "corr_oup"]]
    corr_safety_stock_df = safety_stock_df.merge(df_corrected_to_merge,
                                                 on="drug_id", how="left")

    # Make corrections for required drugs
    corr_safety_stock_df["safety_stock"] = np.where(
        corr_safety_stock_df["corr_ss"] >= 0, corr_safety_stock_df["corr_ss"],
        corr_safety_stock_df["safety_stock"])
    corr_safety_stock_df["reorder_point"] = np.where(
        corr_safety_stock_df["corr_rop"] >= 0, corr_safety_stock_df["corr_rop"],
        corr_safety_stock_df["reorder_point"])
    corr_safety_stock_df["order_upto_point"] = np.where(
        corr_safety_stock_df["corr_oup"] >= 0, corr_safety_stock_df["corr_oup"],
        corr_safety_stock_df["order_upto_point"])

    corr_safety_stock_df.drop(["corr_ss", "corr_rop", "corr_oup"], axis=1, inplace=True)
    corr_safety_stock_df["max_value"] = corr_safety_stock_df["order_upto_point"] * \
                                        corr_safety_stock_df["fptr"]

    assert safety_stock_df.shape == corr_safety_stock_df.shape

    # Evaluate PRE and POST correction
    pre_post_metrics = {
        "metric": ["pre_corr", "post_corr"],
        "ss_qty": [safety_stock_df["safety_stock"].sum(),
                   corr_safety_stock_df["safety_stock"].sum()],
        "ss_val": [round((safety_stock_df["safety_stock"] * safety_stock_df["fptr"]).sum(), 2),
                   round((corr_safety_stock_df["safety_stock"] * corr_safety_stock_df["fptr"]).sum(), 2)],
        "rop_qty": [safety_stock_df["reorder_point"].sum(), corr_safety_stock_df["reorder_point"].sum()],
        "rop_val": [round((safety_stock_df["reorder_point"] * safety_stock_df["fptr"]).sum(), 2),
                    round((corr_safety_stock_df["reorder_point"] * corr_safety_stock_df["fptr"]).sum(), 2)],
        "oup_qty": [safety_stock_df["order_upto_point"].sum(), corr_safety_stock_df["order_upto_point"].sum()],
        "oup_val": [round((safety_stock_df["order_upto_point"] * safety_stock_df["fptr"]).sum(), 2),
                    round((corr_safety_stock_df["order_upto_point"] * corr_safety_stock_df["fptr"]).sum(), 2)]
    }
    pre_post_metics_df = pd.DataFrame.from_dict(pre_post_metrics).set_index('metric').T
    pre_post_metics_df["delta"] = pre_post_metics_df["post_corr"] - pre_post_metics_df["pre_corr"]
    pre_post_metics_df["change%"] = round((pre_post_metics_df["delta"] / pre_post_metics_df["pre_corr"]) * 100, 2)
    logger.info(f"\n{str(pre_post_metics_df)}")

    return corr_safety_stock_df


def max_mode(pd_series):
    return int(max(pd_series.mode()))


def get_3m_drug_std_qty(store_id, db, schema, logger):
    """
        To fetch repeatable patient-drug qty from past 90days and calculate
        standard drug qty.
    """
    start_date = (dt.date.today() - dt.timedelta(days=90)).strftime("%Y-%m-%d")
    end_date = dt.date.today().strftime("%Y-%m-%d")

    q_3m = """
        select "patient-id" , "old-new" , "drug-id" , 
                date("created-at") as "on-date", quantity as "tot-qty"
        from "{schema}".sales
        where "store-id" = {0}
        and "is-repeatable" = 1
        and "bill-flag" = 'gross'
        and "created-at" > '{1} 00:00:00' and "created-at" < '{2} 00:00:00'
        """.format(store_id, start_date, end_date, schema=schema)
    df_3m = db.get_df(q_3m)
    df_3m.columns = [c.replace('-', '_') for c in df_3m.columns]

    # Get patient-drug-level STD Qty
    df_3m["3m_bills"] = 1
    df_3m["std_qty"] = df_3m["tot_qty"]
    df_3m_patient = df_3m.groupby(["patient_id", "drug_id"],
                                  as_index=False).agg(
        {"3m_bills": "sum", "tot_qty": "sum", "std_qty": max_mode})
    logger.info(f"Total repeatable patients: {len(df_3m_patient.patient_id.unique())}")

    # Get drug-level STD Qty
    df_3m_drugs = df_3m_patient.groupby("drug_id", as_index=False).agg(
                                        {"std_qty": "max"})

    # STD Qty > 10 is considered outliers, to drop.
    drug_count_before = df_3m_drugs.shape[0]
    df_3m_drugs = df_3m_drugs.loc[df_3m_drugs["std_qty"] <= 10]
    drug_count_after = df_3m_drugs.shape[0]
    logger.info(f"Number of outlier drugs STD Qty: {drug_count_before-drug_count_after}")

    # Repeatable drugs STD Qty to check against IPC set ROP
    unique_drugs_3m = list(df_3m_drugs["drug_id"].unique())

    return df_3m_drugs, unique_drugs_3m




