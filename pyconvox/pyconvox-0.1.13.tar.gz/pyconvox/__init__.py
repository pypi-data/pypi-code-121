__all__ = (
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
)

__requirements__ = {
    'all': [
        "setuptools",
        "importlib-metadata"
    ]
}

import importlib_metadata

metadata = importlib_metadata.metadata("pyconvox")


__title__ = metadata["name"]
__summary__ = metadata["summary"]
__version__ = metadata["version"]
__author__ = metadata["author"]
__email__ = metadata["author-email"]
__license__ = metadata["license"]
__requirements__ = metadata["requirements"]