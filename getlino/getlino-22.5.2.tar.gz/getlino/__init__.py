"""
.. autosummary::
   :toctree:

   configure
   startsite
   utils
   cli

"""

from .setup_info import SETUP_INFO
__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="https://lino-framework.gitlab.io/getlino")
srcref_url = 'https://gitlab.com/lino-framework/getlino/blob/master/%s'
doc_trees = ['docs']
