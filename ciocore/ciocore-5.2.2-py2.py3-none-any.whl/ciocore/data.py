"""
A singleton containing all the data from Conductor endpoints that's needed for writing submission
tools. Specifiically, it provides projects, instance types, and software package data.

It's also possible to use cached fixtures for development purposes.

"""

import json
import os
from ciocore.package_tree import PackageTree
from ciocore import api_client

__data__ = {}
__products__ = None
__fixtures_dir__ = None
__platforms__ = None

def init(*products, **kwargs):
    """
    Initialize and let the module know what host products to provide in the `software` property.

    Arguments:

    * **`products`** -- Provide a list of products as a filter. If no products are given, the
      software data structure is built using all products from the packages endpoint. If you provide
      more than one product, they must all be host level products.

    Keyword Arguments:

    * **`product`** -- (DEPRECATED) You can provide one product with the product keyword, or you can
      provide the string `"all"`. This is ignored if any product args are present. -- Defaults to
      `None`.

    ???+ example
        ``` python

        from ciocore import data as coredata
        coredata.init()
        # OR
        coredata.init("maya-io")
        # OR LEGACY
        coredata.init(product="all")
        # OR
        coredata.init(product="maya-io")
        
        ```
    """

    global __products__
    if products:
        if  kwargs.get("product"):
            raise ValueError("Arguments: `products` and `product` specified. Please don't use both together. The `product` arg is deprecated.")
        __products__ = list(products)
    elif kwargs.get("product"):
        if kwargs.get("product") == "all":
            __products__ = [] 
        else:
            __products__ = [kwargs.get("product")]
    else:
        __products__ = []

def data(force=False):
    """
    Provides projects, instance types, and software package data.

    If data has been fetched already, then return it, otherwise make requests to fetch it.
    The user may have to authentiicate.

    The set of instance types and software are each potentially pruned to match the available
    platforms represented by the other. If the instance types come from an orchestrator that
    provides both windows and linux machines, and the software product(s) are available on both
    platforms, then no pruning occurs. However, if there are no windows machines, then any windows
    software is removed from the package tree. Likewise, if a product is chosen that only runs on
    Windows, then Linux instance types will be culled from the list of available hardware.

    Keyword Arguments:

    * **`force`** -- If `True`, then fetch fresh data -- Defaults to `False`.

    Raises:

    * **`ValueError`** -- Module was not initialized with the [init()](#init) method.

    Returns:

    * A dictionary with 3 keys: `projects`, `instance_types`, `software`.

    * `projects` is a list of project names for the authenticated account. 
    * `instance_types` is a list of machine specifications available. 
    * `software` is a [PackageTree](/developer/ciocore/package_tree) object containing either all
      software available at conductor, or a subset according to the product specified on
      initialization.
    

    ???+ example
        ``` python

        from ciocore import data as coredata
        coredata.init(product="maya-io")
        coredata.data()["software"]

        # Result:
        # <ciocore.package_tree.PackageTree object at 0x10e9a4040>
        
        coredata.data()["projects"][0]

        # Result:
        # ATestForScott

        coredata.data()["instance_types"][-1]["description"]
        # Result:
        # 160 core, 3844GB Mem
        ```
    """

    global __data__
    global __products__
    global __fixtures_dir__
    global __platforms__

    if __products__ == None:
        raise ValueError(
            'Data must be initialized before use, e.g. data.init("maya-io") or data.init().'
        )

    if force:
        clear()

    if __data__ == {}:
        # PROJECTS
        projects_json = _get_json_fixture("projects")
        if projects_json:
            __data__["projects"] = projects_json
        else:
            __data__["projects"] = sorted(api_client.request_projects())

        # INST_TYPES
        instance_types = _get_json_fixture("instance_types")
        if not instance_types:
            instance_types = api_client.request_instance_types()

        it_platforms = set([it["operating_system"] for it in instance_types])

        # SOFTWARE
        software = _get_json_fixture("software")
        if not software:
            software = api_client.request_software_packages()

        kwargs = {"platforms":it_platforms}

        # If there's only one product, it's possible to initialize the software tree with a plugin.
        # So we set the product kwarg. Otherwise, we set the host_products kwarg
        host_products = __products__
        if len(__products__) == 1:
            host_products = []
            kwargs["product"] = __products__[0]

        software_tree = PackageTree(software, *host_products, **kwargs)

        if software_tree:
            __data__["software"] = software_tree
            # Revisit instance types to filter out any that are not needed for any software package.
            sw_platforms = software_tree.platforms()
            instance_types = [it for it in instance_types if it["operating_system"] in sw_platforms]
        
        __data__["instance_types"] = sorted(instance_types, key=lambda k: (k["cores"], k["memory"]))
        __platforms__ = set([it["operating_system"] for it in __data__["instance_types"]])
    
    return __data__


def valid():
    """
    Check validity of the data.

    Returns:

    * True if `projects`, `instance_types`, and `software` exists.

    ???+ example
        ``` python

        from ciocore import data as coredata
        coredata.valid()

        # Result:
        # True

            
        ```
    """
    global __data__
    if not __data__.get("projects"):
        return False
    if not __data__.get("instance_types"):
        return False
    if not __data__.get("software"):
        return False
    return True


def clear():
    """
    Clear out the data.

    [valid()](#valid) returns False after clear().
    """
    global __data__
    __data__ = {}
    __products__ = None
    __platforms__ = None
    """
    Let the module know what host products to provide in the `software` property.

    Keyword Arguments:

    * **`products`** -- Product args, such as `maya-io, cinema4d` -- Defaults to `None` which means all.

    Raises:

    * **`ValueError`** -- _description_.

    ???+ example
        ``` python

        from ciocore import data as coredata
        coredata.init()
        # OR
        coredata.init("maya-io")

        ```
    """



def products():
    """

    Returns:

    * The product names. An empty array signifies all products. 
    """
    global __products__
    return __products__


def set_fixtures_dir(path):
    """
    Specify a directory in which to find JSON files representing the three sets of data to provide.
    The individual filenames are:

    * projects.json
    * instance_types.json
    * software.json

    These files could be used in an environment where machines can't access the internet. They are
    also useful as a cache for developers who need to reload often as it avoids waiting for the
    network.

    In order to get the content for the fixtures files, use the following Example

    ???+ example
        ``` python

        from ciocore import api_client

        projects = api_client.request_projects()
        instance_types = api_client.request_instance_types()
        software = api_client.request_software_packages()

        # Write that data as JSON to the filenames listed above.
        ```

    Arguments:

    * **`path`** -- Directory in which to find the above files.
 
    """

    global __fixtures_dir__
    __fixtures_dir__ = path or ""


def _get_json_fixture(resource):
    global __fixtures_dir__
    if __fixtures_dir__:
        cache_path = os.path.join(__fixtures_dir__, "{}.json".format(resource))
        if os.path.isfile(cache_path):
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except BaseException:
                pass

def platforms():
    """
    The set of platforms that are found in both software and instance types.

    Returns:

    * A set containing platforms: windows and/or linux or neither.
    """
    global __platforms__
    return __platforms__

