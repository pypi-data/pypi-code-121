"""
A class to provide available packages as DAG structure. 

In reality, the structure is just two levels deep: **hosts** and **plugins**. DCCs such as **Maya** and
**Cinema4D** are top-level host packages. Renderers and other plugins are children of those hosts.
Methods are provided to traverse the tree to find packages by name, version, platform and so on. 

If you are writing submission tools there's no need to create a Package tree directly.
It is recommended to use the singleton module: [ciocore.data](/developer/ciocore/data/). The only
functions you should need from this module are: [supported_host_names()](#supported_host_names) and [supported_plugins()](#supported_plugins)
"""

import copy
import json

from ciocore.package_environment import PackageEnvironment

WINDOWS = "windows"
LINUX = "linux"

#: The set of supported platforms, currently windows and linux.
PLATFORMS = {WINDOWS, LINUX}


def to_name(pkg):
    """
    Generate Name like `houdini 16.5.323 linux` or `maya 2016.SP3 linux`.

    This name is derived from the product and version fields in a package. Note: It is not
    necessarily possible to go the other way and extract version fields from the name..

    Arguments:

    * **`pkg`** -- An object with product, platform , and all version fields.

    Returns:

    * The package name.

    ???+ example
        ``` python

        from ciocore import api_client, package_tree
        packages = api_client.request_software_packages()
        package_tree.to_name(packages[0])

        # Result:
        # redshift-maya 3.0.64 linux

        ```
    """

    version_parts = [
        pkg["major_version"],
        pkg["minor_version"],
        pkg["release_version"],
        pkg["build_version"],
    ]
    version_string = (".").join([p for p in version_parts if p])
    if pkg["platform"] not in PLATFORMS:
        raise KeyError("Invalid platform: {}".format(pkg["platform"]))
    return " ".join(filter(None, [pkg["product"], version_string, pkg["platform"]]))


def _build_tree(packages, package):
    """Build a tree of dependent software plugins.

    Add a children key, and For each ID in the `plugins` key, add the package to which it refers to
    children. Recurse until no more plugins are left.
    """

    for child_id in package.get("plugins", []):
        child_package = next((c for c in packages if c["package_id"] == child_id), None)
        if child_package:
            child_package = _build_tree(packages, child_package)
            package["children"].append(child_package)
    package.pop("plugins", None)
    return package




def _find_by_name(branch, name, limit=None, depth=0):
    """Given a name made by `to_name` find the package.

    Name is typically part of a path. Limit will limit the search depth and is useful when you know
    the package should be a direct child and not any descndent.
    """
    if not branch:
        return None

    if  branch.get("product") and name == to_name(branch):
        return branch
    depth += 1

    if (not limit) or depth <= limit:
        for child_branch in branch["children"]:
            result = _find_by_name(child_branch, name, limit, depth)
            if result:
                return result
    return None


def _find_by_path(tree, path):
    """Find the package uniquely described by this path.

    This method loops through parts of the path name and searches the tree for each part.  When it
    finds a matching package, we use that package as the root of the tree for the next search. As we
    are searching for an exact path match, we limit the search to one level deep each time.
    """

    if not path:
        return None


    result = None
    for name in [p for p in path.split("/") if p]:
        tree = _find_by_name(tree, name, 1)
        result = tree
    return result


def _to_path_list(tree, **kw):
    """Get paths to all nodes.

    This means starting at the level of the given tree, get all the paths to intermediate and leaf
    nodes. This is useful for populating a chooser to choose packages fully qualified by path.
    Houdini's tree widget for example, takes the below format unchanged and generates the
    appropriate UI. 

    * 'houdini 16.0.736 linux'
    * 'houdini 16.0.736 linux/arnold-houdini 2.0.1 linux'
    * 'houdini 16.0.736 linux/arnold-houdini 2.0.1 linux/al-shaders 1.0 linux'
    """
    parent_name = kw.get("parent_name", "")
    paths = kw.get("paths", [])

    for child_tree in tree["children"]:
        name = ("/").join([n for n in [parent_name, to_name(child_tree)] if n])
        paths.append(name)
        paths = _to_path_list(child_tree, paths=paths, parent_name=name)
    return paths


def _clean_package(package):
    """Remove some unwanted keys.

    TODO - Some of these may turn out to be wanted after all.
    """
    pkg = copy.deepcopy(package)
    for att in [
        "build_id",
        "time_updated",
        "description",
        "updated_at",
        "time_created",
        "plugin_hosts",
        "relative_path",
    ]:
        pkg.pop(att, None)

    pkg["children"] = []
    return pkg


class PackageTree(object):
    def __init__(self, packages,  *host_products, **kwargs):
        """
        Build the tree with a list of packages.

        Arguments:

        * **`packages`** -- List of packages direct from the [Conductor packages
        endpoint](https://dashboard.conductortech.com/api/v1/ee/packages).
      
      
        * **`*host_products`** -- Filter the tree to contain only top-level host packages of
        products specified in this list and their plugins. If there are no host_products specified,
        and the product keyword is omitted, the tree contains all packages.

        Keyword Arguments:

        * **`product`** -- Build the tree from versions of a single product and its compatible
            plugins -- Defaults to `None`, in which case the tree is built from all packages. It is
            an error to specify both host_products and product. If a nonexistent product is given,
            the PackageTree is empty. By specifying `product`, you can build the object based on a
            single plugin product.
        * **`platforms`** -- Build the tree from versions for a specific platform -- Defaults to the
          set `{"linux", "windows"}`.

        Raises:

        * **`KeyError`** -- An invalid platform was provided.
        * **`ValueError`** --  Cannot choose both product and host_products.


        ???+ example
            ``` python

            from ciocore import api_client, package_tree

            # Request packages as a flat list from Conductor.
            packages = api_client.request_software_packages()

            # Build tree of dependencies from packages list
            pt = package_tree.PackageTree(packages, "cinema4d", "maya-io")
            for path in pt.to_path_list():
                print(path)

            # Result
            # cinema4d 22.118.RB320081 linux
            # cinema4d 22.118.RB320081 linux/redshift-cinema4d 3.0.43 linux
            # cinema4d 22.118.RB320081 linux/redshift-cinema4d 3.0.45 linux
            # maya-io 2022.SP3 linux
            # ...
            ```
        """

        platforms = kwargs.get("platforms",PLATFORMS)
        product=kwargs.get("product")

        unknown_platforms = set(platforms) - PLATFORMS
        if unknown_platforms:
            raise KeyError("Unrecognized platform {}".format(" ".join(unknown_platforms)))

        if product and host_products:
            raise ValueError("You cannot choose both product and host_products.")

        packages = [_clean_package(p) for p in packages if p["platform"] in platforms]

        root_ids = [] 
        if product:
             root_ids = [p["package_id"] for p in packages if p["product"] == product]
        else:
            for p in packages:
                if not p["plugin_host_product"]:
                    if p["product"] in host_products or not host_products:
                        root_ids.append(p["package_id"])

        self._tree = _build_tree(packages, {"children": [], "plugins": root_ids})

    def find_by_name(self, name, limit=None):
        """
        Search the tree for a product with the given name.

        Arguments:

        * **`name`** -- This name is the name originally constructed from the package using
          to_name(). It must be an exact match with product, version, platform.
          For example: `maya 2018.0 windows`

        Keyword Arguments:

        * **`limit`** -- Limit the search depth -- Defaults to `None`.

        Returns:

        * The package that matches.

        ???+ example
            ``` python

            from ciocore import api_client, package_tree
            packages = api_client.request_software_packages()

            pt = package_tree.PackageTree(packages, product="cinema4d")
            pt.find_by_name("redshift-cinema4d 3.0.64 linux")

            # Result:
            # {
            #     'platform': 'linux',
            #     'plugin_host_product': 'cinema4d',
            #     'product': 'redshift-cinema4d',
            #     'major_version': '3',
            #     'release_version': '64',
            #     'vendor': 'maxon',
            #     'children': [],
            #     ...
            # }
            ```
        """

        return _find_by_name(self._tree, name, limit, 0)

    def find_by_path(self, path):
        """
        Find the package uniquely described by the given path.

        The path is of the form returned by the to_path_list() method.

        Arguments:

        * **`path`** -- The path

        Returns:

        * The package or None if no package exists with the given path.

        ???+ example
            ``` python

            from ciocore import api_client, package_tree, package_environment
            packages = api_client.request_software_packages()
            pt = package_tree.PackageTree(packages, product="cinema4d")
            pt.find_by_path("cinema4d 24.111 linux/redshift-cinema4d 3.0.62 linux")

            # Result:
            # {
            #     'platform': 'linux',
            #     'plugin_host_product': 'cinema4d',
            #     'product': 'redshift-cinema4d',
            #     'major_version': '3',
            #     'release_version': '62',
            #     'vendor': 'maxon',
            #     'children': [],
            #     'plugin_host_version': "24",
            #     ...
            # }
            ```
        """

        return _find_by_path(self._tree, path)

 
    def to_path_list(self, name=None):
        """
        Get paths to all nodes.
        
        This is useful for populating a chooser to choose packages fully qualified by path.
        Houdini's tree widget for example, takes the below format unchanged and generates the
        appropriate UI. 

        Keyword Arguments:

        * **`name`** -- Get paths below the tree represented by the name. -- Defaults to `None` (root node).

        Returns:

        * _description_.

        ???+ example
            ``` python

            from ciocore import api_client, package_tree
            packages = api_client.request_software_packages()
            pt = package_tree.PackageTree(packages, product="cinema4d")

            pt.to_path_list()
            # Result:
            # cinema4d 22.118.RB320081 linux
            # cinema4d 22.118.RB320081 linux/redshift-cinema4d 3.0.43 linux
            # cinema4d 22.118.RB320081 linux/redshift-cinema4d 3.0.45 linux
            # cinema4d 22.118.RB320081 linux/redshift-cinema4d 3.0.22 linux
            # cinema4d 22.118.RB320081 linux/arnold-cinema4d 3.3.2.100 linux
            ...

            pt.to_path_list(name="cinema4d 24.111 linux")
            # Result:
            # redshift-cinema4d 3.0.57 linux
            # redshift-cinema4d 3.0.62 linux
            # redshift-cinema4d 3.0.45 linux
            # redshift-cinema4d 3.0.64 linux


            ```
        """
        if name:
            subtree = self.find_by_name(name)
            return _to_path_list(subtree)
        return _to_path_list(self._tree)

    def platforms(self):
        """
        Get the set of platforms represented by packages in the tree.

        Returns a set.
        """

        # No need to recurse. Plugins are assumed to be compatible with the host.
        return set([host["platform"] for host in self._tree["children"]])

    def json(self):
        """
        The whole tree as json.

        Returns:

        * JSON object.

        """
        return json.dumps(self._tree)

    def __bool__(self):
        return True if self._tree["children"] else False

    def __nonzero__(self):
        # Python 2.7
        return self.__bool__()

    def as_dict(self):
        """
        Returns:

        * The underlying dictionary.

        """
        return self._tree

    def supported_host_names(self):
        """
        All host names from the software tree.

        These names can be used to populate a dropdown menu. Then a single selection from that menu
        can be used to retrieve the complete package in order to generate an environment dictionary
        and get package IDs.

        Returns:

        * A list of fully qualified DCC hosts of the form: `product`, `version`, `platform`.

        ???+ example
            ``` python

                from ciocore import api_client, package_tree
                packages = api_client.request_software_packages()
                pt = package_tree.PackageTree(packages,
                product="cinema4d")

                pt.supported_host_names()

                # Result:
                # cinema4d 21.209.RB305619 linux
                # cinema4d 22.116.RB316423 linux
                # cinema4d 22.118.RB320081 linux
                # cinema4d 23.110.RB330286 linux
                # cinema4d 24.111 linux
                # cinema4d 24.111 windows

            ```
        """

        paths = []
        for pkg in self._tree["children"]:
            paths.append(to_name(pkg))
        return sorted(paths)

    def supported_plugins(self, host):
        """
        Find the plugins that are children of the given DCC host.

        The result does not contain platform information since we assume that plugins are compatible with the DCC host that was used to
        request them.

        Arguments:

        * **`host`** -- Name of the DCC host, typically one of the entries returned by supported_host_names().

        Returns:

        * A list of dictionaries, where each entry contains a plugin product and a list of versions.

        ???+ example
            ``` python

            from ciocore import api_client, package_tree packages =
            api_client.request_software_packages() pt = package_tree.PackageTree(packages,
            product="cinema4d")
            name = pt.supported_host_names()[0]

            pt.supported_plugins(name)
            # Result:
            #
            # [
            #     {
            #         "plugin": "arnold-cinema4d",
            #         "versions": [
            #             "3.3.2.100",
            #             "3.3.3.0"
            #         ]
            #     },
            #     {
            #         "plugin": "redshift-cinema4d",
            #         "versions": [
            #             "2.6.54",
            #             "2.6.56",
            #             "3.0.21",
            #             "3.0.22",
            #         ],
            #     },
            # ]

            ```
        """

        try:
            subtree = self.find_by_name(host)
            plugin_versions = _to_path_list(subtree)
        except TypeError:
            return []

        if not plugin_versions:
            return []

        plugin_dict = {}
        for plugin, version, _ in [pv.split(" ") for pv in plugin_versions]:
            if plugin not in plugin_dict:
                plugin_dict[plugin] = []
            plugin_dict[plugin].append(version)

        # convert to list so it can be sorted
        plugins = []
        for key in plugin_dict:
            plugins.append({"plugin": key, "versions": sorted(plugin_dict[key])})

        return sorted(plugins, key=lambda k: k["plugin"])
