import os
import copy
import json
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.urls import reverse
import sqlite3

from enrichsdk.lib.customer import find_usecase

from .models import ComplexSearchRecord

logger = logging.getLogger("app")

dbpath = os.path.expandvars("path-to-db.sqlite")


def get_complex_task_url(spec, request):
    return reverse("APPNAME:complex_request")


def get_filters():
    """
    All the Filters that must could be applied
    """
    if not os.path.exists(dbpath):
        return []

    # First get all the rules...
    con = sqlite3.connect(dbpath)
    cur = con.cursor()

    # => Get all the rules...
    table = "some_table"
    rules = list(cur.execute(f"SELECT distinct rule FROM {table} order by rule"))
    rules = [r[0] for r in rules]
    rule_conditions = []
    for index, r in enumerate(rules):
        rule_conditions.append({"value": r, "condition": f"(rule = '{r}')"})

    result = [{"name": "Matching Rule", "conditions": rule_conditions}]

    con.close()

    return result


def get_queries():

    base = """\
SELECT *
FROM {}
WHERE (%(conditions)s)
ORDER BY total_txn_value desc
limit {}"""

    # Note: We are implementing uniqueness of the kycid using the groupby
    return [
        {
            "name": "All Available",
            "sql": base.format("tablename", 50000),
            "clean": lambda df: df.groupby("primary_key_id").first().reset_index(),
        },
        {
            "name": "Top 10",
            "sql": base.format("tablename", 100),
            "clean": lambda df: df.groupby("primary_key_id").first().reset_index()[:10],
        },
        {
            "name": "Top 50",
            "sql": base.format("tablename", 500),
            "clean": lambda df: df.groupby("primary_key_id").first().reset_index()[:50],
        },
    ]


search_spec = {
    "name": "Profiles",
    "description": "Profiles for Multiple Usecases",
    "usecase": find_usecase(__file__),
    "links": [{"name": "APPNAME", "url": "APPNAME:index"}],
    "models": {"search_record": ComplexSearchRecord},
    "personas": [
        {
            "type": "sqlite",
            "dbpath": dbpath,
            "name": "Profiles",
            "description": "Profiles match one of many rules. Note that there could be multiple entries per",
            "tables": [
                {
                    "name": "Sample",
                    "table": "tablename",
                    "action": "sample",
                    "download": True,
                },
                {
                    "name": "Queries",
                    "table": "tablename",
                    "action": "query",
                    "download": True,
                    "queries": get_queries(),
                    "filters": get_filters(),
                    "workflow_columns": ["rule", "columns_to_post_to_workflow"],
                },
                {
                    "name": "Search",
                    "table": "tablename",
                    "action": "search",
                    "search_columns": ["columns_to_search"],
                    "workflow_columns": ["rule", "columns_to_post_to_workflow"],
                },
            ],
            "workflows": [
                {"name": "ComplexTask", "url": get_complex_task_url},
            ],
        },
    ],
}


def get_spec():
    spec = copy.copy(search_spec)
    return spec
