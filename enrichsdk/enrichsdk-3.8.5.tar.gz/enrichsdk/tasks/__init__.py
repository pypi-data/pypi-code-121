import copy
import json
import logging

logger = logging.getLogger("app")

__all__ = ["Task"]


class Task(object):
    """
    This is the task base class. This is 'executed' by
    a 'runner'
    """

    NAME = "BaseTask"

    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config")
        self.name = "BaseTask"
        self.description = "Baseclass of tasks"
        self.version = "1.0"
        self.testdata = {"data": {}}

        self.supported_extra_args = []
        """Extra arguments that can be passed on the commandline to 
        the module. 

        self.extra_args = [
               {
                  "name": "jobid",
                  "description": "Export JobID",
                  "type": "str",
                  "required": True,
                  "default": "22832",
               }
        ]
        """

    #################################################
    # Configuration the Module
    #################################################
    def preload_clean_args(self, args):
        """
        Clean the arguments before using them

        Parameters
        ----------
        args: Args specified in the config file
        """

        if not self.config.enable_extra_args:
            return args

        # Override the defaults with the parameters
        # Three sources for a given args attribute in the order of
        # priority
        #
        # 1. command line
        # 2. Configuration
        # 3. Default

        readonly = self.config.readonly
        cmdargs = self.config.get_cmdline_args()
        supported_extra_args = self.supported_extra_args

        # Collect the final values for all the defaults
        final = {}
        for a in supported_extra_args:
            name = a["name"]
            cmdlabel = "{}:{}".format(self.name, name)
            default = a["default"]
            required = a["required"]
            if required and not readonly:
                # Required and specified on the command line...
                if cmdlabel not in cmdargs:
                    logger.error(
                        "Invalid configuration",
                        extra={
                            "transform": self.name,
                            "data": "Variable {} for task {} is required but missing in command line".format(
                                name, self.name
                            ),
                        },
                    )
                    raise Exception("Invalid configuration")
                final[name] = cmdargs[cmdlabel]
            elif cmdlabel in cmdargs:
                # Optional but specified on the command line
                final[name] = cmdargs[cmdlabel]
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

    def preload_validate_self(self):
        """
        Check whether definition of the task is fine

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

            required = ["name", "description", "default", "required"]
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

    def get_default_metadata(self, state):
        """
        Get reuse metadata dict with some standard fields.
        """
        metadata = {
            "schema": "standalone:task",
            "version": "1.0",
            "timestamp": datetime.now().replace(microsecond=0).isoformat(),
            "task": {
                "usecase": self.config.usecase["org"]["name"],
                # Backward compatability
                "customer": self.config.usecase["org"]["name"],
                "name": state.name,
                "description": self.config.description,
                "host": state.stats["platform"]["name"],
                "runid": state.runid,
                "pid": state.pid,
                "start_time": state.start_time.replace(microsecond=0).isoformat(),
                "end_time": state.end_time.replace(microsecond=0).isoformat(),
                "versionmap": self.config.get_versionmap(),
                "stats": state.stats,
                "cmdline": list(sys.argv),
            },
        }

        return metadata

    def preload_validate_conf(self, conf):
        """
        Check whether this configuration is even valid?

        Parameters
        ----------
        conf: Module configuration specified in the config file
        """

        if not (isinstance(conf, dict) and len(conf) > 0):
            logger.error(
                "Conf is not a valid dictionary",
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Conf is not a valid dictionary")

        if self.version != conf.get("version", "1.0"):
            logger.error(
                "Version mismatch",
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Version mismatch between config and module")

    def get_supported_extra_args(self):
        """
        What extra command line arguments are supported

        Returns
        -------
        list: List of arg specifications

        see supported_extra_args
        """
        return copy.copy(self.supported_extra_args)

    def configure(self, spec):
        """
        Configure this task
        """

        # => Check whether internal configuration is valid
        self.preload_validate_self()

        # => Check whether passed configuration is fine
        self.preload_validate_conf(spec)

        # Make a copy of the spec
        self.spec = copy.deepcopy(spec)

        # Override attributes from the spec
        for attr in ["name", "output_version", "test", "enable"]:
            if (attr in spec) and hasattr(self, attr):
                setattr(self, attr, spec[attr])

        # Clean and load args
        args = spec.get("args", {})
        self.args = self.preload_clean_args(args)

    # => Validation code
    def validate_conf(self, what, state):
        pass

    def validate_args(self, what, state):
        pass

    def validate_results(self, what, state):
        pass

    def validate_testdata(self, what, state):

        if not hasattr(self, "testdata"):
            raise Exception("testdata element is missing")

        testdata = self.testdata
        if (
            not isinstance(testdata, dict)
            or ("conf" not in testdata)
            or ("data" not in testdata)
        ):
            raise Exception("testdata should be dictionary with conf and data elements")

    def validate(self, what, state):
        """
        Validate various aspects of the task state,
        configuration, and data. Dont override this function. Override
        specific functions such as `validate_args`.

        Args:
            what (str): What should be validated? args, conf, results etc.

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

    def initialize(self):
        """
        Initialize the task by connecting to database etc.
        """
        pass

    def get_credentials(self, name):
        """
        Helper function to access siteconf for credentials
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

    def run(self, *args, **kwargs):
        """
        Main execution func. Override this
        """
        raise Exception("Should be implemented by the derived class")


if __name__ == "__main__":
    print(vars())
    subclasses = vars()["Task"].__subclasses__()
    for cls in subclasses:
        print(cls.NAME)
