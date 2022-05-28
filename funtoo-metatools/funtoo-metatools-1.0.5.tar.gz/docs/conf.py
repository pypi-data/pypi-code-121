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

import os
import sys

sys.path.append(os.path.abspath("./_ext"))


# -- Project information -----------------------------------------------------

project = 'funtoo-metatools'
copyright = '2020-2021, Daniel Robbins'
author = 'Daniel Robbins'
html_context = {
    "project_url" : "https://projects.funtoo.org/metatools"
}
# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

master_doc = 'index'


import sphinx_funtoo_theme

extensions = [
    "consoleoutput",
    "sphinx_funtoo_theme",
    'sphinx.ext.autosectionlabel'
]

html_theme = "sphinx_funtoo_theme"
