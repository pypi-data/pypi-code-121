# -*- coding: utf-8 -*-
import logging
from os.path import exists
from typing import Union

from cgbeacon2.constants import (
    BUILD_MISMATCH,
    INVALID_COORDINATES,
    NO_MANDATORY_PARAMS,
    NO_POSITION_PARAMS,
    NO_SECONDARY_PARAMS,
    QUERY_PARAMS_API_V1,
    UNKNOWN_DATASETS,
)
from cgbeacon2.models import DatasetAlleleResponse
from cgbeacon2.utils.add import add_variants as variants_loader
from cgbeacon2.utils.delete import delete_variants as variant_deleter
from cgbeacon2.utils.md5 import md5_key
from cgbeacon2.utils.parse import (
    compute_filter_intervals,
    count_variants,
    extract_variants,
    get_vcf_samples,
)
from cgbeacon2.utils.update import update_dataset
from flask import current_app

RANGE_COORDINATES = ("startMin", "startMax", "endMin", "endMax")
LOG = logging.getLogger(__name__)


def stats() -> dict:
    """Return general stats to be displayed on landing page"""
    db = current_app.db
    stats = dict(
        db_name=current_app.config.get("DB_NAME"),
        n_datasets=db["dataset"].count_documents({}),
        variant_count=db["variant"].count_documents({}),
    )
    return stats


def validate_add_data(req) -> Union[None, str]:
    """Validate the data specified in the paramaters of an add request received via the API.

    Accepts:
        req(flask.request): POST request received by server

    Returns:
        validate_request: None, a string describing errong if not validated
    """
    db = current_app.db
    req_data = req.json

    dataset_id = req_data.get("dataset_id")
    dataset = db["dataset"].find_one({"_id": dataset_id})

    # Invalid dataset
    if dataset is None:
        return "Invalid request. Please specify a valid dataset ID"

    vcf_path = req_data.get("vcf_path")

    # Check that provided VCF file exists
    if exists(vcf_path) is False:
        return f"VCF file was not found at the provided path:{vcf_path}"

    vcf_samples = get_vcf_samples(vcf_path)
    if not vcf_samples:
        return f"Samples {vcf_samples} were not found in VCF files"

    samples = req_data.get("samples", [])
    if overlapping_samples(vcf_samples, samples) is False:
        return f"One or more provided samples were not found in VCF. VCF samples:{vcf_samples}"

    genes = req_data.get("genes")
    if genes is None:  # Return validated OK and then load the entire VCF
        return

    if genes.get("id_type") not in ["HGNC", "Ensembl"]:
        return "Please provide id_type (HGNC or Ensembl) for the given list of genes"

    filter_intervals = compute_filter_intervals(req_data)
    if filter_intervals is None:
        return "Could not create a gene filter using the provided gene list"


def validate_delete_data(req) -> Union[None, str]:
    """Validate the data specified in the parameters of a delete request received via the API.

    Accepts:
        req(flask.request): POST request received by server

    Returns:
        validate_request: None or a string describing errong if not validated
    """
    db = current_app.db
    req_data = req.json

    dataset_id = req_data.get("dataset_id")
    dataset = db["dataset"].find_one({"_id": dataset_id})
    samples = req_data.get("samples")

    # Invalid dataset
    if dataset is None:
        return "Invalid request. Please specify a valid dataset ID"

    # Invalid samples
    if isinstance(samples, list) is False or not samples:
        return "Please provide a valid list of samples"

    if overlapping_samples(dataset.get("samples", []), samples) is False:
        return "One or more provided samples was not found in the dataset"


def add_variants_task(req) -> None:
    """Perform the actual task of adding variants to the database after receiving an add request
    Accepts:
        req(flask.request): POST request received by server
    """
    db = current_app.db
    req_data = req.json
    dataset_id = req_data.get("dataset_id")
    samples = req_data.get("samples", [])
    assembly = req_data.get("assemblyId")
    filter_intervals = None
    genes = req_data.get("genes")
    if genes:
        filter_intervals = compute_filter_intervals(req_data)

    vcf_obj = extract_variants(
        vcf_file=req_data.get("vcf_path"), samples=samples, filter=filter_intervals
    )
    nr_variants = count_variants(vcf_obj)
    vcf_obj = extract_variants(
        vcf_file=req_data.get("vcf_path"), samples=samples, filter=filter_intervals
    )
    added = variants_loader(
        database=db,
        vcf_obj=vcf_obj,
        samples=set(samples),
        assembly=assembly,
        dataset_id=dataset_id,
        nr_variants=nr_variants,
    )
    if added > 0:
        # Update dataset object accordingly
        update_dataset(database=db, dataset_id=dataset_id, samples=samples, add=True)
    LOG.info(f"Number of inserted variants for samples:{samples}:{added}")


def overlapping_samples(dataset_samples, request_samples) -> bool:
    """Check that samples provided by user are contained in either VCF of dataset object

    Accepts:
        dataset_samples(list): the list of samples contained in the dataset or the VCF
        request_samples(list): the list of samples provided by user

    Returns:
        bool: True if all samples in the request are contained in the dataset or the VCF
    """
    ds_sampleset = set(dataset_samples)
    sampleset = set(request_samples)
    # return False if not all samples in provided samples list are found in dataset
    return all(sample in ds_sampleset for sample in sampleset)


def delete_variants_task(req) -> None:
    """Perform the actual task of removing variants from the database after receiving an delete request
    Accepts:
        req(flask.request): POST request received by server
    """
    db = current_app.db
    req_data = req.json

    dataset_id = req_data.get("dataset_id")
    samples = req_data.get("samples")

    updated, removed = variant_deleter(db, dataset_id, samples)
    if updated + removed > 0:
        update_dataset(database=db, dataset_id=dataset_id, samples=samples, add=False)
        LOG.info(f"Number of updated variants:{updated}. Number of deleted variants:{removed}")


def create_allele_query(resp_obj, req) -> dict:
    """Populates a dictionary with the parameters provided in the request

    Accepts:
        resp_obj(dictionary): response data that will be returned by server
        req(flask.request): request received by server

    Returns:
        mongo_query(dict): database query to retrieve allele info

    """
    customer_query = {}
    mongo_query = {}
    error = None
    data = None

    if req.method == "GET":
        data = dict(req.args)
        customer_query["datasetIds"] = req.args.getlist("datasetIds")
    else:  # POST method
        if req.headers.get("Content-type") == "application/x-www-form-urlencoded":
            data = dict(req.form)
            customer_query["datasetIds"] = req.form.getlist("datasetIds")

        else:  # application/json, This is default with POST requests containing json data
            data = req.json
            customer_query["datasetIds"] = data.get("datasetIds", [])

        # Remove null parameters from the query
        remove_keys = []
        for key, value in data.items():
            if value == "":
                remove_keys.append(key)
        for key in remove_keys:
            data.pop(key)

    # loop over all available query params
    for param in QUERY_PARAMS_API_V1:
        if data.get(param):
            customer_query[param] = data[param]
    if "includeDatasetResponses" not in customer_query:
        customer_query["includeDatasetResponses"] = "NONE"

    # check if the minimum required params were provided in query
    error = check_allele_request(resp_obj, customer_query, mongo_query)

    return customer_query, mongo_query, error


def check_allele_request(resp_obj, customer_query, mongo_query) -> None:
    """Check that the query to the server is valid

    Accepts:
        resp_obj(dict): response data that will be returned by server
        customer_query(dict): a dictionary with all the key/values provided in the external request
        mongo_query(dict): the query to collect variants from this server
    """
    chrom = customer_query.get("referenceName")
    start = customer_query.get("start")
    end = customer_query.get("end")
    ref = customer_query.get("referenceBases")
    alt = customer_query.get("alternateBases")
    build = customer_query.get("assemblyId")
    datasets = customer_query.get("datasetIds", [])
    variant_type = customer_query.get("variantType")

    error = None

    # If customer wants to match a SNV with precise coordinates, alt and ref
    if (
        customer_query.get("variantType") is None
        and all([chrom, start, end, ref, alt, build])
        and not "N" in ref
        and not "N" in alt
    ):
        # generate md5_key to quickly compare with our database
        mongo_query["_id"] = md5_key(
            chrom,
            start,
            end,
            ref,
            alt,
            build,
        )
        return

    # Check that the 3 mandatory parameters are present in the query
    if None in [
        chrom,
        ref,
        build,
    ]:
        # return a bad request 400 error with explanation message
        return NO_MANDATORY_PARAMS

    if len(datasets) > 0:
        # Check that requested datasets are contained in this beacon
        dsets = list(current_app.db["dataset"].find({"_id": {"$in": datasets}}))
        if len(dsets) == 0:  # requested dataset is not present in database
            return UNKNOWN_DATASETS

        if build not in [dset["assembly_id"] for dset in dsets]:
            # Requested genome build doesn't correspond to genome build of available datasets
            return BUILD_MISMATCH

    # alternateBases OR variantType is also required
    if all(
        param is None
        for param in [
            alt,
            variant_type,
        ]
    ):
        # return a bad request 400 error with explanation message
        return NO_SECONDARY_PARAMS

    # Check that genomic coordinates are provided (even rough)
    if (
        start is None
        and any([coord in customer_query.keys() for coord in RANGE_COORDINATES]) is False
    ):
        # return a bad request 400 error with explanation message
        return NO_POSITION_PARAMS

    if start:  # query for exact position
        try:
            if end is not None:
                mongo_query["end"] = int(end)
            mongo_query["start"] = int(start)

        except ValueError:
            # return a bad request 400 error with explanation message
            return INVALID_COORDINATES

    # Range query
    elif any([coord in customer_query.keys() for coord in RANGE_COORDINATES]):  # range query
        # In general startMin <= startMax <= endMin <= endMax, but allow fuzzy ends query

        fuzzy_start_query = {}
        fuzzy_end_query = {}
        try:
            if "startMin" in customer_query:
                fuzzy_start_query["$gte"] = int(customer_query["startMin"])
            if "startMax" in customer_query:
                fuzzy_start_query["$lte"] = int(customer_query["startMax"])
            if "endMin" in customer_query:
                fuzzy_end_query["$gte"] = int(customer_query["endMin"])
            if "endMax" in customer_query:
                fuzzy_end_query["$lte"] = int(customer_query["endMax"])
        except ValueError:
            # return a bad request 400 error with explanation message
            return INVALID_COORDINATES

        if fuzzy_start_query:
            mongo_query["start"] = fuzzy_start_query
        if fuzzy_end_query:
            mongo_query["end"] = fuzzy_end_query

    mongo_query["assemblyId"] = build
    mongo_query["referenceName"] = chrom

    add_coords_query(mongo_query, "referenceBases", ref)

    if "alternateBases" in customer_query:
        add_coords_query(mongo_query, "alternateBases", alt)

    if "variantType" in customer_query:
        mongo_query["variantType"] = variant_type


def add_coords_query(mongo_query, field, value) -> None:
    """Created a regex for a database query when ref or alt coords contain Ns

    Accepts:
        mongo_query(dict): an allele query dictionary
        field(string): "referenceBases" or "alternateBases"
        value(string): A stretch of bases, might containg Ns
    """

    if "N" in value:
        mongo_query[field] = {"$regex": value.replace("N", ".")}
    else:
        mongo_query[field] = value


def dispatch_query(mongo_query, response_type, datasets=[], auth_levels=([], False)) -> tuple:
    """Query variant collection using a query dictionary

    Accepts:
        mongo_query(dic): a query dictionary
        response_type(str): individual dataset responses -->
            ALL means all datasets even those that don't have the queried variant
            HIT means only datasets that have the queried variant
            MISS means opposite to HIT value, only datasets that don't have the queried variant
            NONE don't return datasets response.
        datasets(list): dataset ids from request "datasetIds" field
        auth_levels(tuple): (registered access datasets(list), bona_fide_status(bool))

    Returns:
        tuple(bool, list): (allele_exists(bool), datasetAlleleResponses(list))

    """
    variant_collection = current_app.db["variant"]

    LOG.info(f"Perform database query -----------> {mongo_query}.")
    LOG.info(f"Response level (datasetAlleleResponses) -----> {response_type}.")

    # End users are only interested in knowing which datasets have one or more specific vars, return only datasets and callCount
    variants = list(
        variant_collection.find(mongo_query, {"_id": 0, "datasetIds": 1, "call_count": 1})
    )

    # Filter variants by auth level specified by user token (or lack of it)
    variants = results_filter_by_auth(variants, auth_levels)

    if response_type == "NONE":
        if len(variants) > 0:
            return True, []

    else:
        # request datasets:
        req_dsets = set(datasets)

        # IDs of datasets found for this variant(s)
        result = create_ds_allele_response(response_type, req_dsets, variants)
        return result

    return False, []


def results_filter_by_auth(variants, auth_levels) -> list:
    """Filter variants returned by query using auth levels (specified by token, if present, otherwise public access only datasets)

    Accepts:
        variants(list): a list of variants returned by database query
        auth_levels(tuple): (registered access datasets(list), bona_fide_status(bool))

    Return:
        filtered_variants(list): Variants filtered using authlevel criteria
    """

    # Filter variants by auth level (specified by token, if present, otherwise public access only datasets)
    ds_collection = current_app.db["dataset"]
    public_ds = ds_collection.find({"authlevel": "public"})
    pyblic_ds_ids = [ds["_id"] for ds in public_ds]

    LOG.info(f"The following public dataset were found in database:{public_ds}")

    registered_access_ds_ids = auth_levels[0]
    controlled_access_ds_ids = []

    if auth_levels[1] is True:  # user has access to controlled access datasets
        controlled_access_ds = ds_collection.find({"authlevel": "controlled"})
        controlled_access_ds_ids = [ds["_id"] for ds in controlled_access_ds]

    dataset_filter = pyblic_ds_ids + registered_access_ds_ids + controlled_access_ds_ids

    # Filter results
    LOG.info(f"Filtering out results with datasets different from :{dataset_filter}")
    filtered_variants = []

    for variant in variants:
        for key in variant.get("datasetIds", []):
            if key in dataset_filter:
                filtered_variants.append(variant)

    return filtered_variants


def create_ds_allele_response(response_type, req_dsets, variants) -> tuple:
    """Create a Beacon Dataset Allele Response

    Accepts:
        response_type(str): ALL, HIT or MISS
        req_dsets(set): datasets requested, could be empty
        variants(list): a list of query results

    Returns:
        ds_responses(list): list of cgbeacon2.model.DatasetAlleleResponse
    """
    ds_responses = []
    exists = False

    all_dsets = current_app.db["dataset"].find()
    all_dsets = {ds["_id"]: ds for ds in all_dsets}

    if len(req_dsets) == 0:  # if query didn't specify any dataset
        # Use all datasets present in this beacon
        req_dsets = set(all_dsets)

    for ds in req_dsets:
        # check if database contains a dataset with provided ID:
        if ds not in all_dsets:
            LOG.info(f"Provided dataset {ds} could not be found in database")
            continue

        ds_response = DatasetAlleleResponse(all_dsets[ds], variants).__dict__

        # collect responses according to the type of response requested
        if (
            response_type == "ALL"
            or (response_type == "HIT" and ds_response["exists"] is True)
            or (response_type == "MISS" and ds_response["exists"] is False)
        ):
            ds_responses.append(ds_response)

        if ds_response["exists"] is True:
            exists = True

    return exists, ds_responses
