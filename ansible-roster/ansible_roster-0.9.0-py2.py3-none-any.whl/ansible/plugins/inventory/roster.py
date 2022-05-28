import os
import re
import yaml

from copy import copy, deepcopy
from functools import wraps

import glob

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.utils.display import Display
from ansible.errors import AnsibleParserError

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
short_description: Host based yaml inventory.
requirements:
    - boltons
    - torxtools
    - exrex
    - cerberus
description:
    - Lorem Ipsum
options:
    plugin:
        description: The name of this plugin. It must always be set to 'roster' for this plugin to recognize it as it's own.
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
      merge_vars: *vars
      parents:
        type: list
        default: []
        schema: *group_name

labels:
  type: dict
  default: {}
  keysrules: &label_name
    type: string
    regex: '^[\w]+$'
  valuesrules:
    type: dict
    default: {}
    nullable: true
    schema:
      vars: *vars
      parents:
        type: list
        default: []
        schema: *label_name

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
      labels:
        type: list
        default: []
        schema: *label_name
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
            display.debug("roster inventory plugin ignoring '%s': wrong file extension" % path)
            return False

        # if file is called 'name.ext', then accept it without opening it
        if os.path.basename(path) in ["{}.{}".format(name, e) for e in ext]:
            display.debug("roster inventory plugin accepting '%s': exact file name match" % path)
            return True

        with open(path, "r") as fd:
            data = yaml.safe_load(fd)

        if data.get("plugin") == name:
            return True
        display.warning("roster inventory plugin ignoring '%s': no 'plugin: %s' key-value" % (path, name))
    except yaml.scanner.ScannerError as err:
        display.warning("syntax error %s: %s" % (str(err.problem_mark).strip(), err.problem))
    except Exception as err:
        display.warning("unknown exception: %s" % str(err))
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
            raise Exception(f"Range sequence [{first}:{second-1}] is invalid")

        fmt = "{:d}"
        if len(match[1]) > 1 and match[1][0] == "0":
            cnt = len(match[1])
            fmt = "{:0" + str(cnt) + "d}"

        rv = "(" + "|".join([str(fmt).format(x) for x in range(first, second)]) + ")"
        rv = exrex.simplify(rv)
        display.vvv(f"    Expand range sequence [{first}:{second-1}] with '{fmt}' format generates '{rv}'")
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
        display.vv("Generating %s hostnames from '%s'" % (count, hostname))
        if count > 1000:
            raise Exception(
                "error: extraction of the regex hostname '%s' would generate %s hostnames" % (hostname, count)
            )

        for hostname in exrex.generate(exrex_hostname):
            rv[hostname] = item

    return rv


def _validate_data(data=None):
    """
    Validate the yaml data against a known and valid schema.

    :param data: yaml data to validate
    :returns: {bool, data} True if valid, False if empty, Exception otherwise.
    """

    def visit(_path, key, _value):
        # drop all items that start with a dot ('.')
        if isinstance(key, str) and (key[0] == "."):
            return False
        return True

    if data is None:
        return False, None

    # drop the 'plugin' if present, it's not needed anymore
    data.pop("plugin", None)

    data = remap(data, visit=visit)
    validator = cerberus.Validator(schema)

    if not validator.validate(data):
        raise Exception(validator.errors)

    return True, data


@catch_recursion
def _include_file(filepath, data, display):
    """
    Recursivly include file and merge into data

    :param filepath: yaml file path to be read and included
    :param data: current data
    :param display: ansible display object
    :returns: merged data
    """
    display.vvv("including file '%s'" % filepath)
    with open(filepath, "r") as fd:
        try:
            new_data = yaml.safe_load(fd)
            rv, new_data = _validate_data(new_data)
        except Exception as err:
            # by default this error should be blocking.
            # - this means that if you checkout a repo with git crypt'ed files, then the plugin will choke on
            #   the binary file and not run with a potentially harmful or empty variable value.
            # - we should, in the future, support a envvar to disable the error and treat it as a warning since
            #   a carefuly crafted inventory could work perfectly with binary un-encrypted files it can't include.
            display.error("roster inventory plugin error while reading '%s': %s." % (filepath, str(err)))
            raise

    if not rv:
        return data

    data = dicttools.deepmerge(new_data, data, visit=dicttools.strip_none)
    return _recursive_include(data, display)


def _recursive_include(data, display):
    """
    Search for a yaml 'include' key, and include all files from this key

    :param: data dictionnary
    :param: display ansible display object
    :returns: dictionnary
    """
    if not data.get("include"):
        return data

    files = data.pop("include")
    for pathname in files:
        for f in glob.glob(pathname, recursive=True):
            data = _include_file(f, data, display)
    return data


class RosterInventory:
    def __init__(self, data, display):
        """
        Initialize inventory by going through all includes

        :param data: yaml data
        :param display: yaml ansible display object
        """
        self.display = display
        self._inventory = None

        self._data = deepcopy(data)
        self._settings = self._data.pop("settings", None)

        self._data = _recursive_include(self._data, display)

    def validate_schema(self):
        """
        Validate the yaml data against a known and valid schema.

        :returns: True if valid, False if empty, Exception otherwise.
        """
        self.display.vv("Validating schema")
        rv, data = _validate_data(self._data)
        if not rv:
            return False

        self._data = data
        return True

    def _validate_groups(self):
        """
        Validate and fixup all group hosts. If invalid,
        ignore and handle the error elsewhere.
        If a group pre-declaration is missing, warn and create.
        """
        self.display.vv("Validating groups")

        def fill_in(root_groups):
            for groupname, group in root_groups.items():
                if "parents" not in group:
                    group["parents"] = []
                if "vars" not in group:
                    group["vars"] = {}

        for groupname, group in self._root_groups.items():
            if group is None:
                self._root_groups[groupname] = {}

        fill_in(self._root_groups)
        for groupname, group in copy(self._root_groups).items():
            for parentname in group["parents"] or []:
                if parentname not in self._root_groups:
                    self.display.warning(
                        "Group '%s' in group '%s' is not declared in root 'groups'" % (parentname, groupname)
                    )
                    self._root_groups[parentname] = {}
                pass
        fill_in(self._root_groups)

    def _validate_hosts(self):
        """
        Validate and fixup all root hosts. If invalid,
        ignore and handle the error elsewhere.
        If a group pre-declaration is missing, warn and create.
        """
        self.display.vv("Validating hosts")
        # for every host, warn if group does not yet exist
        # if host is not set, ignore and error will be handled elsewhere
        for hostname, host in self._root_hosts.items():
            if host is None:
                self._root_hosts[hostname] = {}

        for hostname, host in self._root_hosts.items():
            if "groups" not in host:
                host["groups"] = []
            if "vars" not in host:
                host["vars"] = {}
            for groupname in host["groups"]:
                if groupname not in self._root_groups:
                    self.display.warning(
                        "Group '%s' in host '%s' is not declared in root 'groups'" % (groupname, hostname)
                    )
                    self._root_groups[groupname] = {}
                pass

    def parse(self, inventory, _display):
        """
        :params inventory: An InventoryData object
        :params display: An InventoryData object
        :returns: Inventory passed as params
        """
        # discard any invalid files with no hosts
        if not self._data.get("hosts"):
            raise AnsibleParserError("Inventory file has no hosts declared")

        self._roster = self._data
        self._inventory = inventory

        # for every group, and host, add it to it's list
        self._root_hosts = self._roster.get("hosts") or {}
        self._root_groups = self._roster.get("groups") or {}
        self._validate_hosts()
        self._validate_groups()

        self.display.vv("Adding global variables")
        self._add_item_vars(name="all", content=self._roster)

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
            "funcs": [self._add_item, self._add_item_labels, self._add_item_subgroups, self._add_item_host_vars],
            "add_fn": self._inventory.add_host,
            "subgroups_keyname": "groups",
            "subgroups_msg": "Group '%s' for host '%s' not declared in root groups",
        })
        # fmt: on

        # call reconcile to ensure "ungrouped" contains all hosts
        self.display.vv("Reconciling inventory")
        self._inventory.reconcile_inventory()
        return self._inventory

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
        # if there's no groups in host, just call the default function
        if "groups" not in content:
            return self._add_item_vars(name, content)

        if "vars" not in content:
            content["vars"] = {}

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
                if not group["merged"]:
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
            v["merged"] = False

        complete = False
        while not complete:
            complete = True

            for group_name, group in self._root_groups.items():
                if group["merged"]:
                    continue
                complete = False
                if not are_all_parents_merged(group):
                    continue
                group["merged"] = True

                # make a list of all keys that are lists:
                list_keys = self.get_parent_list_keys(group, "parents")
                if not list_keys:
                    continue

                # for every key, append them all together
                for key in list_keys:
                    self._root_groups[group_name]["vars"][key] = merge_all_list_key_values(group)

    @catch_recursion
    def _add_item_label(self, name, label_name):
        if not self._roster.get("labels") or not self._roster["labels"].get(label_name):
            self.display.warning("Label named '%s' for host '%s' is not declared in root 'labels'" % (label_name, name))
            return

        label = self._roster["labels"][label_name]
        for label_name in label.get("parents") or []:
            self._add_item_label(name, label_name)

        # add the labels's variables to this host
        self._add_item_vars(name, content=label)

    def _add_item_labels(self, name, content, sublabels_name="labels", **_kwargs):
        if not content:
            return
        for label_name in content.get(sublabels_name) or []:
            self._add_item_label(name, label_name)

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
                "error: missing Python3 dependencies. Please install the following Python3 modules: boltons torxtools exrex cerberus"
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
        r = RosterInventory(loader.load_from_file(path, cache=False) or {}, display)

        display.debug("Validating roster schema (%s)" % (path))
        r.validate_schema()

        display.debug("Converting roster schema (%s)" % (path))
        inventory = r.parse(inventory, display)
