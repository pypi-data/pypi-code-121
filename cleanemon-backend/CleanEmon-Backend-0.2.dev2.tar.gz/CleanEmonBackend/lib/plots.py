import os
from datetime import datetime
from typing import List

from matplotlib import pyplot as plt
import pandas as pd

from CleanEmonCore.models import EnergyData

from .. import PLOT_DIR

if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR, exist_ok=True)


def timestamp_to_label(stamp):
    """Converts `stamp` into a datetime object and returns its reformatted string representation"""

    dt = datetime.fromtimestamp(stamp)
    return dt.strftime("%H:%M:%S")


def plot_data(energy_data: EnergyData, *, columns: List[str] = None, name="plot"):
    """Visualization the given dataframe"""

    df = pd.DataFrame(energy_data.energy_data)

    if not columns:
        columns = []
    else:
        columns = [col.lower() for col in columns]

    timestamp_label = "timestamp"

    if timestamp_label in df:
        time = df[timestamp_label]
        df = df.drop([timestamp_label], axis=1)
    else:
        time = df.index

    for col, data in df.iteritems():
        # Filter only selected columns
        if (columns and str(col).lower() in columns) or (not columns):
            plt.plot(time, data, label=col)
    skip = len(time) // 15

    plt.subplots_adjust(bottom=0.25)
    plt.xticks(time[0:-1:skip], time[0:-1:skip].map(timestamp_to_label), rotation=90, fontsize=8)
    plt.legend()
    plt.title(energy_data.date)
    plt.xlabel("Time")
    fout_name = os.path.join(PLOT_DIR, f"{name}.png")
    plt.savefig(fout_name, dpi=1000)
    return fout_name

