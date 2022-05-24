from . import loader
from zope.interface import Interface
from zope.schema import NativeStringLine

import logging


logger = logging.getLogger(__name__)


class IIncludePluginsDirective(Interface):
    """Auto-include any ZCML in the dependencies of this package."""

    target = NativeStringLine(
        title="Package to auto-include for",
        description="Auto-include all plugins to this package.",
        # Note: z3c.autoinclude has required=True
        required=False,
    )

    file = NativeStringLine(
        title="ZCML filename to look for",
        description="""
        Name of a particular ZCML file to look for.
        If omitted, autoinclude will scan for standard filenames
        (e.g. meta.zcml, configure.zcml, overrides.zcml)
        """,
        required=False,
    )


def includePluginsDirective(context, target="", file=None):
    if file is None:
        zcml_to_look_for = ["meta.zcml", "configure.zcml"]
    else:
        zcml_to_look_for = [file]
    dists = loader.load_packages(target)
    for filename in zcml_to_look_for:
        loader.load_configure(context, filename, dists)


def includePluginsOverridesDirective(context, target="", file=None):
    if file is None:
        zcml_to_look_for = ["overrides.zcml"]
    else:
        zcml_to_look_for = [file]
    dists = loader.load_packages(target)
    for filename in zcml_to_look_for:
        loader.load_overrides(context, filename, dists)
