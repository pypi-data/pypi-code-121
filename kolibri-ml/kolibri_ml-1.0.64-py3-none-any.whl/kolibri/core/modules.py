from typing import Any
from typing import Optional
from typing import Text
from typing import Type

from kolibri.registry import ModulesRegistry

def find_unavailable_packages(package_names):
    """Tries to import all the package names and returns
    the packages where it failed."""
    import importlib

    failed_imports = set()
    for package in package_names:
        try:
            importlib.import_module(package)
        except ImportError:
            failed_imports.add(package)
    return failed_imports


def validate_requirements(component_names):
    """Ensures that all required python packages are installed to
    instantiate and used the passed components."""
    from kolibri.core import modules

    # Validate that all required packages are installed
    failed_imports = set()
    for component_name in component_names:
        component_class = modules.get_component_class_from_name(component_name)
        failed_imports.update(find_unavailable_packages(
            component_class.required_packages()))
    if failed_imports:  # pragma: no cover
        # if available, use the development file to figure out the correct
        # version numbers for each requirement
        raise Exception("Not all required packages are installed. " +
                        "To use this pipeline, you need to install the "
                        "missing dependencies. " +
                        "Please install {}".format(", ".join(failed_imports)))



def class_from_module_path(module_path):
    """Given the module name and path of a class, tries to retrieve the class.

    The loaded class can be used to instantiate new objects. """
    import importlib

    # load the module, will raise ImportError if module cannot be loaded
    if "." in module_path:
        module_name, _, class_name = module_path.rpartition('.')

        m = importlib.import_module(module_name)
        # get the class, will raise AttributeError if class cannot be found
        return getattr(m, class_name)
    else:
        return globals()[module_path]


def get_component_class_from_name(component_name):
    # type: (Text) -> Optional[Type[Component]]
    """Resolve component name to a registered components class."""
    if component_name not in ModulesRegistry.registry['kolibri']:
        try:
            return class_from_module_path(component_name)
        except Exception:
            raise Exception(
                "Failed to find component class for '{}'. Unknown "
                "component name. Check your configured pipeline and make "
                "sure the mentioned component is not misspelled. If you "
                "are creating your own component, make sure it is either "
                "listed as part of the `component_classes` in "
                "`kolibti.modules.py` or is a proper name of a class "
                "in a module.".format(component_name))
    return ModulesRegistry.registry['kolibri'][component_name]['class']

def load_component_by_name(component_name, model_dir, metadata, cached_component, **kwargs):
    """Resolves a component and calls its load method to init it based on a
    previously persisted model."""

    component_clz = get_component_class_from_name(component_name)
    return component_clz.load(model_dir, metadata, cached_component, **kwargs)


def create_component_by_name(component_name, config):
    """Resolves a component and calls it's create method to init it based on a
    previously persisted model."""

    component_clz = get_component_class_from_name(component_name)
    return component_clz.create(config)


def module_path_from_instance(inst):
    # type: (Any) -> Text
    """Return the module path of an instances class."""
    return inst.__module__ + "." + inst.__class__.__name__


def all_subclasses(cls):
    # type: (Any) -> List[Any]
    """Returns all known (imported) subclasses of a class."""

    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]

