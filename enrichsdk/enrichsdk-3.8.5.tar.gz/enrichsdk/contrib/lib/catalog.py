import os
import json
import logging
from enrichsdk.core.node import Node

logger = logging.getLogger("app")


class Schema(object):
    """
    This class allows one to use load exported catalog data
    """

    def __init__(self, filename):

        if not os.path.exists(filename):
            raise Exception("Invalid or missing schema file: {}".format(filename))

        try:
            catalogs = json.load(open(filename))
        except:
            logger.exception("Unable to read filename")
            raise Exception("Unsupported format: {}".format(filename))

        if isinstance(catalogs, dict):
            catalogs = [catalogs]

        for catalog in catalogs:
            if ("schema" not in catalog) or (catalog["schema"] != "Catalog"):
                raise Exception("Only catalog level exports supported")

        self.catalogs = catalogs

    def find_source(self, catalogname, sourcename):

        catalog = None
        for c in self.catalogs:
            if c["name"] == catalogname:
                catalog = c
                break

        if catalog is None:
            return None

        source = None

        for s in catalog["sources"]:
            if s["name"] == sourcename:
                source = s
                break

        return source

    def get_column_docs(self, catalogname, sourcename):
        """
        Summarize the output in form that it usable by the
        transform
        """

        outputs = {}

        source = self.find_source(catalogname, sourcename)
        if source is None:
            # Didnt find the source
            return outputs

        for c in source["columns"]:
            colname = c["name"]
            coldesc = c.get("description", c.get("desc", ""))
            notes = c.get("notes", "")

            outputs[colname] = coldesc + "\n" + notes

        return outputs


class TransformSchemaMixin(object):
    def documentation_from_catalog(self, catalog, frames):

        # Check if the transform is an instance of the sdk
        if not isinstance(self, Node):
            raise Exception("Transform should be an instance of the Node")

        # Check if the catalog exists
        catalog = self.config.get_file(catalog)
        schema = Schema(catalog)
        outputs = self.outputs

        for frame, details in frames.items():
            catalogname = details["catalog"]
            sourcename = details["source"]

            # Initialize
            if frame not in outputs:
                outputs[frame] = {}

            frameoutputs = schema.get_column_docs(catalogname, sourcename)
            if len(frameoutputs) == 0:
                continue

            outputs[frame].update(frameoutputs)
