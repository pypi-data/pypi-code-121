"""
Core classes that must be used to build transforms
"""
import os
import sys
import json
import copy
import re
import logging
import warnings
import markdown
import importlib
import traceback
import s3fs
import pandas as pd
from datetime import datetime
import abc
import jsonschema

from ..lib.exceptions import *
from ..lib import renderlib
from ..lib.misc import get_checksum, get_file_size

logger = logging.getLogger("app")
thisdir = os.path.dirname(__file__)
templatedir = os.path.join(thisdir, "..", "templates")
templatedir = os.path.abspath(templatedir)
widgetdir = os.path.join(templatedir, "widgets")


__all__ = ["Node", "Transform", "Model", "Skin", "Integration"]


def flatten(c):
    if isinstance(c, (int, float, str)):
        return c

    try:
        if isinstance(c, (datetime, date)):
            c = c.isoformat()
        elif isinstance(c, (dict, list)):
            c = json.dumps(c)
        else:
            c = str(c)
    except:
        c = str(c)
    return c[:30]


class NodeMeta(abc.ABCMeta):
    """
    Meta class for all elements with schemas. This allows for
    registration, validation, and tracking of the schema implementors.
    """

    def __init__(cls, name, bases, dct):
        if cls.__name__ not in ["Node"]:
            if not hasattr(Node, "_registry"):
                Node._registry = []

            if cls.instantiable():
                Node._registry.append(cls)

        # Now initialize
        super().__init__(name, bases, dct)


##################################################
# Transform objects
##################################################
class Node(metaclass=NodeMeta):
    """
    This is the base class for all modules including transforms,
    models, skins etc.

    This provides a number of infrastructural elements that enable the
    module to the plugged into the application infrastructure.

    This is for understanding only. Subclassing is done from derived
    classes such as Source, SearchSkin etc.
    """

    @classmethod
    def implementation_list(cls):
        return cls._registry

    @classmethod
    def implementation_get(cls, name):
        for c in cls._registry:
            if c.__name__ == name:
                return c

        raise InvalidNode("Unknown node name: {}".format(name))

    @classmethod
    def instantiable(cls):
        """
        Whether this transform should/can be instantiated.
        This is usually used by base classes.
        """
        return True

    def __init__(self, *args, **kwargs):

        # Note the this or subclass path path
        m = importlib.import_module(self.__module__)
        self.transform_root = os.path.abspath(os.path.dirname(m.__file__))

        if "config" not in kwargs:
            raise Exception("config parameter is missing")

        self.config = kwargs.pop("config")
        """
        object: Configuration object

        This is passed to the module during instantiation by the
        enrich compute engine
        """
        self.node_type = "Unknown"
        """
        str: Node type

        This is one of Transform, Model, Skin, Integration
        """

        self.name = "Unknown"
        """
        str: Name of the transform. Required

        This is overridden by name specified in the manifest.json
        """

        self.description = "Unknown"
        """
        str: Text description of the transform

        This is overridden by description specified in the manifest.json
        """

        self.author = "Builtin"
        """
        str: Author of this module.

        This is overridden by author specified in the manifest.json
        """

        self.version = 1.0
        """
        float: Version of this module
        """

        self.minorversion = 1.0
        """
        float: Minor version of this module
        """

        self.output_version = 1.0
        """
        float: Version of the output of this module
        """

        self.debug = False
        """
        bool: Debug mode operation at the transform level
        """

        self.files = ["manifest.json"]
        """
        list: Files in this module
        """

        self.test = False
        """
        bool: Whether this transform is being operated in test mode
        """

        self.dependencies = {}
        """Specifies the list of frames and transformations that this
        transform dependens on. This value has to be overriden by the
        subclass explicitly. Otherwise it transform will throw a
        validation error. For example::

            {
              'article': 'Core',
              'store': ['EnrichedStore', 'EnrichedTransform']
              ...
            }

        """

        self.datasets = []
        """
        Input and output datasets handled by this transform
        """

        self.args_schema = {}
        """
        dict: JSON Schema to validate the input args::

           See: https://python-jsonschema.readthedocs.io/en/latest/
                https://json-schema.org/

            self.args_schema = {
                "type": "object",
                "properties": {
                    "name": {
                         "type": "string"
                         "description": "Name of the dataset"
                     },
                    "count": {
                         "type": "number"
                         "description": "Threshold"
                     }
                     ...
                 }
                 "required": ["name", "count"]
                }
            }

        """

        self.supported_extra_args = []
        """
        Extra arguments that can be passed on the command line and the GUI to
        the module::

            self.supported_extra_args = [
                {
                    "name": "jobid",
                    "description": "Export JobID",
                    "type": "str",
                    "required": True,
                    "default": "22832"

                }

            ]

        """

        self.data_root = self.get_file("%(data_root)s")
        """

        """
        self.testdata = self.get_testdata
        """dict: Test data to be used for testing module

        The default structure is instantiated by self.get_testdata. Each
        of the elements (e.g., conf) can be specified by over-riding
        corresponding method (e.g., self.get_testdata_conf). Such
        functions are supported for conf, args, global, data.

        It has the form::

            {
              'data_root': os.path.join(os.environ['ENRICH_TEST'], self.name),
              'outputdir': os.path.join(os.environ['ENRICH_TEST'], self.name),
              'inputdir': os.path.join(os.environ['ENRICH_TEST']),
              'statedir': os.path.join(os.environ['ENRICH_TEST'], self.name, 'state'),
              'datasets': {
               ...
              },
              'global': {
                'args': {
                    'rundate': '2020-01-01'
                }
              },
              'conf': {
                 'args': {
                       'threshold': 0.6
                       ...
                  }
              },
              'data': {
                'article': {
                    'filename': 'test.csv',
                    'transform': 'Core',
                    'frametype': 'pandas',
                    'stages': [ 'transform1'],
                    'params': {
                        'sep': ','
                    }
                }
              }
            }

        When the module is tested, the sdk loads
        `$ENRICH_DATA/test/temp-configname/Core/test.csv` and makes it
        available to the module using the state interface

        If data in the frame is to be loaded from multiple files,
        you can specify the list and a merge function that gets
        the list of frames to merge::

            {
              ..
              'data': {
                'article': {
                    'filename': {
                         'transform1': ['test.csv'],
                         'transform2': ['test.csv']
                    },
                    'frametype': 'pandas',
                    'mergedf': self.test_merge_func, # function
                    'transform': 'transform1',
                    'stages': ['transform2'],
                    'params': {
                        'sep': ','
                    }
                }
              }
            }
            ...

           def test_merge_func(self, dfs):
               ...

        See `get_test_conf` function to dynamically generate these
        configurations.

        `datasets` is a dictionary with a specification for where the
        input datasets should be stored and obtained from::

            {
               "command": command,
               'params': {
                   'enrich_data_dir': '/home/ubuntu/enrich/data',
                   'backup_root': 'some-s3-path',
                   'node': 'some hostname'
                },
               'available': [
                    Dataset({
                       'name': "inventory_dataset",
                       ...
                    }),
                     ...
               ]
            }

        """

        self.enable = True
        """
        bool: Is this transform enabled?

        A transform could be included but not enabled
        """

        self.outputs = {}
        """
        dict: Outputs of this module

        It has the form::

            {
                <pattern> : <description>,
                <pattern>: {
                   'description': <text>
                }
            }
            """
        self.tags = []
        """
        list: Tags associated with this transform
        """

        self.metadata = {}

        self.data_version_map = {}
        """
        dict: Versions of the preprocessed data

        .. warning::

            .. deprecated:: 2.0

        It has the form::

            {
               'raw': 1.0,
               'preprocessed': 1.3
            }
        """

        self.roles_supported = ["default"]
        """
        list: A transform can support multiple roles such as source, sink etc. This lists the roles.

        This attribute was used to sequence the transforms in early versions of Enrich. Now it is deprecated.

        .. warning::

            .. deprecated:: 2.0


        """

        self.roles_current = "default"
        """
        str: Current role of this transform

        This attribute was used to sequence the transforms in early versions of Enrich. Now it is deprecated.

        .. warning::

           .. deprecated:: 2.0

        """

        # Interface variables...
        self.manifest = {}
        """
        dict: Manifest json file loaded
        """

        self.args = {}
        """
        dict: Arguments passed to the transformation from the configuration file

        """

        try:
            module = sys.modules[self.__module__]
        except:
            raise Exception("Could not find module")

        self.modulepath = os.path.dirname(module.__file__)

    @property
    def fullname(self):
        """
        str: One line summary of the transform
        """
        return "{} (v{}:v{} by {})".format(
            self.name, self.version, self.minorversion, self.author
        )

    #############################################
    # Helper functions
    #############################################
    def get_testdata(self):
        """
        Generate test data structure

        Returns:

           testdata (dict) : Dictionary

        """
        test_root = os.environ["ENRICH_TEST"]

        return {
            "data_root": os.path.join(test_root, self.name),
            "inputdir": test_root,
            "outputdir": os.path.join(test_root, self.name, "output"),
            "statedir": os.path.join(test_root, self.name, "state"),
            "conf": self.get_testdata_conf(),
            "data": self.get_testdata_data(),
            "global": self.get_testdata_global(),
        }

    def get_testdata_conf(self):
        """
        Get testdata conf attribute

        Returns
        -------
        dict: a dictionary of args and any other elements

        """
        return {"args": self.get_testdata_args()}

    def get_testdata_args(self):
        """
        Get testdata args attribute of conf

        Returns
        -------
        dict: a dictionary of args

        """
        return {}

    def get_testdata_global(self):
        """
        Get testdata global attribute. Global args are pipeline-wide
        args.

        Returns
        -------
        dict: a dictionary of global args

        Example::

            return {
               'args': {
                    'rundate': '2020-01-01'
                }
             }

        """
        return {}

    def get_testdata_data(self):
        """
        Get 'data' element of test data. This specifies
        what dataframes have to be loaded to test this
        transform.

        Returns
        -------
        dict: A specification of dataframes and loading instructions

        Example::

          return {
                'article': {
                    'filename': 'test.csv',
                    'transform': 'Core',
                    'frametype': 'pandas',
                    'stages': [ 'transform1'],
                    'params': {
                        'sep': ','
                    }
                }
              }
        """
        return {}

    def is_enabled(self):
        """
        bool: Check whether this module is enabled

        Returns
        -------
        bool
        """
        return self.enable

    def is_transform(self):
        """
        bool: Test whether the module is a transform

        Returns
        -------
        bool
        """
        return self.node_type == "Transform"

    def is_model(self):
        """
        Test whether the module is a module

        Returns
        -------
        bool
        """
        return self.node_type == "Model"

    def is_skin(self):
        """
        Test whether the module is a skin

        Returns
        -------
        bool

        .. warning::

           .. deprecated:: 2.0
           Use enrichsdk.render library functions

        """
        return self.node_type == "Skin"

    def is_integration(self):
        """
        Test whether the module is an integration

        Returns
        -------
        bool

        .. warning::

           .. deprecated:: 2.0
           Will be dropped in future

        """
        return self.node_type == "Integration"

    def is_sink(self):
        """
        Is current role a sink?

        Returns
        -------
        bool

        """
        return (self.node_type == "Transform") and (self.roles_current == "Sink")

    def is_source(self):
        """
        Is current role a source?

        Returns
        -------
        bool

        """
        return (self.node_type in ["Transform", "Model"]) and (
            self.roles_current == "Source"
        )

    def has_tag(self, tags):
        """
        Does the module have any of the specified tags?

        Returns
        ----
        bool
            True if there is an overlapping tag otherwise False

        """
        common = [t for t in tags if t in self.tags]
        return len(common) > 0

    def is_search(self):
        """
        Is the current module a search skin?

        Returns
        -------
        bool
        """
        return (self.node_type == "Skin") and self.has_tag(["search"])

    def is_notification(self):
        """
        Is the current module a notification implementation?

        Returns
        -------
        bool
        """
        return (self.node_type == "Integration") and self.has_tag(["notification"])

    def get_supported_extra_args(self):
        """
        Get the command line arguments. This will handle any callables specified
        by the default.

        Returns:
           args (list): List of arg specifications. Default values can be actual   strings/numbers or callback functions

        See supported_extra_args
        """

        final = []
        for a in self.supported_extra_args:
            a = copy.copy(a)
            if callable(a["default"]):
                a["default"] = a["default"]()
            final.append(a)

        return final

    #################################################
    # Configuration the Module
    #################################################
    def preload_clean_args(self, args):
        """
        Clean the arguments before using them

        Args:
           args: args to be resolved/cleaned/extended

        Returns:
           list: Cleaned args

        """

        # Nothing to clean if there are no extra args that could be
        # changed at runtime.
        if not self.config.enable_extra_args:
            return args

        # Override the defaults with the parameters
        # Three sources for a given args attribute in the order of
        # priority
        #
        # 1. command line
        # 2. Configuration
        # 3. Default

        transform = self.name
        readonly = self.config.readonly
        cmdargs = self.config.get_cmdline_args()

        # Module-specific args..
        supported_extra_args = self.get_supported_extra_args()

        # Insert the global args if not already present. Module
        # specific value overrides the global values
        duplicates = []
        present = [a["name"] for a in supported_extra_args]
        for arg in self.config.supported_extra_args:
            arg = copy.copy(arg)
            if arg["name"] not in present:
                supported_extra_args.append(arg)
                present.append(arg["name"])
            else:
                duplicates.append(arg["name"])

        if len(duplicates) > 0:
            msg = "Module-specific args over-riding the global args\n"
            msg += "Args : {}".format(", ".join(duplicates))
            logger.warning(
                "Module args over-riding the global args",
                extra={"transform": self.name, "data": msg},
            )

        # Collect the final values for all the defaults
        final = {}
        for a in supported_extra_args:
            name = a["name"]
            transform_cmdlabel = "{}:{}".format(transform, name)
            global_cmdlabel = "global:{}".format(name)
            default = a["default"]
            if callable(default):
                default = default()
            required = a["required"]
            if required and not readonly:
                # Required and specified on the command line...
                if transform_cmdlabel in cmdargs:
                    final[name] = cmdargs[transform_cmdlabel]
                elif global_cmdlabel in cmdargs:
                    final[name] = cmdargs[global_cmdlabel]
                elif name in args:
                    final[name] = args[name]
                else:
                    logger.error(
                        "Invalid configuration",
                        extra={
                            "transform": self.name,
                            "data": "Variable {} for transform {} is required but missing in command line".format(
                                name, self.name
                            ),
                        },
                    )
                    raise Exception(
                        "Missing Commandline arg: {} or {}".format(
                            transform_cmdlabel, global_cmdlabel
                        )
                    )
            elif transform_cmdlabel in cmdargs:
                # Optional but specified on the command line
                final[name] = cmdargs[transform_cmdlabel]
            elif global_cmdlabel in cmdargs:
                # Optional but specified on the command line
                final[name] = cmdargs[global_cmdlabel]
            elif name in args:
                # Priority 2
                final[name] = args[name]
            else:
                # Priority 3
                final[name] = default

        # => Log what has happened...
        msg = ""
        for k, v in final.items():
            msg += "{}: {}\n".format(k, v)
        logger.debug(
            "Configuration has been overridden",
            extra={"transform": self.name, "data": msg},
        )

        args.update(final)

        return args

    def preload_validate_conf(self, conf):
        """
        Check whether this configuration is even valid?

        Args:
           conf: Module configuration specified in the config file

        Raises:
            Generic exception if conf is not a dictionary or if the version doesnt match

        """

        if not (isinstance(conf, dict) and len(conf) > 0):
            logger.error(
                "Conf is not a valid dictionary",
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Conf is not a valid dictionary")

        if self.version != conf.get("version", 1.0):
            logger.error(
                "Version mismatch",
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Version mismatch between config and module")

    def preload_validate_self(self):
        """
        Syntactic check of the supported_extra_args, output
        other future configurations
        """
        supported_extra_args = self.supported_extra_args
        if not isinstance(supported_extra_args, list):
            logger.error(
                "Invalid configuration. Expected {}, actual {}".format(
                    "list", str(type(supported_extra_args))
                ),
                EXTRA=self.config.get_extra(
                    {
                        "transform": self.name,
                    }
                ),
            )
            raise Exception("Supported extra argument should be a list of dicts")

        for i, a in enumerate(supported_extra_args):
            if not isinstance(a, dict):
                logger.error(
                    "Invalid configuration. Entry {} of supported_extra_args: Expected {}, actual {}".format(
                        i, "dict", str(type(a))
                    ),
                    EXTRA=self.config.get_extra(
                        {
                            "transform": self.name,
                        }
                    ),
                )
                raise Exception("Supported extra argument should be a list of dicts")

            required = [
                "name",
                "description",
                "default",
                "required",
            ]
            missing = [x for x in required if x not in a]
            if len(missing) > 0:
                logger.error(
                    "Invalid configuration. Entry {} of supported_extra_args: Missing attributes: {}".format(
                        i, ", ".join(missing)
                    ),
                    extra=self.config.get_extra(
                        {"transform": self.name, "data": str(a)}
                    ),
                )
                raise Exception("Missing attributes in one of the supported extra args")

        if not hasattr(self, "outputs"):
            raise Exception("Output definition is missing in transform. Critical error")

        if not isinstance(self.outputs, dict):
            raise Exception("Output definition (self.outputs) should be a dict")

        for k, v in self.outputs.items():
            if not isinstance(k, str):
                raise Exception(
                    "Output definition (self.outputs) should have string frame names only ({})".format(
                        k
                    )
                )

            if not isinstance(v, dict):
                raise Exception(
                    "Output definition (self.outputs) should have dict for each frame name ({})".format(
                        k
                    )
                )

    def configure(self, conf):
        """
        Load the module and prepare to execute

        Args:
           conf: Module configuration specified in config

        """
        readonly = self.config.readonly

        # => Check whether internal configuration is valid
        self.preload_validate_self()

        # Validate the configuration specified
        self.preload_validate_conf(conf)

        self.conf = copy.deepcopy(conf)

        if "name" in conf:
            self.name = conf["name"]

        if "output_version" in conf:
            self.output_version = conf["output_version"]

        if "test" in conf:
            self.test = True

        if "enable" in conf:
            self.enable = conf["enable"]

        if "debug" in conf:
            self.debug = conf["debug"]

        if "role" in conf:
            self.roles_current = conf["role"]

        # Add a readonly check to avoid side effects of the enrichgui
        # scanning the transform.
        if "args" in conf:
            if not readonly:
                self.args = self.preload_clean_args(conf["args"])

        if "dependencies" in conf:
            self.dependencies = conf["dependencies"]

    #####################################################
    # => Testing
    #####################################################
    def get_test_conf(self):
        """
        Function to get test configurations.

        This can be used to dynamically generate
        test configurations by overiding this function
        in the derived class.
        """
        return self.testdata.get("conf", {})

    #####################################################
    # => Validation.
    #####################################################
    def validate(self, what, state):
        """
        Validate various aspects of the transform state,
        configuration, and data. Dont override this function. Override
        specific functions such as `validate_args`.

        Args:
            what (str): What should be validated? args, conf, results etc.
            state (object): State to checked

        Returns:

             Nothing

        Raises:

             Exception ("Validation error")

        """

        func = getattr(self, "validate_" + what, None)
        if hasattr(func, "__call__"):
            return func(what, state)
        else:
            logger.error(
                "Cannot find function to validate {}".format(what),
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Validation error")

    def validate_conf(self, what, state):
        """
        Validate user-specified configuration for both content and
        structure.

        Args:
            what (str): "conf"
            state (object): State to checked

        Returns:

             Nothing

        Raises:

             Exception ("Validation error")

        """
        if self.name in [None, "Unknown"]:
            raise Exception("Invalid name for transform")

        if self.node_type == "Unknown":
            raise Exception("Invalid node type")

        if not isinstance(self.dependencies, dict):
            raise Exception("Dependencies should be a dictionary")

    def validate_args(self, what, state):
        """
        Validate user-specified args for both content and
        structure against args_schema.

        Args:
            what (str): "args"
            state (object): State to checked

        Returns:

             Nothing

        Raises:

             Exception ("Validation error")

        """
        # Validate the schema
        try:
            jsonschema.validate(self.args, self.args_schema)
        except:
            logger.exception(
                "Invalid/insufficient arguments. Doesnt match schema",
                extra={"transform": self.name},
            )

    def validate_input(self, what, state):
        """
        Validate input data including dataframes in
        the state

        Args:
            what (str): "args"
            state (object): State to checked

        Returns:

             Nothing

        Raises:

             Exception ("Validation error")

        """
        pass

    def validate_results(self, what, state):
        """
        Post-processing validation check to make sure that the
        computation has happened correctly - existance and values
        of the results.

        Args:
            what (str): "results"
            state (object): State to checked

        Returns:

             Nothing

        Raises:

             Exception ("Validation error")

        """

        pass

    def validate_testdata(self, what, state):
        """
        Validate the test data provided for structure and
        semantics. Test for existance of files and appropriate load
        commands being present.

        Args:
            what (str): "testdata"
            state (object): State to checked (generally ignored)

        Returns:

             Nothing

        Raises:

             Exception ("Validation error")
        """
        if (
            (not hasattr(self, "testdata"))
            or (self.testdata is None)
            or (not isinstance(self.testdata, dict))
        ):
            raise Exception("Invalid test data. Either is it None or not a dictionary")

        data = self.testdata.get("data", {})
        for framename, detail in data.items():
            if "filename" not in detail:
                raise Exception(
                    "Missing frame detail: filename. Only file-based test input supported for now"
                )
            if "params" not in detail:
                raise Exception("Missing frame detail: params")
            if not isinstance(detail["params"], dict):
                raise Exception("Invalid frame detail: params should be a dictionary")
            frametype = detail.get("frametype", "pandas")
            if (frametype in ["pandas", "spark"]) and ("sep" not in detail["params"]):
                raise Exception(
                    "Missing frame detail: A separator 'sep' is minimum required parameter"
                )

        conf = self.testdata.get("conf", {})
        if not isinstance(conf, dict):
            raise Exception("Invalid test configuration: conf should be a dictionary")

    #####################################################
    # => Initialize the system...
    #####################################################
    def initialize(self):
        """
        Called at the time of instantiating the module.

        This can be used to open connections, setup state and other
        functions.

        .. deprecated::

           Use configure/other functions to complete the initialization..

        """
        pass

    #####################################################
    # => Load the module
    #####################################################
    def load(self):
        """
        Run time loading of parameters.

        The primary use of this function is for skins. They load the
        last run details for further processing.
        """
        pass

    #####################################################
    # => Check whether preconditions have been met
    #####################################################
    def ready(self, state):
        """
        Test whether the module is ready for processing.

        This is typically not over-ridden. The platform implemets a
        number of checks including preconditions and checks before
        calling the module. The developer specifies the preconditions
        using the dependencies object (which could be overridden in
        the configuration)

        This function is there for special cases.
        """
        return True

    #####################################################
    # => Execute
    #####################################################
    def process(self, state):
        """
        Execute the module function whatever it is.

        The process function typically extracts the dataframes from
        the state, computes on it, and writes them back.

        Every module implements this function except Skins.

        Args:
           state: State object passed by the pipeline manager

        """
        pass

    ########################################
    # Helper functions
    ########################################
    def get_credentials(self, name):
        """
        Looks up the siteconf in ENRICH_ETC and
        returns appropriate entry

        This name should in specific in the credentials
        section of siteconf.


        """
        if not hasattr(self.config, "siteconf"):
            raise Exception("No siteconf")

        siteconf = self.config.siteconf
        if not isinstance(siteconf, dict):
            raise Exception("Invalid siteconf format")

        try:
            credentials = siteconf["credentials"][name]
        except:
            logger.exception(
                "Cannot acquire credentials",
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Missing/invalid credentials")

        return credentials

    def get_versionmap(self, include_tags=False):
        """
        Export the versionmap

        Args:
            include_tags (bool): Whether to include git tags

        Returns:
            verionmap (list): List of dicts - one for each module

        """
        if not hasattr(self.config, "versionmap"):
            raise Exception("No versionmap")

        versionmap = copy.deepcopy(self.config.get_versionmap())

        # Drop tags unless specified explicitly
        if not include_tags:
            for v in versionmap:
                v.pop("alltags", [])

        return versionmap

    def get_default_metadata(self, state):
        """
        Get reuse metadata dict with some standard fields.

        Args:
            state (object): State object passed by the pipeline

        Returns:
            metadata (dict): Dictionary with standalone:pipeline schema

        """

        usecase = self.config.get_usecase()

        versionmap = self.get_versionmap()
        for v in versionmap:
            v.pop("branches", None)

        metadata = {
            "schema": "standalone:pipeline",
            "version": "1.0",
            "timestamp": datetime.now().replace(microsecond=0).isoformat(),
            "pipeline": {
                "customer": usecase,
                "usecase": usecase,
                "name": state.name,
                "description": self.config.description,
                "host": state.stats["platform"]["node"],
                "runid": state.runid,
                "pid": state.pid,
                "start_time": state.start_time.replace(microsecond=0).isoformat(),
                "end_time": state.end_time.replace(microsecond=0).isoformat(),
                "versionmap": versionmap,
                "stats": state.stats,
                "cmdline": list(sys.argv),
            },
        }

        return metadata

    #############################################
    # Helper functions
    #############################################
    def get_file(self, *args, **kwargs):
        """
        File path resolver. Insert transform and pass to the pipeline
        execution engine.

        Args:
           abspath (bool): Generate absolute path (default: True)
           extra (dict): Extra args for resolving the path

        Returns:
           path (str): Resolved path

        """

        extra = kwargs.pop("extra", {})
        extra = copy.copy(extra)
        if "transform" not in extra:
            extra["transform"] = self

        # Insert caller information?
        extra["transform_root"] = self.transform_root

        # Pass it back
        kwargs["extra"] = extra

        return self.config.get_file(*args, **kwargs)

    def get_relative_path(self, path, what="enrich_data_dir"):
        """
        Get the path relative to a predefined root

        Args:
             path (str): Path of object
             what (str): What should the root of the relative path be?

        """
        return self.config.get_relative_path(path, what)

    def note_access(self, filename, *args, **kwargs):
        """
        Note access to file to enable creation of lineage

        Args:
             filename (str): File being accessed
             args (list): Extra args to be passed to baseclass for use
        """
        self.config.note_access(filename, self, *args, **kwargs)

    def get_cache_dir(self, name=None, subdir=".", what="raw", create=False, extra={}):
        """
        Get a local directory for caching partial results.

        .. warning::

            Deprecated. Not to be used.

        Args:
             name (str): Namespace
             version (str): Version of the cache
             what (str): Class of data being stored
             create (bool): Create the cache directory
             extra (dict): Extra parameters passed to get_file

        Returns:
             path (str): Path of the cache directory

        """
        warnings.warn("Function will be removed soon", DeprecationWarning)

        if name is None:
            name = self.name

        try:
            version = self.data_version_map[what][name]
        except:
            version = 1.0

        if "cache" not in self.args:
            raise Exception("Cache directory not specified")

        cache_path = self.config.get_file(self.args["cache"], extra=extra)

        path = os.path.join(cache_path, what, name, str(version), subdir)
        path = os.path.abspath(path)
        if create:
            try:
                os.makedirs(path)
            except:
                pass

        return path

    def get_arg_overrides(self, state):
        """
        Get any over-rides provided from other transforms.

        Args:
           state (object): State object

        Returns:
            overrides (list)

        """
        return state.transform_overrides.get(self.name, [])

    def set_arg_overrides(self, state, name, detail):
        """
        Set any over-rides provided from other transforms.
        """

        if name not in state.transform_overrides:
            state.transform_overrides[name] = []
        state.transform_overrides[name].append(detail)

    def pass_args(self, state, name, detail):
        """
        Alias for set_arg_overrides
        """
        return self.set_arg_overrides(state, name, detail)

    def frame_get_overrides(self, state_detail):
        """
        Obtain any extra instructions passed by previous
        stage on how to process a frame

        Returns
        -------
            args (dict): Dictionary passed by previous transform

        """

        default = {}
        if (not isinstance(state_detail, dict)) or ("params" not in state_detail):
            return default

        params = state_detail["params"]
        if isinstance(params, dict):
            params = [params]
        for p in params:
            # Is this params of the type args?
            if p.get("type", "unknown") != "overrides":
                continue
            # Is this meant for me?
            if p.get("transform", "Unknown") != self.name:
                continue
            # Return args
            return p.get("args", {})

        return default


##################################################
# Skin base class
##################################################
class Skin(Node):
    """

    .. deprecated:: 2.0

    Renders the data computed the transforms and modules.

    This is typically used by built-in capabilities such as Search.
    An alternative to implementing this is to use the usecase apps
    capabilities (explained elsewhere)

    """

    def __init__(self, *args, **kwargs):
        super(Skin, self).__init__(*args, **kwargs)
        self.node_type = "Skin"

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

    def load(self):
        """
        Run time loading of parameters.

        Each skin loads the last run details for further processing.
        """
        pass

    def render(self):
        """
        This is a generic data rendering capability. Each
        implementation of a skin should provide this.

        This generic rendering capability inturn calls implementation
        specific rendering called render_helper (see below)

        """
        raise Unsupported("Render should be implemented by the plugin")


##################################################
# Transform objects
##################################################
class Transform(Node):
    """
    This is the base class for all transforms.
    """

    def __init__(self, *args, **kwargs):
        super(Transform, self).__init__(*args, **kwargs)
        self.node_type = "Transform"

    def configure(self, conf):

        super(Transform, self).configure(conf)

    def collapse_columns(self, details):
        """
        Collect all columns
        """
        return {}

    #####################################################
    # => Generate state management information
    #####################################################
    def get_file_params(self, name, df, path, fshandle=None):
        """
        Generate output metadata for files (required for compliance)

        Args:
            df (Dataframe): Pandas dataframe
            path (str): Path where the dataframe was dumped
            fshandle (obj): S3 filesystem handle of (s3fs)

        Returns:
            list: List of dicts

        """

        # Collect file information for files that are written to s3/filesystem
        if fshandle is not None:
            info = fshandle.info(path)
            component = {
                "filename": path,
                "sha256sum": info["ETag"].replace('"', ""),
                "filesize": "{0:0.3f} MB".format(info["size"] / (1024 * 1024)),
                "modified_time": info["LastModified"].ctime(),
                "create_time": info["LastModified"].ctime(),
            }
        else:
            root = self.config.enrich_data_dir
            component = {
                "filename": os.path.relpath(path, root),
                "sha256sum": get_checksum(path),
                "filesize": "{0:0.3f} MB".format(get_pathsize(path) / (1024 * 1024)),
                "modified_time": str(time.ctime(os.path.getmtime(path))),
                "create_time": str(time.ctime(os.path.getctime(path))),
            }

        # Insert shape as well..
        component.update({"rows": df.shape[0], "columns": df.shape[1]})

        return [
            {
                "action": "output",
                "type": "table",
                "frametype": "pandas",
                "filename": path,
                "components": [component],
                "columns": self.get_column_metadata(name, df),
                "ddl": pd.io.sql.get_schema(df, name),
            }
        ]

    def get_column_params(self, name, df):
        """
        Generate columns metadata to be associated with
        this dataframe in the state. In params form.

        Args:
            name (str): name of the dataframe being processed
            df (DataFrame): Dataframe to be documented

        Returns:
            List of dicts. Each dict has 'type' (columns) and
            columns metadata (a dict)
        """
        columns = self.get_column_metadata(name, df)

        return [{"type": "compute", "columns": columns}]

    def get_column_metadata(self, name, df):
        """
        Generate columns metadata to be associated with
        this dataframe in the state.

        Args:
            name (str): name of the dataframe being processed
            df (DataFrame): Dataframe to be documented

        Returns:
            Dict with columns metadata
        """

        sampledf = df.sample(min(10, df.shape[0]))

        columns = {}
        for index, c in enumerate(df.columns):

            # Handle the case where there are duplicate column names
            sample = [flatten(c) for c in sampledf.iloc[:, index].tolist()]

            # Handle the case where c is a complex column name
            c_slug = c
            if not isinstance(c_slug, (str, int)):
                c_slug = str(c_slug)

            columns[c_slug] = {
                "touch": self.name,  # Who is introducing this column
                "datatype": df.get_generic_dtype(c),  # What is its type
                "description": self.get_column_description(name, c),
                "version": self.get_column_version(name, c),
                "security": self.get_column_security(name, c),
                "sample": sample,
            }

        return columns

    #####################################################
    # => Column output
    #####################################################
    def lookup_column_output(self, frame, column, outputs=None):
        """
        Look through the output definition to extract the
        description. The output description sometimes specifies a
        pattern that must be matched. Invalid patterns or patterns
        that dont match are ignored.

        Args:
            frame (str): name of the dataframe being processed
            column (str): Name of the column whose description is
                        required

            outputs (dict): A dictionary that has a set of patterns for each frame.

        Returns:
            Description if found else empty string
        """

        # If not over-ride is present, then use the
        # outputs passed in the parameter
        if outputs is None:
            outputs = self.outputs
            if frame not in outputs:
                return []
            outputs = outputs[frame]

        # => Do the exact match first..
        if column in outputs:
            detail = copy.copy(outputs[column])
            if isinstance(detail, str):
                return [{"description": detail}]
            elif isinstance(detail, dict):
                if "description" not in detail:
                    detail["description"] = ""
                return [detail]
            else:
                raise Exception("Unexpected output definition")

        # Now do a regular expression match
        # First sort all patterns by length
        patterns = sorted(list(outputs.keys()), key=lambda k: len(k), reverse=True)

        selected = []
        for pattern in patterns:

            # Get the detail..
            detail = copy.copy(outputs[pattern])
            if isinstance(detail, str):
                """
                If a string is specified, then that is the description
                """
                detail = {"description": detail}

            # Get the regular expression
            matcher_re = detail.get("matcher", r"^{}$".format(pattern))

            try:
                matcher = re.search(matcher_re, column, flags=re.IGNORECASE)
                if matcher is None:
                    continue
            except:
                continue

            # Capture the regex matcher as well. It may have variables
            # from the column name. This is an advanced usecase.
            detail["matcher"] = matcher

            # Return a dictionary...
            selected.append(detail)

        return selected

    def get_column_description(self, frame, column, outputs=None):
        """
        Look through the output definition to extract the
        description. The output description sometimes specifies a
        pattern that must be matched. Invalid patterns or patterns
        that dont match are ignored.

        Args:
            frame (object): name of the dataframe being processed
            column (object): Name of the column whose description is
                        required

        Returns:
            Description if found else empty string

        """

        # There may be multiple
        matched_details = self.lookup_column_output(frame, column, outputs)

        for detail in matched_details:

            if not isinstance(detail, dict):
                # Skip due to invalid format.
                continue

            generator = detail.get("generator", None)

            if generator is None:
                # Nothing to parse
                return detail.get("description", "")

            # Now parse and apply to generate
            variables = detail.get("variables", [])
            context = {}
            for v in variables:
                try:
                    context[v] = matcher.group(v)
                except:
                    context[v] = "error"

            try:
                return generator % context
            except:
                logger.error("Error in configuration", extra={"transform": self.name})
                pass

        return ""

    def get_column_security(self, frame, column, outputs=None):
        """
        Look through the output definition to extract the security
        attributes including privacy.

        Args:
            frame (object): name of the dataframe being processed
            column (object): Name of the column whose security attributes are required

        Returns:
            dict with attribute. Could be multiple

        """
        # There may be multiple matches
        matched_details = self.lookup_column_output(frame, column, outputs)
        if len(matched_details) > 0:
            return matched_details[0].get("security", {})

        return {}

    def get_column_version(self, frame, column, outputs=None):
        """
        Look through the output definition to extract version  attributes

        Args:
            frame (object): name of the dataframe being processed
            column (object): Name of the column whose version attributes are required

        Returns:
            string (version)

        """
        # There may be multiple matches
        matched_details = self.lookup_column_output(frame, column, outputs)
        if len(matched_details) > 0:
            return matched_details[0].get("version", "v1")

        return "v1"  # default

    def validate_results(self, what, state):
        """
        Validate outputs generated by the transform
        """
        pass


class Model(Transform):
    """
    Transforms that are models.

    As of now no additional function interfaces exist. But model
    management functions will be added in future.

    """

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.roles_supported = ["Compute"]
        self.roles_current = "Compute"


##################################################
# Integration
##################################################
class Integration(Node):
    """
    Integration with thirdparty service
    """

    def __init__(self, *args, **kwargs):
        super(Integration, self).__init__(*args, **kwargs)
        self.node_type = "Integration"
