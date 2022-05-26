import inspect
import sys

from modulefinder import Module
from typing import TypeVar

from pydantic import BaseSettings

from .helpers import gen_random_str

VARIATION_MAGIC_STR = "__grit_variation__"
VARIATION_RESOLUTIONS_MAGIC_STR = "__grit_variation_resolutions__"

VARIATION_TYPE = TypeVar("VARIATION_TYPE")

class Variation(BaseSettings):

    debug: bool = False
    name: str = 'default'

    def __init__(self, name: str, env_prefix: str = '', debug: bool = False, **data):
        if debug:
            print(f"Inside Variation.__init__")

        if (self.__class__.__name__.startswith(VARIATION_MAGIC_STR)):
            # Inside variation
            super().__init__(name=name, debug=debug, **data)
        else:
            # Inside base class
            caller = inspect.currentframe().f_back
            caller_module = sys.modules[caller.f_globals['__name__']]

            dynamic_subclass_name = VARIATION_MAGIC_STR + gen_random_str()
            dynamic_subclass_instance_name = f'{VARIATION_MAGIC_STR}{self.__class__.__name__.lower()}__{name}'
            dynamic_subclass_instance_py = (
                f"from {caller_module.__name__} import {self.__class__.__name__}\n"
                f"class {dynamic_subclass_name}({self.__class__.__name__}, env_prefix=\"{env_prefix}\"):\n"
                f"  def __init__(self, debug = False, **data):\n"
                f"    if debug:\n"
                f"      print(\"Inside {dynamic_subclass_name}.__init__\")\n"
                f"    registration_module = sys.modules[\"{caller_module.__name__}\"]\n"
                f"    setattr(registration_module, \"{dynamic_subclass_instance_name}\", self)\n"
                f"    if debug:\n"
                f"      print(\"Registered {dynamic_subclass_instance_name} in {caller_module.__name__}\")\n"
                f"\n"
                f"    super().__init__(debug=debug, **data)\n"
                f"\n"
                f"{dynamic_subclass_name}(name=\"{name}\", env_prefix=\"{env_prefix}\", debug={debug}, **data)\n"
            )
            if debug:
                print(dynamic_subclass_instance_py)
            exec(dynamic_subclass_instance_py)

    @classmethod
    def resolve(cls, fail: bool = False):
        caller = inspect.currentframe().f_back
        caller_module = inspected_module = sys.modules[caller.f_globals['__name__']]
        # Go up and search
        while True:
            # print(f"Resolving {cls} in {inspected_module}")
            resolutions = inspected_module.__dict__.get(VARIATION_RESOLUTIONS_MAGIC_STR)
            if resolutions:
                caller_resolution = resolutions.get(cls)
                if caller_resolution:
                    return caller_resolution

            # not found, search parent module
            parent_module = '.'.join(inspected_module.__name__.split('.')[:-1])
            if len(parent_module):
                inspected_module = sys.modules[parent_module]
            else:
                if fail:
                    raise SystemExit(f"Cannot resolve {cls.__name__} in {caller_module.__name__}, did you declare any resolutions?\n  {caller.f_code.co_filename}:{caller.f_lineno}")
                else:
                    return None
    
    @classmethod
    def find_variations(cls, m: Module) -> dict[VARIATION_TYPE, list[VARIATION_TYPE]]:
        module_members = inspect.getmembers(m)
        variation_class_dict: dict[VARIATION_TYPE, list(VARIATION_TYPE)]= {}
        for _obj_name, _obj in module_members:
            if inspect.isclass(_obj) and issubclass(_obj, Variation) and not _obj_name.startswith(VARIATION_MAGIC_STR):
                variations = []
                for _obj_name2, _obj2 in module_members:
                    if _obj_name2.startswith(VARIATION_MAGIC_STR) and _obj2.__class__.__base__ == _obj:
                        variations.append(_obj2)
                
                if len(variations) > 0:
                    # print(f"  {_obj.__name__}: {list(map(lambda v: v.name, variations))}")
                    variation_class_dict[_obj] = variations
        
        return variation_class_dict

    @classmethod
    def find_variations_simple(cls, m: Module) -> dict[str, list[str]]:
        variations = cls.find_variations(m)
        return {vc.__name__.lower(): list(map(lambda v: v.name, vv)) for vc, vv in variations.items()}

    @classmethod
    def _find_variations(cls, m: Module, klass: VARIATION_TYPE) -> list[VARIATION_TYPE]:
        found_variations: list[VARIATION_TYPE] = []
        for _obj_name in m.__dict__:
            if not _obj_name.startswith(VARIATION_MAGIC_STR):
                continue

            _obj = m.__dict__[_obj_name]

            # if self.debug:
            #     print(f"Checking {_obj_name}: {_obj.__class__.__base__} against {klass.__class__}")

            if _obj.__class__.__base__ == klass:
                found_variations.append(_obj)
        
        return found_variations

    @classmethod
    def get_resolutions(cls, m: Module) -> dict[VARIATION_TYPE, VARIATION_TYPE]:
        return m.__dict__.get(VARIATION_RESOLUTIONS_MAGIC_STR)

    @classmethod
    def resolve_variations(cls, m: Module, resolutions: dict[str, str], ignore_missing: bool = False) -> dict[VARIATION_TYPE, VARIATION_TYPE]:
        _n_resolutions = {key.lower(): val for key, val in resolutions.items()}

        resolved_variations: dict[VARIATION_TYPE, VARIATION_TYPE] = {}

        # find variations in the module
        for _obj_name in m.__dict__:
            if not _obj_name.startswith(VARIATION_MAGIC_STR):
                continue

            _obj = m.__dict__[_obj_name]

            # if self.debug:
            #     print(f"Checking {_obj_name}: {_obj.__class__.__base__} against {resolutions}") 
            _obj_basecls_name_l = _obj.__class__.__base__.__name__.lower()
            if _obj_basecls_name_l in _n_resolutions and _obj.name == _n_resolutions[_obj_basecls_name_l]:
                # if self.debug:
                #     print(f"Resolved class {_obj_name} for variation {_obj.__class__.__base__} in {m.__name__}")

                resolved_variations[_obj.__class__.__base__] = _obj
        
        resolved_variations_str = {v.__name__.lower(): r for v, r in resolved_variations.items()}

        if len(resolved_variations) != len(resolutions):
            # check which we did not find
            for v, r in _n_resolutions.items():
                if v in resolved_variations_str:
                    continue
                else:
                    # TODO: provide helpful hint about declared variation values
                    # possible_resolutions = list(map(lambda v: v.name, cls._find_variations(m=m, klass=v)))
                    print(f"Could not resolve {v} to {r} in {m.__name__}")
            
            if not ignore_missing:
                raise Exception("Could not resolve one or more variations")
        
        module_variations = cls.find_variations_simple(m)
        if len(resolved_variations) != len(module_variations):
            # check which where not passed for resolution
            for v, r in module_variations.items():
                if v not in resolved_variations_str:
                    # TODO: provide helpful hint about declared variation values
                    print(f"{v} is left unresolved")
                    if not ignore_missing:
                        raise Exception("Some variations were unresolved")

        setattr(m, VARIATION_RESOLUTIONS_MAGIC_STR, resolved_variations)

        return resolved_variations

VARIATION_TYPE = TypeVar("VARIATION_TYPE", bound=Variation)