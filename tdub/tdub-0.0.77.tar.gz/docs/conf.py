# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import tdub

# -- Project information -----------------------------------------------------

project = "tdub"
copyright = "2020, Doug Davis"
author = "Doug Davis"

version = tdub.__version__
release = tdub.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_click.ext",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# syntax highlighting style
pygments_style = "default"

autodoc_typehints = "none"

# -- Options for HTML output -------------------------------------------------


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": True,
    "sticky_navigation": True,
}


# html_theme = "pydata_sphinx_theme"
# html_css_files = [
#    'css/custom.css',
# ]

# html_theme_options = {
#    "github_url": "https://github.com/douglasdavis/tdub",
# }

# html_theme = "alabaster"
# html_theme_options = {
#     "description": "tW analysis",
#     "github_user": "douglasdavis",
#     "github_repo": "tdub",
#     "github_type": "star",
#     "github_count": False,
#     "font_family": '-apple-system, BlinkMacSystemFont, "Segoe UI", "Segoe UI Symbol"',
#     "head_font_family": '-apple-system, BlinkMacSystemFont, "Segoe UI", "Segoe UI Symbol"' ,
#     "font_size": "14px",
#     "page_width": "980px",
#     "sidebar_width": "240px",
#     "fixed_sidebar": True,
#     "show_relbars": True,
#     "code_font_size": "1.0em",
# }

intersphinx_mapping = {
    "uproot": ("https://uproot.readthedocs.io/en/latest", None),
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "sklearn": ("https://scikit-learn.org/stable", None),
    "lightgbm": ("https://lightgbm.readthedocs.io/en/latest", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
}
