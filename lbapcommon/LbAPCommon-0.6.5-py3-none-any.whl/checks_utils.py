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
"""Contains utility functions used to display and save the output of the checks.
"""
import copy
import json

import uproot


def hist_to_root(job_name, check_results, output_path):
    """Save histograms in a root file.

    Args:
        job_name (str): The job name. Unused.
        check_results (dict): Dictionary of check results
        output_path: Output directory for root file.
    """
    # Create the file only if the check produce histograms in output
    checks_with_histo = ["range", "range_nd", "range_bkg_subtracted"]
    with uproot.recreate(output_path) as file_root:
        for cr in check_results:
            if (
                check_results[cr].passed
                and check_results[cr].check_type in checks_with_histo
            ):
                for key, data in check_results[cr].tree_data.items():
                    for hist_counter, _histo in enumerate(data.get("histograms", [])):
                        histo_name = f"{key}/{cr}_{hist_counter}"
                        file_root[histo_name] = _histo


def serialise_hist(obj):
    """Serialise a Hist histogram object into a python dictionary representation.

    Args:
        obj: The histogram object to be serialised.

    Returns:
        dict: Representation of histogram (version 1)
    """
    serialised_obj = {
        "version": 1,
        "name": str(obj.name),
        "axes": [
            {
                "name": str(axis.name),
                "nbins": int(len(axis)),
                "min": float(axis.edges[0]),
                "max": float(axis.edges[-1]),
            }
            for axis in obj.axes
        ],
        "contents": list(obj.values(flow=True).tolist()),
        "sumw2": list(obj.variances(flow=True).tolist()),
    }
    return serialised_obj


def checks_to_JSON(
    checks_data,
    all_check_results,
    json_output_path=None,
):
    """Serialise information about all checks into a JSON format.

    Args:
        checks_data (dict): Checks data dictionary.
        all_check_results (dict): CheckResults.
        json_output_path (str, optional): Path to save JSON file if desired. Defaults to None.

    Returns:
        str: JSON string representation of checks output.
    """
    all_check_results_copy = copy.deepcopy(all_check_results)

    result = {}
    for job in all_check_results_copy:
        result[job] = {}
        for check in all_check_results_copy[job]:
            result[job][check] = {}

            result[job][check]["passed"] = all_check_results_copy[job][check].passed
            result[job][check]["messages"] = all_check_results_copy[job][check].messages
            result[job][check]["input"] = checks_data[check]
            result[job][check]["output"] = all_check_results_copy[job][check].tree_data

            # Convert histograms to JSON representation
            for tree in result[job][check]["output"]:
                if "histograms" in result[job][check]["output"][tree]:
                    n_hists = len(result[job][check]["output"][tree]["histograms"])
                    for n in range(n_hists):
                        result[job][check]["output"][tree]["histograms"][
                            n
                        ] = serialise_hist(
                            result[job][check]["output"][tree]["histograms"][n]
                        )

    if json_output_path is not None:
        with open(json_output_path, "w", encoding="utf8") as json_file:
            json.dump(result, json_file, indent="  ")

    return json.dumps(result, indent="  ")
