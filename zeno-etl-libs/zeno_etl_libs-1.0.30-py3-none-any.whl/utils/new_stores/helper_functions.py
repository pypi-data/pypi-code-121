"""
Author  -   shubham.jangir@zeno.health
Objective   -   This module contains helper functions for new store ipc
"""

import numpy as np


# Global Queries
Q_REPEATABLE = """
    SELECT
        id AS "drug-id",
        "is-repeatable"
    FROM
        "{schema}".drugs
    WHERE
        "is-repeatable" = 1
"""

Q_PTR = """
    select
        "drug-id",
        AVG(ptr) as ptr
    FROM
        "{schema}"."inventory-1"
    GROUP BY
        "drug-id"
"""

Q_STORES = """
    select
        id as "store-id",
        name as "store-name"
    FROM
        "{schema}".stores
"""

Q_DRUG_INFO = """
    select
        id as "drug-id",
        "drug-name",
        type,
        category
    FROM
        "{schema}".drugs
"""


# Queries with parameters


def prep_data_from_sql(query_pass, db):
    data_fetched = db.get_df(query_pass)
    data_fetched.columns = [c.replace('-', '_') for c in data_fetched.columns]

    return data_fetched


def query_drug_grade(store_id, schema):
    query = """
        SELECT
            "drug-id",
            "drug-grade"
        FROM
            "{schema}"."drug-order-info"
        WHERE
            "store-id" = {0}
        """.format(store_id, schema=schema)
    return query


def query_max_zero(store_id, schema):
    query = """
    SELECT
        "store-id",
        "drug-id"
    FROM
        "{schema}"."drug-order-info"
    WHERE
        "store-id" = {0}
        and max = 0
    """.format(store_id, schema=schema)
    return query


def query_inventory(store_id, schema):
    query = """
    SELECT
        "store-id",
        "drug-id",
        SUM(quantity) AS "current-inventory"
    FROM
        "{schema}"."inventory-1"
    WHERE
        "store-id" = {0}
    GROUP BY
        "store-id",
        "drug-id"
    """.format(store_id, schema=schema)
    return query


def get_drug_info(store_id, db, schema):
    # Inventory and PTR info for order value
    # Also, drug-type and drug-grade
    q_inv = query_inventory(store_id, schema)
    data_inv = prep_data_from_sql(q_inv, db)

    data_ptr = prep_data_from_sql(Q_PTR.format(schema=schema), db)
    data_ptr["ptr"] = data_ptr["ptr"].astype(float)

    data_drug_info = prep_data_from_sql(Q_DRUG_INFO.format(schema=schema), db)

    q_drug_grade = query_drug_grade(store_id, schema)
    data_drug_grade = prep_data_from_sql(q_drug_grade, db)

    data_stores = prep_data_from_sql(Q_STORES.format(schema=schema), db)

    return data_inv, data_ptr, data_drug_info, data_drug_grade, data_stores


def order_value_report(ss_drug_sales):
    ss_drug_sales['to_order_quantity'] = np.where(
        ss_drug_sales['current_inventory'] < ss_drug_sales['safety_stock'],
        ss_drug_sales['max'] - ss_drug_sales['current_inventory'], 0
    )
    ss_drug_sales['to_order_value'] = (
            ss_drug_sales['to_order_quantity'] * ss_drug_sales['ptr'])

    order_value = ss_drug_sales.groupby(
        ['type', 'store_name', 'drug_grade']). \
        agg({'to_order_quantity': 'sum', 'to_order_value': 'sum'}). \
        reset_index()

    return order_value
