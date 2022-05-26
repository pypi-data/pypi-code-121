import re
from decimal import Decimal

import pandas as pd


def get_parts(val: str):
    """Splits a string into parts respecting double and single quotes

    Examples:
        >>> get_parts("mycol Random Timestamp \"2023-03-03 00:00:00\" '2026-12-12 23:59:59'")
        ["mycol", "Random", "Timestamp", "2023-03-03 00:00:00", "2026-12-12 23:59:59"]

    """
    groups = re.findall(r"[ ]?(?:(?!\"|')(\S+)|(?:\"|')(.+?)(?:\"|'))[ ]?",
                        val)

    # there are two matching groups for the two cases so get the first non empty val
    def first_non_empty(g):
        if g[0]:
            return g[0]
        else:
            return g[1]

    return [first_non_empty(group) for group in groups]


def split_gcs_path(path: str):
    """Splits a path into bucket and the object path parts."""

    pattern = r"(?:gs://)?(?P<bucket>[^/]+)/(?P<obj>.+)"
    re_match = re.match(pattern, path)
    if not re_match:
        raise Exception(f"path [{path}] is invalid")
    return re_match


def extract_precision_and_scale(type_: str) -> tuple[int, int]:
    """Extracts the precision and scale from a `Decimal(14,4)` type string"""

    decimal_scale_prec_pattern = r"Decimal\((?P<precision>\d+),(?P<scale>\d+)\)"
    re_match = re.match(decimal_scale_prec_pattern, type_)

    if not re_match:
        raise Exception(f"Column type [{type_}] did not fit the expected pattern i.e [Decimal(14,2)]")

    return int(re_match.group("precision")), int(re_match.group("scale"))


def load_csv_with_types(path: str) -> pd.DataFrame:
    """Loads a csv from a file if column names are of the form column_name[type]
    then it converts the column to that type."""

    header_with_type_pattern = r"^(\w+)\[([A-z0-9(),]+)\]$"

    df = pd.read_csv(path)
    for column_name in df.columns:

        re_match = re.match(header_with_type_pattern, column_name)

        if re_match:
            clean_column_name = re_match.group(1)
            type_ = re_match.group(2)

            df.rename(columns={column_name: clean_column_name}, inplace=True)

            match type_:
                case 'String':
                    df[clean_column_name] = df[clean_column_name].astype('string')
                case 'Int':
                    df[clean_column_name] = df[clean_column_name].astype('Int64')
                case 'Date':
                    df[clean_column_name] = pd.to_datetime(df[clean_column_name], dayfirst=True).dt.date
                case 'Timestamp':
                    df[clean_column_name] = pd.to_datetime(df[clean_column_name], dayfirst=True)
                case 'Float':
                    df[clean_column_name] = df[clean_column_name].astype('float64')
                case _ as t if t.startswith('Decimal'): # needs to be able to handle scale and precision
                    _, scale = extract_precision_and_scale(t)

                    df[clean_column_name] = df[clean_column_name][df[clean_column_name].notnull()] \
                                    .round(decimals=scale) \
                                    .astype("string") \
                                    .apply(lambda v: Decimal(v)) \
                                    .astype("object")
                case _:
                    raise Exception(f"type [{type_}] not recognised, expected one of String, Int, Float, Timestamp, Date or Decimal(X,X)")

    df['rowId'] = df.index
    return df
