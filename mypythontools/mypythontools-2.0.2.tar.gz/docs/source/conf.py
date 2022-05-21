"""Sphinx config.

Reference: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

from __future__ import annotations
import sys
import pathlib
import datetime


# Suppose separate build and source structure and logo.png in _static folder

# Settings
PROJECT = "mypythontools"
AUTHOR = "Daniel Malachov"
GITHUB_USER = "Malachov"

# End of settings
###################

# Folders to sys path to be able to import
script_dir = pathlib.Path(__file__).resolve()
root = script_dir.parents[2]
lib_path = root / PROJECT

for i in [script_dir, root, lib_path]:
    if i.as_posix() not in sys.path:
        sys.path.insert(0, i.as_posix())


# -- Project information -----------------------------------------------------

copyright = f"2020, {AUTHOR}"  # pylint: disable=redefined-builtin

# The full version, including alpha/beta/rc tags
release = datetime.datetime.now().strftime("%d-%m-%Y")

master_doc = PROJECT  # pylint: disable=invalid-name

source_suffix = [".rst", ".md"]

# -- General configuration ---------------------------------------------------
html_theme_options = {
    "github_user": GITHUB_USER,
    "github_repo": PROJECT,
    "github_banner": True,
}


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.autosectionlabel",
    # "sphinx.ext.intersphinx",
    # "sphinx.ext.imgmath",
    # "m2r2",
    # "myst_parser",
]

# 'about.html',
html_sidebars = {"**": ["navi.html", "searchbox.html"]}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"  # pylint: disable=invalid-name

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# html_extra_path = ['../extra']

html_css_files = [
    "https://malachov.github.io/mypythontools/tools/sphinx-alabaster-css/custom.css",
]

napoleon_custom_sections = [
    ("Types", "returns_style"),
    ("Type", "returns_style"),
    ("Options", "returns_style"),
    ("Default", "returns_style"),
    ("For example", "returns_style"),
]
