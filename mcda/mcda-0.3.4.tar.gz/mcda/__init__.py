"""This package defines shortcuts to access to some specific modules:
    * :mod:`mcda.core.aliases`
    * :mod:`mcda.core.functions`
    * :mod:`mcda.core.performance_table`
    * :mod:`mcda.core.scales`
    * :mod:`mcda.core.sorting`

You can import any of them more easily, for example with :mod:`mcda.core.performance_table`:

.. code:: python

    import mcda
    # You can then use module functions directly with namespace 'mcda.performance_table'
    # Or you can import it specifically
    from mcda import performance_table as ptable
    # Then use it with namespace 'ptable'
    # If you need to import specific functions however or all, you must use:
    from mcda.core.performance_table import *

"""  # noqa: E501
from .core import (  # noqa: F401
    aliases,
    functions,
    performance_table,
    scales,
    sorting,
)
