import abc

from pydmt.core.pydmt import PyDMT


class Feature(abc.ABC):
    """
    A Feature is a piece of code that adds builder to a pydmt system in a predefined
    way. This is a way to share common practices between projects.

    Examples of features can be:
    - all the rules about how to build a python module with documentation and release it.
    - all the rules about how to build a C project and release it.

    These are similar to facets or natures in development environments.
    """

    @abc.abstractmethod
    def setup(self, pydmt: PyDMT) -> None:
        """ build your feature here """
