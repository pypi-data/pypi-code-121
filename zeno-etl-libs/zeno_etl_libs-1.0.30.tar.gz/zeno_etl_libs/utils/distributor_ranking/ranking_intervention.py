"""
To override algorithmic ranking according to distributor preference
author: vivek.revi@zeno.health
"""

import pandas as pd
import numpy as np
import datetime as dt


def ranking_override_dc(features_rank, db, read_schema, logger,
                        override_type_list=['AS/MS']):
    # Get distributor preference list
    current_date = dt.date.today().strftime('%Y-%m-%d')
    q_preference = """
        select "dc-id", "drug-id", "distributor-preference", "distributor-id"
        from "{read_schema}"."distributor-ranking-preference"
        where "is-active" = 1
        and "start-date" < '{0}'
        and "end-date" > '{0}'
        and "dc-id" is not null 
        """.format(current_date, read_schema=read_schema)
    rank_override = db.get_df(q_preference)

    if rank_override.shape[0] != 0:
        # Manual rank override logic starts
        logger.info(f"Overriding for {override_type_list}")
        original_shape = features_rank.shape
        features_rank = features_rank.reset_index(drop=True)
        rank_override = rank_override.dropna()
        rank_override = rank_override.drop_duplicates()
        rank_override = rank_override.sort_values(
            ['dc_id', 'drug_id', 'distributor_preference', 'distributor_id'],
            ascending=[True, True, True, True]).reset_index(drop=True)

        rank_override_grp = rank_override.groupby(["dc_id", "drug_id"],
                                                  as_index=False).agg(
                                                {"distributor_id": dist_order})
        rank_override_grp.rename({"distributor_id": "override_dist_order"}, axis=1,
                                 inplace=True)

        df_merged = features_rank.merge(rank_override_grp, on=["dc_id", "drug_id"],
                                        how="left")

        df_rank_override = df_merged.loc[~df_merged["override_dist_order"].isna()]
        df_rank_override = df_rank_override.loc[
            df_rank_override["request_type"].isin(override_type_list)]
        index_to_drop = df_rank_override.index.values.tolist()
        features_rank = features_rank.drop(index_to_drop)

        logger.info(f"Number of rows to update ranks: {original_shape[0]-features_rank.shape[0]}")

        df_rank_override["final_dist_1"] = df_rank_override["final_dist_1"].fillna(0)
        df_rank_override["final_dist_2"] = df_rank_override["final_dist_2"].fillna(0)
        df_rank_override["final_dist_3"] = df_rank_override["final_dist_3"].fillna(0)

        dist_1 = np.array(df_rank_override["final_dist_1"].astype(int))
        dist_2 = np.array(df_rank_override["final_dist_2"].astype(int))
        dist_3 = np.array(df_rank_override["final_dist_3"].astype(int))

        stacked_dist = np.stack((dist_1, dist_2, dist_3), axis=-1)
        df_rank_override["prev_dist_order"] = list(stacked_dist)

        order_list = []
        for index, row in df_rank_override.iterrows():
            eval_string = str(row["override_dist_order"]) + "+" + str(list(row["prev_dist_order"]))
            order_list.append(str(eval(eval_string)[:3]).replace('[', '').replace(']', '').replace(' ', ''))
        df_rank_override["final_order"] = order_list

        df_final_order = df_rank_override['final_order'].str.split(pat=',', expand=True).rename(
                                                    columns={0: 'final_dist_1',
                                                             1: 'final_dist_2',
                                                             2: 'final_dist_3'})

        df_final_order["final_dist_1"] = df_final_order["final_dist_1"].astype(int)
        df_final_order["final_dist_2"] = df_final_order["final_dist_2"].astype(int)
        df_final_order["final_dist_3"] = df_final_order["final_dist_3"].astype(int)

        df_final_order = df_final_order.replace({0: np.nan})

        df_rank_override["final_dist_1"] = df_final_order["final_dist_1"]
        df_rank_override["final_dist_2"] = df_final_order["final_dist_2"]
        df_rank_override["final_dist_3"] = df_final_order["final_dist_3"]

        df_rank_override.drop(["override_dist_order", "prev_dist_order", "final_order"],
                              axis=1, inplace=True)

        features_rank = features_rank.append(df_rank_override)
        features_rank.sort_index(ascending=True, inplace=True)

        assert features_rank.shape == original_shape

    else:
        logger.info("Skipping..: no rank preferences present in table")

    return features_rank


def ranking_override_franchisee(features_rank, db, read_schema, logger,
                                override_type_list=['AS/MS', 'PR']):
    # Get distributor preference list
    current_date = dt.date.today().strftime('%Y-%m-%d')
    q_preference = """
        select "dc-id", "drug-id", "distributor-preference", "distributor-id"
        from "{read_schema}"."distributor-ranking-preference"
        where "is-active" = 1
        and start_date < '{0}'
        and end_date > '{0}'
        and "store-id" is not null
        """.format(current_date, read_schema=read_schema)
    rank_override = db.get_df(q_preference)

    if rank_override.shape[0] != 0:
        # Manual rank override logic starts
        logger.info(f"Overriding for {override_type_list}")
        original_shape = features_rank.shape
        features_rank = features_rank.reset_index(drop=True)
        rank_override = rank_override.dropna()
        rank_override = rank_override.drop_duplicates()
        rank_override = rank_override.sort_values(
            ['store_id', 'drug_id', 'distributor_preference', 'distributor_id'],
            ascending=[True, True, True, True]).reset_index(drop=True)

        rank_override_grp = rank_override.groupby(["store_id", "drug_id"],
                                                  as_index=False).agg(
                                                {"distributor_id": dist_order})
        rank_override_grp.rename({"distributor_id": "override_dist_order"}, axis=1,
                                 inplace=True)

        df_merged = features_rank.merge(rank_override_grp, on=["store_id", "drug_id"],
                                        how="left")

        df_rank_override = df_merged.loc[~df_merged["override_dist_order"].isna()]
        df_rank_override = df_rank_override.loc[
            df_rank_override["request_type"].isin(override_type_list)]
        index_to_drop = df_rank_override.index.values.tolist()
        features_rank = features_rank.drop(index_to_drop)

        logger.info(f"Number of rows to update ranks: {original_shape[0]-features_rank.shape[0]}")

        df_rank_override["final_dist_1"] = df_rank_override["final_dist_1"].fillna(0)
        df_rank_override["final_dist_2"] = df_rank_override["final_dist_2"].fillna(0)
        df_rank_override["final_dist_3"] = df_rank_override["final_dist_3"].fillna(0)

        dist_1 = np.array(df_rank_override["final_dist_1"].astype(int))
        dist_2 = np.array(df_rank_override["final_dist_2"].astype(int))
        dist_3 = np.array(df_rank_override["final_dist_3"].astype(int))

        stacked_dist = np.stack((dist_1, dist_2, dist_3), axis=-1)
        df_rank_override["prev_dist_order"] = list(stacked_dist)

        order_list = []
        for index, row in df_rank_override.iterrows():
            eval_string = str(row["override_dist_order"]) + "+" + str(list(row["prev_dist_order"]))
            order_list.append(str(eval(eval_string)[:3]).replace('[', '').replace(']', '').replace(' ', ''))
        df_rank_override["final_order"] = order_list

        df_final_order = df_rank_override['final_order'].str.split(pat=',', expand=True).rename(
                                                    columns={0: 'final_dist_1',
                                                             1: 'final_dist_2',
                                                             2: 'final_dist_3'})

        df_final_order["final_dist_1"] = df_final_order["final_dist_1"].astype(int)
        df_final_order["final_dist_2"] = df_final_order["final_dist_2"].astype(int)
        df_final_order["final_dist_3"] = df_final_order["final_dist_3"].astype(int)

        df_final_order = df_final_order.replace({0: np.nan})

        df_rank_override["final_dist_1"] = df_final_order["final_dist_1"]
        df_rank_override["final_dist_2"] = df_final_order["final_dist_2"]
        df_rank_override["final_dist_3"] = df_final_order["final_dist_3"]

        df_rank_override.drop(["override_dist_order", "prev_dist_order", "final_order"],
                              axis=1, inplace=True)

        features_rank = features_rank.append(df_rank_override)
        features_rank.sort_index(ascending=True, inplace=True)

        assert features_rank.shape == original_shape

    else:
        logger.info("Skipping..: no rank preferences present in table")

    return features_rank


def dist_order(pd_arr):
    """To arrange in preference order and avoid duplication"""
    pd_arr = list(pd_arr)
    dist_list = [i for n, i in enumerate(pd_arr) if i not in pd_arr[:n]]
    return dist_list[:3]
