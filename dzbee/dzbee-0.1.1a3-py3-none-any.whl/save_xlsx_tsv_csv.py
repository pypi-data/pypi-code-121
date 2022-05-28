"""Save list np.ndarray pd.DataFrame as xlsx."""
# pylint: disable=abstract-class-instantiated
from pathlib import Path
from random import choices
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from logzero import logger

from dzbee.color_map import color_map
from dzbee.gen_filename import gen_filename


def save_xlsx_tsv_csv(
    lst: Union[np.ndarray, List[Union[str, float]], pd.core.frame.DataFrame],
    file: Optional[Path] = None,
    # subset: List = [],
    file_ext: Optional[List[str]] = None,  # .tsv, .csv default .xlsx
) -> pd.core.frame.DataFrame:
    """Save list np.ndarray pd.DataFrame as xlsx.

    Args:
        lst: content to save to xlsx
        file: if None save to cwd with a random file name
        x subset: columns that are styled with color_apply
        file_ext: .xlsx or .csv or .tsv, default: .xlsx
    Returns:
        pd.DataFrame
    """
    if file is None:
        _ = "".join([*"aa"] + choices("abcdefg", k=7) + choices("12345", k=3))
        file = Path(_)
    if file_ext is None:
        file_ext = [".xlsx"]
    columns = [str(elm) for elm in list(range(np.array(lst).shape[1]))]

    try:
        df_lst = pd.DataFrame(np.array(lst), columns=columns, dtype="object")
    except Exception as exc:
        logger.error(exc)
        raise

    # return styled df_lst if no filename provided
    # if file is None: return df_lst

    _ = """
    if Path(file).suffix not in [".xlsx"]:
        file = f"{file}.xlsx"
    if Path(file).suffix not in [f"{file_ext}"]:
        file = f"{file}{file_ext}"
    # """

    # save .csv
    # if file_ext in [".csv"]:
    if ".csv" in file_ext:
        _ = file.with_suffix(".csv")
        _ = gen_filename(_)
        df_lst.to_csv(_, index=False, header=False, encoding="gbk")  # or GB18030
        logger.info("csv written to %s", Path(_).absolute())

    # save .tsv
    # if file_ext in [".tsv"]:
    if ".tsv" in file_ext:
        _ = file.with_suffix(".tsv")
        _ = gen_filename(_)
        df_lst.to_csv(_, sep="\t", index=False, header=False)
        logger.info("tsv written to %s", Path(_).absolute())

    if ".xlsx" not in file_ext:
        return df_lst

    # proceed to process .xlsx
    # color the likelihood column (3rd col)

    # s_df = df_lst.style.applymap(color_map, subset=[*df_lst.columns[2:3]])

    _ = file.with_suffix(".xlsx")
    _ = Path(gen_filename(_))

    logger.debug("filep: %s, \n\t%s", _, df_lst.head(1))

    subset = list(df_lst.columns[2:3])  # 3rd col
    s_df = df_lst.style.applymap(color_map, subset=subset)
    try:
        # writer = pd.ExcelWriter(_)
        with pd.ExcelWriter(_, engine="xlsxwriter") as writer:
            s_df.to_excel(writer, index=False, header=False, sheet_name="Sheet1")
            writer.sheets["Sheet1"].set_column("A:A", 70)
            writer.sheets["Sheet1"].set_column("B:B", 70)

        # writer.close()
        logger.info("xlsx written to \n\t %s", Path(_).absolute())
    except Exception as exc:
        logger.exception("Unable to save: %s", exc)
        raise

    return df_lst


def test_save_xlsx1():
    """Test save_xlsx Path."""
    filepath = Path("data/test.xlsx")
    lst = [[0, 1, "a"], [1, 1, 1]]
    res = save_xlsx_tsv_csv(lst, filepath)
    del res
    assert Path(filepath).exists()
