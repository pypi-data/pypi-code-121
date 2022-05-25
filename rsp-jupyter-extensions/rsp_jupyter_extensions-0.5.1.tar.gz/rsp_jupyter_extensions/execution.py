"""
This is a Handler Module to provide an endpoint for notebook execution.
"""
import json
from typing import Dict

import nbconvert
import nbformat
from notebook.base.handlers import APIHandler

# This defines a git repository for each known query_type.


class Execution_handler(APIHandler):
    """
    RSP templated Query Handler.
    """

    @property
    def rubinexecution(self) -> Dict[str, str]:
        return self.settings["rubinexecution"]

    def post(self) -> None:
        """
        POST the contents of a notebook and get back the rendered,
        executed notebook.

        There are two supported formats.  The first is simply the text
        of an ipynb file.  This is expected to be the common use case.

        The second is a JSON representation of a dict containting a
        notebook and associated resources; the notebook contents (a string
        containing an ipynb file) will be in the "notebook" key and
        the resources will be a string in the key "resources" representing
        a JSON-encoded dict).
        """
        input_str = self.request.body.decode("utf-8")
        # Do The Deed
        output_str = self._execute_nb(input_str)
        self.finish(output_str)

    def _execute_nb(self, input_str: str) -> str:
        # We will try to decode it as if it were a resource-bearing document.
        #  If that fails, we will assume it to be a bare notebook string.
        #
        # It will return JSON in the same format as it received it.
        has_resources = False
        try:
            d = json.loads(input_str)
            resources = d["resources"]
            nb_str = d["notebook"]
            has_resources = True
        except Exception:
            resources = None
            nb_str = input_str
        nb = nbformat.reads(nb_str, 4)
        executor = nbconvert.preprocessors.ExecutePreprocessor()
        # Execute the notebook; updates nb/resources in place
        executor.preprocess(nb, resources=resources)
        # Re-export to a notebook
        exporter = nbconvert.exporters.NotebookExporter()
        (rendered, rendered_resources) = exporter.from_notebook_node(
            nb, resources=resources
        )
        if has_resources:
            return json.dumps(
                {"notebook": rendered, "resources": rendered_resources}
            )
        return rendered
