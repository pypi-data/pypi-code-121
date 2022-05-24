"""databases module

This module contains some useful functionsl like delete_old_table_versions

"""

import logging
from . import glue_database


def get_all_databases(glue_client):
    paginator = glue_client.get_paginator("get_databases")
    page_iterator = paginator.paginate()
    result = []
    for page in page_iterator:
        dbs = list(map(lambda t: t["Name"], page["DatabaseList"]))
        result = result + dbs
    logging.debug(f"Found databases {result}")
    return result


def get_all_tables(glue_client, databases=[]):
    if databases == []:
        databases = get_all_databases(glue_client)
    tot = []
    for db in databases:
        logging.info(f"Entering db={db}")
        result = glue_database.get_all_tables(glue_client, database_name)
        tot += result
    return tot


def count_tables(glue_client, databases):
    if databases == []:
        databases = get_all_databases(glue_client)
    tot = 0
    for db in databases:
        logging.info(f"Entering db={db}")
        result = glue_database.count_tables(glue_client, db)
        tot += result
    return tot


def get_tables_with_many_versions(glue_client, databases=[], threshold=100):
    tot = {}
    if databases == []:
        databases = get_all_databases(glue_client)

    for db in databases:
        logging.info(f"Entering db={db}")
        result = glue_database.get_tables_with_many_versions(glue_client, db, threshold)
        tot[db] = result
    return tot


def exist_tables_with_many_versions(glue_client, databases=[], threshold=100):
    if databases == []:
        databases = get_all_databases(glue_client)

    for db in databases:
        logging.info(f"Entering db={db}")
        if glue_database.exist_tables_with_many_versions(glue_client, db, threshold):
            return True

    return False


def count_tables_versions(glue_client, databases=[]):
    result = 0
    if databases == []:
        databases = get_all_databases(glue_client)
    for db in databases:
        logging.info(f"Entering db={db}")
        result += glue_database.count_tables_versions(glue_client, db)
    return result


def delete_all_tables(glue_client, databases=[], dryrun=False):
    if databases == []:
        databases = get_all_databases(glue_client)
    for db in databases:
        logging.info(f"Entering db={db}")
        aws_ext.glue_database.delete_all_tables(glue_client, db, dryrun=dryrun)


def delete_old_tables_versions(glue_client, databases=[], keep=100, dryrun=False):
    if databases == []:
        databases = get_all_databases(glue_client)
    for db in databases:
        logging.info(f"Entering db={db}")
        glue_database.delete_old_tables_versions(glue_client, db, keep, dryrun=dryrun)
