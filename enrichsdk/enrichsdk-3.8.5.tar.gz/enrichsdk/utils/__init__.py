import json
from sqllineage.runner import LineageRunner

from .sample import *

def get_lineage_of_query(engine, sql):
    """
    Given an engine and an SQL expression, find the input
    and output tables. Replace <default> with database
    name from the engine
    """
    dependencies = []
    result = LineageRunner(sql, verbose=True)

    database = engine.url.database

    # Get input tables..
    if len(result.source_tables) > 0:
        tables = [str(t).replace("<default>", database) for t in result.source_tables]

        tables = {
            t.split(".")[-1]: {"text": t.replace(".", " "), "table": t} for t in tables
        }
        dependencies.append(
            {
                "type": "db",
                "nature": "input",
                "objects": tables,
            }
        )

    # Get output dependencies
    if len(result.target_tables) > 0:
        tables = [str(t).replace("<default>", database) for t in result.target_tables]
        tables = {
            t.split(".")[-1]: {"text": t.replace(".", " "), "table": t} for t in tables
        }

        dependencies.append({"type": "db", "nature": "output", "objects": tables})

    return dependencies

class SafeEncoder(json.JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, (datetime, date)):
                result = obj.isoformat()
            elif isinstance(obj, (tuple)):
                result = super().default(list(obj))
            else:
                result = super().default(obj)
        except:
            result = str(obj)

        return result

##################################
# Datetime helpers
##################################
from datetime import datetime, date, timedelta

def get_today():
    return date.today().isoformat()

def get_yesterday():
    yesterday = date.today() + timedelta(days=-1)
    return yesterday.isoformat()

def get_daybefore():
    daybefore = date.today() + timedelta(days=-2)
    return daybefore.isoformat()

##################################
# Helper...
##################################
def note(df, title):
    """
     Quick summary of a dataframe including shape, column, sample etc.

     Args:
        df (dataframe): Input dataframe
        title (str): Title

    Returns:
        str: A formatted text to be used for logging

    """
    msg = title + "\n"
    msg += "--------" + "\n"
    msg += "Timestamp: " + str(datetime.now()) + "\n"
    msg += "\nShape: " + str(df.shape) + "\n"
    msg += "\nColumns: " + ", ".join(df.columns) + "\n"
    if len(df) > 0:
        msg += "\nSample:" + "\n"
        msg += df.sample(min(2, len(df))).T.to_string() + "\n" + "\n"
    msg += "\nDtypes" + "\n"
    msg += df.dtypes.to_string() + "\n"
    msg += "------" + "\n"
    return msg
