import abc
import logging
from collections import deque
from typing import Callable, Generator, List, Optional, Union

from flywheel_gear_toolkit.utils.datatypes import Container

log = logging.getLogger(__name__)

hierarchy = ["project", "subject", "session", "acquisition"]


class Walker:
    """A class to walk the container hierarchically

    example usage:

    .. code-block:: python

        proj = fw.lookup('test/test_proj')
        proj_walker = walker.Walker(proj, depth_first=True)
        for container in proj.walk():
            if container.container_type == 'session':
                print('Found a session')
        proj = fw.lookup('test/test_proj')
    """

    def __init__(
        self,
        root: Container,
        depth_first: bool = True,
        reload: bool = False,
        stop_level: Optional[str] = None,
    ):
        """
        Args:
            root (Container):
                The root container, one of `flywheel.Project,flywheel.Subject, flywheel.Session, flywheel.Acquisition, flywheel.FileEntry, flywheel.AnalysisOutput`
            depth_first (bool): Depth first of breadth first traversal, True for depth first, False fo breadth first
            reload (bool): If `True`, reload containers when walking to load all metadata (default: False)
            stop_level (Optional[str]): Optional container type at which to stop walking. Default None.
                If specified, the children of this level will not be added to the walker, and thus will not be visited.
        """
        self.reload = reload
        self.depth_first = depth_first
        if self.reload:
            self.deque = deque([root.reload()])
        else:
            self.deque = deque([root])
        self._exclude = []

        if stop_level:
            try:
                idx = hierarchy.index(stop_level)
                self._exclude = hierarchy[idx:]
            except ValueError:
                log.warning(
                    f"Expected stop_level to be one of {hierarchy}, found {stop_level}."
                    + " . Not excluding any containers"
                )

    def next(self, callback: Optional[Callable[[Container], bool]] = None) -> Container:
        """Returns the next element from the walker and adds its children.

        Args:
            callback (Optional[Callable[[Container],bool]]).  Optional callback that takes
                in the `next_element` and returns a boolean of whether or not to queue
                its' children.  Defaults to None.

        Returns:
            Container: next element in the hierarchy.
        """
        to_queue = True
        if self.depth_first:
            next_element = self.deque.pop()
        else:
            next_element = self.deque.popleft()

        if callback and callable(callback):
            to_queue = callback(next_element)

        if to_queue:
            self.queue_children(next_element)

        return next_element

    def add(self, element: Union[List[Container], Container]):
        """Adds an element to the walker.

        Args:
            element (List[Container] or Container): Element or list of elements to add to deque
        """
        try:
            self.deque.extend(element)
        except TypeError:
            # element not an iterable
            self.deque.append(element)
        except AttributeError:
            self.deque.append(element)

    def _reload_container(self, container):
        """Returns reloaded container is `self.reload` is True."""
        if self.reload:
            return container.reload()
        return container

    def queue_children(self, element: Container) -> None:
        """Returns children of the element.

        Args:
            element (Container): container to find children of.
        """
        container_type = element.container_type

        # No children of files
        if container_type == "file":
            return

        if container_type == "analysis":
            return

        # Return nothing right away if stop_level was set.
        if container_type in self._exclude:
            return

        # Files aren't "containers" but they still can be and should be reloaded.
        self.deque.extend(
            [self._reload_container(file_) for file_ in element.files] or []
        )

        # Make sure that the analyses attribute is a list before iterating
        if isinstance(element.analyses, list):
            self.deque.extend(
                [self._reload_container(analysis) for analysis in element.analyses]
            )
        if container_type == "project":
            self.deque.extend(
                [
                    self._reload_container(subject)
                    for subject in element.subjects.iter_find()
                ]
            )
        elif container_type == "subject":
            self.deque.extend(
                [
                    self._reload_container(session)
                    for session in element.sessions.iter_find()
                ]
            )
        elif container_type == "session":
            self.deque.extend(
                [
                    self._reload_container(acquisition)
                    for acquisition in element.acquisitions.iter_find()
                ]
            )

    def is_empty(self):
        """Returns True if the walker is empty.

        Returns:
            bool
        """
        return len(self.deque) == 0

    def walk(
        self, callback: Optional[Callable[[Container], bool]] = None
    ) -> Generator[Container, None, None]:
        """Walks the hierarchy from a root container.

        Args:
            callback (Optional[Callable[[Container],bool]]).  Optional callback that takes
                in the `next_element` and returns a boolean of whether or not to queue
                its' children.  Defaults to None.

        Yields:
            Generator[Container, None, None]: Next element in walker.
        """

        while not self.is_empty():
            yield self.next(callback=callback)
