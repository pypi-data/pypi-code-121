"""A module to generate a Nipype interface for gear toolkit context."""

import logging
import re
import typing as t
from typing import Optional

try:
    from nipype.interfaces.base import (
        BaseInterfaceInputSpec,
        File,
        SimpleInterface,
        TraitedSpec,
        traits,
    )
except (ModuleNotFoundError, ImportError) as e:
    raise RuntimeError("Need the `nipype` extra to use this module.") from e

ContextType = t.Union[traits.TraitType, File]

log = logging.getLogger(__name__)

GLOBALS = globals()


def get_traits_object(
    datatype, description: Optional[str] = None
) -> t.Union[None, ContextType]:
    """Returns the corresponding traits for the input datatype."""
    if datatype == "boolean":
        return traits.Bool(desc=description)
    elif datatype == "string" or datatype == "context":
        return traits.Str(desc=description)
    elif datatype == "integer":
        return traits.Int(desc=description)
    elif datatype == "number":
        return traits.Float(desc=description)
    elif datatype == "array":
        return traits.List(desc=description)
    elif datatype == "file":
        return File(desc=description)
    else:
        raise TypeError(
            f"{datatype} type is not supported. Please only use valid datatype."
        )


class GearContextInterfaceInputSpec(BaseInterfaceInputSpec):
    """InputSpec for GearContextInterface."""

    # TODO: consider adding context as input
    config_dict = traits.Dict(mandatory=True, desc="Gear config.json as dictionary")


class GearContextInterfaceOutputSpecBase:
    """A class factory for building nipype OutputSpec from gear manifest.json."""

    @staticmethod
    def get_outputspec_attr(manifest: t.Dict = None) -> t.Dict[str, ContextType]:
        """Returns OutputSpect attributes."""
        attrs = {}
        for k, v in manifest.get("config").items():
            traits_obj = get_traits_object(v["type"], v.get("description"))
            if traits_obj:
                # prefixing with "config_" to avoid collision with inputs
                attrs[f"config_{k}"] = traits_obj

        for k, v in manifest.get("inputs").items():
            if v["base"] in ["file", "context"]:
                traits_obj = get_traits_object(v["base"], v.get("description"))
                # prefixing with "inputs_" to avoid collision with config
                if traits_obj:
                    attrs[f"inputs_{k}"] = traits_obj

        return attrs

    @staticmethod
    def get_class_name(manifest: t.Dict = None) -> t.AnyStr:
        """Return class name from gear name in manifest.

        Example: 'my-gear' -> MyGearContextInterface
        """
        gn = manifest.get("name")
        gn_clean_cap = "".join([x.capitalize() for x in re.split("[^a-zA-Z0-9]", gn)])
        return f"{gn_clean_cap}ContextInterfaceOutputSpec"

    @classmethod
    def factory(cls, manifest):
        """Returns an OutputSpec class based on manifest.json"""
        class_name = cls.get_class_name(manifest)
        attrs = {"_manifest": manifest, "__module__": __name__}
        traits_attrs = cls.get_outputspec_attr(manifest)
        attrs.update(traits_attrs)
        output_spec = type(class_name, (cls, TraitedSpec), attrs)
        # if class_name not in GLOBALS:  # needed for pickle
        #     GLOBALS[class_name] = output_spec
        return output_spec

    def __getstate__(self):
        # To give a hand to pickle dump those dynamically built classes
        if self.__class__.__name__ not in GLOBALS:  # needed for pickle
            GLOBALS[self.__class__.__name__] = self.__class__
        return (self.__dict__, self.__class__._manifest)

    def __setstate__(self, state):
        # To give a hand to pickle load those dynamically built classes
        if self.__class__.__name__ in GLOBALS:  # needed for pickle
            self.__class__ = GLOBALS[self.__class__.__name__]
        else:
            self.__class__ = self.__class__.factory(state[1])
        self.__dict__.update(state[0])


class GearContextInterfaceBase(SimpleInterface):
    """A class factory for building nipype Intefaces from gear manifest.json."""

    @staticmethod
    def get_class_name(manifest: t.Dict = None) -> t.AnyStr:
        """Returns the class name from the gear name in manifest.

        Example: 'my-gear' -> 'MyGearContextInterface'"""
        gn = manifest.get("name")
        gn_clean_cap = "".join([x.capitalize() for x in re.split("[^a-zA-Z0-9]", gn)])
        return f"{gn_clean_cap}ContextInterface"

    @classmethod
    def factory(cls, manifest: t.Dict = None) -> type:
        """Returns a new GearContextInterface instance for the given manifest."""
        class_name = cls.get_class_name(manifest)
        attrs = {
            "_run_interface": cls._run_interface,
            "_manifest": manifest,
            "input_spec": GearContextInterfaceInputSpec,
            "output_spec": GearContextInterfaceOutputSpecBase.factory(manifest),
        }
        interface = type(class_name, (cls,), attrs)

        return interface

    def _run_interface(self, runtime):
        outputs = self._outputs().get()
        config = self.inputs.config_dict.get("config")
        inputs = self.inputs.config_dict.get("inputs")

        # Parse config_dict
        for k, v in outputs.items():
            if k.startswith("config_"):
                self._results[k] = config.get(k.split("config_")[1])
            elif k.startswith("inputs_"):
                input_key = k.split("inputs_")[1]
                base_type = inputs[input_key].get("base")
                if base_type == "context":
                    self._results[k] = inputs[input_key].get("value")
                if base_type == "file":
                    self._results[k] = inputs[input_key].get("location").get("path")

        return runtime

    def __getstate__(self):
        # To give a hand to pickle dump those dynamically built classes
        if self.__class__.__name__ not in GLOBALS:  # needed for pickle
            GLOBALS[self.__class__.__name__] = self.__class__
        return (self.__dict__, self.__class__._manifest)

    def __setstate__(self, state):
        # To give a hand to pickle load those dynamically built classes
        if self.__class__.__name__ in GLOBALS:  # needed for pickle
            self.__class__ = GLOBALS[self.__class__.__name__]
        else:
            self.__class__ = self.__class__.factory(state[1])
        self.__dict__.update(state[0])
