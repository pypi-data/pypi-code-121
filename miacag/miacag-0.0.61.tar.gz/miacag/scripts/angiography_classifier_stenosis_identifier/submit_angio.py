import uuid
import os
import socket
from datetime import datetime
import yaml
from miacag.preprocessing.split_train_val import splitter
from miacag.utils.sql_utils import copy_table, add_columns, \
    copyCol, changeDtypes
import pandas as pd
from miacag.postprocessing.append_results import appendDataFrame
import torch
from miacag.trainer import train
from miacag.tester import test
from miacag.configs.config import load_config, maybe_create_tensorboard_logdir
from miacag.configs.options import TrainOptions
import argparse
from miacag.preprocessing.labels_map import labelsMap
from miacag.preprocessing.utils.check_experiments import checkExpExists, \
    checkCsvExists
from miacag.plots.plotter import plot_results
import pandas as pd
from miacag.preprocessing.transform_thresholds import transformThreshold
from miacag.preprocessing.transform_missing_floats import transformMissingFloats
from miacag.scripts.angiography_classifier.submit_angio import angio_classifier
from miacag.scripts.stenosis_identifier.submit_angio import stenosis_identifier
from miacag.utils.script_utils import create_empty_csv, mkFolder


parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--cpu', type=str,
    help="if cpu 'True' else 'False'")
parser.add_argument(
            "--local_rank", type=int,
            help="Local rank: torch.distributed.launch.")    
parser.add_argument(
            "--num_workers", type=int,
            help="Number of cpu workers for training")    
parser.add_argument(
    '--config_path_lca_rca', type=str,
    help="path to folder with config files")
parser.add_argument(
    '--config_path_stenosis', type=str,
    help="path to folder with config files")

if __name__ == '__main__':
    args = parser.parse_args()
    table_name = angio_classifier(args.cpu, args.num_workers,
                                  args.config_path_lca_rca)
    stenosis_identifier(args.cpu, args.num_workers,
                        args.config_path_stenosis, table_name)
