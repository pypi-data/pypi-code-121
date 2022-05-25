"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

from typing import Dict

from blackduck_c_cpp.katiska.bdio.bdio_entries import (
    BDIOBuilder,
)

from blackduck_c_cpp.katiska.custom_types import JsonDict

from typing import List
import json
import os

'''
Python wrapper to convert json to bdio2 format 
@author Mayur kadu
@date March 11 2021
'''


class BDIO2Transformer:
    BDIO2_OUT_FILENAME = "c_cpp_bdio2.jsonld"
    PUBLISHER = "c-cpp-bdio2"
    PUBLISHER_VERSION = "1.0.0"
    BDIO2_FILENAME_SUFFIX = "-BDIO2"

    def __init__(self, cov_output, hub_api):
        self.cov_output = cov_output
        self.out_biod2_filepath_name = os.path.join(self.cov_output, self.BDIO2_OUT_FILENAME)
        self.hub_api = hub_api
        self.vers_result = self.hub_api.hub.version_info['version'].split(".")


    def write_bdio2_document(self, result):
        '''
        Write the bdio2 file to cov_output path
        @return : path with filename of bdio2 file generated
        '''
        with open(self.out_biod2_filepath_name, "w") as outfile:
            json.dump(result, outfile, indent=2)

        return self.out_biod2_filepath_name

    def generate_bdio2(self, code_loc_name,
                       project_name,
                       project_version,
                       cov_results: List[JsonDict],
                       scanned_path,
                       scan_size=0
                       ):
        '''
        code_loc_name : Code location name
        project_name  : Project Name
        project_version : project version
        cov_result : List[JsonDict] components identified
        scanned_path : coverity output path of project
        scan_size : size of scan

        @return : string representation of jsonld bdio2
        '''

        code_location_name = code_loc_name + self.BDIO2_FILENAME_SUFFIX
        if self.vers_result[0] == 2021 and self.vers_result[1] == 8:
            self.PUBLISHER = "Protecode-SC"
            self.PUBLISHER_VERSION = "1.0.0"
        bdio_builder = BDIOBuilder()
        bdio_builder.bdio_file(self.PUBLISHER, self.PUBLISHER_VERSION, code_location_name, None, True)

        fileentry_project_base = bdio_builder.fileentry_project_base(scanned_path, scan_size)
        bdio_builder.project(project_name, project_version, fileentry_project_base)
        dir_comp_dict = dict()  # key: direct dependency compoenent ,value:(comp value, set of fullpath)

        for entry in cov_results[0]["extended-objects"]:
            # all entrys are direct deps
            comp = entry["distro"] + entry["package-name"] + entry["package-version"] + entry["package-architecture"]

            if comp in dir_comp_dict and entry['fullpath'][1] in dir_comp_dict[comp][1]:
                continue

            if comp in dir_comp_dict:  # use existing direct dependency component
                direct_dep_component = dir_comp_dict[comp][0]
                dir_comp_dict[comp][1].add(entry['fullpath'][1])  # append path
            else:  # else create new one if it was never seen before
                direct_dep_component = bdio_builder.component(
                    entry["distro"],
                    entry["package-name"],
                    entry["package-version"],
                    entry["package-architecture"],
                    allow_duplicates=True,
                )
                dir_comp_dict[comp] = (direct_dep_component, {entry['fullpath'][1]})

            direct_dep_file = bdio_builder.fileentry_from_fullpath(
                entry["fullpath"],
                entry["timestamp"],
                entry["sha1"],
                entry["size"],
                bdio_builder.matching_info(entry),
            )
            bdio_builder.dependency_direct_with_evidence_file(
                direct_dep_component, direct_dep_file, match_type=entry["matchType"]
            )

            # add all transitive components
            transitive_entry: Dict = {}  # needed for type checker to stop complaining
            for transitive_entry in entry.get("trans-dep", []):
                transitive_dep_component = bdio_builder.component(
                    transitive_entry["distro"],
                    transitive_entry["package-name"],
                    transitive_entry["package-version"],
                    transitive_entry["package-architecture"],
                    allow_duplicates=True,
                )
                transitive_dep_file = bdio_builder.fileentry_from_fullpath(
                    transitive_entry["fullpath"],
                    transitive_entry["timestamp"],
                    transitive_entry["sha1"],
                    transitive_entry["size"],
                    bdio_builder.matching_info(transitive_entry),
                )
                bdio_builder.dependency_transitive_with_evidence_file(
                    direct_dep_component,
                    transitive_dep_component,
                    transitive_dep_file,
                    match_type_file=transitive_entry["matchType"],
                )
        bdio = bdio_builder.get_result()

        return bdio, code_location_name
