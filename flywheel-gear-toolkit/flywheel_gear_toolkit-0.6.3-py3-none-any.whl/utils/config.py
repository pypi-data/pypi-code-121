"""Config module"""
import json
from pathlib import Path

from flywheel_gear_toolkit.utils.manifest import Manifest, ManifestValidationError


class Config:
    """Basic Config class akin to Manifest class.

    This class is mainly used as a helper for the
    `gear config create` function of the python-cli,
    however it may have unforseen programmatic usages.

    There is some confusing nomenclature here.  The gear
    configuration is stored in a file named `config.json`,
    within the config.json file, there are at three keys:
        * config:  configuration options for the gear,
            often booleans, integers, floats, or short
            strings.
        * inputs: Gear inputs, usually in the form of files,
            longer text.
        * destination: Information on where the gear is
            being run within the flywheel hierarchy.

    This class represents the `config.json` file, meaning
    that is has attributes which store the configuration
    options, inputs, and destination. That means that the
    class `Config` has a `config` attribute (configuration
    options) and the constructor accepts a `config`
    dictionary that contains a `config` (configuration
    options) key.
    """

    def __init__(self, config=None, path=Path.cwd()):
        """Generates initial config for gear.


        Args:
            config (dict, optional): Config dictionary with any of
                the following keys: 'config','inputs','destination'.
                Defaults to None.
            path (str or pathlib.Path, optional): Path to existing
                configuration or path to directory in which to create
                config. Defaults to Path.cwd().

        Raises:
            ConfigValidationError:
                1. When a the config kwarg has been passed but is
                    not of type dict.
                2. When a config.json exists at the passed path
                    but it is not valid JSON
                3. When a file is passed in for path, but it does
                    not exist.
        """
        self._config = dict()
        self._inputs = dict()
        self._destination = dict()
        self._path = Path(path)

        if config is not None:
            if type(config) == dict:
                if "config" in config:
                    self.config = config.get("config")
                if "inputs" in config:
                    self.inputs = config.get("inputs")
                if "destination" in config:
                    self.destination = config.get("destination")
            else:
                raise ConfigValidationError("Passed in", ["Cannot read config"])
        else:
            if self._path.is_dir():
                self._path = self._path / "config.json"
            if self._path.exists() and self._path.is_file():

                with open(self._path, "r") as fp:
                    try:
                        config = json.load(fp)
                        if "config" in config:
                            self.config = config.get("config")
                        if "inputs" in config:
                            self.inputs = config.get("inputs")
                        if "destination" in config:
                            self.destination = config.get("destination")
                    except json.JSONDecodeError:
                        raise ConfigValidationError(
                            self._path, ["Cannot read config file"]
                        )
            else:
                raise ConfigValidationError(self._path, ["File doesn't exist"])

    @property
    def config(self):
        return self._config

    @property
    def inputs(self):
        return self._inputs

    @property
    def destination(self):
        return self._destination

    @config.setter
    def config(self, config):
        self._config = config

    @inputs.setter
    def inputs(self, inputs):
        self._inputs = inputs

    @destination.setter
    def destination(self, dest):
        self._destination = dest

    def update_config(self, vals):
        self._config.update(vals)

    def update_destination(self, dest):
        self._destination.update(dest)

    def add_input(self, name, val, type_="file", api=False):
        """Add an input to the config

        Args:
            name (str): name of input
            val (str): input value, file path, api-key, context
            type_ (str, optional): file, api-key, or context.
                Defaults to "file".
            api (bool, optional): whether or not to connect to
                core to help generate config. Defaults to False.
                NOT YET IMPLEMENTED.

        Raises:
            ValueError: When file can't be resolved
            NotImplementedError: If api == True, not implemented yet.
        """
        if type_ == "file":
            if api:
                raise NotImplementedError(
                    "Adding api and context inputs is not yet supported"
                )
            else:
                path = Path(val)
                try:
                    stat_result = path.resolve().stat()
                except FileNotFoundError:
                    raise ValueError(
                        f"Cannot resolve file input at {path}, is the path correct?"
                    )

                file = {
                    "base": "file",
                    "location": {
                        "name": path.name,
                        "path": f"/flywheel/v0/input/{name}/{path.name}",
                    },
                    "object": {
                        "size": stat_result.st_size,
                        "type": None,
                        "mimetype": "application/octet-stream",
                        "modality": None,
                        "classification": {},
                        "tags": [],
                        "info": {},
                        "zip_member_count": None,
                        "version": 1,
                        "file_id": "",
                        "origin": {"type": "user", "id": ""},
                    },
                }
                self.inputs.update({name: file})
        elif type_ == "api-key":
            self.inputs.update({name: {"base": "api-key", "key": val}})
        else:
            raise NotImplementedError("Adding context inputs is not yet supported")

    @classmethod
    def default_config_from_manifest(cls, manifest):
        """Create a default config.json from a manifest file.

        Args:
            manifest (str, or pathlib.Path or Manifest): Path to
                manifest or instantiated Manifest object.

        Raises:
            ValueError: When there is a problem parsing the
                manifest.

        Returns:
            Config: new config class with a default
                configuration.
        """
        if not isinstance(manifest, Manifest):
            try:
                manifest = Manifest(manifest)
            except ManifestValidationError:
                raise ValueError("Could not load manifest to generate config")

        config = {}

        for k, v in manifest.config.items():
            if "default" in v:
                config[k] = v["default"]

        return cls(config={"config": config})

    ############### Utilities
    def to_json(self, path=None):
        to_write = {
            "config": self.config,
            "inputs": self.inputs,
            "destination": self.destination,
        }
        with open(path if path is not None else str(self._path), "w") as fp:
            json.dump(to_write, fp, indent=4)

    def __str__(self):  # pragma: no cover
        to_write = {
            "config": self.config,
            "inputs": self.inputs,
            "destination": self.destination,
        }
        return json.dumps(to_write, indent=4)


class ConfigValidationError(Exception):
    """Indicates that the file at path is invalid.

    Attributes:
        path (str): The path to the file
        errors (list(str)): The list of error messages
    """

    def __init__(self, path, errors):
        super(ConfigValidationError, self).__init__()
        self.path = path
        self.errors = errors

    def __str__(self):
        result = "The config at {} is invalid:".format(self.path)
        for error in self.errors:
            result += "\n  {}".format(error)
        return result
