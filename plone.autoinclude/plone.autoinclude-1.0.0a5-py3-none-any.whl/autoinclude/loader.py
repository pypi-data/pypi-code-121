from pkg_resources import iter_entry_points
from pkg_resources import resource_filename
from pkg_resources import working_set
from zope.configuration.xmlconfig import include
from zope.configuration.xmlconfig import includeOverrides

import importlib
import logging
import os


logger = logging.getLogger(__name__)


# Dictionary of project names and packages that we have already imported.
_known_module_names = {}

# Maybe allow ModuleNotFoundError.
# This can be a boolean (0/1) or a list of project names (from setup.py),
# separated by comma.
AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR = os.getenv(
    "AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR", ""
)
ALLOW_MODULE_NOT_FOUND_SET = set()
ALLOW_MODULE_NOT_FOUND_ALL = False
try:
    ALLOW_MODULE_NOT_FOUND_ALL = bool(int(AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR))
except (ValueError, TypeError):
    _allowed = AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR.replace(" ", "").split(",")
    if _allowed:
        ALLOW_MODULE_NOT_FOUND_SET = set(_allowed)


def load_z3c_packages(target=""):
    """Load packages from the z3c.autoinclude.plugin entry points.

    After running the function, the packages have been imported.
    This returns a dictionary of package names and packages.
    """
    dists = {}
    for ep in iter_entry_points(group="z3c.autoinclude.plugin"):
        # If we look for target 'plone' then only consider entry points
        # that are registered for this target (module name).
        # But if the entry point is not registered for a specific target,
        # we can include it.
        if target and ep.module_name != target:
            continue
        module_name = ep.dist.project_name.replace("-", "_")
        if module_name not in _known_module_names:
            try:
                dist = importlib.import_module(module_name)
            except ModuleNotFoundError:
                # Note: this may happen a lot, at least for z3c.autoinclude,
                # because the project name may not be the same as the package/module.
                # If we accept it, we may hide real errors though:
                # the module may be there but have an ImportError.
                if (
                    not ALLOW_MODULE_NOT_FOUND_ALL
                    and module_name not in ALLOW_MODULE_NOT_FOUND_SET
                ):
                    logger.error(
                        f"Could not import {module_name}. Set environment variable "
                        "AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR=1 if you want to "
                        f"allow this. Or set it to '{module_name}' to only allow for "
                        "this project. Can be a comma-separated list of project "
                        "names. Or replace the z3c.autoinclude.plugin entry point of "
                        "this project with plone.autoinclude.plugin and a module name."
                    )
                    raise
                logger.exception(
                    f"Could not import {module_name}. Accepted due to "
                    "AUTOINCLUDE_ALLOW_MODULE_NOT_FOUND_ERROR environment variable."
                )
                _known_module_names[module_name] = None
                continue
            _known_module_names[module_name] = dist
        dist = _known_module_names[module_name]
        if dist is not None:
            dists[module_name] = dist
    return dists


def load_own_packages(target=""):
    """Load packages from the plone.autoinclude.plugin entry points.

    After running the function, the packages have been imported.
    This returns a dictionary of package names and packages.

    Etnry points are like this:

        [plone.autoinclude]
        target = plone
        module = collective.mypackage

    Both options are optional, but you must have at least one,
    and it must have a value.
    """
    dists = {}
    for wsdist in working_set:
        eps = wsdist.get_entry_map("plone.autoinclude.plugin")
        if not bool(eps):
            continue
        # If we look for target 'plone' then only consider entry points
        # that are registered for this target (module name).
        # But if the entry point is not registered for a specific target,
        # we can include it.  The biggest reason for doing this,
        # is that I first thought you could not specify both
        # target and module at the same time.
        module_name = None
        if "target" in eps:
            if target and eps["target"].module_name != target:
                # entry point defines target X but we only want target Y.
                continue
            module_name = wsdist.project_name.replace("-", "_")
        if "module" in eps:
            # We could load the dist with ep.load(), but we do it differently.
            module_name = eps["module"].module_name
        if module_name is None:  # pragma: no cover
            # We could log a warning, but really this is an error.
            raise ValueError(
                "plone.autoinclude.plugin entry point with no suitable name found."
            )
        if module_name not in _known_module_names:
            # We could try/except ModuleNotFoundError, but this is an unexpected error.
            dist = importlib.import_module(module_name)
            _known_module_names[module_name] = dist
        else:
            dist = _known_module_names[module_name]
        dists[module_name] = dist
    return dists


def load_packages(target=""):
    """Load packages from the autoinclude entry points.

    After running the function, the packages have been imported.
    This returns a dictionary of package names and packages.
    """
    dists = load_own_packages(target=target)
    z3c_dists = load_z3c_packages(target=target)
    dists.update(z3c_dists)
    return dists


def get_zcml_file(module_name, zcml="configure.zcml"):
    try:
        filename = resource_filename(module_name, zcml)
    except ModuleNotFoundError:
        # Note: this may happen a lot, at least for z3c.autoinclude,
        # because the project name may not be the same as the package/module.
        logger.exception(f"Could not import {module_name}.")
        _known_module_names[module_name] = None
        return
    if not os.path.isfile(filename):
        return
    return filename


def load_zcml_file(
    context, module_name, package=None, zcml="configure.zcml", override=False
):
    filename = get_zcml_file(module_name, zcml)
    if not filename:
        return
    if package is None and context.package is not None:
        package = context.package
    if override:
        logger.debug(f"Loading {module_name}:{zcml} from {filename} in override mode.")
        # The package as third argument seems not needed because we have an absolute file name.
        # But it *is* needed when that file loads other relative files.
        includeOverrides(context, filename, package)
    else:
        logger.debug(f"Loading {module_name}:{zcml} from {filename}")
        include(context, filename, package)


def load_configure(context, filename, dists):
    logger.debug(f"Loading {filename} files.")
    for module_name, package in dists.items():
        logger.debug(module_name)
        load_zcml_file(context, module_name, package, filename)


def load_overrides(context, filename, dists):
    logger.debug(f"Loading {filename} files in override mode.")
    for module_name, package in dists.items():
        logger.debug(module_name)
        load_zcml_file(context, module_name, package, "overrides.zcml", override=True)
