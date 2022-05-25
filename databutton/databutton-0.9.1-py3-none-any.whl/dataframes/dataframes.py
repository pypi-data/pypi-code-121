import io
import os

import pandas as pd
from databutton.utils import (
    download_from_bucket,
    get_databutton_config,
    upload_to_bucket,
)


def get(key: str) -> pd.DataFrame:
    config = get_databutton_config()
    res = download_from_bucket(key, config)
    return pd.read_json(io.BytesIO(res.content), compression="gzip")


def put(df: pd.DataFrame, key: str):
    config = get_databutton_config()
    tmpname = "/tmp/df.json.gz"
    df.to_json(tmpname, compression="gzip")
    with open(tmpname, "rb") as tmpfile:
        upload_to_bucket(tmpfile, config, key, content_type="application/tar+gzip")
    os.remove(tmpname)

    return True
