"""Each Orange3 add-on installs entry-points for widgets and tutorials.

Widget and example discovery is done from these entry-points.
"""

import pkgutil
import importlib
from typing import List, Optional
import pkg_resources
import logging

from .orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from orangewidget.canvas.discovery import WidgetDiscovery
    from orangecanvas.registry.base import WidgetRegistry
    from orangecanvas.registry.description import WidgetDescription
    from orangecanvas.registry.description import InputSignal
    from orangecanvas.registry.description import OutputSignal
    from orangecanvas.registry import global_registry
    from orangecanvas.registry.utils import category_from_package_globals

    def get_widget_description(widget_class) -> WidgetDescription:
        widget_cls_name = widget_class.__name__

        qualified_name = "%s.%s" % (widget_class.__module__, widget_cls_name)

        inputs = [
            InputSignal(s.name, s.type, s.handler, s.flags, s.id, s.doc)
            for s in widget_class.inputs
        ]
        outputs = [
            OutputSignal(s.name, s.type, s.flags, s.id, s.doc)
            for s in widget_class.outputs
        ]
        # Convert all signal types into qualified names.
        # This is to prevent any possible import problems when cached
        # descriptions are unpickled (the relevant code using this lists
        # should be able to handle missing types better).
        for s in inputs + outputs:
            if isinstance(s.type, type):
                s.type = "%s.%s" % (s.type.__module__, s.type.__name__)

        return WidgetDescription(
            name=widget_class.name,
            id=widget_class.id,
            version=widget_class.version,
            description=widget_class.description,
            long_description=widget_class.long_description,
            qualified_name=qualified_name,
            inputs=inputs,
            outputs=outputs,
            author=widget_class.author,
            author_email=widget_class.author_email,
            maintainer=widget_class.maintainer,
            maintainer_email=widget_class.maintainer_email,
            help=widget_class.help,
            help_ref=widget_class.help_ref,
            url=widget_class.url,
            keywords=widget_class.keywords,
            priority=widget_class.priority,
            icon=widget_class.icon,
            background=widget_class.background,
            replaces=widget_class.replaces,
        )

    NATIVE_WIDGETS_PROJECT = "oasys1"
else:
    from orangewidget.workflow.discovery import WidgetDiscovery
    from orangecanvas.registry.base import WidgetRegistry
    from orangecanvas.registry import WidgetDescription
    from orangecanvas.registry import global_registry
    from orangecanvas.registry.utils import category_from_package_globals

    if ORANGE_VERSION == ORANGE_VERSION.latest_orange:
        NATIVE_WIDGETS_PROJECT = "orange3"
    else:
        NATIVE_WIDGETS_PROJECT = "orange"

from ewoksorange import setuptools
from .canvas.utils import get_orange_canvas

logger = logging.getLogger(__name__)


def get_distribution(distroname):
    try:
        return pkg_resources.get_distribution(distroname)
    except Exception:
        return None


def add_entry_points(distribution, entry_points):
    """Add entry points to a package distribution

    :param dict entry_points: mapping of "groupname" to a list of entry points
                              ["ep1 = destination1", "ep1 = destination2", ...]
    """
    if isinstance(distribution, str):
        distroname = distribution
        dist = get_distribution(distroname)
        if dist is None:
            logger.error(
                "Distribution '%s' not found. Existing distributions:\n %s",
                distroname,
                list(pkg_resources.working_set.by_key.keys()),
            )
            raise pkg_resources.DistributionNotFound(distroname, [repr("ewoksorange")])
    else:
        dist = distribution
        distroname = dist.project_name

    entry_map = dist.get_entry_map()
    for group, lst in entry_points.items():
        group_map = entry_map.setdefault(group, dict())
        for entry_point in lst:
            ep = pkg_resources.EntryPoint.parse(entry_point, dist=dist)
            if ep.name in group_map:
                raise ValueError(
                    f"Entry point {repr(ep.name)} already exists in group {repr(group)} of distribution {repr(distroname)}"
                )
            group_map[ep.name] = ep
            logger.debug("Dynamically add entry point for '%s': %s", distroname, ep)


def create_fake_distribution(distroname, location):
    distroname = pkg_resources.safe_name(distroname)
    dist = get_distribution(distroname)
    if dist is not None:
        raise RuntimeError(
            f"A distribution with the name {repr(distroname)} already exists"
        )
    if isinstance(location, list):
        location = location[0]
    from ewoksorange import __version__

    dist = pkg_resources.Distribution(
        location=location, project_name=distroname, version=__version__
    )
    pkg_resources.working_set.add(dist)
    return dist


def get_subpackages(package):
    for pkginfo in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if pkginfo.ispkg:
            yield importlib.import_module(pkginfo.name)


def register_addon_package(package, distroname: Optional[str] = None):
    """An Orange3 add-on package which has not been installed."""
    entry_points = dict()
    packages = list(get_subpackages(package))
    if not distroname:
        distroname = package.__name__.split(".")[-1]
    setuptools.update_entry_points(packages, entry_points, distroname)
    dist = create_fake_distribution(distroname, package.__path__)
    add_entry_points(dist, entry_points)


def widget_discovery(discovery, distroname, subpackages):
    dist = pkg_resources.get_distribution(distroname)
    for pkg in subpackages:
        discovery.process_category_package(pkg, distribution=dist)


def iter_entry_points(group):
    """Do not include native orange entry points"""
    for ep in pkg_resources.iter_entry_points(group):
        if ep.dist.project_name.lower() != NATIVE_WIDGETS_PROJECT:
            yield ep


def global_registry_objects() -> List[WidgetRegistry]:
    registry_objects = list()
    scene = None
    canvas = get_orange_canvas()
    if canvas is not None:
        scene = canvas.current_document()
        reg = canvas.widget_registry
        if reg is not None:
            registry_objects.append(reg)
    if ORANGE_VERSION != ORANGE_VERSION.oasys_fork and scene is not None:
        reg = scene.registry()
        if reg is not None:
            registry_objects.append(reg)
    if not registry_objects:
        reg = global_registry()
        if reg is not None:
            registry_objects.append(reg)
    return registry_objects


def global_discovery_objects() -> List[WidgetDiscovery]:
    return [WidgetDiscovery(reg) for reg in global_registry_objects()]


def local_discovery_object() -> WidgetDiscovery:
    return WidgetDiscovery(WidgetRegistry())


def get_owwidget_descriptions():
    """Do not include native orange widgets"""
    disc = local_discovery_object()
    disc.run(iter_entry_points(setuptools.WIDGET_GROUP))
    return disc.registry.widgets()


def get_owwidget_description(
    widget_class, package_name: str, category_name: str, project_name: str
):
    if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
        description = get_widget_description(widget_class)
    else:
        kwargs = widget_class.get_widget_description()
        description = WidgetDescription(**kwargs)
    description.package = setuptools.orangecontrib_qualname(package_name)
    description.category = widget_class.category or category_name
    description.project_name = project_name
    return description


def get_owcategory_description(
    package_name: str, category_name: str, project_name: str
):
    description = category_from_package_globals(package_name)
    description.name = category_name
    description.project_name = project_name
    return description


def register_owcategory(
    package_name: str,
    category_name: str,
    project_name: str,
    discovery_object: Optional[WidgetDiscovery] = None,
):
    description = get_owcategory_description(package_name, category_name, project_name)
    if discovery_object is None:
        for discovery_object in global_discovery_objects():
            discovery_object.handle_category(description)
    else:
        discovery_object.handle_category(description)


def register_owwidget(
    widget_class,
    package_name: str,
    category_name: str,
    project_name: str,
    discovery_object: Optional[WidgetDiscovery] = None,
):
    register_owcategory(
        package_name, category_name, project_name, discovery_object=discovery_object
    )
    description = get_owwidget_description(
        widget_class, package_name, category_name, project_name
    )

    logger.debug("Register widget: %s", description.qualified_name)
    if discovery_object is None:
        for discovery_object in global_discovery_objects():
            if (
                discovery_object.registry is not None
                and discovery_object.registry.has_widget(description.qualified_name)
            ):
                continue
            discovery_object.handle_widget(description)
    else:
        if (
            discovery_object.registry is not None
            and discovery_object.registry.has_widget(description.qualified_name)
        ):
            return
        discovery_object.handle_widget(description)
