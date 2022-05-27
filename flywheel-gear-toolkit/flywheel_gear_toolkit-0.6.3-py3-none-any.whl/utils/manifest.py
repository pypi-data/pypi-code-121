"""Manifest module"""
import copy
import json
import logging
import os
from json import JSONDecodeError
from pathlib import Path

import jsonschema
from dotty_dict import dotty
from gears.generator import get_master_schema

log = logging.getLogger(__name__)


class Manifest:
    """A class to host a manifest and a methods around it.

    Args:
        manifest (Path-like or dict): Path to a manifest.json file or a manifest dictionary.
            If none is provided, try to load manifest.json from the current working directory.

    Attributes:
        manifest (dotty_dict.Dotty): Dictionary (dotty-enhanced version to be exact) of the
            manifest.json file.

    Raises:
        FileNotFoundError: If no manifest.json found
    """

    def __init__(self, manifest=None):
        self._schema = None
        self._path = None
        self.manifest = None
        if isinstance(manifest, dict):
            self.manifest = dotty(manifest)
        else:
            if not manifest:  # look into current directory
                self._path = (Path(".") / "manifest.json").absolute()
                if not self._path.exists():
                    raise FileNotFoundError(
                        f"manifest.json not found in cwd ({os.getcwd()}"
                    )
                log.info("Using manifest.json in current working directory.")
                self.manifest = dotty(self.get_manifest_from_file(path=self._path))
            else:  # Load from path
                self._path = Path(manifest)
                self.manifest = dotty(self.get_manifest_from_file(path=self._path))

    @property
    def schema(self):
        """Returns the json schema definition of the manifest.json file."""
        if not self._schema:
            self._schema = get_master_schema()
        return self._schema

    @property
    def author(self):
        """Returns manifest author"""
        return self.get_value("author")

    @property
    def config(self):
        """Returns manifest config"""
        return self.get_value("config")

    @property
    def description(self):
        """Returns manifest description"""
        return self.get_value("description")

    @property
    def inputs(self):
        """Returns manifest inputs"""
        return self.get_value("inputs")

    @property
    def label(self):
        """Returns manifest label"""
        return self.get_value("label")

    @property
    def license(self):
        """Returns manifest license"""
        return self.get_value("license")

    @property
    def name(self):
        """Returns manifest name"""
        return self.get_value("name")

    @property
    def source(self):
        """Returns manifest source"""
        return self.get_value("source")

    @property
    def url(self):
        """Returns manifest url"""
        return self.get_value("url")

    @property
    def version(self):
        """Returns manifest version"""
        return self.get_value("version")

    @property
    def environment(self):
        return self.get_value("environment")

    def __getitem__(self, dotty_key):
        """Return any value of the manifest by passing the dotty-dict key

        Args:
            dotty_key (str): A string representing a key or nested key (e.g.
                custom.gear-builder.image)
        """
        return self.get_value(dotty_key)

    @staticmethod
    def get_manifest_from_file(path=None):
        """Returns the dictionary representation of the manifest.json at path.

        Args:
            path (Path-like): Path to manifest. If None, look for manifest.json in current
                directory.

        Returns:
            (dict): The manifest as a dictionary
        """
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(str(path))

        with open(path, "r") as fp:
            try:
                manifest = json.load(fp)
            except JSONDecodeError as e:
                raise ManifestValidationError(
                    path,
                    [f"Error decoding at line {e.lineno}, column {e.colno}"],
                )

        return manifest

    def get_value(self, dotty_key):
        """Returns value found at dotty_key (e.g. 'custom.gear-builder.image') if any.

        More on dotty-dict notation at [here](https://github.com/pawelzny/dotty_dict)

        Args:
            dotty_key (str): A string representing a key or nested key (e.g.
                custom.gear-builder.image)
        """
        return self.manifest.get(dotty_key)

    def to_json(self, path, validate=True):
        """Save as json file to `path`"""
        if not Path(path).name.endswith(".json"):
            raise ValueError("Incorrect path. Must end with .json")

        if validate:
            try:
                self.validate()
            except ManifestValidationError:
                log.warning("The saved manifest.json is invalid")

        with open(path, "w") as fp:
            json.dump(dict(self.manifest), fp, indent=4)

    def get_docker_image_name_tag(self):
        """Returns docker image tag from either locations

        Look first at 'custom.gear-builder.image'. If not defined there, look at
        'custom.docker-image' and log a warning.
        """
        image = self.get_value("custom.gear-builder.image")
        if not image:
            image = self.get_value("custom.docker-image")
            if image:
                log.warning(
                    'Defining image in "custom.docker-image" is deprecated. '
                    'Please use "custom.gear-builder.image" instead'
                )
        return image

    def validate(self):
        """Validates manifest.

        Raises:
            ManifestValidationError: If errors are found in the manifest.
        """
        errors = self._validate()
        if errors:
            raise ManifestValidationError(self._path, errors)

    def is_valid(self):
        """Returns True if manifest is valid, False otherwise."""
        try:
            self.validate()
        except ManifestValidationError:
            return False
        return True

    def _validate(self):
        """Runs validation checks on manifest.

        Returns:
            (list): List of errors found.
        """
        errors = []
        errors += self._validate_schema()
        errors += self._validate_config_default()
        errors += self._is_docker_image_defined()
        errors += self._is_version_matches()
        errors += self._is_docker_images_match()
        return errors

    def _validate_schema(self):
        """Validates the manifest against its schema definition"""
        validator = jsonschema.Draft4Validator(self.schema)
        errors = []
        for error in sorted(validator.iter_errors(dict(self.manifest)), key=str):
            errors.append(error.message)
        return errors

    def _validate_config_default(self):
        """Validate default value in manifest."""
        errors = []
        if "config" in self.manifest:
            config_schema = self.derive_config_schema(full=False)
            validator = jsonschema.Draft4Validator(config_schema)
            # mock a config dict with default values from manifest
            config = {
                "config": {
                    k: v["default"]
                    for k, v in self.manifest.get("config", {}).items()
                    if "default" in v
                }
            }

            for error in sorted(validator.iter_errors(config), key=str):
                errors.append(error.message)
        return errors

    def derive_config_schema(self, full=True):
        """Returns json schema for config from manifest
        Adapted from
        https://gitlab.com/flywheel-io/public/gears/-/blob/master/gears/generator.py#L66

        Args:
            full (bool): Whether to derive a "full" config schema, to be used
                when validating a real config that has been populated.  Set
                "full" to false if you are just validating the default
                values in a config.
        """
        # Config jsonschema
        schema = {
            "title": "Config schema for manifest",
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "config": {"type": "object", "properties": {}, "required": []},
            },
            "required": ["config"],
        }

        # Copy over constraints from manifest
        for key in self.manifest["config"]:
            # Copy constraints, removing 'base' and 'description' keywords which are not constraints
            value = copy.deepcopy(self.manifest["config"][key])
            value.pop("base", None)
            value.pop("description", None)
            optional = value.pop("optional", False)
            schema["properties"]["config"]["properties"][key] = value

            # Require the key be present unless optional flag is set.
            if not optional:
                # Always add the required key if full
                if full:
                    schema["properties"]["config"]["required"].append(key)
                # Else only add the required key if a default value is
                # specified (GEAR-1866)
                elif value.get("default"):
                    schema["properties"]["config"]["required"].append(key)

        # After handling each key, remove required array if none are present.
        # Required by jsonschema (minItems 1).
        if len(schema["properties"]["config"]["required"]) == 0:
            schema["properties"]["config"].pop("required", None)

        # Important: check our work - the schema must be a valid schema.
        jsonschema.Draft4Validator.check_schema(schema)

        return schema

    def _is_docker_image_defined(self):
        """Returns a list of errors if not defined."""
        errors = []
        docker_image = self.get_docker_image_name_tag()
        if not docker_image:
            errors += ['"custom.gear-builder.image" missing from manifest']
        return errors

    def _is_docker_images_match(self):
        """Returns a list of errors if docker images are different."""
        errors = []
        docker_image_1 = self.get_value("custom.gear-builder.image")
        docker_image_2 = self.get_value("custom.docker-image")
        if docker_image_1 and docker_image_2 and docker_image_1 != docker_image_2:
            errors += [
                '"custom.gear-builder.image" is different from "custom.docker-image"'
            ]
        return errors

    def _is_version_matches(self):
        """Returns a list of errors if version does not match."""
        errors = []
        docker_image = self.get_docker_image_name_tag()
        if docker_image and ":" in docker_image:
            _, im_tag = docker_image.split(":")
            if im_tag != self.version:
                errors += ["version and docker image tag do not match"]

        return errors


class ManifestValidationError(Exception):
    """Indicates that the file at path is invalid.

    Attributes:
        path (str): The path to the file
        errors (list(str)): The list of error messages
    """

    def __init__(self, path, errors):
        super(ManifestValidationError, self).__init__()
        self.path = path
        self.errors = errors

    def __str__(self):
        result = "The manifest at {} is invalid:".format(self.path)
        for error in self.errors:
            result += "\n  {}".format(error)
        return result
