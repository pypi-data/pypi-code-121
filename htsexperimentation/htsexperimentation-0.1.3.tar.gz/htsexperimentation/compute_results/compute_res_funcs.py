import pandas as pd
import pickle
import copy
import os
from ..helpers.helper_func import keys_exists
from ..helpers.file_handlers import parse_file_name


def compute_aggreated_results_dict(
    algorithm, dataset, path="../results_probabilistic", err_metric="mase"
):
    results_dict = {}
    for file in [
        path
        for path in os.listdir(path)
        if algorithm in path and dataset in path and "orig" in path
    ]:
        with open(f"{path}/{file}", "rb") as handle:
            sample, version, transformation = parse_file_name(file, dataset)
            if not keys_exists(results_dict, transformation):
                results_dict[transformation] = {}
            if not keys_exists(results_dict, transformation, version):
                results_dict[transformation][version] = {}
            if not keys_exists(results_dict, transformation, version, sample):
                results_dict[transformation][version][sample] = {}

            results_dict_temp = copy.deepcopy(results_dict)
            results_dict_temp[transformation][version][sample] = pickle.load(handle)

            results_dict[transformation][version][sample][err_metric] = {}

            # We are getting the results for each group as lists and we want to store it
            # as objects such as {'mase': {bottom_ind_1: value}, {bottom_ind_2: value}}
            for (k, v_) in results_dict_temp[transformation][version][sample][
                err_metric
            ].items():
                # if it is the original versions we only want to get the individual results
                try:
                    for i in range(len(v_)):
                        results_dict[transformation][version][sample][err_metric][
                            f"{k}_{i}"
                        ] = v_[i]
                except TypeError:
                    # the group has individual results
                    pass
        handle.close()
    return results_dict


def compute_aggregated_results_df(results_dict):
    # shape=(transformation, version, sample, metric, dim)
    # metric = mase, rmse
    # dim = bottom, total, state, gender, legal, all

    df = pd.DataFrame.from_dict(
        {
            (i, j, k, l): results_dict[i][j][k][l]
            for i in results_dict.keys()
            for j in results_dict[i].keys()
            for k in results_dict[i][j].keys()
            for l in results_dict[i][j][k].keys()
        },
        orient="index",
    )
    df = df.reset_index()
    df.rename(
        columns={
            "level_0": "transformation",
            "level_1": "version",
            "level_2": "sample",
            "level_3": "error",
        },
        inplace=True,
    )
    df = df.melt(
        id_vars=["transformation", "version", "sample", "error"],
        var_name="group",
        value_name="value",
    )

    return df


def agg_res_full_hierarchy(results_dict):
    df = compute_aggregated_results_df(results_dict)
    df[['value']] = df[['value']].astype('float')
    df = df.groupby(["group", "version", "sample", "error"]).mean().reset_index()
    df["group"] = df["group"].str.split("_").str[0]
    df["group"] = df["group"].str.lower()
    df.dropna(inplace=True)

    return df


def agg_res_bottom_series(results_dict):
    df = compute_aggregated_results_df(results_dict)

    df_bottom = (
        df.loc[df.group.str.contains("bottom")]
        .groupby(["error", "group"])
        .mean()
        .reset_index()
    )
    df_bottom["order"] = df_bottom["group"].str.split("_").str[2].astype("int32")
    df_bottom["group"] = (
        df_bottom["group"].str.split("_").str[0]
        + "_"
        + df_bottom["group"].str.split("_").str[2]
    )
    return df_bottom.set_index("order").sort_values(by="order")


def calculate_computing_time(
    datasets: list, algorithms: list, path: str = "../results_probabilistic"
):
    res = []
    for d in datasets:
        for algo in algorithms:
            res.append(
                pd.DataFrame(
                    compute_aggreated_results_dict(
                        algorithm=algo, dataset=d, path=path
                    ),
                    index=[algo],
                )
            )
        df = pd.concat(res)
        pass


def calculate_agg_results_all_datasets(
    datasets: list, algorithms: list, err: str, path: str = "../results_probabilistic"
) -> list:
    """Calculate aggregated results for all datasets with the purpose of plotting

    Parameters
    ----------
    :param algorithms: list of algorithms
    :param datasets:  list of datasets
    :param err:  string with the error to be calculated
    :param path: string with the path for the results pickle files

    Returns
    ----------
        list[pd.Dataframe]: - returns list of dataframes for each dataset to be plotted individually

    """
    df_orig_list = []
    for d in datasets:
        res = []
        for algo in algorithms:
            dict_res = compute_aggreated_results_dict(
                algorithm=algo, dataset=d, err_metric=err, path=path
            )
            if dict_res:
                df_res = agg_res_full_hierarchy(dict_res)
                df_res["algorithm"] = algo
                res.append(df_res)

        df = pd.concat(res)
        df_orig = (
            df[(df["version"] == "orig") & (df["error"] == err)]
            .reset_index()
            .drop(["index"], axis=1)
        )

        # sort values by algorithm to plot gpf -> mint -> deepar
        sorter = algorithms
        df_orig = df_orig.sort_values(by="group")
        df_orig.algorithm = df_orig.algorithm.astype("category")
        df_orig.algorithm.cat.set_categories(sorter, inplace=True)
        df_orig_list.append(df_orig)

    return df_orig_list


def get_output(dataset, algorithm, transf, path="../results_probabilistic"):
    for file in [
        path
        for path in os.listdir(path)
        if algorithm in path and dataset in path and "orig" in path and transf in path
    ]:
        with open(f"{path}/{file}", "rb") as handle:
            e = pickle.load(handle)
            handle.close()
    return e
