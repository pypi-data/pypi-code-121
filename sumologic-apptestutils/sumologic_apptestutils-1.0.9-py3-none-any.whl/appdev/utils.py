import difflib
import json
import os
from collections import OrderedDict
from sumoapputils.common.testutils import get_test_class
from sumoapputils.common.utils import run_cmd, get_file_data


default_extract_keys = ["name", "panels.name", "type", "*.title", "*.queryString", "*.description", "*.searchQuery",
                        "*.timeRange", "*.timerange", "*.queryText", "*.query", "*.defaultTimeRange"]

def show_diff(text, n_text):
    class Colors:
        # RED = '\033[91m'
        RED = '\033[31m'
        END = '\033[0m'
        # END = '\033[m'
        GREEN = '\033[32m'

    seqm = difflib.SequenceMatcher(None, text, n_text)
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':

            output.append(Colors.GREEN + seqm.b[b0:b1] + Colors.END)
        elif opcode == 'delete':

            output.append(Colors.RED + seqm.a[a0:a1] + Colors.END)
        elif opcode == 'replace':
            # pass
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append(Colors.RED + seqm.a[a0:a1] + Colors.END)
            output.append(Colors.GREEN + seqm.b[b0:b1] + Colors.END)
        else:
            raise Exception("unexpected opcode")
    return ''.join(output)


def show_vimdiff(old_file, new_file):
    return_code, cmd = run_cmd("vimdiff %s %s -c 'colo molokai' -c TOhtml -c 'w! diff.html' -c 'qa!'" % (old_file, new_file))
    if return_code:
        raise Exception("Makesure you are running this command in unix systems with vimdiff installed. Process code: %d" % return_code)
    if not os.path.isfile("diff.html"):
        raise Exception('Unable to find generated diff.html')
    return_code, cmd = run_cmd("open diff.html")
    if return_code:
        raise Exception("Unable to open html file. Process code: %d" % return_code)


def is_key_present(preserve_keys, cur_key):
    for key in preserve_keys:
        if key.startswith("*"):

            if cur_key.endswith(key.rsplit(".", 1)[-1]):
                return True
        elif key == cur_key:
            return  True
    return False


def filterjson(jsonobj, preserve_keys, cur_key=""):
    next_key = cur_key+"." if cur_key else cur_key
    has_any_preserved_key = flag = False
    if jsonobj:
        if isinstance(jsonobj, dict):
            keys_to_delete = []
            for k, v in jsonobj.items():
                if is_key_present(preserve_keys, next_key+k):
                    flag = True
                elif isinstance(v, (dict, list)):
                    # dict of dict # dict of list
                    jsonobj[k], flag = filterjson(v, preserve_keys, next_key+k)
                    if not is_key_present(preserve_keys, next_key+k) and not flag:
                        keys_to_delete.append(k)
                elif not is_key_present(preserve_keys, next_key+k):
                    keys_to_delete.append(k)
                    flag = False

                has_any_preserved_key = flag or has_any_preserved_key
            # if keys_to_delete:
            #     print('deleting keys', keys_to_delete)
            # else:
            #     print('preserving', jsonobj.keys())
            for k in keys_to_delete:
                del jsonobj[k]
        elif isinstance(jsonobj, list):
            for idx, item in enumerate(jsonobj):
                if isinstance(item, (dict, list)):
                    # list of dict #list of list
                    jsonobj[idx], flag = filterjson(item, preserve_keys, cur_key)
                    has_any_preserved_key = flag or has_any_preserved_key

    return jsonobj, has_any_preserved_key


def generate_mini_appfile(filepath, extract_keys):
    appjson = get_file_data(filepath)
    appDict = json.loads(appjson, object_pairs_hook=OrderedDict)
    dashboard_class = get_test_class(appjson=appDict)
    dashboards, searches = dashboard_class.get_content(appDict)
    dashboard_class.remove_text_panels(dashboards)


    dashboards = dashboard_class.order_dashboards_by_name(dashboards)
    dashboards = dashboard_class.order_panels_by_name(dashboards)
    searches = dashboard_class.order_searches_by_name(searches)
    filterjson(dashboards, extract_keys)
    filterjson(searches, extract_keys)
    output = {"appname": appDict["name"], "dashboards": dashboards, "searches": searches}
    if "description" in extract_keys:
        output["description"] = appDict["description"]
    return output

