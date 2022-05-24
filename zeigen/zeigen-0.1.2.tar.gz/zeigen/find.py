# -*- coding: utf-8 -*-
"""Find hydrated waters in structure."""
import pandas as pd
from loguru import logger
from statsdict import Stat  # type: ignore

from .common import APP
from .common import NAME
from .common import STATS
from .config import read_config


@APP.command()
@STATS.auto_save_and_report
def find(set_name: str) -> None:
    """Find hydrated waters in structure file."""
    conf = read_config(NAME)
    print(conf["find"])
    # find_params = conf["find"]
    # logger.info(f"find params={find_params}")
    output = "hydrated_waters.tsv"
    logger.info(f"writing file {output}")
    df = pd.DataFrame({"A": [1, 2, 3]})
    df.to_csv(output, sep="\t")
    STATS["n"] = Stat(1)
