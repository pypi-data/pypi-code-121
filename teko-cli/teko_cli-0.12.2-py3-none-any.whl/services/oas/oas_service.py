import json
import yaml
import sys
import urllib
import re

import requests
from colorama import Fore, Back, Style

from teko.helpers.clog import CLog
from teko.services.oas.parse.openapi3 import OpenAPI
from teko.services.oas.parse.openapi3.object_base import Map
from teko.services.oas.parse.openapi3.schemas import Schema


class OasService:
    """
    Oas API docs:
    """
    DIFFERENCE_STATUS = 'difference'
    MISS_STATUS = 'miss'
    REDUNDANCY_STATUS = 'redundancy'
    WARNING = 'warning'
    ERROR = 'error'
    NOT_COMPARE_PROPERTY_LIST = ['dct', 'example', 'examples', 'x-examples', 'tags', 'description', 'operationId']
    WARNING_PROPERTY_LIST = ["summary", "description", "operationId", "title", "examples", "example", "x-examples"]

    def parse_file(self, file):
        spec = self.load_data(file)

        o = OpenAPI(spec, validate=True)
        self.print_class_object(o)

        errors = o.errors()

        if errors:
            # print errors
            for e in errors:
                print('{}: {}'.format('.'.join(e.path), e.message[:300]))
            print()
            print('{} errors'.format(len(errors)))
            sys.exit(1)  # exit with error status
        else:
            print('OK')

    @classmethod
    def diff_oas(cls, code_spec, doc_spec):
        """code_spec, doc_spec: string path of file json/yaml openapi"""
        diff = {"difference": {}, "miss": {}, "redundancy": {}}

        # decode
        code_spec = OasService.load_data(code_spec)
        doc_spec = OasService.load_data(doc_spec)

        # parse to Openapi object
        code_o = OpenAPI(code_spec, validate=True)
        doc_o = OpenAPI(doc_spec, validate=True)
        root_code_spec = code_o
        root_doc_spec = doc_o
        OasService.compare_api(diff, code_o, doc_o, root_doc_spec, root_code_spec, "spec")
        OasService.compare_api(diff, doc_o, code_o, root_doc_spec, root_code_spec, "real")
        OasService.print_result(diff)
        return diff

    @classmethod
    def print_result(cls, result, count=0, count_errors=0, count_warnings=0):
        for key, value in result.items():
            if "severity" in value.keys():
                if value["validation_status"] == OasService.DIFFERENCE_STATUS:
                    if value["severity"] == OasService.WARNING:
                        count_warnings += 1
                        print('  ' * count, key + Style.RESET_ALL)
                        print(Fore.LIGHTYELLOW_EX + '- ', '  ' * (count - 1), str(value['spec']) + Style.RESET_ALL)
                        print(Fore.LIGHTYELLOW_EX + '+ ', '  ' * (count - 1), str(value['real']) + Style.RESET_ALL)
                    else:
                        count_errors += 1
                        print('  ' * count, key)
                        print(Back.LIGHTRED_EX + '- ', '  ' * (count - 1), str(value['spec']) + Style.RESET_ALL)
                        print(Back.LIGHTCYAN_EX + '+ ', '  ' * (count - 1), str(value['real']) + Style.RESET_ALL)
                else:
                    if value["validation_status"] == OasService.MISS_STATUS:
                        operator = '- '
                        background = Back.LIGHTRED_EX
                    # elif value["validation_status"] == OasService.REDUNDANCY_STATUS:
                    else:
                        operator = '+ '
                        background = Back.LIGHTCYAN_EX
                    if value["severity"] == OasService.WARNING:
                        count_warnings += 1
                        print(Fore.LIGHTYELLOW_EX + operator, '  ' * (count - 1), key + Style.RESET_ALL)
                    else:
                        count_errors += 1
                        print(background + operator, '  ' * (count - 1), key + Style.RESET_ALL)
            else:
                if key in [OasService.MISS_STATUS, OasService.DIFFERENCE_STATUS, OasService.REDUNDANCY_STATUS]:
                    print('  ' * count, Fore.MAGENTA + key + Style.RESET_ALL)
                else:
                    print('  ' * count, key)
                count += 1
                OasService.print_result(value, count, count_errors, count_warnings)
                count -= 1
        # if count == 0:
        #     exit(count_errors)

    @classmethod
    def compare_api(cls, diff, code_spec, doc_spec, root_doc_spec, root_code_spec, root="spec"):
        """diff: variable for result compare, initialed before call method"""
        # compare paths object
        for key, doc_value in doc_spec.paths.items():
            if key not in code_spec.paths.keys():
                if root == "spec":
                    OasService.add_miss_or_redundancy_object(diff, doc_spec.paths.path, key, OasService.MISS_STATUS)
                # root == "real"
                else:
                    OasService.add_miss_or_redundancy_object(diff, doc_spec.paths.path, key,
                                                             OasService.REDUNDANCY_STATUS)
            else:
                for k, v in code_spec.paths.items():
                    if k == key:
                        code_value = v
                        OasService.compare_object(diff, code_value, doc_value, root_doc_spec, root_code_spec, root=root)

        # compare similar components (class model) of doc and code
        #   todo: before check parse error if miss model => key always exist in code_spec.components
        for key, doc_value in doc_spec.components.schemas.items():
            for k, code_value in code_spec.components.schemas.items():
                if k == key:
                    OasService.compare_object(diff, code_value, doc_value, root_doc_spec, root_code_spec, root=root)

    @classmethod
    def compare_object(cls, diff, code_spec, doc_spec, root_doc_spec, root_code_spec, root="spec", name_parameter=""):
        for item in doc_spec.__slots__:
            if item in OasService.NOT_COMPARE_PROPERTY_LIST or item.startswith('_') or \
                    (not isinstance(getattr(doc_spec, item), bool) and not getattr(doc_spec, item)):
                continue
            if "parameters" not in doc_spec.path:
                name_parameter = ""

            # check item in remain object
            # ! code addition check: or (not isinstance(getattr(code_spec, item), Map))
            if not hasattr(code_spec, item):
                if root == "spec":
                    OasService.add_diff_object(diff, doc_spec.path, item, OasService.MISS_STATUS,
                                               getattr(doc_spec, item))
                # root == "real"
                else:
                    OasService.add_diff_object(diff, doc_spec.path, item, OasService.REDUNDANCY_STATUS,
                                               getattr(doc_spec, item))
                continue

            if isinstance(getattr(doc_spec, item), Map):
                for key, doc_value in getattr(doc_spec, item).items():
                    if key not in getattr(code_spec, item).keys():
                        if root == "spec":
                            OasService.add_diff_object(diff, getattr(doc_spec, item).path, key, OasService.MISS_STATUS,
                                                       doc_value)
                        # root == "real"
                        else:
                            # print('|' * len(doc_spec.path), doc_spec, code_spec, item,
                            #       OasService.DIFFERENCE_STATUS, key, name_parameter)
                            OasService.add_diff_object(diff, getattr(doc_spec, item).path, key,
                                                       OasService.REDUNDANCY_STATUS,
                                                       doc_value)
                        continue
                    else:
                        for k, code_value in getattr(code_spec, item).items():
                            if k == key:
                                # compare name schema if doc_value, code_value is Schema Model
                                if doc_value.path[:2] == ['components', 'schemas'] and \
                                        len(doc_value.path) == len(code_value.path) == 3:
                                    if doc_value.path[-1] != code_value.path[-1]:
                                        OasService.add_diff_object(diff, doc_spec.path, key,
                                                                   OasService.DIFFERENCE_STATUS,
                                                                   doc_value.path[-1], code_value.path[-1])
                                        continue
                                OasService.compare_object(diff, code_value, doc_value, root_doc_spec, root_code_spec,
                                                          root)

            elif isinstance(getattr(doc_spec, item), list) and getattr(doc_spec, item):
                # find miss params if parameter object then compare name
                if item == 'parameters':
                    name_parameters_code = set(x.name for x in getattr(code_spec, item))
                    miss_parameter_objects = [x for x in getattr(doc_spec, item) if
                                              x.name not in name_parameters_code]
                    # check code miss parameters
                    if miss_parameter_objects:
                        for obj in miss_parameter_objects:
                            if root == "spec":
                                OasService.add_diff_object(diff, obj.path, obj.name, OasService.MISS_STATUS, obj,
                                                           '', obj.name)
                            # root == "real"
                            else:
                                OasService.add_diff_object(diff, obj.path, obj.name, OasService.REDUNDANCY_STATUS,
                                                           obj, '', obj.name)

                # todo: show diff many element of List (Array). Error: only element to show. And when compare
                # sub element such as instance, then path don't distinguish other elements of List
                # compare object
                for o_doc in getattr(doc_spec, item):
                    if hasattr(o_doc, '__slots__'):
                        # find code_obj and doc_obj having same name
                        for o_code in getattr(code_spec, item):
                            if item == 'parameters' and o_code.name == o_doc.name:
                                OasService.compare_object(diff, o_code, o_doc, root_doc_spec, root_code_spec, root,
                                                          o_doc.name)
                                break
                            elif isinstance(o_code, Schema) and o_code.type == o_doc.type:
                                #  todo schema error when oneOf/ allOf has many same type
                                OasService.compare_object(diff, o_code, o_doc, root_doc_spec, root_code_spec, root)
                                break

                    # i: string
                    elif isinstance(o_doc, str) or isinstance(o_doc, int) or isinstance(o_doc, bool) \
                            or isinstance(o_doc, float):
                        if o_doc not in getattr(code_spec, item):
                            if root == "spec":
                                OasService.add_diff_object(diff, doc_spec.path, item, OasService.MISS_STATUS, o_doc)
                            else:
                                OasService.add_diff_object(diff, doc_spec.path, item, OasService.REDUNDANCY_STATUS,
                                                           o_doc)
                        # todo check compare
                        else:
                            pass

            elif getattr(doc_spec, item) or isinstance(getattr(doc_spec, item), bool):
                # item: ref and both doc spec, code spec have ref property
                if item == 'ref' and root == 'spec':
                    name_schema_doc = getattr(doc_spec, item).split('/')[-1]
                    name_schema_code = getattr(code_spec, item).split('/')[-1]
                    OasService.add_diff_object(diff, doc_spec.path, item, OasService.DIFFERENCE_STATUS,
                                               name_schema_doc, name_schema_code)
                    continue
                # item: class object (note: Schema don't have __slots__, others have!)
                if hasattr(getattr(doc_spec, item), '__slots__') or isinstance(getattr(doc_spec, item), Schema):
                    # compare Reference with Schema properties
                    if hasattr(getattr(doc_spec, item), 'ref') != hasattr(getattr(code_spec, item), 'ref'):
                        if root == 'spec':
                            if hasattr(getattr(doc_spec, item), 'ref'):
                                name_schema = getattr(getattr(doc_spec, item), 'ref').split('/')[-1]
                                OasService.compare_object(diff, getattr(code_spec, item),
                                                          root_doc_spec.components.schemas[name_schema],
                                                          root_doc_spec, root_code_spec,
                                                          root, name_parameter)
                            else:
                                name_schema = getattr(getattr(code_spec, item), 'ref').split('/')[-1]
                                OasService.compare_object(diff, root_code_spec.components.schemas[name_schema],
                                                          getattr(doc_spec, item),
                                                          root_doc_spec, root_code_spec,
                                                          root, name_parameter)
                    elif hasattr(doc_spec, 'items') and hasattr(code_spec, 'items') and \
                            getattr(doc_spec, 'items').path[:2] == ['components', 'schemas'] and \
                            len(getattr(doc_spec, 'items').path) \
                            == len(getattr(code_spec, 'items').path) == 3 and \
                            getattr(doc_spec, 'items').path[-1] \
                            != getattr(code_spec, 'items').path[-1]:
                        OasService.add_diff_object(diff, doc_spec.path, item, OasService.DIFFERENCE_STATUS,
                                                   getattr(doc_spec, 'items').path[-1],
                                                   getattr(code_spec, 'items').path[-1])
                        break
                    elif isinstance(getattr(doc_spec, item), Schema) and isinstance(getattr(code_spec, item), Schema) \
                            and getattr(doc_spec, item).path[:2] == ['components', 'schemas'] and \
                            len(getattr(doc_spec, item).path) \
                            == len(getattr(code_spec, item).path) == 3 and \
                            getattr(doc_spec, item).path[-1] \
                            != getattr(code_spec, item).path[-1]:
                        OasService.add_diff_object(diff, doc_spec.path, item, OasService.DIFFERENCE_STATUS,
                                                   getattr(doc_spec, item).path[-1], getattr(code_spec, item).path[-1])
                        break
                    else:
                        OasService.compare_object(diff, getattr(code_spec, item), getattr(doc_spec, item),
                                                  root_doc_spec, root_code_spec, root, name_parameter)
                # item: string / bool / int
                elif getattr(doc_spec, item) != getattr(code_spec, item):
                    if root == 'spec':
                        # print('|' * len(doc_spec.path), doc_spec.path, doc_spec.path[-3:], code_spec.path, item,
                        #       OasService.DIFFERENCE_STATUS, getattr(doc_spec, item), getattr(code_spec, item), name_parameter)
                        OasService.add_diff_object(diff, doc_spec.path, item, OasService.DIFFERENCE_STATUS,
                                                   getattr(doc_spec, item),
                                                   getattr(code_spec, item), name_parameter)
                        if doc_spec.path[-3:] == ['content', 'application/json', 'schema'] and item == 'title':
                            break

    @classmethod
    def add_diff_object(cls, diff, paths, key, validation_status, doc_value, code_value='',
                        name_different_parameter=""):
        if not isinstance(doc_value, str) and not isinstance(doc_value, list) and not isinstance(doc_value, bool) and \
                not isinstance(doc_value, int) and not isinstance(doc_value, float):
            doc_value = 'Class object'
        if key == 'in_':
            key = 'in'
        # if object is element of Parameter object
        if name_different_parameter != "":
            index_parameters = paths.index("parameters")
            # if miss/ redundancy, name = key and paths[-1] is string of integer
            if index_parameters == len(paths) - 2 and name_different_parameter == key:
                paths = paths[:-1]
            # difference then paths[-1] which is string of integer, is set by name_param
            else:
                paths[index_parameters + 1] = name_different_parameter

        if validation_status == OasService.DIFFERENCE_STATUS:
            if key in OasService.WARNING_PROPERTY_LIST:
                value_status = {
                    'spec': doc_value,
                    'real': code_value,
                    'severity': OasService.WARNING,
                    'validation_status': validation_status
                }
            else:
                value_status = {
                    'spec': doc_value,
                    'real': code_value,
                    'severity': OasService.ERROR,
                    'validation_status': validation_status
                }
        # miss or redundancy
        else:
            if validation_status == OasService.MISS_STATUS:
                spec = doc_value
                real = None
            # validation_status == OasService.REDUNDANCY_STATUS:
            else:
                spec = None
                real = doc_value
            if key in OasService.WARNING_PROPERTY_LIST:
                value_status = {
                    'spec': spec,
                    'real': real,
                    'severity': OasService.WARNING,
                    'validation_status': OasService.DIFFERENCE_STATUS
                }
            else:
                value_status = {
                    'spec': spec,
                    'real': real,
                    'severity': OasService.ERROR,
                    'validation_status': OasService.DIFFERENCE_STATUS
                }

        # change elements(api_path, method) of paths to one element "api method"
        if len(paths) < 3:
            return
        elif paths[2] in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
            paths[1] = paths[1] + " " + paths[2].upper()
            paths.pop(2)
        prev_diff = diff["difference"]
        for index in range(0, len(paths)):
            if paths[index] not in prev_diff.keys():
                remain_paths = paths[index + 1:]
                beside_value = {key: value_status}

                value_diff = {}
                for sub_path in remain_paths[::-1]:
                    value_diff = {sub_path: beside_value}
                    beside_value = value_diff
                prev_diff[paths[index]] = value_diff
                prev_diff = prev_diff[paths[index]]
                break
            prev_diff = prev_diff[paths[index]]
        if (index == len(paths) - 1) and (key not in prev_diff.keys()):
            prev_diff[key] = value_status

    @classmethod
    def add_miss_or_redundancy_object(cls, diff, paths, key, status):
        # change elements(api_path, method) of paths to one element "api method"
        if len(paths) >= 2 and paths[2] in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
            paths[1] = paths[1] + " " + paths[2].upper()
            paths.pop(2)

        value = {
            'validation_status': status,
            'description': 'No more detail!',
            "severity": OasService.WARNING
        }

        prev_diff = diff[status]
        for index in range(0, len(paths)):
            if paths[index] not in prev_diff.keys():
                remain_paths = paths[index + 1:]
                beside_value = {key: value}
                value_diff = {}
                for sub_path in remain_paths[::-1]:
                    value_diff = {sub_path: beside_value}
                    beside_value = value_diff
                prev_diff[paths[index]] = value_diff
                prev_diff = prev_diff[paths[index]]
                break
            prev_diff = prev_diff[paths[index]]
        if (index == len(paths) - 1) and (key not in prev_diff.keys()):
            prev_diff[key] = value

    @classmethod
    def print_class_object(cls, o, count=1):
        for item in o.__slots__:
            if item == 'dct':
                return
            if isinstance(getattr(o, item), Map):
                print('  ' * count, item, end=" ")
                print(type(getattr(o, item)), end=" ")
                print()
                for key, value in getattr(o, item).items():
                    print('  ' * (count + 1), key)
                    OasService.print_class_object(value, count + 2)
            elif isinstance(getattr(o, item), list) and getattr(o, item):
                print('  ' * count, item, end=" ")
                for value in getattr(o, item):
                    if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool) or isinstance(value,
                                                                                                                 float):
                        print('  ' * (count + 1), value)
                    else:
                        print(value)
                        OasService.print_class_object(value, count + 1)
            elif getattr(o, item) or isinstance(getattr(o, item), bool):
                if item.startswith('_'):
                    return
                print('  ' * count, item if item != 'in_' else 'in', end=" ")
                print(type(getattr(o, item)), end=" ")
                if hasattr(getattr(o, item), '__slots__'):
                    print()
                    OasService.print_class_object(getattr(o, item), count + 1)
                else:
                    print(getattr(o, item))

    @staticmethod
    def load_data(spec_parameter: str):
        # TODO: http with yaml, error parse json to yaml spec to object spec
        if 'http' in spec_parameter:
            with urllib.request.urlopen(spec_parameter) as response:
                try:
                    return yaml.safe_load(response)
                except yaml.YAMLError:
                    CLog.info(f"Could not open/read: {spec_parameter}. Make sure that input is path to local file "
                              f"(.yaml/ .yml/ .json) or url to yaml content!")
                    exit()
        elif '.yaml' in spec_parameter or '.yml' in spec_parameter:
            try:
                with open(spec_parameter) as f:
                    return yaml.safe_load(f.read())
            except OSError:
                CLog.info(f"Could not open/read file: {spec_parameter}. Make sure that input is path to local file "
                          f"(.yaml/ .yml/ .json) or url to yaml content!")
                exit()
        elif '.json' in spec_parameter:
            try:
                with open(spec_parameter, 'r') as f:
                    return json.loads(f.read())
            except OSError:
                CLog.info(f"Could not open/read file: {spec_parameter}. Make sure that input is path to local file "
                          f"(.yaml/ .yml/ .json) or url to yaml content!")
                exit()
        else:
            CLog.info("Failed to load data. Make sure that input is path to local file "
                      f"(.yaml/ .yml/ .json) or url to yaml content!")
            exit()


if __name__ == "__main__":
    oas_srv = OasService()
