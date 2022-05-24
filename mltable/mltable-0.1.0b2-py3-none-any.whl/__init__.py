# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Contains functionality for interacting with existing and creating new MLTable files.

With the **mltable** package you can load, transform, and analyze data in
any Python environment, including Jupyter Notebooks or your favorite Python IDE.
"""
from .mltable import MLTable, load

__all__ = ['MLTable', 'load']

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
