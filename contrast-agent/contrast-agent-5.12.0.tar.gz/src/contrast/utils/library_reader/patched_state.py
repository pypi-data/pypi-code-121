# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os

from contrast.utils import get_installed_distributions
from contrast.utils.singleton import Singleton
from contrast.utils.library_reader.utils import (
    get_top_level_directories,
    get_data,
    get_hash,
    SITE_PACKAGES_DIR,
    DIST_PACKAGES_DIR,
    get_top_level_directories_namespace_pkg,
)

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class DistributionContext(Singleton):
    """
    This class is used to maintain state between calls to python import functions.
    The main reason why we need to do all this is because Python doesn't provide
    us with a function that maps a loaded file name
    (e.g /Users/nliccione/lib/python3.7/site-packages/django/https.py)
    to the distribution it belongs to.
    """

    class TopLevelDirNode:
        def __init__(self, top_level_dir, dist):
            version, _, _ = get_data(dist)
            name = str(dist).split(" ")[0]

            self.namespace_tlds = set()
            self.dist_hash = get_hash(name, version)
            self.dist = dist
            self.distribution_install_dir = dist.location
            self.full_package_path = os.path.join(dist.location, top_level_dir)

    def init(self):
        # dictionary containing mapping of top level directory name -> ( TopLevelDirNode, )
        self.top_level_dir_map = {}
        self.installed_dists = get_installed_distributions()

        for dist in self.installed_dists:
            self._build_tld_entries_from_dist(dist)

    def _get_dist_ctx_from_file_path(self, file_path):
        """
        This function returns the TopLevelDirNode that represents the given file_path.
        @param file_path: Path to the file (e.g /Users/nliccione/lib/python3.7/site-packages/django/https.py)
        @rtype: TopLevelDirNode
        """
        ret = None

        if not file_path:
            return ret

        # Using this as an example: /Users/nliccione/lib/python3.7/site-packages/django/https.py
        # package_dirs[1] should be "django/https.py" where django is the top level importable package
        # and https.py is the specific module to be loaded (top level module, then https.py after)
        package_dirs = file_path.rsplit(SITE_PACKAGES_DIR)

        if len(package_dirs) < 2:
            package_dirs = file_path.rsplit(DIST_PACKAGES_DIR)
            if len(package_dirs) < 2:
                return None

        # Get the top level importable module/package from the file path and set it to top_level_name
        # Using the django example top_level_name should be "django"
        top_level_relative_dir = package_dirs[1]
        top_level_dirs = top_level_relative_dir.split(os.sep)
        top_level_name = top_level_dirs[0]

        if top_level_name:
            top_level_node = None

            # If the top level name is a module file than we report on that because that is the top level import
            if top_level_name.endswith(".py") or top_level_name.endswith(".pyc"):
                top_level_name = os.path.splitext(top_level_name)[0]

            nodes = self.top_level_dir_map.get(top_level_name, [None])
            if len(nodes) == 1:
                top_level_node = nodes[0]
            elif len(top_level_dirs) > 1:
                # Handling a namespace package where multiple distributions share the same top level directory
                # tests/samples/sample_packages/sample_namespace_pkg1 and sample_namespace_pkg2
                # are examples of this case
                namespace_tld = top_level_dirs[1]
                for node in nodes:
                    if namespace_tld in node.namespace_tlds:
                        top_level_node = node
                        break

            # Once we get the TopLevelDirNode associated with the top_level_name found in file_path, we then verify
            # TopLevelDirNode is the node that actually matches file_path based on the path to the distribution
            # found in TopLevelDirNode
            if top_level_node and file_path.startswith(
                top_level_node.full_package_path
            ):
                ret = top_level_node

        return ret

    def get_dist_hash_from_file_path(self, file_path):
        """
        Convenience wrapper around _get_dist_ctx_from_file_path for getting the distribution hash for a file
        @param file_path: Path to the file (e.g /Users/nliccione/lib/python3.7/site-packages/django/https.py)
        @return dist_hash of the distribution associated with file_path
        @rtype: string
        """
        dist_hash = None

        ctx = self._get_dist_ctx_from_file_path(file_path)
        if ctx:
            dist_hash = ctx.dist_hash

        return dist_hash

    @staticmethod
    def _add_namespace_tlds_to_node(tld, node):
        dist = node.dist

        tld_namespace_dirs = get_top_level_directories_namespace_pkg(dist, tld)

        if len(tld_namespace_dirs) == 0:
            logger.debug(
                "WARNING - namespace package does not have a RECORD file. Unable to parse \
                top level directory for the distribution: %s",
                str(dist),
            )
        else:
            node.namespace_tlds = tld_namespace_dirs

    def _build_tld_entries_from_dist(self, dist):
        """
        This function builds the data structure containing the mapping of a top level package/module name
        belonging to a specific distribution.
        For example, if /Users/nliccione/lib/python3.7/site-packages/django/https.py is the file that is imported, an entry in self.top_level_dir_map
        will look like this: self.top_level_dir_map = {"django": [ TopLevelDirNode, ]}. When https.py is imported, we check to see if "django"
        exists in self.top_level_dir_map. If it does, and the file path found in sys.module matches TopLevelDirNode.full_package_path, than
        we know the imported file belongs to the distribution cached in self.top_level_dir_map.

        This function also handles namespace distributions. Namespace distributions share a top level import name
        (e.g zope namespace where zope.deprecation is a distribution using that namespace). As a result, we need to have an additional
        data structure to maintain the list of top level directories or file names belonging to that namespace.

        @param dist: Distribution object used to determine how many top level importable packages/modules exist in it
        @type dist: pkg_resources.DistInfoDistribution
        """
        for tld in get_top_level_directories(dist):
            # The namespace dist we support is building a namespace package
            # using the pkg_resources method of defining one
            # https://packaging.python.org/guides/packaging-namespace-packages/#pkg-resources-style-namespace-packages
            new_node = DistributionContext.TopLevelDirNode(tld, dist)

            namespace_dists = self.top_level_dir_map.get(tld, None)
            if namespace_dists:
                self._add_namespace_tlds_to_node(tld, new_node)

                if len(namespace_dists) == 1:
                    # Handle case where we didn't know we have a namespace dist before.
                    # Now that we know we need to go back and add the tlds for that namespace node
                    prev_node = namespace_dists[0]
                    self._add_namespace_tlds_to_node(tld, prev_node)

                namespace_dists.append(new_node)
            else:
                self.top_level_dir_map[tld] = [new_node]
