"""This subpackage also provides direct access to module
:mod:`mcda.plot.plot` as all its functions are imported at the subpackage
level.

If you want to access plotting utilities, use simply:

.. code:: python

    import mcda.plot as pplot
    # Or
    from mcda.plot import *

"""
from .plot import *  # noqa: F401,F403
