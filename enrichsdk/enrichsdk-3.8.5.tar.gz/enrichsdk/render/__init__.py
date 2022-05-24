"""
.. deprecated:: 2.0
   Skins were present in early versions of Enrich. Now 
   we have dashboard apps. Use them.

"""
import os
import sys
import json
import copy
import re
import traceback
import logging
import markdown
from datetime import timezone
import pytz
import humanize
import pandas as pd

from ..lib.exceptions import *
from ..lib import renderlib

logger = logging.getLogger("app")

######################################################
# Sample data
######################################################
sample_metadata = {
    "version": 1.0,
    "timestamp": "2018-03-06T19:49:42",
    "tables": {
        "voters": {
            "attributes": 22,
            "records": 3761184,
            "columns": [
                {"id": "Mobile", "label": "Mobile", "type": "text"},
                {
                    "list": [
                        {"id": "Housing", "label": "Housing", "count": 224434},
                    ]
                },
            ],
        }
    },
}

######################################################
# Global variables...
######################################################
thisdir = os.path.dirname(__file__)
templatedir = os.path.join(thisdir, "..", "templates")
templatedir = os.path.abspath(templatedir)
widgetdir = os.path.join(templatedir, "widgets")


class ExtractorSkin(object):
    def __init__(self, conf, *args, **kwargs):
        self.conf = conf
        self.required = ["extractor", "skinargs"]
        self.required_skinargs = []

    def validate_skinargs(self):

        missing = [e for v in self.required_skinargs if v not in self.skinargs]
        if len(missing) > 0:
            raise Exception("Missing variables: {}".format(missing))

    def validate_conf(self):

        missing = [
            e
            for v in self.required
            if ((v not in self.conf) and (not hasattr(self, v)))
        ]
        if len(missing) > 0:
            raise Exception("Missing variables: {}".format(missing))

        for r in self.required:
            setattr(self, r, self.conf[r])

        self.validate_skinargs()

    ####################################################
    # Rendering engine...
    ####################################################
    # Template rendering functions
    def template_render(self, widgetname, context):
        """
        Render a specified template using the context

        Args:
            widgetname (str): Name of the template
            context (dict): Key-value pairs

        Returns:
            Rendered html template that can be embedded

        """
        return renderlib.template_render(widgetdir, widgetname, context)

    def template_get_variables(self, widgetname):
        """
        Get the variables from a template

        Args:
            widgetname (str): Name of the template

        Returns:
            List of variables
        """
        return renderlib.template_get_variables(widgetdir, widgetname)

    def render_helper(self, rules, inputdata, params):
        data = []
        html = ""
        for r in rules:
            enable = r.get("enable", True)
            if not enable:
                continue
            c = r["context"](inputdata, params)
            rendered = self.template_render(r["template"], c)
            html += "\n" + rendered

        data.append({"target": "result", "rendered": html})

        return data

    def render(self, **kwargs):

        data = kwargs.pop("data")
        params = kwargs.pop("params", {})

        rules = self.skinargs["dashboard_rules"]
        return self.render_helper(rules, data, params)


class GenericExtractorSkin(ExtractorSkin):
    pass


class SearchExtractorSkin(ExtractorSkin):
    """

    This provides a search interface using the dataextractor

    """

    def __init__(self, *args, **kwargs):
        super(SearchExtractorSkin, self).__init__(*args, **kwargs)

    def validate_skinargs(self):

        super().validate_skinargs()

        extractor = self.extractor

        if not hasattr(self, "metadata"):
            self.metadata = extractor.get_metadata()

        if self.metadata is None:
            raise Exception("No metadata. So cant process")

        # Check whether all the parameters are valid
        table = self.skinargs["table"]
        if (not isinstance(table, str)) or (table not in self.metadata["tables"]):
            raise Exception("Missing or invalid table specified: {}".format(table))

        tablemetdata = self.metadata["tables"][table]
        columns = tablemetdata["columns"]

        autocomplete_column = self.skinargs["autocomplete_column"]
        columndetails = [c for c in columns if c["id"] == autocomplete_column]
        if (not isinstance(autocomplete_column, str)) or (len(columndetails) == 0):
            raise Exception(
                "Invalid or missing autocomplete column: {}".format(autocomplete_column)
            )

        if ("dashboard_rules" not in self.skinargs) or (
            not isinstance(self.skinargs["dashboard_rules"], list)
        ):
            raise Exception("Invalid dashboard rule format. Should be a list")

        invalid = []
        for i, r in enumerate(self.skinargs["dashboard_rules"]):
            if "template" not in r:
                invalid.append("Rule {} missing template".format(i))

            if ("context" not in r) or (not hasattr(r["context"], "__call__")):
                invalid.append("Rule {} invalid or missing context".format(i))

        if len(invalid) > 0:
            logger.error(
                "Invalid dashboard rules",
                extra={"transform": "SkinRenderer", "data": "\n".join(invalid)},
            )
            raise Exception("Invalid dashboard rules")

    def autocomplete(self, term, **kwargs):

        count = kwargs.pop("count", 10)
        extractor = self.extractor

        if not hasattr(self, "metadata"):
            self.metadata = extractor.get_metadata()

        if self.metadata is None:
            raise Exception("No metadata. So cant process autocomplete")

        table = self.skinargs["table"]
        autocomplete_column = self.skinargs["autocomplete_column"]

        # => Get the column details
        columns = self.metadata["tables"][table]["columns"]
        columndetails = [c for c in columns if c["id"] == autocomplete_column]
        columndetail = columndetails[0]

        if columndetail["type"] == "list":
            # Use the metadata results to search and return
            data = [
                {"label": c["label"], "key": c["id"]}
                for c in columndetail["list"]
                if (
                    (term.lower() in c["label"].lower())
                    or (term.lower() in c["id"].lower())
                )
            ]
            # Return a limited count
            data = data[:count]
            return data

        # Now this is regular 'contains' search
        # => Filter for the data
        try:

            filterargs = {
                "table": self.skinargs["table"],
                "outputs": [self.skinargs["autocomplete_column"]],
            }

            searchspec = {
                "method": "autocomplete",
                "rules": [
                    [
                        {
                            "operator": {"label": "contains", "value": "ct"},
                            "field": {
                                "label": self.skinargs["autocomplete_column"],
                                "value": self.skinargs["autocomplete_column"],
                            },
                            "value": {"label": term.lower(), "value": term.lower()},
                        },
                        {
                            "operator": {"label": "limit", "value": "limit"},
                            "field": {
                                "label": "__meta__",
                                "value": "__meta__",
                            },
                            "value": {"label": "count", "value": count},
                        },
                    ]
                ],
            }
        except:
            error = "Could not construct the search arguments"
            logger.exception(error)
            return []

        # Constructed arguments. So search
        try:
            extractor = self.extractor
            columns, records = extractor.query_by_spec(
                spec=searchspec, filterargs=filterargs
            )

            if len(records) > 0:
                data = [{"label": r[0], "key": r[0]} for r in records]
            else:
                data = []
        except:
            error = "Could not construct the dataframe required for the output"
            logger.exception(error)
            return None

        # Return a limited count
        data = data[:count]
        return data

    def search(self, query):

        # => Filter for the data
        try:
            filterargs = {"table": self.skinargs["table"], "outputs": []}

            searchspec = {
                "method": "autocomplete",
                "rules": [
                    [
                        {
                            "operator": {"label": "exact", "value": "ex"},
                            "field": {
                                "label": self.skinargs["autocomplete_column"],
                                "value": self.skinargs["autocomplete_column"],
                            },
                            "value": {"label": query, "value": query},
                        }
                    ]
                ],
            }
        except:
            error = "Could not construct the search arguments"
            logger.exception(error)
            return None

        try:
            extractor = self.extractor
            columns, records = extractor.query_by_spec(
                spec=searchspec, filterargs=filterargs
            )

            if len(records) > 0:
                # Load the records into df
                df = pd.DataFrame(records)
                df.columns = [c["name"] for c in columns]
            else:
                df = pd.DataFrame([])

        except:
            error = "Could not construct the dataframe required for the output"
            logger.exception(error)
            return None

        return df

    def render(self, *args, **kwargs):

        data = kwargs.pop("data")
        params = kwargs.pop("params", {})

        # Query the extractor
        table = self.skinargs["table"]
        autocomplete_column = self.skinargs["autocomplete_column"]

        # Now render the
        rules = self.skinargs["dashboard_rules"]
        data = self.render_helper(rules, data, params)

        return data
