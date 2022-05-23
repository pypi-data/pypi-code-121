# -*- coding: utf-8 -*-
import logging

LOG = logging.getLogger(__name__)


def delete_genes(collection, build="GRCh37") -> int:
    """Delete all genes from gene database collection

    Accepts:
        build(str): GRCh37 or GRCh38

    Returns:
        result.deleted(int): number of deleted documents
    """
    query = {"build": build}
    try:
        result = collection.delete_many(query)
    except Exception as err:
        LOG.error(err)
        return
    return result.deleted_count


def delete_dataset(database, id) -> int:
    """Delete a dataset from dataset collection

    Accepts:
        database(pymongo.database.Database)
        id(str): dataset id

    Returns:
        result.deleted(int): number of deleted documents
    """

    collection = "dataset"

    try:
        result = database[collection].delete_one({"_id": id})
    except Exception as err:
        LOG.error(err)
        return
    return result.deleted_count


def delete_variants(database, ds_id, samples) -> tuple:
    """Delete variants for one or more samples

    Accepts:
        database(pymongo.database.Database)
        ds_id(str): dataset id
        samples(tuple): name of samples in this dataset

    Returns:
        n_updated, n_removed(tuple): number of variants updated/removed from database
    """
    n_updated = 0
    n_removed = 0
    query = {"$or": []}

    sample_list = list(samples)
    for sample in sample_list:
        nested_doc_id = ".".join(["datasetIds", ds_id, "samples", sample])
        query["$or"].append({nested_doc_id: {"$exists": True}})

    results = database["variant"].find(query)
    for res in results:
        updated, removed = delete_variant(database, ds_id, res, sample_list)
        if updated is True:
            n_updated += 1
        if removed is True:
            n_removed += 1

    return n_updated, n_removed


def delete_variant(database, dataset_id, variant, samples) -> tuple:
    """Delete one variant from database or just update the samples having it

    Accepts:
        database(pymongo.database.Database)
        dataset_id(str): dataset id
        variant(dict): one variant
        samples(list) : list of samples to remove this variant for

    Returns:
        (updated, removed)(tuple of bool): if variant was updated or removed

    """
    updated = False
    removed = False

    # {sample1:{allele_count:2}, sample2:{allele_count:1}, ..}
    dataset_samples = variant["datasetIds"][dataset_id].get("samples", {})

    remove_allele_count = 0
    for sample in samples:  # loop over the samples to remove
        if sample in dataset_samples:
            remove_allele_count += dataset_samples[sample]["allele_count"]
            dataset_samples.pop(sample)

    # If there are still samples in database with this variant
    # Keep variant and update the list of samples
    if dataset_samples != {}:
        results = database["variant"].find_one_and_update(
            {"_id": variant["_id"]},
            {
                "$set": {
                    ".".join(["datasetIds", dataset_id, "samples"]): dataset_samples,
                    "call_count": variant["call_count"] - remove_allele_count,
                }
            },
        )
        if results is not None:
            updated = True
    else:  # No samples in database with this variant, remove it
        results = database["variant"].find_one_and_delete({"_id": variant["_id"]})
        if results is not None:
            removed = True

    return updated, removed
