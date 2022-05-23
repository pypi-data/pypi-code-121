# -*- coding: utf-8 -*-
import json
import logging
import os
import re
from tempfile import NamedTemporaryFile
from typing import Union

from cgbeacon2.resources import variants_add_schema_path
from cyvcf2 import VCF
from flask import current_app
from jsonschema import ValidationError, validate
from pybedtools.bedtool import BedTool

BND_ALT_PATTERN = re.compile(r".*[\],\[](.*?):(.*?)[\],\[]")
CHR_PATTERN = re.compile(r"(chr)?(.*)", re.IGNORECASE)

LOG = logging.getLogger(__name__)


def validate_add_params(req) -> Union[None, dict]:
    """Validated the parameters in the request sent to add new variants into the database

    Accepts:
        req(flask.request): POST request received by server

    Returns:
        validate_request: True if validated, a dictionary with specific error message if not validated
    """
    # Check if params provided in request are valid using a json schema
    schema = None
    with open(variants_add_schema_path) as jsonfile:
        schema = json.load(jsonfile)
        try:
            validate(req.json, schema)
        except ValidationError as ve:
            return ve.message
    return True


def get_vcf_samples(vcf_file) -> list:
    """Returns a list of samples contained in the VCF

    Accepts:
        vcf_file(str): path to VCF file

    Returns:
        vcf_samples(list)
    """
    vcf_samples = []
    try:
        vcf_obj = VCF(vcf_file)
        vcf_samples = vcf_obj.samples

    except Exception as err:
        LOG.error(f"Error while creating VCF iterator from variant file:{err}")

    return vcf_samples


def bnd_mate_name(alt, chrom) -> str:
    """Returns chromosome and mate for a BND variant

    Accepts:
        alt(str): vcf_variant.ALT[0]
        chrom(st): cf_variant.CHROM

    Returns:
        end_chr(str): a chromosome (1-22, X, Y, MT)
    """
    end_chrom = chrom
    if ":" not in alt:
        return end_chrom

    match = BND_ALT_PATTERN.match(alt)

    # BND will often be translocations between different chromosomes
    if match:
        other_chrom = match.group(1)
        match = CHR_PATTERN.match(other_chrom)
        end_chrom = match.group(2)
    return end_chrom


def sv_end(pos, alt, svend=None, svlen=None) -> int:
    """Return the end coordinate for a structural variant

    Accepts:
        pos(int): variant start, 1-based
        alt(str)
        svend(int)
        svlen(int)

    Returns:
        end(int)

    """
    end = svend

    if ":" in alt:
        match = BND_ALT_PATTERN.match(alt)
        if match:
            end = int(match.group(2))

    if svend == pos:
        if svlen:
            end = pos + svlen

    return end - 1  # coordinate should be zero-based


def compute_filter_intervals(req_data) -> Union[None, BedTool]:
    """Compute filter intervals from a list of genes

    Accepts:
        req_data(dict): a dictionary with add request data
        db()

    Returns:
        filter_intervals(list) a lits of genomic intervals to filter VCF with
    """
    db = current_app.db
    hgnc_ids = None
    ensembl_ids = None
    assembly = req_data.get("assemblyId")
    if req_data["genes"]["id_type"] == "HGNC":
        hgnc_ids = req_data["genes"]["ids"]
    else:
        ensembl_ids = req_data["genes"]["ids"]
    filter_intervals = genes_to_bedtool(db["gene"], hgnc_ids, ensembl_ids, assembly)
    return filter_intervals


def genes_to_bedtool(
    gene_collection, hgnc_ids=None, ensembl_ids=None, build="GRCh37"
) -> Union[None, BedTool]:
    """Create a Bedtool object with gene coordinates from a list of genes contained in the database

    Accepts:
        hgnc_ids(list): a list of hgnc genes ids
        ensembl_ids(list): a list of ensembl gene ids
        gene_collection(pymongo.collection.Collection)
        build(str): genome build, GRCh37 or GRCh38

    Returns:
        bt(pybedtools.bedtool.BedTool): a BedTool object containing gene intervals
    """
    if not (hgnc_ids or ensembl_ids):
        return None  # No gene was specified to filter VCF file with

    query = {"build": build}
    if hgnc_ids:
        query["hgnc_id"] = {"$in": hgnc_ids}
    elif ensembl_ids:  # either HGNC or ENSEMBL IDs, not both in the query dictionary
        query["ensembl_id"] = {"$in": ensembl_ids}
    # Query database for genes coordinates
    results = gene_collection.find(query)
    # Create a string containing gene intervals to initialize a Bedtool object with
    bedtool_string = ""
    for gene in results:
        bedtool_string += (
            "\t".join([gene["chromosome"], str(gene["start"]), str(gene["end"])]) + "\n"
        )
    if bedtool_string == "":
        return None
    bt = BedTool(bedtool_string, from_string=True)
    return bt


def extract_variants(vcf_file, samples=None, filter=None) -> Union[None, VCF]:
    """Parse a VCF file and return its variants as cyvcf2.VCF objects

    Accepts:
        vcf_file(str): path to VCF file
        samples(set): samples to extract variants for
        filter(BcfTool object)
    """
    vcf_obj = None
    try:
        if filter is not None:
            # filter VCF using one or more panels
            intersections = _compute_intersections(vcf_file, filter)
            temp_intersections_file = NamedTemporaryFile("w+t", dir=os.getcwd())
            intersections.saveas(temp_intersections_file.name)

            vcf_obj = VCF(temp_intersections_file.name, samples=list(samples))

            # remove temporary file:
            temp_intersections_file.close()
        else:
            vcf_obj = VCF(vcf_file, samples=list(samples))

    except Exception as err:
        LOG.error(f"Error while creating VCF iterator from variant file:{err}")

    return vcf_obj


def _compute_intersections(vcf_file, filter) -> BedTool:
    """Create a temporary file with the gene panel intervals

    Accepts:
        vcf_file(str): path to the VCF file
        filter(BcfTool object)

    Returns:
        intersections(BedTool)
    """

    vcf_bed = BedTool(vcf_file)
    LOG.info(
        "Extracting %s intervals from the %s total entries of the VCF file.",
        filter.count(),
        vcf_bed.count(),
    )
    intersections = vcf_bed.intersect(filter, header=True)
    intersected_vars = intersections.count()
    LOG.info("Number of variants found in the intervals:%s", intersected_vars)

    return intersections


def count_variants(vcf_obj) -> int:
    """Count how many variants are contained in a VCF object

    Accepts:
        vcf_obj(cyvcf2.VCF): a VCF object

    Returns:
        nr_variants(int): number of variants
    """
    nr_variants = 0
    for vcf_variant in vcf_obj:
        nr_variants += 1

    return nr_variants


def merge_intervals(panels) -> BedTool:
    """Create genomic intervals to filter VCF files starting from the provided panel file(s)

    Accepts:
        panels(list) : path to one or more panel bed files

    Returns:
        merged_panels(Temp BED File): a temporary file with merged panel intervals

    """
    merged_panels = BedTool(panels[0])
    if len(panels) > 1:
        merged_panels = merged_panels.cat(*panels[1:])

    return merged_panels


def variant_called(vcf_samples, gt_positions, g_types) -> dict:
    """Return a list of samples where variant was called

    Accepts:
        vcf_samples(list): list of samples contained in VCF, ordered
        gt_positions(list): list of positions to check GT for, i.e [0,2]: (check first and third sample)
        g_types(list): list of GTypes, one for each sample, ordered.

    Returns:
        samples_with_call(dict): a dictionary of samples having the specific variant call with the allele count.
            Example: {sample1:1, sample2:2}
    """

    samples_with_call = {}
    allele_count = 0

    for i, g_type in enumerate(g_types):
        if i not in gt_positions:  # this sampple should not be considered, skip
            continue

        if g_type in [1, 3]:
            # gt_types is array of 0,1,2,3==HOM_REF, HET, UNKNOWN, HOM_ALT
            # Collect only samples with HET or HOM_ALT calls
            if g_type == 1:
                allele_count = 1  # HET
            else:
                allele_count = 2  # HOM_ALT

            samples_with_call[vcf_samples[i]] = {"allele_count": allele_count}

    return samples_with_call
