"""tables module

This module contains some useful functionsl like delete_old_table_versions

"""
import logging
from botocore.exceptions import ClientError


def delete_table_version(
    glue_client, database_name, table_name, version_ids, dryrun=False
):
    """delete_table_version"""
    try:
        logging.warning(
            f"Deleting version {version_ids} for table {database_name}.{table_name}"
        )
        if dryrun:
            logging.warning(f"Dryrun: nothing will be changed")
            response = 1
        else:
            ## split version in lists < 100
            ## Member must have length less than or equal to 100
            for ids in [
                version_ids[i : i + 100] for i in range(0, len(version_ids), 100)
            ]:
                version_ids_str = list(map(lambda t: str(t), ids))
                response = glue_client.batch_delete_table_version(
                    DatabaseName=database_name,
                    TableName=table_name,
                    VersionIds=version_ids_str,
                )
        return True
    except ClientError as e:
        raise Exception("boto3 client error in delete_table_version: " + e.__str__())
    except Exception as e:
        raise Exception("Unexpected error in delete_table_version: " + e.__str__())


def get_table_version_ids(
    glue_client, database_name, table_name, max_items=300, page_size=300
):

    ## resp = glue_client.get_table_versions(
    ##    DatabaseName=database_name, TableName=table_name
    ## )
    paginator = glue_client.get_paginator("get_table_versions")
    page_iterator = paginator.paginate(
        DatabaseName=database_name,
        TableName=table_name,
        # PaginationConfig={
        #    "MaxItems": max_items,
        #    "PageSize": page_size
        #'StartingToken':starting_token
        # },
    )

    result = []
    for page in page_iterator:
        alist = list(map(lambda t: int(t["VersionId"]), page["TableVersions"]))
        logging.debug(alist)
        result += alist
    result.sort(reverse=True)
    return result


def delete_old_table_versions(
    glue_client, database_name, table_name, keep, dryrun=False
):
    if int(keep) < 1:
        logging.error(
            f"cannot delete all table versions: keep={keep} must be greater than 0"
        )
        return 1
    versions = get_table_version_ids(glue_client, database_name, table_name)
    logging.warning(
        f"Deleting old versions for table {table_name} keeping {keep} versions"
    )
    version_ids = versions[keep:]
    return delete_table_version(
        glue_client, database_name, table_name, version_ids, dryrun=dryrun
    )


def count_table_versions(glue_client, database_name, table_name):
    resp = get_table_version_ids(glue_client, database_name, table_name)
    return len(resp)
