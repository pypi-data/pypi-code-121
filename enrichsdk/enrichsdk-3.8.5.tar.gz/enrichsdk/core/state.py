"""Enrich has a notion of a pipeline state. The State object is used
to keep track of all available data objects (dataframes, dictionaries,
html objects etc.) and deliver it to whatever transform requires it.

The combination of transform and state allows a complex pipeline to be
split into multiple stages, and independent development. Further the
transform code can be spread across multiple repositories.

The State object associates metadata with every data object, that is
dumped into the metadata.json at the end of the run.

The metadata associated with a data object includes::

  1. Name of the frame (each data object has a unique name)
  2. Category of the data object
  3. Type of frame (e.g., pandas, html, dict)
  4. History of access to the dataframe
  5. Parameters that can have arbitrary informations such as
     column documentation, security, messages etc.
  6. Stages that each data object goes through


"""

import os
import sys
import json
import logging
import platform
import getpass
import distro
from datetime import datetime


class EnrichStateBase(object):
    """
    Base class for state manager
    """

    def __init__(self, config, *args, **kwargs):
        """
        Config object is a required parameter
        """
        self.config = config
        self.start_time = self.config.now()
        self.end_time = self.config.now()
        self.name = config.name
        self.display = config.display
        self.runid = config.runid
        self.pid = os.getpid()

        # Status...
        self.histid = 0
        self.status = "started"
        self.summary = []  # notes that must be shared.
        self.performance_summary = []
        self.dataset_accesses = []
        self.frames = {}
        self.transforms = {}
        self.transform_overrides = {}

        self.notification = {"email": []}

        self.expectations = []

        # Who is running this?
        user = getpass.getuser()
        cmdline_args = self.config.get_cmdline_args()
        if "user" in cmdline_args:
            user = cmdline_args["user"]

        # Background system information
        self.stats = {
            "platform": {
                "node": platform.node(),
                "os": platform.system(),
                "release": platform.release(),
                "processor": platform.processor(),
                "python": platform.python_version(),
                "distribution": distro.linux_distribution(),
            },
            "user": user,
        }

    def update_frame(self, name, detail, create=True):
        """
        Update the state with the details of a dataframe

        Args:
            name (str): Name of the dataframe
            detail (dict): Dict with a number of details
            create (bool): Add if the frame doesnt exist.

        The detail has the elements mentioned above::

            {
               'df': df,               # data object
               'params': params,       # extra metadata
               'transform': self.name, # Callee
               'history': [
                   {
                      'log': 'Passed some additional params'
                   }
               ]
            }

        Params could be a dict or a list of dicts. Each
        entry has a `type` and type-specific attributes.
        Over a period of time a nuber of different
        attributes were added. Some of them are::

              1. Compute - column information and description
              2. Overrides - information/instructions from one
                 transform to another
              3. Lineage - Input and output dependencies for
                 better tracking

        For example::

            [
                {
                    # Column metadata
                    'type': 'compute',
                    'columns': columns,
                    'description': [
                        "Cars1 Dataset with no changes"
                    ]
                },
                {
                    # 'Fake' the saving
                    'type': 'overrides',
                    'transform': 'TableSink',
                    'args': {
                        'save': False,
                        'rows': 193332
                    }
                },
                {
                    # Dependency information
                    "type": "lineage",
                    "transform": self.name,
                    "dependencies": [
                        {
                            "type": "file",
                            "nature": "output",
                            "objects": [sqloutput, output]
                        },
                        {
                            "type": "dataframe",
                            "nature": "input",
                            "objects": ["cars1", "cars2"]
                        }
                    ]
                }

            ]

        """
        pass

    def make_dataset_access_note(self, dataset, metadata, nature="read-write"):
        self.dataset_accesses.append({
            'timestamp': datetime.now(),
            'name': dataset.name,
            'nature': nature,
            'description': dataset.description,
            'metadata': metadata
        })
