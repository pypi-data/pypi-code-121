import os
import re
import sys

from copy import copy, deepcopy
from functools import wraps

import glob
import yaml

from ansible.cli.inventory import INTERNAL_VARS
from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.utils.display import Display

try:
    from boltons.iterutils import remap
    from torxtools import dicttools
    import exrex
    import cerberus

    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False


display = Display()


__metaclass__ = type

DOCUMENTATION = r"""
name: roster
plugin_type: inventory
authors:
  - Julien Lecomte (julien@lecomte.at)
short_description: 'Roster is an Ansible yaml inventory plugin with focus on groups applied to hosts.'
requirements:
  - boltons
  - cerberus
  - exrex
  - torxtools
description:
  - 'Roster is an Ansible inventory plugin with focus on groups applied to hosts instead of hosts included in groups. It supports ranges (eg: "[0:9]"), regex hostnames (eg: "(dev|prd)-srv"), file inclusions, and variable merging.'
options:
  plugin:
    description: Required field that must always be set to 'roster' for this plugin to recognize it as it's own.
    type: str
    required: true
    choices:
      - roster
"""

EXAMPLES = """
---
# roster.yml
plugin: roster
"""

SCHEMA = r"""
---
include:
  type: list
  default: []
  schema:
    type: string

vars: &vars
  type: dict
  default: {}
  keysrules:
    type: string
    # source: VALID_VAR_REGEX from ansible/playbook/conditional.py
    regex: '^[_A-Za-z]\w*$'

groups:
  type: dict
  default: {}
  keysrules: &group_name
    type: string
    # source: _SAFE_GROUP from somewhere
    regex: '^[_A-Za-z]\w*$'
  valuesrules:
    type: dict
    default: {}
    nullable: true
    schema:
      vars: *vars
      parents:
        type: list
        default: []
        schema: *group_name

hosts:
  type: dict
  default: {}
  keysrules:
    type: string
    # Accept almost anything and validate later
    regex: '^\S+$'
  valuesrules:
    type: dict
    default: {}
    nullable: true
    schema:
      vars: *vars
      groups:
        type: list
        default: []
        schema: *group_name
"""
schema = yaml.safe_load(SCHEMA)

# match a 'flat' part of hostname, that is without [], ()
flat_name_re = re.compile(r"^([^\[\(]+)")

# match a simple char class
range_seq_re = re.compile(r"^(\[(?:\d+:\d+)\])")
range_seq_parts = re.compile(r"^\[(\d+):(\d+)\]$")

# match a group
group_class_re = re.compile(r"^(\((?:[^\)\s]+)\))")

# catch recursions
kwd_mark = object()


def catch_recursion(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (func.__qualname__,) + args + (kwd_mark,) + tuple(sorted(kwargs.items()))

        if key in catch_recursion.func_list:
            raise Exception("Recursive infinite dependency loop detected.")
        catch_recursion.func_list.append(key)
        rv = func(*args, **kwargs)
        catch_recursion.func_list.remove(key)
        return rv

    return wrapper


catch_recursion.func_list = []


# ------------------------------------------------------------------------------
# Libary part
def verify_roster(path, display, ext=None):
    """
    Verify if file is usable by this plugin.
    To be accepted by this plugin, file must be a yaml file and contain:

    ~~~yaml
    ---
    plugin: *name*
    ~~~

    :param path: file path
    :param display: Ansible display object
    :returns: True if file is accepted
    """
    name = "roster"
    if not ext:
        ext = ["yml", "yaml"]

    try:
        lpath = path.lower()
        if not lpath.endswith(tuple([".{}".format(e.lower()) for e in ext])):
            display.debug(f"Roster inventory plugin ignoring '{path}': wrong file extension")
            return False

        # if file is called 'roster.yml', then accept it without opening it
        if os.path.basename(path) in ["{}.{}".format(name, e) for e in ext]:
            display.debug(f"Roster inventory plugin accepting '{path}': exact file name match")
            return True

        with open(path, "r") as fd:
            data = yaml.safe_load(fd)

        if data.get("plugin") == name:
            return True
        display.warning("Roster inventory plugin ignoring '%s': no 'plugin: %s' key-value" % (path, name))
    except yaml.scanner.ScannerError as err:
        display.warning("Syntax error %s: %s" % (str(err.problem_mark).strip(), err.problem))
    except Exception as err:
        display.warning("Unknown exception: %s" % str(err))
    return False


# ------------------------------------------------------------------------------
# Roster main part
def _recompose_host(hostname, display):
    # convert foo[0-9]bar into parts, eg: foo, [0-9], and bar
    # we'll only exrex the regex'y parts
    #
    # The point being desktop[0-9].example.com should be treated as desktop[0-9]\.example\.com
    # There's probably a much easier way
    #
    # Convert range to regex
    def convert_range_to_regex(value, display):
        match = range_seq_parts.fullmatch(value)
        first = int(match[1])
        second = int(match[2]) + 1

        if first >= second:
            raise Exception(f"Range sequence [{first}:{second}] is invalid")

        fmt = "{:d}"
        if len(match[1]) > 1 and match[1][0] == "0":
            cnt = len(match[1])
            fmt = "{:0" + str(cnt) + "d}"

        rv = "(" + "|".join([str(fmt).format(x) for x in range(first, second)]) + ")"
        rv = exrex.simplify(rv)
        display.vvv(f"    Expand range sequence [{first}:{second}] with '{fmt}' format generates '{rv}'")
        return rv

    rv = []

    original = hostname
    display.vv(f"Splitting hostname = '{hostname}' via exrex...")
    while hostname:
        display.vvv(f"  Current hostname = '{hostname}'")
        for what in [
            [flat_name_re, "plain", re.escape],
            [range_seq_re, "range", lambda x: convert_range_to_regex(x, display)],
            [group_class_re, "group", lambda x: x],
        ]:
            match = what[0].match(hostname)
            if bool(match):
                part = match[0]
                display.vvv("    Found %s section '%s'" % (what[1], part))
                rv.append(what[2](part))
                hostname = hostname[len(part) :]
                break
        else:
            raise Exception(f"Failed to recompose range sequence or regex from '{original}'")

    return "".join(rv)


def _split_hosts(hosts, display):
    """
    split hosts if we find a regex
    """

    def is_regex(k):
        return "(" in k or "[" in k

    split_required = [True for k, _ in hosts.items() if is_regex(k)]
    if not split_required:
        return hosts

    rv = {}
    for hostname, item in hosts.items():
        if not is_regex(hostname):
            rv[hostname] = item
            continue

        exrex_hostname = _recompose_host(hostname, display)
        # split with exreg
        count = exrex.count(exrex_hostname)
        display.vv(f"Generating {count} hostnames from '{hostname}'")
        if count > 1000:
            raise Exception(f"Extraction of the regex hostname '{hostname}' would generate {count} hostnames")

        for hostname in exrex.generate(exrex_hostname):
            rv[hostname] = item

    return rv


def _validate_reserved_keyword(name):
    if name not in INTERNAL_VARS:
        return
    raise Exception(f"Ansible reserved keyword '{name}' is used as a variable name in playbook.")


def _validate_data(data):
    """
    Validate the yaml data against a known and valid schema.

    :param data: yaml data to validate
    :returns: data, Exception otherwise.
    """

    def visit(_path, key, _value):
        # drop all items that start with a dot ('.')
        if isinstance(key, str) and (key[0] == "."):
            return False
        return True

    if data is None:
        return

    # drop the 'plugin' if present, it's not needed anymore
    data.pop("plugin", None)

    data = remap(data, visit=visit)
    validator = cerberus.Validator(schema)

    if not validator.validate(data):
        raise Exception("YAML schema validation error: " + str(validator.errors))

    # Fill in missing parts
    if not data.get("vars"):
        data["vars"] = {}
    for k, _ in data["vars"].items():
        _validate_reserved_keyword(k)

    if not data.get("hosts"):
        data["hosts"] = {}
    for host in data["hosts"]:
        _validate_reserved_keyword(host)
        if not data["hosts"].get(host):
            data["hosts"][host] = {}
        if not data["hosts"][host].get("vars"):
            data["hosts"][host]["vars"] = {}
        if not data["hosts"][host].get("groups"):
            data["hosts"][host]["groups"] = []
        for k, _ in data["hosts"][host]["vars"].items():
            _validate_reserved_keyword(k)

    if not data.get("groups"):
        data["groups"] = {}
    for group in data["groups"]:
        _validate_reserved_keyword(group)
        if not data["groups"].get(group):
            data["groups"][group] = {}
        if not data["groups"][group].get("vars"):
            data["groups"][group]["vars"] = {}
        if not data["groups"][group].get("parents"):
            data["groups"][group]["parents"] = []
        for k, _ in data["groups"][group]["vars"].items():
            _validate_reserved_keyword(k)

    return data


@catch_recursion
def _include_file(filepath, data, source_path, display):
    """
    Recursivly include file and merge into data

    :param filepath: yaml file path to be read and included
    :param data: current data
    :param display: ansible display object
    :returns: merged data
    """
    display.vvv(f"Roster including file '{filepath}'")
    try:
        with open(filepath, "r") as fd:
            new_data = yaml.safe_load(fd)
            new_data = _validate_data(new_data)

    except Exception as err:
        # by default this error should be blocking.
        # - this means that if you checkout a repo with git crypt'ed files, then the plugin will choke on
        #   the binary file and not run with a potentially harmful or empty variable value.
        raise Exception("While reading '%s': %s." % (filepath, to_native(err)))

    retval = dicttools.deepmerge(new_data, data, visit=dicttools.strip_none)
    return _recursive_include(retval, source_path, display)


def _recursive_include(data, source_path, display):
    """
    Search for a yaml 'include' key, and include all files from this key

    :param: data dictionnary
    :param: display ansible display object
    :returns: dictionnary
    """
    if not data.get("include"):
        return data

    includes = data.pop("include")
    for pathname in includes:
        searchpath = pathname
        if not os.path.isabs(searchpath):
            searchpath = os.path.join(source_path, searchpath)

        files = glob.glob(searchpath, recursive=True)
        if not files:
            # if escaped version is the same, then pathname didn't contain wildcards
            if glob.escape(searchpath) == searchpath:
                raise AnsibleParserError(f"Include file not found: '{pathname}'")
            else:
                display.warning(f"No include files found in path: '{pathname}'")
        else:
            for f in files:
                data = _include_file(f, data, source_path, display)
    return data


class RosterInventory:
    def __init__(self, data, path, display, inventory):
        """
        Initialize inventory by going through all includes

        :param data: yaml data
        :param display: yaml ansible display object
        """
        self.display = display
        self._inventory = inventory
        self._source_path = os.path.dirname(path)

        self._data = deepcopy(data)

        self._data = _recursive_include(self._data, self._source_path, display)
        self._data = _validate_data(self._data)

    def _validate_groups(self):
        """
        Validate and fixup all group hosts. If invalid,
        ignore and handle the error elsewhere.
        If a group pre-declaration is missing, warn and create.
        """
        self.display.vv("Validating groups")
        for groupname, group in copy(self._root_groups).items():
            for parentname in group["parents"] or []:
                if parentname not in self._root_groups:
                    self.display.warning(
                        f"Group '{parentname}' in group '{groupname}' is not declared in root 'groups'"
                    )
                    self._root_groups[parentname] = {"vars": {}, "parents": []}

    def _validate_hosts(self):
        """
        Validate and fixup all root hosts. If invalid,
        ignore and handle the error elsewhere.
        If a group pre-declaration is missing, warn and create.
        """
        self.display.vv("Validating hosts")
        # for every host, warn if group does not yet exist
        for hostname, host in self._root_hosts.items():
            for groupname in host["groups"]:
                if groupname not in self._root_groups:
                    self.display.warning(f"Group '{groupname}' in host '{hostname}' is not declared in root 'groups'")
                    self._root_groups[groupname] = {"vars": {}, "parents": []}

    def parse(self):
        # discard any invalid files with no hosts
        if not self._data.get("hosts"):
            raise AnsibleParserError("Inventory file has no hosts declared")

        self._root_hosts = self._data["hosts"]
        self._root_groups = self._data["groups"]
        self._validate_hosts()
        self._validate_groups()

        self.display.vv("Adding global variables")
        self._add_item_vars(name="all", content=self._data)
        self.display.vv("Splitting host ranges and regex")
        self._root_hosts = _split_hosts(self._root_hosts, self.display)

        self.display.vv("Merging group variables")
        self._merge_group_list_vars()

        # fmt: off
        self.display.vv("Call group methods")
        self._call_methods(self._root_groups, {
            "funcs": [self._add_item, self._add_item_vars, self._add_item_subgroups],
            "add_fn": self._inventory.add_group,
            "subgroups_keyname": "parents",
            "subgroups_msg": "Parent group '%s' in '%s' not declared in root groups",
        })

        self.display.vv("Call host methods")
        self._call_methods(self._root_hosts, {
            "funcs": [self._add_item, self._add_item_subgroups, self._add_item_host_vars],
            "add_fn": self._inventory.add_host,
            "subgroups_keyname": "groups",
            "subgroups_msg": "Group '%s' for host '%s' not declared in root groups",
        })
        # fmt: on

        # call reconcile to ensure "ungrouped" contains all hosts
        self.display.vv("Reconciling inventory")
        self._inventory.reconcile_inventory()

    def _call_methods(self, source, method):
        """
        for every item in source, call everyfunction, one by one
        from method.funcs
        """
        for name, content in source.items():
            for fn in method.get("funcs", []):
                fn(name=name, content=content, method=method)

    def _add_item(self, name, method, **_kwargs):
        """
        adds the item by calling the methods' 'add_fn'
        :params name item to add
        :params method structure containing 'add_fn'
        """
        method["add_fn"](name)

    def _add_item_vars(self, name, content, **_kwargs):
        """
        Add key, value contents of the 'vars' key to the inventory
        replacing previous value, or, in the case of a list,
        appending to it.
        """
        if not (content or {}).get("vars"):
            return

        for k, v in content["vars"].items():
            self._inventory.set_variable(name, k, v)

    def _add_item_host_vars(self, name, content, **_kwargs):
        """
        Add key, value contents of the 'vars' key to the inventory
        replacing previous value, or, in the case of a list,
        appending to it.
        """
        # make a list of all keys that are lists:
        merge_keys = self.get_parent_list_keys(content, "groups")
        if not merge_keys:
            return self._add_item_vars(name, content)

        # Remove keys that are specified in vars
        for k, _v in content["vars"].items():
            if k in merge_keys:
                merge_keys.remove(k)

        for k in merge_keys:
            for parent_name in content["groups"]:
                # for the first item, we need to create the array
                if k in self._root_groups[parent_name]["vars"]:
                    if k not in content["vars"]:
                        content["vars"][k] = []
                    content["vars"][k] += self._root_groups[parent_name]["vars"][k]

        for k, v in content["vars"].items():
            self._inventory.set_variable(name, k, v)

    def get_parent_list_keys(self, group, keyname):
        """
        returns an array of keynames of variables that are lists and
        used in parent groups and itself.
        """
        retval = []
        # this group keys
        for k, v in group["vars"].items():
            if isinstance(v, list) and k not in retval:
                retval += [k]

        # all the parents
        for parent_name in group[keyname]:
            parent = self._root_groups[parent_name]
            for k, v in parent["vars"].items():
                if isinstance(v, list) and k not in retval:
                    retval += [k]
        return sorted(retval)

    def _merge_group_list_vars(self, **_kwargs):
        """
        merge values to every identical key from content['parents']
        """
        root_groups = self._root_groups

        def are_all_parents_merged(group):
            for parent_name in group["parents"]:
                group = root_groups[parent_name]
                if not group["__merged"]:
                    return False
            return True

        def merge_all_list_key_values(group):
            retval = []
            for parent_name in group["parents"]:
                parent = root_groups[parent_name]
                if key in parent["vars"]:
                    retval += parent["vars"][key]
            if key in group["vars"]:
                retval += group["vars"][key]
            return retval

        # start
        for _k, v in self._root_groups.items():
            v["__merged"] = False

        complete = False
        while not complete:
            complete = True

            for group_name, group in self._root_groups.items():
                if group["__merged"]:
                    continue
                complete = False
                if not are_all_parents_merged(group):
                    continue
                group["__merged"] = True

                # make a list of all keys that are lists:
                list_keys = self.get_parent_list_keys(group, "parents")
                if not list_keys:
                    continue

                # for every key, append them all together
                for key in list_keys:
                    self._root_groups[group_name]["vars"][key] = merge_all_list_key_values(group)
            else:
                # the Ansible inventory will catch the group infinite loop
                break

    def _add_item_subgroups(self, name, content, method):
        if not content:
            return
        for group in content.get(method["subgroups_keyname"], []):
            if group not in self._root_groups:
                self.display.warning(method["subgroups_msg"] % (group, name))
            self._inventory.add_group(group)
            self._inventory.add_child(group, name)


# ------------------------------------------------------------------------------
# Plugin part
class InventoryModule(BaseInventoryPlugin):
    """
    Host inventory parser for roster.yml source
    """

    NAME = "julien_lecomte.roster.roster"

    def __init__(self):
        super(InventoryModule, self).__init__()

        if not HAS_DEPENDENCIES:
            raise AnsibleParserError(
                "Missing Python3 dependencies. Please install the following Python3 modules: boltons cerberus exrex torxtools"
            )

    def verify_file(self, path):
        """
        Verify if file is usable by this plugin.
        To be accepted by this plugin, file must be a yaml file and contain:

        ~~~yaml
        ---
        plugin: roster
        ~~~

        :param path: file path
        :returns: True if file is accepted
        """
        # we expect a yaml file, with 'plugin: roster'
        return verify_roster(path, display=display)

    def parse(self, inventory, loader, path, cache=True):
        try:
            display.debug("Loading roster schema (%s)" % (path))
            r = RosterInventory(loader.load_from_file(path, cache=False) or {}, path, display, inventory)

            display.debug("Converting roster schema (%s)" % (path))
            r.parse()

        except Exception as err:
            display.error(f"Roster inventory plugin error: {err}")
            sys.exit(1)
