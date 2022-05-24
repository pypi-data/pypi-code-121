"""
Services to allow enrichsdk to be used in notebooks. It
provides:

1. Security - access to obfuscated credentials
2. Resource - limit resource usage
3. Indexing - search notebooks
4. Metadata - Generate metadata to be included in the output files

"""
import os
import sys
import platform
import distro
import resource
import psutil
import nbformat
import glob
import json
import warnings
from datetime import datetime, date
from shutil import copy
import mimetypes
import logging
import pandas as pd
from collections import OrderedDict

from .utils import *

logger = logging.getLogger("app")


class Notebook(object):
    """
    This class allows one to read and search in notebooks
    """

    def __init__(self, data_root=None):
        if data_root is not None:
            if not os.path.exists(data_root):
                raise Exception("Invalid or missing path or file: {}".format(data_root))
            else:
                self.data_root = data_root
                self.output_dir = os.path.join(data_root, "output")
        else:
            if "JUPYTERLAB_HOME" not in os.environ:
                warnings.warn(
                    "Notebook using JUPYTERLAB_HOME when being executed outside jupyter environment. Either use data_root, define the variable or dont use this class"
                )
                raise Exception("JUPYTERLAB_HOME not defined")

            self.data_root = os.path.join(os.environ["JUPYTERLAB_HOME"], "data")
            self.output_dir = os.path.join(
                os.environ["JUPYTERLAB_HOME"], "data", "output"
            )

    def set_resource_limits(self, params={}):
        """
        Set resource limits for the notebook. This applies
        only to this notebook.

        Parameters
        ----------
        params: Only one member (memory) is accessed. It is fraction
                of available memory to be used.

        """

        # Default fraction of max memory to be used
        fraction = params.get("memory", 0.8)

        # Get available virtual memory
        vmem = psutil.virtual_memory()

        max_vmem = int(fraction * vmem.available)

        # use AS as alternative to VMEM if the attribute isn't defined.
        # http://stackoverflow.com/a/30269998/5731870
        if hasattr(resource, "RLIMIT_VMEM"):
            resource.setrlimit(resource.RLIMIT_VMEM, (max_vmem, max_vmem))
        elif hasattr(resource, "RLIMIT_AS"):
            resource.setrlimit(resource.RLIMIT_AS, (max_vmem, max_vmem))

        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        soft = round(soft / (1.0 * 1024 * 1024))
        hard = round(hard / (1.0 * 1024 * 1024))

        return "Memory: Soft ({}MB) Hard ({}MB)".format(soft, hard)

    def get_metadata(self, filename=None, file_type=None):
        """
        Get reusable metadata dict with some standard fields.

        Parameters
        ---------
        filename: Name of the file covered by this metadata

        Returns
        -------
        metadata: Dictionary with a number of fields
        """
        metadata = OrderedDict()

        metadata["schema"] = "standalone:notebook"
        metadata["version"] = "1.0"
        metadata["timestamp"] = datetime.now().replace(microsecond=0).isoformat()
        metadata["platform"] = {
            "node": platform.node(),
            "os": platform.system(),
            "release": platform.release(),
            "processor": platform.processor(),
            "python": platform.python_version(),
            "distribution": distro.linux_distribution(),
        }
        metadata["filename"] = filename
        metadata["filetype"] = mimetypes.guess_type(filename)[0]
        metadata["filesize"] = os.stat(filename).st_size
        if file_type in ["csv", "tsv"]:
            if file_type == "csv":
                df = pd.read_csv(filename)
            elif file_type == "tsv":
                df = pd.read_csv(filename, sep="\t")
            metadata["rows"] = df.shape[0]
            metadata["columns"] = df.shape[1]
            metadata["headers"] = list(df.columns)

        return metadata

    def read_notebook(self, notebook_path, as_version=nbformat.NO_CONVERT):
        """
        Parameters
        ----------
        notebook_path: Absolute path of ipynb file
        as_version: Version of Notebook. Default = nbformat.NO_CONVERT

        Returns
        -------
        NotebookNode: Dictionary representation of file
        """
        try:
            notebook = nbformat.read(notebook_path, as_version=as_version)
            return notebook
        except Exception as e:
            print("Exception reading Notebook - {}".format(e))

    def search_within_notebook(self, notebook_path, keyword):
        """
        Parameters
        ----------
        notebook_path: Absolute path of ipynb file
        keyword: String to search for within notebook

        Returns
        -------
        Boolean, true if keyword is found in ipynb file; False if not.
        """
        try:

            notebook = self.read_notebook(notebook_path)
            if keyword in notebook:
                return True
            return False
        except Exception as e:
            print("Exception searching in notebook - {}".format(e))

    def search_notebooks(self, user_notebook_dir, keyword):
        """
        Parameters
        ----------
        notebook_path: Absolute path of ipynb file
        keyword: String to search for within notebook

        Returns
        -------
        List of path strings to Notebooks that satisfy the search
        """
        try:
            notebooks = []
            ipynb_files = glob.glob(
                os.path.join(notebook_dir, "/**/*.ipynb"), recursive=True
            )
            for ipynb in ipynb_files:
                present = self.search_within_notebook(ipynb, keyword)
                if present:
                    notebooks.append(ipynb)
            return notebooks

        except Exception as e:
            print("Exception searching in notebook directory - {}".format(e))

    def get_file(self, path, create_dir=False):
        """
        Parameters
        ----------
        path: Path specification
        create_dir: Should the parent director for the file be created

        Example
        ----------
        %(data_root)/acme/Projects/commands
        This is resolved into `/home/ubuntu/enrich/data/notebooks/acme/Projects/commands`

        Returns
        -------
        Full path from abstract specification
        """
        try:
            path = path.replace(
                "%(", "%%("
            )  # This will make the strftime handling safe
            path = datetime.now().strftime(path)
            path = path % {
                "data_root": self.data_root,
                "dt": datetime.now().date().isoformat(),
                "datetime": datetime.now().replace(microsecond=0).isoformat(),
            }

            if create_dir:
                try:
                    os.makedirs(os.path.dirname(path))
                except:
                    pass

            return path
        except Exception as e:
            print("Exception in get_file() - {}".format(e))

    def save(self, file_name, metadata_path=None):
        """
        Parameters
        ----------
        file_name: Relative path of file including filename with extension

        Returns
        -------
        None. Saves the data file specified and metadata about the file into Enrich's data dir
        """
        try:
            metadata_file = None
            abs_file_name = self.get_file(file_name)
            file_type = abs_file_name.split(".")[-1]

            # Validate that file is "csv" or "tsv". More file types can be added to list
            if os.path.exists(abs_file_name) and file_type in accepted_types():
                metadata_info = self.get_metadata(abs_file_name, file_type)
                if metadata_path is None:
                    metadata_file = os.path.join(self.output_dir, "metadata.json")
                elif isinstance(metadata_path, str):
                    resolved_metadata_path = self.get_file(metadata_path)
                    create_dir("/".join(resolved_metadata_path.split("/")[:-1]))
                    metadata_file = resolved_metadata_path
                elif callable(metadata_path):
                    data_dump_dir = metadata_path()

                with open(metadata_file, "w") as f:
                    json.dump(metadata_info, f, indent=4)
        except Exception as e:
            print("Exception in save() - {}".format(e))
