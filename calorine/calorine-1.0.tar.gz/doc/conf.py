#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../../'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.graphviz',
    'sphinx_autodoc_typehints',
    'sphinx_sitemap',
    'nbsphinx']

graphviz_output_format = 'svg'
templates_path = ['_templates']
default_role = 'code'
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'
todo_include_todos = True

# Collect basic information from main module
version = '0.1'
release = ''
copyright = 'CMMT'
project = 'calorine'
author = 'various'

site_url = 'https://calorine.materialsmodeling.org/'
html_css_files = ['custom.css']
html_logo = '_static/logo.png'
html_favicon = '_static/logo.ico'
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_theme_options = {'display_version': True}
htmlhelp_basename = 'calorinedoc'
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
}

# Settings for nbsphinx
nbsphinx_execute = 'never'

# Options for LaTeX output
_PREAMBLE = r"""
\usepackage{amsmath,amssymb}
\renewcommand{\vec}[1]{\boldsymbol{#1}}
\DeclareMathOperator*{\argmin}{\arg\!\min}
\DeclareMathOperator{\argmin}{\arg\!\min}
"""

latex_elements = {
    'preamble': _PREAMBLE,
}
latex_documents = [
    (master_doc, 'calorine.tex', 'calorine Documentation',
     'The calorine developer team', 'manual'),
]


# Options for manual page output
man_pages = [
    (master_doc, 'calorine', 'calorine Documentation',
     [author], 1)
]


# Options for Texinfo output
texinfo_documents = [
    (master_doc, 'calorine', 'calorine Documentation',
     author, 'calorine', 'Strong coupling calculator',
     'Miscellaneous'),
]
