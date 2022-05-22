#!/usr/bin/env python3

import json
import re
import os
import pandas as pd
from typing import List
import yaml

import detectron2.config
from detectron2.config import get_cfg


def strip_filepath(fpath: str):
    return fpath.replace("file://", "")


def put_slurm_id_to_front(df):
    colnames = df.columns.tolist()
    colnames = [colnames.pop(colnames.index("SLURM_ID"))] + colnames
    return df[colnames]


def create_empty_eval_results():
    data = {"bbox.AP": [pd.NA],
            "bbox.AP50": [pd.NA],
            "bbox.AP75": [pd.NA],
            "bbox.APs": [pd.NA],
            "bbox.APm": [pd.NA],
            "bbox.APl": [pd.NA],
            }
    return pd.DataFrame(data)


def get_slurm_id_from_path(fpath: str):
    pattern = re.compile(r".*/(\d\d\d\d)_\d\d\d\d-\d\d-\d\d_\d\d\d\d\d\d")
    match = pattern.findall(fpath)[0]
    return match


def load_cfg(fpath_cfg: str) -> detectron2.config.CfgNode:
    cfg = get_cfg()
    cfg.merge_from_file(fpath_cfg)
    return cfg


def flatten_cfg(cfg: detectron2.config.CfgNode):
    cfg_dict = dict(cfg.items())
    cfg_flat = pd.DataFrame(pd.json_normalize(cfg_dict))
    cfg_flat["SLURM_ID"] = get_slurm_id_from_path(cfg_flat["OUTPUT_DIR"].values[0])
    return cfg_flat


def load_cfg_flat(fpath_cfg: str):
    try:
        cfg = load_cfg(fpath_cfg)
    except KeyError as e:
        print(f"KeyError. Falling back to loading via yaml. {fpath_cfg}: Error: {e}")
        with open(fpath_cfg, "r") as f:
            cfg = yaml.safe_load(f)
    return flatten_cfg(cfg)


def load_eval_results(fpath_eval_results_txt: str):
    try:
        with open(fpath_eval_results_txt, "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"Did not find eval file {fpath_eval_results_txt}. Creating empty fallback results object.")
        results = create_empty_eval_results()
    return results


def merge_cfg_and_results(fpath_cfg, fpath_eval_results_txt):
    cfg = load_cfg_flat(fpath_cfg)
    results = pd.json_normalize(load_eval_results(fpath_eval_results_txt))
    line = pd.DataFrame(cfg)
    line = line.join(results)  # Glue the results to the end of the line
    return line


def add_line_to_existing_csv(fpath_csv: str, line: pd.DataFrame):
    try:
        existing = pd.read_csv(fpath_csv)
    except FileNotFoundError:
        print(f"Creating new csv file, provided csv file not found: {fpath_csv}")
        line.to_csv(fpath_csv)
    else:
        existing = existing.append(line)
        existing.to_csv(fpath_csv)


def load_table(fdir_results):
    cfg_path = os.path.join(fdir_results, "cfg.yaml")
    res_fpath = os.path.join(fdir_results, "evaluation_results.txt")
    data = merge_cfg_and_results(cfg_path, res_fpath)
    return data


def merge_multiple_results(fdirs: List[str]):
    """
    Takes a list of training result dirs and merges all their settings and results into one data frame
    :param fdirs:
    :return:
    """
    fdirs = [strip_filepath(fpath) for fpath in fdirs]
    data = pd.DataFrame()
    for fdir in fdirs:
        data = data.append(load_table(fdir))
    return data


if __name__ == "__main__":

    save_path = "/home/findux/Desktop/results.csv"

    fdirs = [
        "/media/findux/DATA/Documents/Malta_II/results/5644_2022-05-21_204705",
        "file:///media/findux/DATA/Documents/Malta_II/results/5659_2022-05-22_013436",
        "file:///media/findux/DATA/Documents/Malta_II/results/5660_2022-05-22_030906",
        "file:///media/findux/DATA/Documents/Malta_II/results/5661_2022-05-22_045237",
        "file:///media/findux/DATA/Documents/Malta_II/results/5662_2022-05-22_045337",
        "file:///media/findux/DATA/Documents/Malta_II/results/5663_2022-05-22_045437",
        "file:///media/findux/DATA/Documents/Malta_II/results/5664_2022-05-22_045537",
    ]

    data = merge_multiple_results(fdirs)
    data.to_csv(save_path)