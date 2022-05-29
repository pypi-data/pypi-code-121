"""Convert two iesl to pandas.DataFrame."""
# pylint: disable=invalid-name

import tempfile
from itertools import zip_longest

import pandas as pd

from litbee.process_upload import process_upload


def files2df(file1, file2):
    """Convert two files to pd.DataFrame."""
    text1 = [_.strip() for _ in process_upload(file1).splitlines() if _.strip()]

    # if file2 is tempfile._TemporaryFileWrapper:
    if isinstance(file2, tempfile._TemporaryFileWrapper):
        try:
            filename = file2.name
        except AttributeError:
            filename = ""
    else:
        filename = file2
    if filename:
        # text2 = [_.strip() for _ in process_upload(file2).splitlines() if _.strip()]
        text2 = [_.strip() for _ in process_upload(filename).splitlines() if _.strip()]
    else:
        text2 = [""]

    text1, text2 = zip(*zip_longest(text1, text2, fillvalue=""))

    df = pd.DataFrame({"text1": text1, "text2": text2})

    return df


_ = """
    # return tabulate(df)
    # return tabulate(df, tablefmt="grid")
    # return tabulate(df, tablefmt='html')
# """
