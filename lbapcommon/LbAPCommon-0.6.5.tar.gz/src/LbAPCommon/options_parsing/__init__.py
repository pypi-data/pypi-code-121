###############################################################################
# (c) Copyright 2021-2022 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import json

import uproot

from LbAPCommon.parsing import is_simulation_job


def validate_options(json_file: str, ntuple_fn: str, job_name: str, prod_data: dict):
    """Validate YAML options.

    Check existence of expected TTrees and ensure at least one
    DecayTree and MCDecayTree (for MC samples) exist(s) in output files.

    Args:
        json_file (str): json_file listing the expected TTrees
        ntuple_fn (str): Local test output tuple to validate against
        job_name (str): Name of job to validate
        prod_data (dict): Entire production information from yaml parsing

    Returns:
        tuple[list[str]]: Errors if any expected TTrees are not found in job output,
            warnings if at least one (MC)DecayTree isn't found in job output
    """
    with open(json_file, "rb") as fp:
        json_dump = json.load(fp)

    file = uproot.open(ntuple_fn)
    tuple_keys = file.keys(cycle=False)

    errors = []
    warnings = []

    mc_decay_tree = any({"MCDecayTree" in key for key in tuple_keys})
    decay_tree = any(
        {("DecayTree" in key and "MCDecayTree" not in key) for key in tuple_keys}
    )

    if not decay_tree:
        warnings.append(
            "No DecayTree detected in the output file! Is this intentional?"
        )

    # It's not possible to statically check if using transform_ids as input
    if "transform_ids" not in prod_data[job_name]["input"]:
        if is_simulation_job(prod_data, job_name) and not mc_decay_tree:
            warnings.append(
                "No MCDecayTree detected in the output file! Is this intentional?"
            )

    # Checking DecayTreeTuples
    for ntuple in json_dump["DecayTreeTuple"]:
        if ntuple not in tuple_keys:
            errors.append(f"ERROR: DecayTreeTuple {ntuple} missing in test result")

    # Checking MCDecayTreeTuples
    for ntuple in json_dump["MCDecayTreeTuple"]:
        if ntuple not in tuple_keys:
            errors.append(f"ERROR: MCDecayTreeTuple {ntuple} missing in test result")

    # Checking MCDecayTreeTuples
    for ntuple in json_dump["EventTuple"]:
        if ntuple not in tuple_keys:
            errors.append(f"ERROR: EventTuple {ntuple} missing in test result")

    return errors, warnings
