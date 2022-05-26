import os
from typing import List, Tuple

import numpy as np
import pandas as pd

from .. import NILM_INPUT_FILE_PATH
from .. import NILM_INPUT_DIR
from ..lib.black_sorcery import nilm_path_fix


def _set_inference_input(df: pd.DataFrame) -> bool:
    df = df.copy()

    # Reformat as expected by NILM-Inference-APIs like "2022-05-16 00:00:17+01:00"
    df["Time"] = pd.to_datetime(df["Time"], unit='s')
    if not os.path.exists(NILM_INPUT_DIR):
        os.makedirs(NILM_INPUT_DIR, exist_ok=True)

    df.to_csv(NILM_INPUT_FILE_PATH, index=False)
    return True


def _disaggregate_to_files() -> List[Tuple[str, str]]:
    with nilm_path_fix():

        # ------------------------------------------------------#
        # Extremely ~spooky~ and error prune piece of code      #
        # Just for the history, this was deprecated since the   #
        # time of writing.                                      #
        #                                                       #
        # Uncle Bob, if you are reading, please forgive me :(   #
        # ------------------------------------------------------#
        from lab.nilm_trainer import nilm_inference
        from constants.enumerates import ElectricalAppliances
        from constants.enumerates import WaterAppliances

        # Consider all known devices
        devices = list(ElectricalAppliances) + list(WaterAppliances)
        devices = [dev.value for dev in devices]

        return nilm_inference(devices=devices, sample_period=5, inference_cpu=True, window_size=1)


def disaggregate(df: pd.DataFrame, timestamp_label: str = "timestamp", target_label: str = "power") -> pd.DataFrame:
    df = df.copy()

    # Filter unneeded columns
    df_filtered = df[[timestamp_label, target_label]]
    df_filtered = df_filtered.rename(columns={timestamp_label: "Time", target_label: "mains"})

    # Write dataframe to input file
    _set_inference_input(df_filtered)

    # Inference
    devices_files = _disaggregate_to_files()

    # Read data back into memory
    for device, file in devices_files:
        temp_df = pd.read_csv(file)
        assert df.shape[0] == temp_df.shape[0], "Mismatch on number of input-output for disaggregated rows"

        col = device.lower().replace(" ", "_")
        col = f"pred_{col}"

        df[col] = temp_df["preds"]

    # Clear rows that originally had NaN as target value, but keep timestamps
    df.loc[df[target_label].isna(), df.columns != timestamp_label] = np.NaN

    return df
