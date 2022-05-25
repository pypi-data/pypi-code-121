"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

from collections import defaultdict
from blackduck_c_cpp.util import util
import os
import subprocess
import re
import pandas as pd
from blackduck_c_cpp.util import global_settings


class LdDebugParser:

    def __init__(self):
        pass

    def initialize(self, nodes):
        self.graph = defaultdict(list)
        self.n = nodes

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def run_ld_debug(self, executable, bld_dir):
        ld_debug_dict = defaultdict(set)
        if os.path.exists(executable):
            out = subprocess.getstatusoutput("LD_DEBUG=files ldd " + "{}".format(executable) + " 2> /dev/null")
        elif os.path.exists(os.path.join(bld_dir, executable)):
            out = subprocess.getstatusoutput(
                "LD_DEBUG=files ldd " + "{}".format(os.path.join(bld_dir, executable)) + " 2> /dev/null")
        else:
            return ld_debug_dict

        status, ld_result = util.value_getstatusoutput(out)
        output_path_set = defaultdict(list)

        if status and ('no path found matching pattern' not in ld_result):
            parsed_results = re.findall(r'^\s*(\S+)\s+=>(.*) \(.*\)$', ld_result, re.MULTILINE)
            for fname, path in parsed_results:
                """ storing filename: fullpath eg: a.so: g/f/d/a.so"""
                output_path_set[fname.strip()] = path.strip()
            pattern_transitive = re.compile('(?<=file=)([^ ])*')
            pattern_direct = re.compile('(?<=needed by )([^ ])*')
            self.initialize(list(output_path_set.values()))
            row_df = []
            for each_line in ld_result.split("\n"):
                col_df = []
                res_transitive = re.search(pattern_transitive, each_line)
                res_direct = re.search(pattern_direct, each_line)
                if res_transitive and res_direct:
                    res_direct_path = res_direct.group().strip()
                    res_transitive_path = res_transitive.group().strip()
                    res_direct_basename = os.path.basename(res_direct_path)
                    res_transitive_basename = os.path.basename(res_transitive_path)

                    if res_direct_basename not in output_path_set:
                        output_path_set[res_direct_basename] = res_direct_path

                    self.add_edge(output_path_set[res_direct_basename], output_path_set[res_transitive_basename])
                    col_df.append(output_path_set[res_direct_basename])
                    col_df.append(output_path_set[res_transitive_basename])
                    row_df.append(col_df)
            dep_df = pd.DataFrame(row_df, columns=['dep', 'dep_of_dep'])
            dep_df = dep_df[dep_df.astype(str)['dep'] != '[]']
            dep_df = dep_df[dep_df.astype(str)['dep_of_dep'] != '[]']
            ld_debug_dict = defaultdict(set)
            for dep, dep_dep in zip(list(dep_df['dep']), list(dep_df['dep_of_dep'])):
                ld_debug_dict[dep].add(dep_dep)
            dep_of_dep_list = list(ld_debug_dict.values())
            dep_list = list(ld_debug_dict.keys())
            keys_to_del = []
            """if dep is present in list of transitive dependencies,
            add everything to dependency and del transitive dependency key"""
            for dep, dep_of_dep in ld_debug_dict.items():
                if re.match(global_settings.so_pattern, dep):
                    dep_key = [dep_list[idx] for idx, trans_dep in enumerate(dep_of_dep_list) if dep in trans_dep]
                    if re.match(global_settings.so_pattern, dep_key[0]):
                        ld_debug_dict[dep_key[0]].update(ld_debug_dict[dep])
                        keys_to_del.append(dep)
            for each_key in keys_to_del:
                del ld_debug_dict[each_key]
            return ld_debug_dict
        else:
            return ld_debug_dict
