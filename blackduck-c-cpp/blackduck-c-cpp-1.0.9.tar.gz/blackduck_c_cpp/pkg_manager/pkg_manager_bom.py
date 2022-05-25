"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import os
import tqdm
import tarfile
import logging
import pandas as pd
import re
import shutil
import csv
import json
import ast
from blackduck_c_cpp.util.build_log_parser import LogParser
from blackduck_c_cpp.pkg_manager.ld_debug_parse import LdDebugParser
from collections import defaultdict
import hashlib
import sys
import itertools
import subprocess
from blackduck_c_cpp.util import global_settings
from blackduck_c_cpp.util import util
from datetime import datetime

PKG_MGR_MODE = 'pkg_mgr'
BDBA_MODE = 'bdba'
ALL_MODE = 'all'


class PkgManagerBom:
    """
    Runs package manager on all linker,header,executable and transitive dependency files
    and creates a tar file to send to bdba
    """

    def __init__(self, pkg_manager, build_log, cov_home, blackduck_output_dir, os_dist, bld_dir, unresolved_files_list,
                 resolved_files_list, binary_files_list, json_grep_files_list, skip_build, skip_transitives,
                 skip_dynamic, run_modes,
                 cov_header_files, debug, header_files_set, linker_files_set, executable_files_set,
                 resolved_cov_files_list, unresolved_cov_files_list,
                 hub_api, offline, use_offline_files):
        self.pkg_manager = pkg_manager
        self.build_log = build_log
        self.skip_build = skip_build
        self.skip_transitives = skip_transitives
        self.skip_dynamic = skip_dynamic
        self.output_dir = blackduck_output_dir
        self.cov_home = cov_home
        self.header_list = cov_header_files
        self.bld_dir = bld_dir
        self.os_dist = os_dist
        self.resolved_files_path = resolved_files_list
        self.unresolved_files_path = unresolved_files_list
        self.run_modes = run_modes

        self.resolved_cov_files_path = resolved_cov_files_list
        self.unresolved_cov_files_path = unresolved_cov_files_list

        self.binary_files_path = binary_files_list
        self.json_grep_files_list = json_grep_files_list
        self.debug = debug
        self.cov_header_files_set = header_files_set
        self.cov_linker_files_set = linker_files_set
        self.cov_executable_files_set = executable_files_set
        self.hub_api = hub_api
        self.offline = offline
        self.use_offline_files = use_offline_files

        self.csv_file_path = os.path.join(self.output_dir, "raw_bdio.csv")
        self.json_file_path = os.path.join(self.output_dir, "raw_bdio.json")
        self.executable_list = None
        self.linker_list = None
        self.lib_path_set = None
        self.build_dir_dict = None
        self.components_data = None
        self.final_components_dict = None
        self.file_dict = dict()
        self.resolved_file_dict = dict()
        self.unresolved_file_dict = dict()
        self.cov_file_dict = dict()
        self.resolved_cov_file_dict = dict()
        self.unresolved_cov_file_dict = dict()
        self.pkg_mgr_data = dict()
        self.bdba_data = dict()
        self.ldd_linker = dict()
        self.lddebug_executable = dict()
        self.unrecognized_pkg_manager = True
        self.direct_match_evidence = 'Binary'
        self.transitive_match_evidence = 'Binary'
        self.unresol_set = set()

    def run_log_parser(self):
        """
        This function calls LogParser.parse_build_log method to get all paths from linker invocations,
        all output executables and -L paths from build_log.txt for path resolution

        """
        start_parser = datetime.now()
        log_parser = LogParser()
        self.linker_list = log_parser.parse_build_log(self.build_log, self.os_dist)
        self.lib_path_set = log_parser.lib_path
        self.executable_list = log_parser.get_exectuable(self.build_log)
        end_parser = datetime.now()
        logging.info("time taken to parse for files from build-log.txt : {}".format(end_parser - start_parser))

    def get_files(self, list_paths):
        """
        Function to create a dictionary with input list of paths in sorted order with length
        {a.so: [g/b/c/a.so,c/a.so],...}
        param: list of paths
        return: dictionary containing key as basefile and value as list of all paths with basefile
        """
        basefile_list = list(map(lambda path: os.path.basename(path).strip(), list_paths))
        basefiles_dict = dict.fromkeys(basefile_list, None)
        for basefile in basefiles_dict.keys():
            basefiles_dict[basefile] = sorted(
                set(map(lambda path_1: path_1.strip(),
                        filter(lambda path: os.path.basename(path).endswith(basefile), list_paths))),
                key=len,
                reverse=True)
        return basefiles_dict

    def generate_build_dir_files(self):
        """ This function gets all files in build dir
        return: dictionary containing key as basefile and value as list of all paths with basefile in build directory
        """
        start_gen = datetime.now()
        basefiles_dict = dict()
        dirs_set = set()
        count = 0
        for (root, dirs, files) in os.walk(self.bld_dir, followlinks=True):
            logging.debug("root is {}".format(root))
            st = os.stat(root)
            walk_dirs = []
            for dirname in dirs:
                st = os.stat(os.path.join(root, dirname))
                dir_key = st.st_dev, st.st_ino
                if dir_key not in dirs_set:
                    dirs_set.add(dir_key)
                    walk_dirs.append(dirname)
            for file in files:
                if file in self.unresol_set:
                    if file in basefiles_dict:
                        basefiles_dict[file] = basefiles_dict[file] + [os.path.join(root, file)]
                    else:
                        basefiles_dict[file] = [os.path.join(root, file)]
                    count += 1
                    if (count % 1000 == 0):
                        logging.debug("files resolved so far {}".format(len(basefiles_dict.keys())))
            dirs[:] = walk_dirs
        end_gen = datetime.now()
        logging.debug("total list of files found are : {}".format(len(basefiles_dict.keys())))
        logging.debug("time taken to get all files in build dir : {}".format(end_gen - start_gen))
        return basefiles_dict

    def test_for_dash_l_file_completion(self, path_list):
        """ This function will attempt to resolve paths to files based on paths found
        as -L flags in the build-log
        param: list of paths
        return: set of resolved paths with length used for sort in descending order
        """
        resolved_paths = set()
        for path in path_list:
            if os.path.exists(path):
                resolved_paths.add(path)
            else:
                for lib_path in self.lib_path_set:
                    test_path = os.path.abspath(util.resolve_path(os.path.join(lib_path, path)))
                    if os.path.exists(test_path):
                        resolved_paths.add(test_path)
                        break
        return sorted(resolved_paths, key=len, reverse=True)

    def resolve_file_paths(self, basefiles_dict):
        """ This function separates all files to resolved and unresolved files
        param: dictionary containing key as basefile and value as list of all paths with basefile
        return: resolved and unresolved dictionaries with key as basefile and value as list of all paths with basefile
        """
        resolved_files_dict = dict()
        unresolved_files_dict = dict()
        for basefile, paths_list in basefiles_dict.items():
            resolved_paths = self.test_for_dash_l_file_completion(paths_list)
            if len(resolved_paths) > 0:
                resolved_files_dict[basefile] = set(resolved_paths)
            else:
                try:
                    """looks in build directory files"""
                    if basefile in self.build_dir_dict:
                        resolved_files_dict[basefile] = set(self.build_dir_dict[basefile])
                    else:
                        """ add to unresolved dictionary only if not even a single path in paths_list is resolved"""
                        unresolved_files_dict[basefile] = set(paths_list)
                except IndexError:
                    continue
        return resolved_files_dict, unresolved_files_dict

    def write_to_txt(self, input_dict, path):
        """This function is used to write resolved files, unresolved files and all files to text files
        param: dictionary to write to a file
        """
        try:
            with open(path, "w") as file_wr:
                file_wr.write("{\n")
                for type in input_dict.keys():
                    file_wr.write("'For {}:'\n".format(type))
                    for basefile in input_dict[type].keys():
                        file_wr.write("'{}':'{}'\n".format(basefile, input_dict[type][basefile]))
                        file_wr.write("\n")
                file_wr.write("}")
        except OSError:
            logging.error("Couldn't write file: {}".format(path))

    def join_components(self, sha1, confidence, pkg_result, matchType):
        """ This function joins sha1,confidence and package manager result with matchType to return a single string
        param:
            sha1: string
            confidence: string
            pkg_result: string
            matchType: string
        return: string
        """
        matchType = "matchType:{}".format(matchType)
        pkg_result = " ".join([pkg_result, sha1])
        pkg_result = " ".join([pkg_result, confidence])
        pkg_result = " ".join([pkg_result, matchType])
        return pkg_result

    def check_pkg_mgr(self, basefiles_dict):
        """ This function sends files to package manager and if no result adds those files to bdba
        param: dictionary containing key as basefile and value as list of all paths with basefile
        return: package manager dicitonary with key as filepath and value as result of package manager
                bdba dicitonary with key as basefile and value as list of all paths with basefile
        """
        if self.pkg_manager == 'rpm' or self.pkg_manager == 'dpkg':
            self.unrecognized_pkg_manager = False
        pkg_dict = {}
        bdba_dict = {}
        MatchType = self.direct_match_evidence
        pattern_file = re.compile('(?<=file:)([^ ])*')
        for basefile, paths_list in basefiles_dict.items():
            sha1, confidence, pkg_result, result = self.run_pkg_query(paths_list)
            if result:
                pkg_result = self.join_components(sha1, confidence, pkg_result, MatchType)
                file_path = re.search(pattern_file, pkg_result).group()
                pkg_dict[file_path] = pkg_result
                if self.debug or self.unrecognized_pkg_manager:
                    bdba_dict[basefile] = paths_list
            else:
                bdba_dict[basefile] = paths_list
        return pkg_dict, bdba_dict

    def run_pkg_query(self, paths_list):
        """ This function calls respective package manager function
        param: list of paths
        return: returns package manager result if exists otherwise returns "error"
            sha1: string
            confidence: string
            pkg_result: string
            result: Boolean
        """
        result = False
        sha1, confidence, pkg_result = "error", "error", "error"
        for path in paths_list:
            symlink_command = "readlink -f " + "{}".format(path)
            out = subprocess.getstatusoutput(symlink_command)
            status, symlink_path = util.value_getstatusoutput(out)
            if status and ("no path found matching pattern" not in symlink_path):
                sha1, confidence, pkg_result = getattr(self, self.call_func("command"))([path, symlink_path])
            else:
                sha1, confidence, pkg_result = getattr(self, self.call_func("command"))([path])
            if ("\n" not in pkg_result) and ("error" not in pkg_result):
                result = True
                break;
        return sha1, confidence, pkg_result, result

    def run_dpkg_command(self, paths_list):
        """ This function runs dpkg package manager command
        param: list of paths
        return: sha1,confidence and package result - all params in string format
        """
        sha1, confidence, dpkg_result = "error", "error", "error"
        for path in paths_list:
            dpkg_command = "dpkg-query --showformat='file:" + "{}".format(
                path) + " src:${Source}  pkg:${Package} version:${Version} package-architecture:${Architecture} timestamp:${db-fsys:Last-Modified} size:${Installed-Size}\n' --show `dpkg -S " + "{}".format(
                path) + "| awk -F: '{print $1}'`"
            out = subprocess.getstatusoutput(dpkg_command)
            status, dpkg_result_1 = util.value_getstatusoutput(out)
            if status and ("dpkg: error:" not in dpkg_result_1) and (
                    "no path found matching pattern" not in dpkg_result_1):
                confidence = "confidence:100"
                sha1 = self.find_sha1sum(path)
                dpkg_result = dpkg_result_1
                break;
        return sha1, confidence, dpkg_result

    def run_rpm_command(self, paths_list):
        """ This function runs rpm package manager command
        param: list of paths
        return: sha1,confidence and package result - all params in string format
        """
        sha1, confidence, rpm_result = "error", "error", "error"
        for path in paths_list:
            rpm_command = "rpm -q --queryformat " + "'file:{} ".format(path) + \
                          "src:%{SOURCERPM} pkg:%{Name} version:%{Version} package-architecture:/%{ARCH} timestamp:%{FILEMTIMES} size:%{FILESIZES} epoch:%{EPOCH}: release:-%{RELEASE}\n' --whatprovides " \
                          + "{}".format(path)
            out = subprocess.getstatusoutput(rpm_command)
            status, rpm_result_1 = util.value_getstatusoutput(out)
            if status and ("no path found matching pattern" not in rpm_result_1):
                confidence = "confidence:100"
                sha1 = self.find_sha1sum(path)
                rpm_result = rpm_result_1
                break;
        return sha1, confidence, rpm_result

    def run_brew_command(self, paths_list):
        """ This function runs brew package manager command
        param: list of paths
        return: sha1,confidence and package result - all params in string format
        """
        sha1, confidence, brew_result = "error", "error", "error"
        match_type = self.direct_match_evidence
        match_type = "matchType:{}".format(match_type)
        for path in paths_list:
            path_split = path.split('/')
            idx = 0
            for element in path_split:
                idx += 1
                if element == 'Cellar':
                    try:
                        brew_result = "file:{} pkg:{} version:{}".format(path, path_split[idx].split("@")[0],
                                                                         path_split[idx + 1])
                        sha1 = self.find_sha1sum(path)
                        confidence = "confidence:100"
                        size = "size:0"
                        timestamp = "timestamp:111"
                        package_architecture = "package-architecture:none"
                        brew_result = " ".join([brew_result, timestamp])
                        brew_result = " ".join([brew_result, size])
                        brew_result = " ".join([brew_result, package_architecture])
                        brew_result = " ".join([brew_result, match_type])
                        break;
                    except IndexError:
                        break;
        return sha1, confidence, brew_result

    def run_windows_command(self, paths_list):
        """ This function runs for windows or when package manager and os_dist is not found
        """
        return "error", "error", "error"

    def run_not_found_command(self, paths_list):
        """when package manager or os_dist is not found
        """
        return "error", "error", "error"

    def check_ldd(self, basefiles_dict):
        """ This function calls ldd function of all .so files
        param: dictionary containing key as basefile and value as list of all paths with basefile
        return: dictionary with key as filepath and
        value as dictionary with key transitive dependency element and value package manager results for it
        """
        ldd_linker = dict()
        bdba_dict = dict()
        for filepath, pkg_result in basefiles_dict.items():
            if re.match(r".*\.so$|.*\.so\..+$", filepath):
                list_ldd = self.get_ldd_for_sharedlib(filepath)
                if len(list_ldd) > 0:
                    ldd_linker[filepath], bdba_dict = self.check_pkg_for_ldds(list_ldd, bdba_dict)
        return ldd_linker, bdba_dict

    def check_pkg_for_ldds(self, ldd_list, bdba_dict):
        """ This function calls package manager for ldds
        param: list of transitive dependencies for each .so file
        return: dictionary with key transitive dependency element and value as package manager result for it
        """
        match_type = self.transitive_match_evidence
        ldd_dict = dict()
        for ldd_ele in ldd_list:
            ldd_ele = ldd_ele.strip()
            sha1, confidence, pkg_result, result = self.run_pkg_query(
                [ldd_ele, os.path.basename(ldd_ele)])
            if result:
                pkg_result = self.join_components(sha1, confidence, pkg_result, match_type)
                ldd_dict[ldd_ele] = pkg_result
                if self.debug:
                    bdba_dict[os.path.basename(ldd_ele)] = set([ldd_ele])
            else:
                bdba_dict[os.path.basename(ldd_ele)] = set([ldd_ele])
        return ldd_dict, bdba_dict

    def get_ldd_for_sharedlib(self, so_filepath):
        """This function calls ldd parse function on .so files
        param: .so filepath - string
        return: list of distinct transitive dependencies
        """
        if not os.path.exists(so_filepath):
            return []
        output_path_set = self.ldd_output_parse(so_filepath)
        return list(output_path_set)

    def ldd_output_parse(self, full_path):
        """This function performs parsing on output of ldd command
        param: .so filepath - string
        return: list of distinct transitive dependencies
        """
        output_path_set = set()
        ldd_return = subprocess.getoutput('ldd {}'.format(full_path))
        parsed_results = re.findall(r'^\s*(\S+)\s+=>(.*) \(.*\)$', ldd_return, re.MULTILINE)
        for fname, path in parsed_results:
            output_path_set.add(path)
        return output_path_set

    def find_sha1sum(self, path):
        """This function finds sha1 of a file
        param: filepath - string
        return: sha1 - string
        """
        sha1 = hashlib.sha1()
        try:
            with open(path, 'rb') as f:
                data = f.read()
                sha1.update(data)
                sha1_result = "sha1sum:{}".format(sha1.hexdigest())
        except Exception as e:
            # logging.debug("exception is {}".format(e))
            sha1_result = "sha1sum:notAvailable"
        return sha1_result

    def call_func(self, string):
        """To call specific package manager function
        param: part of function name - string
        return: full function name - string
        """
        return "run_" + self.pkg_manager + '_' + string

    def can_perform_ldd(self):
        """This function checks if ldd is present in the system"""
        return shutil.which('ldd') is not None

    def check_ldd_deb(self, executables):
        """This function calls ld debug function on executables
        param: dictionary of executables - key: executable basefile, value: list of paths
        return: dictionary with key: direct dependency,
        value: dictionary with key transitive dependency element and value as package manager result for it
        """
        ld = LdDebugParser()
        ld_deb_dict = dict()
        ld_return_dict = dict()
        bdba_dict = dict()
        for executable, exec_list in executables.items():
            for each_ele in exec_list:
                str_ele = each_ele.strip(" ").strip('\"')
                ld_debug_dict = ld.run_ld_debug(str_ele, self.bld_dir)
                ld_deb_dict[str_ele] = ld_debug_dict
        for executable, components in ld_deb_dict.items():
            for dependency, dependency_of_dep in components.items():
                ld_return_dict[dependency], bdba_dict = self.check_pkg_for_ldds(list(dependency_of_dep), bdba_dict)
        return ld_return_dict, bdba_dict

    def check_components(self):
        """This function creates final dictionary joining all direct (from linker and header)
        and transitive dependencies from ldd and ld_debug
        """
        pkg_mgr_components = {**self.pkg_mgr_data['linker'], **self.pkg_mgr_data['header']}
        # logging.debug("pkg_manager_components now are {}".format(pkg_mgr_components))
        linker_components = self.ldd_linker
        ld_debug_components = self.lddebug_executable
        left_ovr_pairs_linker = set(linker_components.keys())
        left_ovr_pairs_ld_debug = set(ld_debug_components.keys())

        trans_dep_dict = defaultdict(set)
        for each_component, pkg_result in pkg_mgr_components.items():

            if each_component in linker_components:
                for dep_1, ldd_pkg_mgr_res in linker_components[each_component].items():
                    trans_dep_dict[pkg_result].add(ldd_pkg_mgr_res)
                left_ovr_pairs_linker.remove(each_component)

            if each_component in ld_debug_components:
                for dep_2, ld_pkg_mgr_res in ld_debug_components[each_component].items():
                    trans_dep_dict[pkg_result].add(ld_pkg_mgr_res)
                left_ovr_pairs_ld_debug.remove(each_component)

            if (each_component not in linker_components) and (each_component not in ld_debug_components):
                trans_dep_dict[pkg_result] = set()

        sub_linker_components = {key: linker_components[key] for key in left_ovr_pairs_linker if
                                 key in linker_components}
        sub_ld_debug_components = {key: ld_debug_components[key] for key in left_ovr_pairs_ld_debug if
                                   key in ld_debug_components}

        logging.debug("sub_linker_components is {}".format(sub_linker_components))
        logging.debug("sub_ld_debug_components is {}".format(sub_ld_debug_components))

        for dep, dep_trans in sub_linker_components.items():
            sha1, confidence, pkg_result_1, result = self.run_pkg_query([dep])
            if result:
                pkg_result_1 = self.join_components(sha1, confidence, pkg_result_1, self.direct_match_evidence)
                for dep_3, ld_pkg_mgr_r in dep_trans.items():
                    trans_dep_dict[pkg_result_1].add(ld_pkg_mgr_r)

        for dep, dep_trans in sub_ld_debug_components.items():
            sha1, confidence, pkg_result_1, result = self.run_pkg_query([dep])
            if result:
                pkg_result_1 = self.join_components(sha1, confidence, pkg_result_1, self.direct_match_evidence)
                for dep_3, ld_pkg_mgr_r in dep_trans.items():
                    trans_dep_dict[pkg_result_1].add(ld_pkg_mgr_r)
        return trans_dep_dict

    def create_csv(self, table_df):
        """This function creates raw_bdio.csv"""
        self.csv_fields_size()
        if table_df != []:
            if self.pkg_manager == 'rpm':
                df = pd.DataFrame(table_df,
                                  columns=["distro", "fullpath", "package-name", "package-version", "confidence",
                                           "size",
                                           "timestamp", "sha1", "matchType", "package-architecture", "epoch", "release",
                                           "trans-dep"])

            elif self.pkg_manager == 'dpkg':
                df = pd.DataFrame(table_df,
                                  columns=["distro", "fullpath", "package-name", "package-version", "confidence",
                                           "size",
                                           "timestamp", "sha1", "matchType", "package-architecture", "trans-dep"])
            elif self.pkg_manager == 'brew':
                df = pd.DataFrame(table_df,
                                  columns=["distro", "fullpath", "package-name", "package-version", "confidence",
                                           "size",
                                           "timestamp", "sha1", "matchType", "trans-dep"])
                df['package-architecture'] = 'none'
            df['separator'] = '/'
            df['package-type'] = self.pkg_manager
            df['type'] = 'distro-package'
            # csv_file_short = os.path.join(self.output_dir, "raw_bdio_short.csv")
            df[["size", "timestamp", "confidence"]] = df[["size", "timestamp", "confidence"]].apply(pd.to_numeric,
                                                                                                    errors='coerce')
            df[["size", "timestamp", "confidence"]] = df[["size", "timestamp", "confidence"]].fillna(value=0)
            df[["size", "timestamp", "confidence"]] = df[["size", "timestamp", "confidence"]].astype(int)
            df.fullpath = df.fullpath.apply(lambda x: tuple(x) if type(x) != str else tuple([x]))
            logging.debug("length of dataframe is {}".format(len(df)))
            df1 = df.groupby(
                ["package-name", "package-version", "package-architecture"]).agg({'trans-dep': sum}).reset_index()
            df1 = pd.merge(df1, df[
                ["distro", "fullpath", "package-name", "package-version", "package-architecture", "confidence", "size",
                 "timestamp", "sha1",
                 "matchType", "type", "package-type"]], on=["package-name", "package-version", "package-architecture"],
                           how='inner')
            df1['trans-dep'] = df['trans-dep'].apply(
                lambda x: [list(tdep_t) for tdep_t in set(tuple(tdep) for tdep in x)])
            duplicate_res = df1['trans-dep'].astype(str).duplicated()
            df1['trans-dep'] = df1['trans-dep'].where(~duplicate_res, "[]")
            df1['trans-dep'] = df1['trans-dep'].astype(str)
            df1['length'] = df1['trans-dep'].str.len()
            logging.debug("df1 columns are {}".format(df1.columns))
            df1.sort_values('length', ascending=False, inplace=True)
            df1.to_csv(self.csv_file_path,
                       columns=["distro", "fullpath", "package-name", "package-version", "package-architecture",
                                "confidence",
                                "size", "timestamp", "sha1", "matchType", "type", "package-type", "trans-dep"],
                       index=False)
            logging.info("raw_bdio.csv written to location {}".format(self.output_dir))
        else:
            df1 = pd.DataFrame(columns=["distro", "fullpath", "package-name", "package-version", "package-architecture",
                                        "confidence",
                                        "size", "timestamp", "sha1", "matchType", "type", "package-type", "trans-dep"])
            df1.to_csv(self.csv_file_path, index=False)
            logging.warning("Empty csv written..no package manager result found")

    def parse_components_info(self):
        """function to parse package manager result string into list of values"""
        table_df = []
        for component, trans_components_set in self.final_components_dict.items():
            col_df = self.parse_logic(component)
            trans_list = []
            for each_trans_comp in trans_components_set:
                trans_col_df = self.parse_logic(each_trans_comp, trans_status=True)
                trans_list.append(trans_col_df)
            trans_list.sort()
            uniq_trans_list = list(trans_list for trans_list, _ in itertools.groupby(trans_list))
            col_df.append(uniq_trans_list)
            table_df.append(col_df)
        self.create_csv(table_df)

    def parse_logic(self, component_str, trans_status=False):
        """ parsing logic for package manager result string
        param: string - package manager result
        return: list
        for eg: ['a/b/c.so','openssl','1.2.3',100,12436,2425364646,'faa816df1c632fcba5c4d525a180aa4c8b85f515',...]
        """
        component_info = []
        """ If os distribtion is mac/windows, setting it to fedora to get more external id matches """
        if self.os_dist == "Mac" or self.os_dist == "windows":
            self.os_dist = "fedora"
        component_info.append(self.os_dist)

        pattern_file = re.compile('(?<=file:)([^ ])*')
        fullpath_info = (self.bld_dir, re.search(pattern_file, component_str).group())
        pattern_pkg = re.compile('(?<=pkg:)([^ ])*')
        pkg_info = re.search(pattern_pkg, component_str).group()
        pattern_vers = re.compile('(?<=version:)([^ ])*')
        pkg_version_info = re.search(pattern_vers, component_str).group()
        pattern_conf = re.compile('(?<=confidence:)([^ ])*')
        try:
            confidence_info = int(re.search(pattern_conf, component_str).group())
        except ValueError:
            confidence_info = 0
        pattern_size = re.compile('(?<=size:)([^ ])*')
        try:
            size_info = int(re.search(pattern_size, component_str).group())
        except ValueError:
            size_info = 0
        pattern_time = re.compile('(?<=timestamp:)([^ ])*')
        try:
            time_info = int(re.search(pattern_time, component_str).group())
        except ValueError:
            time_info = 0
        pattern_sha1 = re.compile('(?<=sha1sum:)([^ ])*')
        sha1_info = re.search(pattern_sha1, component_str).group()

        pattern_matchtype = re.compile('(?<=matchType:)([^ ])*')
        matchtype_info = re.search(pattern_matchtype, component_str).group()

        if self.pkg_manager != 'brew':
            pattern_arch = re.compile('(?<=package-architecture:)([^ ])*')
            rx = re.compile('([()])')
            architecture_info = re.sub(rx, '', re.search(pattern_arch, component_str).group())
        if self.pkg_manager == 'rpm':
            pattern_epoch = re.compile('(?<=epoch:)([^ ])*')
            rx = re.compile('([()])')
            epoch_info = re.sub(rx, '', re.search(pattern_epoch, component_str).group())

            pattern_release = re.compile('(?<=release:)([^ ])*')
            release_info = re.sub(rx, '', re.search(pattern_release, component_str).group())

            pkg_version_info = epoch_info.replace('none:', '') + pkg_version_info + release_info.replace('-none', '')
            architecture_info = re.sub(rx, '', re.search(pattern_arch, component_str).group()).strip('/')

        component_info.append(fullpath_info)
        component_info.append(pkg_info)
        component_info.append(pkg_version_info)
        component_info.append(confidence_info)
        component_info.append(size_info)
        component_info.append(time_info)
        component_info.append(sha1_info)
        if trans_status:
            component_info.append('distro-package')
        component_info.append(matchtype_info)
        if self.pkg_manager != 'brew':
            component_info.append(architecture_info)
        if self.pkg_manager == 'rpm':
            component_info.append(epoch_info)
            component_info.append(release_info)
        return component_info

    def trans_key_value(self, string_in):
        """ function to append keys for transitive dependency list from csv for json
        param: string - package manager result for transitive dependency
        return: list of dictionaries
        eg: [{'distro':'ubuntu',..'package-name':'curl'..},
         {'distro':'ubuntu',..'package-name':'gcc'..}..]
        """
        dict_keys = ['distro', 'fullpath', 'package-name', 'package-version', 'confidence', 'size', 'timestamp', 'sha1',
                     'type',
                     'matchType', 'package-architecture']
        trans_dep_list = []
        list_in = ast.literal_eval(string_in)
        for each_list in list_in:
            if each_list != "[]":
                trans_dep_dict = dict(zip(dict_keys, each_list))
                trans_dep_list.append(trans_dep_dict)
        return trans_dep_list

    def csv_to_json(self):
        """This function converts raw_bdio.csv to raw_bdio.json"""
        data = {}
        try:
            with open(self.csv_file_path, encoding='utf-8') as csvf:
                csvReader = csv.DictReader(csvf)
                key1 = 'extended-objects'
                data['extended-objects'] = []
                for rows in csvReader:
                    new_row = dict()
                    for key, value in rows.items():
                        if key == 'trans-dep':
                            if value != "[]":
                                trans_dep_list = self.trans_key_value(value)
                                new_row[key] = trans_dep_list
                        elif key != 'fullpath':
                            try:
                                new_row[key] = int(value)
                            except ValueError:
                                new_row[key] = value
                        else:
                            new_row[key] = ast.literal_eval(value)
                    data[key1].append(new_row)
            try:
                with open(self.json_file_path, 'w', encoding='utf-8') as jsonf:
                    jsonf.write(json.dumps(data, indent=4))
                logging.info("raw_bdio.json written to location {}".format(self.output_dir))
            except OSError:
                logging.error("Couldn't write file {}".format(self.json_file_path))
        except FileNotFoundError:
            logging.error("raw_bdio.csv file not found - make sure csv file is written correctly")

    ## tar file
    def tar_files(self):
        """this function tars file for bdba"""
        tar_set_files = set()
        [[[tar_set_files.add(path) for path in paths] for paths in type.values()] for type in self.bdba_data.values()]
        logging.info("\nTarring all binary files\n")
        dir_path = os.path.join(self.output_dir, "bdba_ready.tar")
        if os.path.exists(dir_path):
            os.remove(dir_path)
        with tarfile.open(dir_path, 'w') as bdba_tar:
            for path in tqdm.tqdm(tar_set_files, total=len(tar_set_files)):
                if os.path.exists(path):
                    bdba_tar.add(path)
        logging.info("Files are placed in '{}' ".format(self.output_dir))
        logging.info("Number of files in bdba tar file are {}".format(len(tar_set_files)))

    def csv_fields_size(self):
        max_int = sys.maxsize
        while True:
            # decrease the maxInt value by factor 10  as long as the OverflowError occurs.
            try:
                csv.field_size_limit(max_int)
                break
            except OverflowError:
                max_int = int(max_int / 10)

    def get_dict_difference(self, json_dict, grep_dict):
        """ function to get files present in json and not in grep and vice versa
        param: json_dict: key with basefile, value as list of paths with that file from coverity json
               grep_dict: key with basefile, value as list of paths with that file from grep
        return: dict_json : files present in json not present in grep as dictionary with key as basefile and value as list of paths
                dict_grep : files present in grep not present in json as dictionary with key as basefile and value as list of paths
        """
        json_keys = set(json_dict.keys())
        # logging.debug("json keys are {}".format(json_keys))
        grep_keys = set(grep_dict.keys())
        # logging.debug("grep keys are {}".format(grep_keys))
        other_keys_in_json = json_keys - grep_keys
        other_keys_in_grep = grep_keys - json_keys
        dict_json = dict((key, json_dict[key]) for key in other_keys_in_json)
        dict_grep = dict((key, grep_dict[key]) for key in other_keys_in_grep)
        return dict_json, dict_grep

    def join_json_grep(self, json_dict, file_type):
        """ function to append resolved coverity json paths which were not found by grep to resolved_file_dict
        param: json_dict: key with basefile, value as list of paths with that file from coverity json
               file_type: 'header', 'linker' or 'executable'
        """
        # adding the values with common key
        for key in json_dict:
            if key in self.resolved_file_dict[file_type]:
                # logging.debug("self.resolved_file_dict[file_type][key] is {}".format(self.resolved_file_dict[file_type][key]))
                self.resolved_file_dict[file_type][key].union(json_dict[key])
            else:
                self.resolved_file_dict[file_type][key] = set(json_dict[key])
        # logging.debug("joined file_type {}".format(file_type))

    def skip_dynamic_files(self):
        self.linker_list = {each_file for each_file in self.linker_list if not (
                re.match(global_settings.so_pattern, each_file.strip()) or re.match(global_settings.dll_pattern,
                                                                                    each_file.strip()))}
        self.cov_linker_files_set = {each_file for each_file in self.cov_linker_files_set if not (
                re.match(global_settings.so_pattern, each_file.strip()) or re.match(global_settings.dll_pattern,
                                                                                    each_file.strip()))}

    def skip_pkg_mgr(self, basefiles_dict):
        bdba_dict = {}
        pkg_dict = {}
        for basefile, paths_list in basefiles_dict.items():
            bdba_dict[basefile] = paths_list
        return pkg_dict, bdba_dict

    def set_csv_matchtpye(self):
        """
        this function reads raw_bdio.csv and sets matchtype based on hub_version
        """
        if (PKG_MGR_MODE in self.run_modes or ALL_MODE in self.run_modes):  # and
            logging.info("Attempting to use offline files for package manager at location: {}".format(
                os.path.join(self.output_dir, 'raw_bdio.csv')))
            if os.path.exists(os.path.join(self.output_dir, 'raw_bdio.csv')):
                logging.info("found package manager csv file")
                raw_bdio_df = pd.read_csv(os.path.join(self.output_dir, 'raw_bdio.csv'))
                self.set_matchtype_per_hub_version()
                raw_bdio_df['matchType'] = self.direct_match_evidence
                raw_bdio_df['trans-dep'] = raw_bdio_df['trans-dep'].apply(
                    lambda x: x.replace('unknown', self.transitive_match_evidence))
                raw_bdio_df.to_csv(self.csv_file_path, index=False)
            else:
                logging.error(
                    "Unable to find previously generated offline files for package manager..please make sure use_offline_files and run_modes are set correctly")

    def set_matchtype_per_hub_version(self):
        """ this function gets hub version information and sets matchtype"""
        hub_version = self.hub_api.get_hub_version()
        logging.info("BLACK DUCK VERSION IS {}".format(hub_version))
        vers_result = hub_version.split(".")
        if (int(vers_result[0]) >= 2021 and int(vers_result[1]) >= 6) or int(vers_result[0]) >= 2022:
            self.direct_match_evidence = 'DIRECT_DEPENDENCY_BINARY'
            self.transitive_match_evidence = 'TRANSITIVE_DEPENDENCY_BINARY'
        else:
            self.direct_match_evidence = 'Binary'
            self.transitive_match_evidence = 'Binary'

    def run(self):
        run_mode_res = PKG_MGR_MODE in self.run_modes or ALL_MODE in self.run_modes
        if not self.use_offline_files:
            self.run_log_parser()

            if self.skip_dynamic:
                self.skip_dynamic_files()

            start_file_dict = datetime.now()
            self.file_dict['executable'] = self.get_files(self.executable_list)
            self.file_dict['linker'] = self.get_files(self.linker_list)
            self.file_dict['header'] = self.get_files(self.header_list)

            self.cov_file_dict['cov-executable'] = self.get_files(self.cov_executable_files_set)
            self.cov_file_dict['cov-linker'] = self.get_files(self.cov_linker_files_set)
            self.cov_file_dict['cov-header'] = self.get_files(self.cov_header_files_set)
            end_file_dict = datetime.now()
            logging.debug(
                "time taken to create dictionary from parsed and json files {}".format(end_file_dict - start_file_dict))

            logging.info("number of distinct executable files are {}".format(len(self.file_dict['executable'])))
            logging.info("number of distinct linker files are {}".format(len(self.file_dict['linker'])))
            logging.info("number of distinct header files are {}".format(len(self.file_dict['header'])))

            logging.info("coverity json - number of distinct executable files are {}".format(
                len(self.cov_file_dict['cov-executable'])))
            logging.info(
                "coverity json - number of distinct linker files are {}".format(len(self.cov_file_dict['cov-linker'])))
            logging.info(
                "coverity json - number of distinct header files are {}".format(len(self.cov_file_dict['cov-header'])))
            self.write_to_txt(self.file_dict, self.binary_files_path)
            self.unresol_set = set(
                list(self.file_dict['executable'].keys()) + list((self.file_dict['linker'].keys())) + list(
                    (self.file_dict['header'].keys())))
            logging.info("total number of unresolved files at beginning are : {}".format(len(self.unresol_set)))

            self.build_dir_dict = self.generate_build_dir_files()
            # logging.debug("number of distinct build dir files are {}".format(len(self.build_dir_dict)))

            start_resolv = datetime.now()
            self.resolved_file_dict['executable'], self.unresolved_file_dict['executable'] = self.resolve_file_paths(
                self.file_dict['executable'])
            self.resolved_file_dict['linker'], self.unresolved_file_dict['linker'] = self.resolve_file_paths(
                self.file_dict['linker'])
            self.resolved_file_dict['header'], self.unresolved_file_dict['header'] = self.resolve_file_paths(
                self.file_dict['header'])

            self.resolved_cov_file_dict['cov-executable'], self.unresolved_cov_file_dict[
                'cov-executable'] = self.resolve_file_paths(
                self.cov_file_dict['cov-executable'])
            self.resolved_cov_file_dict['cov-linker'], self.unresolved_cov_file_dict[
                'cov-linker'] = self.resolve_file_paths(
                self.cov_file_dict['cov-linker'])
            self.resolved_cov_file_dict['cov-header'], self.unresolved_cov_file_dict[
                'cov-header'] = self.resolve_file_paths(
                self.cov_file_dict['cov-header'])

            logging.debug("total resolved files: {} and total unresolved files : {} for executables".format(
                len(self.resolved_file_dict['executable']), len(self.unresolved_file_dict['executable'])))
            logging.debug("total resolved files: {} and total unresolved files : {} for linker".format(
                len(self.resolved_file_dict['linker']), len(self.unresolved_file_dict['linker'])))
            logging.debug("total resolved files: {} and total unresolved files : {} for header".format(
                len(self.resolved_file_dict['header']), len(self.unresolved_file_dict['header'])))

            logging.debug(
                "coverity json - total resolved files: {} and total unresolved files : {} for executables".format(
                    len(self.resolved_cov_file_dict['cov-executable']),
                    len(self.unresolved_cov_file_dict['cov-executable'])))
            logging.debug("coverity json - total resolved files: {} and total unresolved files : {} for linker".format(
                len(self.resolved_cov_file_dict['cov-linker']), len(self.unresolved_cov_file_dict['cov-linker'])))
            logging.debug("coverity json - total resolved files: {} and total unresolved files : {} for header".format(
                len(self.resolved_cov_file_dict['cov-header']), len(self.unresolved_cov_file_dict['cov-header'])))

            self.difference_dict = {}
            self.difference_dict['extra-exe-in-json'], self.difference_dict[
                'extra-exe-in-grep'] = self.get_dict_difference(self.resolved_cov_file_dict['cov-executable'],
                                                                self.resolved_file_dict['executable'])
            self.difference_dict['extra-linker-in-json'], self.difference_dict[
                'extra-linker-in-grep'] = self.get_dict_difference(self.resolved_cov_file_dict['cov-linker'],
                                                                   self.resolved_file_dict['linker'])
            self.difference_dict['extra-header-in-json'], self.difference_dict[
                'extra-header-in-grep'] = self.get_dict_difference(self.resolved_cov_file_dict['cov-header'],
                                                                   self.resolved_file_dict['header'])

            logging.info("total executables present in json not present in grep are : {}".format(
                len(self.difference_dict['extra-exe-in-json'])))
            logging.info("total linker present in json not present in grep are : {}".format(
                len(self.difference_dict['extra-linker-in-json'])))
            logging.info("total header present in json not present in grep are : {}".format(
                len(self.difference_dict['extra-header-in-json'])))
            logging.info("total executables present in grep not present in json are : {}".format(
                len(self.difference_dict['extra-exe-in-grep'])))
            logging.info("total linker present in grep not present in json are : {}".format(
                len(self.difference_dict['extra-linker-in-grep'])))
            logging.info("total header present in grep not present in json are : {}".format(
                len(self.difference_dict['extra-header-in-grep'])))

            self.write_to_txt(self.resolved_file_dict, self.resolved_files_path)
            self.write_to_txt(self.unresolved_file_dict, self.unresolved_files_path)
            self.write_to_txt(self.difference_dict, self.json_grep_files_list)
            self.write_to_txt(self.resolved_cov_file_dict, self.resolved_cov_files_path)
            self.write_to_txt(self.unresolved_cov_file_dict, self.unresolved_cov_files_path)

            # join here cov-json and grep
            self.join_json_grep(self.resolved_cov_file_dict['cov-linker'], 'linker')
            self.join_json_grep(self.resolved_cov_file_dict['cov-header'], 'header')
            self.join_json_grep(self.resolved_cov_file_dict['cov-executable'], 'executable')

            logging.debug("after join: total resolved files: {} and total unresolved files : {} for executables".format(
                len(self.resolved_file_dict['executable']), len(self.unresolved_file_dict['executable'])))
            logging.debug("after join: total resolved files: {} and total unresolved files : {} for linker".format(
                len(self.resolved_file_dict['linker']), len(self.unresolved_file_dict['linker'])))
            logging.debug("after join: total resolved files: {} and total unresolved files : {} for header".format(
                len(self.resolved_file_dict['header']), len(self.unresolved_file_dict['header'])))

            end_resolv = datetime.now()
            logging.debug(
                "time taken to resolve paths and join parse files with json files {}".format(end_resolv - start_resolv))

            # check hub version if online or take version input from user
        logging.debug("self.offline mode is {}".format(self.offline))
        logging.debug("self.use_offline_files is {}".format(self.use_offline_files))

        if self.offline:
            self.direct_match_evidence = 'unknown'
            self.transitive_match_evidence = 'unknown'
        else:
            self.set_matchtype_per_hub_version()

        if not self.use_offline_files:
            start_pkg = datetime.now()
            if run_mode_res:
                logging.debug("self.direct match evd is {}".format(self.direct_match_evidence))
                logging.debug("self.trans match evd is {}".format(self.transitive_match_evidence))

                self.pkg_mgr_data['linker'], self.bdba_data['linker'] = self.check_pkg_mgr(
                    self.resolved_file_dict['linker'])
                self.pkg_mgr_data['header'], self.bdba_data['header'] = self.check_pkg_mgr(
                    self.resolved_file_dict['header'])
            else:
                self.pkg_mgr_data['linker'], self.bdba_data['linker'] = self.skip_pkg_mgr(
                    self.resolved_file_dict['linker'])
                self.pkg_mgr_data['header'], self.bdba_data['header'] = self.skip_pkg_mgr(
                    self.resolved_file_dict['header'])
            end_pkg = datetime.now()
            logging.info("time taken to get package manager results {}".format(end_pkg - start_pkg))

            logging.debug("length of pkg_mgr_data for linker is {}".format(len(self.pkg_mgr_data['linker'])))
            logging.debug("length of bdba_data for linker is {}".format(len(self.bdba_data['linker'])))
            logging.debug("bdba_data for linker is {}".format(self.bdba_data['linker']))

            logging.debug("length of pkg_mgr_data for header is {}".format(len(self.pkg_mgr_data['header'])))
            logging.debug("length of bdba_data for header is {}".format(len(self.bdba_data['header'])))
            logging.debug("bdba_data for header is {}".format(self.bdba_data['header']))

            if self.can_perform_ldd() and not self.skip_transitives and not self.skip_dynamic and run_mode_res:
                start_ldd = datetime.now()
                self.ldd_linker, self.bdba_data['ldd_linker'] = self.check_ldd(self.pkg_mgr_data['linker'])
                logging.debug("ldd_linker is {}".format(self.ldd_linker))
                logging.debug("length of ldd_linker is {}".format(len(self.ldd_linker)))
                logging.debug("length of bdba_data for ldd_linker is {}".format(len(self.bdba_data['ldd_linker'])))
                logging.debug("bdba_data for ldd_linker is {}".format(self.bdba_data['ldd_linker']))

                self.lddebug_executable, self.bdba_data['lddebug_exe'] = self.check_ldd_deb(
                    self.resolved_file_dict['executable'])
                logging.debug("lddebug_executable is {}".format(self.lddebug_executable))
                logging.debug("length of lddebug_executable is {}".format(len(self.lddebug_executable)))
                logging.debug(
                    "length of bdba_data for lddebug_executable is {}".format(len(self.bdba_data['lddebug_exe'])))
                logging.debug("bdba_data for lddebug_executable is {}".format(self.bdba_data['lddebug_exe']))
                end_ldd = datetime.now()
                logging.info("time taken to get ldd results {}".format(end_ldd - start_ldd))

            if run_mode_res:
                self.final_components_dict = self.check_components()
                logging.debug("final_components_dict is  {}".format(self.final_components_dict))
                self.parse_components_info()  ## csv created in offline/online mode
                if not self.offline:
                    self.csv_to_json()
            if BDBA_MODE in self.run_modes or ALL_MODE in self.run_modes:
                self.tar_files()

        else:  ## if use_offline_files is set to True
            if run_mode_res:
                self.set_csv_matchtpye()
                self.csv_to_json()
