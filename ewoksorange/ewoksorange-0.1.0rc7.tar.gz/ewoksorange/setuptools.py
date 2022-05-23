"""An Orange3 add-on project has a NAMESPACE_PACKAGE package
it namespace declaration in its __init__.py

Sub-packages with the attribute `NAME` are considered Orange3
category packages.

Using `ewoksorange.setuptools.setup` instead of `setuptools.setup`
in the addon project ensures the NAMESPACE_PACKAGE package is
installed according to the Orange3 conventions so that:
* the addon can be found on pypi
* the widgets can be auto-discovered by Orange3
"""

import os
import sys
import importlib
from glob import glob
from pprint import pprint
from setuptools import find_packages
from setuptools import setup as _setup


from .orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.canvas.conf import WIDGETS_ENTRY as WIDGET_GROUP
else:
    from orangewidget.workflow.config import WIDGETS_ENTRY as WIDGET_GROUP


NAMESPACE_PACKAGE = "orangecontrib"
PYPI_KEYWORD = "orange3 add-on"
TUTORIAL_GROUP = WIDGET_GROUP + ".tutorials"
HELP_GROUP = "orange.canvas.help"
TUTORIAL_EXT = ("*.ows",)
ICON_EXT = ("*.png", "*.svg")


def include_documentation(local_dir, install_dir):
    if "bdist_wheel" in sys.argv and not os.path.exists(local_dir):
        print(
            "Directory '{}' does not exist. "
            "Please build documentation before running bdist_wheel.".format(
                os.path.abspath(local_dir)
            )
        )
        sys.exit(0)

    doc_files = []
    for dirpath, _, files in os.walk(local_dir):
        doc_files.append(
            (
                dirpath.replace(local_dir, install_dir),
                [os.path.join(dirpath, f) for f in files],
            )
        )
    return doc_files


def orangecontrib_qualname(qualname):
    if ".orangecontrib." in qualname:
        return "orangecontrib." + qualname.partition(".orangecontrib.")[-1]
    return qualname


def register_category(cat_package, entry_points, defaultname=None):
    qualname = orangecontrib_qualname(cat_package.__name__)
    try:
        catname = cat_package.NAME
    except AttributeError:
        if defaultname:
            catname = defaultname
        else:
            catname = qualname.split(".")[-1]

    # For auto-discovery of widgets in this package
    eps = entry_points.setdefault(WIDGET_GROUP, list())
    eps.append(f"{catname} = {qualname}")

    # For auto-discovery of help for the category
    eps = entry_points.setdefault(HELP_GROUP, list())
    eps.append(f"{catname} = {qualname}:WIDGET_HELP_PATH")


def register_tutorials(tut_package, entry_points):
    qualname = orangecontrib_qualname(tut_package.__name__)

    # For auto-discovery of tutorials in this package
    eps = entry_points.setdefault(TUTORIAL_GROUP, list())
    eps.append(f"{qualname} = {qualname}")


def update_entry_points(packages, entry_points, distroname):
    super_categories = list(iter_super_category_packages(packages))
    if len(super_categories) != 1:
        distroname = None
    for cat_package in super_categories:
        register_category(cat_package, entry_points, defaultname=distroname)

    for cat_package in iter_category_packages(packages):
        if not any(
            cat_package.__name__.startswith(supercat_package.__name__)
            for supercat_package in super_categories
        ):
            register_category(cat_package, entry_points)

    for tut_package in iter_tutorial_packages(packages):
        register_tutorials(tut_package, entry_points)


def has_resources(paths, exts):
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        for ext in exts:
            if len(glob(os.path.join(path, ext))):
                return True
    return False


def get_resources(paths, exts):
    if isinstance(paths, str):
        paths = [paths]
    if isinstance(exts, str):
        exts = [exts]
    resources = list()
    for path in paths:
        for ext in exts:
            resources += glob(os.path.join(path, ext))
    return resources


def iter_category_packages(packages):
    for package in packages:
        if hasattr(package, "NAME"):
            yield package


def iter_super_category_packages(packages):
    for package in packages:
        if hasattr(package, "widget_discovery"):
            yield package


def iter_tutorial_packages(packages):
    for package in packages:
        if has_resources(package.__path__, TUTORIAL_EXT):
            yield package


def iter_icon_packages(packages):
    for package in packages:
        if has_resources(package.__path__, ICON_EXT):
            yield package


def setup(setup_filename, with_orangecontrib=True, **kw):
    """Like `setuptools.setup` but with automic orangecontrib arguments"""
    print("\n\n\n\nORANGE3 ADDON SETUP ARGUMENTS")

    project_root = os.path.dirname(setup_filename)
    distroname = kw["name"]

    # Define packages to include
    packages = kw.get("packages", None)
    if not packages:
        packages = kw["packages"] = find_packages(where=project_root)

    if not with_orangecontrib:
        packages = [
            name
            for name in packages
            if not name.startswith(NAMESPACE_PACKAGE + ".")
            and name != NAMESPACE_PACKAGE
        ]

    kw["packages"] = packages

    # Orange3 auto-discovery
    if with_orangecontrib:
        entry_points = kw.setdefault("entry_points", dict())
        packages = [importlib.import_module(qualname) for qualname in packages]
        update_entry_points(packages, entry_points, distroname)

        namespace_packages = kw.setdefault("namespace_packages", list())
        if NAMESPACE_PACKAGE not in namespace_packages:
            namespace_packages.append(NAMESPACE_PACKAGE)

    # Add package resources
    package_data = kw.setdefault("package_data", dict())
    all_packages_data = package_data.setdefault("", list())
    all_packages_data.extend(TUTORIAL_EXT + ICON_EXT)

    # Add exernal resources
    data_files = kw.setdefault("data_files", list())
    data_files += include_documentation("doc/_build/html", "help/" + distroname)
    kw.setdefault("zip_safe", False)

    # Descrition on pypi and the Orange3 addon manager
    project_readme = os.path.join(project_root, "README.md")
    if os.path.exists(project_readme) and "long_description" not in kw:
        kw["long_description"] = open(project_readme, "r").read()
        kw["long_description_content_type"] = "text/markdown"

    # Ensure Orange3 can find the contribution on Pypi
    keywords = kw.setdefault("keywords", list())
    if PYPI_KEYWORD not in keywords:
        keywords.append(PYPI_KEYWORD)

    # Use the normal setuptools
    pprint(kw)
    print("\n\n\n\n")
    _setup(**kw)
