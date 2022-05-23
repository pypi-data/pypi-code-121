"""Main entry point

.. code: bash

    python -m ewoksorange.canvas --with_example

Which is equivalent to

.. code: bash

    python -m orangecanvas

or

.. code: bash

    python -m Orange.canvas

but it registers the example add-on before launching.
"""

import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
