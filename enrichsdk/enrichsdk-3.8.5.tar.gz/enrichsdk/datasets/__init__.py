"""

Transforms have numerous data dependencies, and as time is progressing
the dependencies are increasing and they have to tracked. Further
datasets are used in multiple places including the feature marketplace
and compliance modules.

Abstract dataset specification. This is useful for:

(a) handling dependent datasets
(b) cleaning
(c) checking
(d) validating & sampling
(e) discovery of data

There are two abstractions: Dataset and DatasetRegistry.

"""

from .discover import *
from . import discover
