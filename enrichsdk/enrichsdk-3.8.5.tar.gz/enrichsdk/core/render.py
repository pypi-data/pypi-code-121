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
from ..lib.exceptions import *
from .node import *

logger = logging.getLogger("app")

__all__ = ["SearchSkin", "GenericSkin"]


class SearchSkin(Skin):
    """

    This provides a search interface to the dataframes.

    .. deprecated::
           Use enrichsdk.render functions from the app

    """

    def __init__(self, *args, **kwargs):
        super(SearchSkin, self).__init__(*args, **kwargs)

        self.framename = None
        """
        Dataframe to service the search interface 
        """

        self.autocomplete_column = None
        """
        Column to feed the autocomplete function of the search interface
        """

        self.dashboard_rules = []
        """
        Specification of the layout of the search result. 
        """
        self.run = None
        self.detail = None
        self.tags.extend(["skin", "search"])

    def load(self):

        # If not loaded or loaded run not the last one:
        lastrun = self.config.runmanager.get_last_run()
        if (
            (self.run is not None)
            and (lastrun is not None)
            and (lastrun.runid == self.run.runid)
        ):
            return

        # Note it
        self.run = lastrun

        # If still not loaded, give up
        if self.run is None:
            return

        # Load the details...
        self.run.load_files(include_output_frame=True)
        self.detail = self.run.find_file_detail(
            framename=self.framename, action="output"
        )

        if self.detail is None:
            raise Exception("Could not find detail")

    def autocomplete(self, term):

        if self.run is None:
            try:
                self.load()
            except:
                pass

        if self.run is None or self.detail is None:
            return []

        df = self.detail["df"]
        names = df[self.autocomplete_column].values
        names = [n for n in names if term.lower() in n.lower()]

        data = [{"label": n, "key": n} for n in names][:10]

        return data

    def render_helper(self, rules, row):
        data = []
        html = ""
        for r in rules:
            enable = r.get("enable", True)
            if not enable:
                continue
            c = r["context"](row)
            rendered = self.template_render(r["template"], c)
            html += "\n" + rendered

        data.append({"target": "result", "rendered": html})

        return data

    def render(self, name):

        if self.run is None:
            try:
                self.load()
            except:
                pass

        if self.run is None:
            return {}

        if name is None or len(name) == 0:
            return {}

        if self.detail is None:
            # Try loading
            try:
                self.load()
            except:
                pass

        if self.detail is None:
            return {}

        df = self.detail["df"]
        row = df[df[self.autocomplete_column] == name]

        if len(row) > 0:
            row = row.iloc[0].to_dict()
            data = self.render_helper(self.dashboard_rules, row)
        else:
            data = []

        return data


class GenericSkin(Skin):
    """
    This skin allows rendering of arbitrary content.

    It takes all available dataframes in the last available run as
    input. The render function can display content from one or more
    dataframes.
    """

    def __init__(self, *args, **kwargs):
        super(GenericSkin, self).__init__(*args, **kwargs)
        self.run = None
        self.tags.extend(["skin", "generic"])

    def load(self):
        """
        Load the last run of the pipeline that this skin is
        included in.

        """
        # If not loaded, load now
        lastrun = self.config.runmanager.get_last_run()
        if (
            (self.run is not None)
            and (lastrun is not None)
            and (lastrun.runid == self.run.runid)
        ):
            return

        # Note it
        self.run = lastrun

        # If still not loaded, give up
        if self.run is None:
            logger.error("Could not find run in GenericSkin")
            return

        # Load the details...
        self.run.load_files(include_output_frame=True)

    def discover_params_helper(self, data):
        """
        This is overridden by the renderer
        """
        raise Exception("To be overridden by the renderer")

    def discover_params(self):
        """
        Parameters that can be passed

          {
             name: [val1, val2, ..]
          }

        """

        if self.run is None:
            try:
                self.load()
            except:
                traceback.print_exc()
                pass

        if self.run is None:
            raise Exception("Run not available")

        # Collect all the frames...
        data = self.run.get_file_hash()

        return self.discover_params_helper(data)

    def render_helper(self, rules, params):
        """
        This function renders the last run's data according
        to rules.

        Args:
            rules (list): A list of widget configurations

        Returns:

            Rendered html

        """
        # Collect all the frames...
        data = self.run.get_file_hash()

        response = []
        html = ""
        for r in rules:
            enable = r.get("enable", True)
            meta = r.get("meta", False)
            if not enable:
                continue

            t = r["template"]
            if not meta:
                c = r["context"](data, params)
                rendered = self.template_render(t, c)
                html += "\n" + rendered
            else:

                # Render the subset of rules...
                subresponse = self.render_helper(r["rules"], params)
                subresponsehtml = "\n".join([s["rendered"] for s in subresponse])

                # Now incorporate it...
                c = r["context"](data, params, subresponsehtml)
                rendered = self.template_render(t, c)
                html += "\n" + rendered

        response.append({"target": "result", "rendered": html})

        return response

    def render(self, params):
        """
        Generic render function that first loads the run,
        all the files that are part of the run, and call
        the render helper.
        """
        try:
            self.load()
        except:
            traceback.print_exc()
            pass

        if self.run is None:
            return {}

        data = self.render_helper(self.dashboard_rules, params)

        return data

    def get_metadata_context(self, data, params):
        """
        Include standard metadata
        """

        pairs = [
            {"name": "RunID", "value": self.run.runid},
            {
                "name": "Run Date",
                "value": humanize.naturaltime(self.run.start_time.replace(tzinfo=None)),
            },
        ]

        return {"title": "Run Metadata", "width": 12, "pairs": pairs}
