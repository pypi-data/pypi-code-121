"""
"""
import os
import sys
import json
import copy

from ..lib import read_siteconf


class Service(object):
    """
    Base class for all services.

    Each class of services extends this base class to achieve its
    performance and other objectives. For example, `data quality
    service` (DataSourceService) that is provided by the `Contrib`
    application from `Scribble` customer.

    """

    def __init__(self, conf, *args, **kwargs):
        """
        Initialize the service manager
        """
        if "name" not in conf:
            raise Exception("Invalid configuration: Every service requires a name")

        self.conf = conf
        """
        Configuration of this service. 
        
        This is interpreted by the subclass functions 
        """

        self.name = self.conf["name"]
        """
        Name of the service. 
        """

        self.context = {
            "enrich_root": os.environ["ENRICH_ROOT"],
            "enrich_root_dir": os.environ["ENRICH_ROOT"],
            "enrich_data": os.environ["ENRICH_DATA"],
            "enrich_data_dir": os.environ["ENRICH_DATA"],
        }
        """
        Context for path resolution
        """

    def get_file(self, path, extra={}):
        """
        Resolve a path
        """

        fullcontext = copy.copy(self.context)
        fullcontext.update(extra)
        return path % fullcontext

    def get_credentials(self, name):
        """
        Look up the credentials file
        """

        siteconf = read_siteconf()
        if siteconf is None:
            raise Exception("Could not find siteconf")

        if ("credentials" not in siteconf) or (name not in siteconf["credentials"]):
            raise Exception("missing credentials")

        return siteconf["credentials"][name]
