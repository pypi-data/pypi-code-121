# -*- coding: utf-8 -*-
import datetime
import logging

from flask.cli import current_app
from pymongo.results import InsertOneResult

from .delete import delete_genes

LOG = logging.getLogger(__name__)


def update_genes(gene_lines, build="GRCh37") -> list:
    """Update database genes using Ensembl Biomart service

    Accepts:
        gene_lines(types.GeneratorType)

    Returns:
        inserted_ids(int): number of genes inserted
    """
    gene_collection = current_app.db["gene"]
    delete_genes(gene_collection, build)
    gene_objects = []
    for line in gene_lines:
        hgnc_id = None
        hgnc_symbol = None
        parsed_line = line.rstrip().split("\t")

        if len(parsed_line) != 6:
            continue  # it's probably the last line (success message)

        # No HGNC ID, do not insert gene into database
        if parsed_line[1] == "":
            continue
        if "HGNC:" in parsed_line[1]:
            parsed_line[1] = parsed_line[1].split(":")[1]
        hgnc_id = int(parsed_line[1])
        if parsed_line[2] != "":
            hgnc_symbol = parsed_line[2]

        gene_obj = dict(
            ensembl_id=parsed_line[0],
            hgnc_id=hgnc_id,
            symbol=hgnc_symbol,
            build=build,
            chromosome=parsed_line[3],
            start=int(parsed_line[4]),
            end=int(parsed_line[5]),
        )
        # gene_collection.insert_one(gene_obj)
        gene_objects.append(gene_obj)

    result = gene_collection.insert_many(gene_objects)
    return result.inserted_ids


def update_event(database, dataset_id, updated_collection, add) -> InsertOneResult.inserted_id:
    """Register an event corresponding to a change in the database

    Accepts:
        database(pymongo.database.Database)
        dataset_id(str): id of dataset that was updated
        updated_collection(str): 'variant', or 'dataset'
        add(bool): whether the variants or the dataset were added or removed
    """
    action = "add"
    if add is False:
        action = "remove"

    event_obj = dict(
        dataset=dataset_id,
        updated_collection=updated_collection,
        created=datetime.datetime.now(),
        add=action,
    )
    # save action
    event_id = database["event"].insert_one(event_obj).inserted_id

    return event_id


def update_dataset(database, dataset_id, samples, add) -> None:
    """Update dataset object in dataset collection after adding or removing variants

    Accepts:
        database(pymongo.database.Database)
        dataset_id(str): id of dataset to be updated
        samples(list): list of samples to be added to/removed from dataset
        add(bool): whether the samples should be added or removed from dataset
    """
    dataset_obj = database["dataset"].find_one({"_id": dataset_id})

    # update list of samples for this dataset
    updated_samples = update_dataset_samples(dataset_obj, samples, add)

    # update variants count for this dataset
    n_variants = update_dataset_variant_count(database, dataset_id)

    # Update number of allele calls for this dataset
    n_alleles = update_dataset_allele_count(database, dataset_id, list(updated_samples))

    result = database["dataset"].find_one_and_update(
        {"_id": dataset_id},
        {
            "$set": {
                "samples": list(updated_samples),
                "variant_count": n_variants,
                "allele_count": n_alleles,
                "updated": datetime.datetime.now(),
            }
        },
    )

    # register an event for this update
    update_event(database, dataset_id, "variant", add)


def update_dataset_samples(dataset_obj, samples, add=True) -> set:
    """Update the list of samples for a dataset

    Accepts:
        dataset_obj(dict): a dataset object
        samples(list): list of samples to be added to/removed from dataset
        add(bool): whether the samples should be added or removed from dataset

    Returns:
        datasets_samples(set): the updated set of samples
    """
    datasets_samples = set(dataset_obj.get("samples", []))

    for sample in samples:  # add or remove samples from dataset object
        if add is True:
            datasets_samples.add(sample)
        else:
            datasets_samples.remove(sample)

    LOG.info(f"Updated dataset contains {len(datasets_samples)} samples")
    return datasets_samples


def update_dataset_variant_count(database, dataset_id) -> int:
    """Count how many variants there are for a dataset and update dataset object with this number

    Accepts:
        database(pymongo.database.Database)
        dataset_id(str): id of dataset to be updated

    Returns:
        n_variants(int): the number of variants with calls for this dataset
    """

    variant_collection = database["variant"]
    # Get all variants present with calls for this dataset
    query = {".".join(["datasetIds", dataset_id]): {"$exists": True}}
    n_variants = sum(1 for i in variant_collection.find(query))

    LOG.info(f"Updated dataset contains {n_variants} variants")
    return n_variants


def update_dataset_allele_count(database, dataset_id, samples) -> int:
    """Count how many allele calls are present for a dataset and update dataset object with this number

    Accepts:
        database(pymongo.database.Database)
        dataset_id(str): id of dataset to be updated
        samples(list): list of dataset samples

    Returns:
        updated_dataset(obj): the updated dataset
    """
    allele_count = 0
    variant_collection = database["variant"]

    n_beacon_datasets = sum(1 for i in database["dataset"].find())

    # If beacon contains only one dataset, then allele count is the sum of allele count for each variant
    if n_beacon_datasets == 1:
        pipe = [{"$group": {"_id": None, "alleles": {"$sum": "$call_count"}}}]
        aggregate_res = variant_collection.aggregate(pipeline=pipe)
        for res in aggregate_res:
            allele_count += res.get("alleles")

    # Else count calls for each sample of this dataset in variant collection and sum them up
    else:
        allele_count = _samples_calls(variant_collection, dataset_id, samples)

    return allele_count


def _samples_calls(variant_collection, dataset_id, samples) -> int:
    """Count all allele calls for a dataset in variants collection

    Accepts:
        variant_collection(pymongo.database.Database.Collection)
        dataset_id(str): id of dataset to be updated
        samples(list): list of dataset samples
    Returns:
        allele_count(int)
    """
    allele_count = 0

    for sample in samples:
        pipe = [
            {
                "$group": {
                    "_id": None,
                    "alleles": {"$sum": f"$datasetIds.{dataset_id}.samples.{sample}.allele_count"},
                }
            }
        ]
        aggregate_res = variant_collection.aggregate(pipeline=pipe)
        for res in aggregate_res:
            allele_count += res.get("alleles")

    return allele_count
