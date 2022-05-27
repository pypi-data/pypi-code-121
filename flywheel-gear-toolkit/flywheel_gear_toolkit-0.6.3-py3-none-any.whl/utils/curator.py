import abc
import contextlib
import copy
import dataclasses
import importlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

try:
    import flywheel
except (ModuleNotFoundError, ImportError) as e:
    raise ValueError("Please install `sdk` extra to use this module.") from e

from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.datatypes import Container, PathLike
from flywheel_gear_toolkit.utils.reporters import (
    AggregatedReporter,
    BaseLogRecord,
    LogRecord,
)

log = logging.getLogger(__name__)


def _load_curator(curator_path: PathLike):
    """Load curator from the file, return the module.

    Args:
        curator_path (Path-like): Path to curator script.

    Returns:
        (module): A python module.
    """
    if isinstance(curator_path, str):
        curator_path = Path(curator_path).resolve()
    if curator_path.is_file():
        old_syspath = sys.path[:]
        try:
            sys.path.append(str(curator_path.parent))
            ## Investigate import statement
            mod = importlib.import_module(curator_path.name.split(".")[0])
            mod.filename = str(curator_path)
        finally:
            sys.path = old_syspath
    else:
        mod = None

    return mod


def get_curator(
    context: GearToolkitContext,
    curator_path: PathLike,
    write_report: bool = False,
    **kwargs,
):
    """Returns an instantiated curator

    Args:
        context (GearToolkitContext): The flywheel GearToolkitContext instance.
        curator_path (Path-like): A path to a curator module.
        **kwargs: Extra keyword arguments.
    """
    curator_mod = _load_curator(curator_path)
    try:
        curator = curator_mod.Curator(
            context=context, write_report=write_report, **kwargs
        )
    except TypeError:
        log.warning(
            f"Couldn't set input arguments, context, write_report and kwargs: {list(kwargs.keys())}"
        )
        curator = curator_mod.Curator()
        setattr(curator, "context", context)
        setattr(curator, "write_report", write_report)
        for key, val in kwargs.items():
            setattr(curator, key, val)

    return curator


@dataclasses.dataclass
class CuratorConfig:
    """Class to hold curator configuration options."""

    # General config
    multi: bool = True
    workers: int = 1

    # Walking config
    depth_first: bool = True
    reload: bool = True
    stop_level: Optional[str] = None
    filter_walker: bool = False
    callback: Optional[Callable[[Container], bool]] = None

    # Reporting config
    report: bool = False
    format: Type[BaseLogRecord] = LogRecord
    path: Path = Path("/flywheel/v0/output/output.csv")


class Curator(abc.ABC):
    """Abstract curator base class.

    Args:
        context (GearToolkitContext): A GearToolkitContext instance.
        extra_packages (list, optional): List of additional PyPi packages to install.
        kwargs (Dict[str,Any], optional): Dictionary of attributes to set on the instance
            as attributes.
    """

    def __init__(
        self,
        context: GearToolkitContext = None,
        extra_packages: List[str] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> None:
        """An abstract class to be implemented in the input python file."""
        self.config = CuratorConfig()
        self.lock = None
        self.context = context
        self.extra_packages = extra_packages
        self.data = dict()
        self.reporter = None

        if self.config.report:
            self.reporter = AggregatedReporter(
                output_path=self.config.path,
                format=self.config.format,
                multi=self.config.multi,
            )

        if isinstance(self.context, GearToolkitContext):
            self.client = self.context.client

        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.extra_packages:
            self._install_extra_package()
            self._import_module()

    @contextlib.contextmanager
    def open_input(self, path, mode="r"):
        """Wrapper around <builtins>.open() that is thread safe.

        Args:
            path (str): Path of file to open.
            mode (str): mode to be passed into `open`. Default 'r'.
        """
        if self.lock:
            # Let this raise an AttributeError if lock is still None
            self.lock.acquire()
        try:
            with open(path, mode) as fp:
                yield fp
        finally:
            if self.lock:
                self.lock.release()

    def _import_module(self):
        converter_file = Path(__file__).absolute()
        path, fname = os.path.split(converter_file)
        sys.path.append(path)

    def _install_extra_package(self):
        for p in self.extra_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])

    @abc.abstractmethod
    def curate_container(
        self, container: Union[Container, Dict[str, Any]]
    ):  # pragma: no cover
        """Curates a generic container.

        Args:
            container (Container or dict): A Flywheel container or its dictionary representation.
        """
        raise NotImplementedError

    def finalize(self):
        """Use for doing stuff after curation."""
        pass


class HierarchyCurator(Curator):
    """An abstract class to curate the Flywheel Hierarchy.

    The user-defined Curator class should inherit from
    HierarchyCurator.

    This class defines abstract methods for each container type (e.g
    `curate_project`) (i.e. methods that need to be defined in the child
    curator Class implemented by the user, see example scripts in the example
    folder). Such methods are decorated with the `abc.abstractmethod` decorator
    in this abstract class.

    Validation methods are also defined for each container type. Validation
    methods become handy when, for example, curating a file is a time
    consuming process; it allows for marking a file during the curation
    method and checking for that mark elsewhere in the validate method.

    """

    def __init__(
        self,
        context: GearToolkitContext = None,
        extra_packages: List[str] = None,
        **kwargs: Optional[Dict[str, Any]],
    ) -> None:
        """An curator class to be extended for the HierarchyCurator."""
        super().__init__(context, extra_packages=extra_packages, **kwargs)

    def __deepcopy__(self, memo: Dict) -> "HierarchyCurator":
        """Custom deepcopy method for HierarchyCurator.

        Override the default deepcopy method.  All attributes can be shared
        except for the special _dict attribute which is handled in __getattr__
        and __setattr__

        Returns:
            HierarchyCurator: Result of the deepcopy
        """
        cls = self.__class__
        res = cls.__new__(cls)
        # Get self and new dicts
        self_dict = self.__dict__
        res_dict = res.__dict__
        # Update (shallow copy) each attribute except special data atrribute
        data = self_dict.pop("data")
        res_dict.update(self_dict)
        # Deep copy data attribute and restore
        res.data = copy.deepcopy(data, memo)
        self.data = data
        return res

    def validate_container(self, container: Container) -> bool:
        """Decide whether or not a container should be curated.

        Args:
            container (Container): Container to make decision on.

        Returns:
            bool: Whether or not it should be curated
        """
        if hasattr(container, "container_type"):
            container_type = container.container_type
            validate_method = getattr(self, f"validate_{container_type}")
            return validate_method(container)  # type: ignore
        else:
            # element is a file and has no children
            return self.validate_file(container)  # type: ignore

    def curate_container(self, container: Container):
        """Curates a generic container.

        Args:
            container (Container): A Flywheel container.
        """
        if hasattr(container, "container_type"):
            container_type = container.container_type
            curate_method = getattr(self, f"curate_{container_type}")
            curate_method(container)
        else:
            # element is a file and has no children
            self.curate_file(container)  # type: ignore

    def curate_project(self, project: flywheel.Project):  # pragma: no cover
        """Curates a project.

        Args:
            project (flywheel.Project): The project object to curate
        """
        pass

    def curate_subject(self, subject: flywheel.Subject):  # pragma: no cover
        """Curates a subject.

        Args:
            subject (flywheel.Subject): The subject object to curate
        """
        pass

    def curate_session(self, session: flywheel.Session):  # pragma: no cover
        """Curates a session.

        Args:
            session (flywheel.Session): The session object to curate
        """
        pass

    def curate_acquisition(self, acquisition: flywheel.Acquisition):  # pragma: no cover
        """Curates an acquisition.

        Args:
            acquisition (flywheel.Acquisition): The acquisition object to
                curate
        """
        pass

    def curate_analysis(self, analysis: flywheel.AnalysisOutput):  # pragma: no cover
        """Curates an analysis.

        Args:
            analysis (flywheel.Analysis): The analysis object to curate
        """
        pass

    def curate_file(self, file_: flywheel.FileEntry):  # pragma: no cover
        """Curates a file.

        Args:
            file_ (flywheel.FileEntry): The file entry object to curate
        """
        pass

    def validate_project(self, project: flywheel.Project):  # pragma: no cover
        """Returns True if a project needs curation, False otherwise.

        Args:
            project (flywheel.Project): The project object to validate

        Returns:
            bool: Whether or not the project is curated correctly
        """
        return True

    def validate_subject(self, subject: flywheel.Subject):  # pragma: no cover
        """Returns True if a subject needs curation, False otherwise.

        Args:
            subject (flywheel.Subject): The subject object to validate

        Returns:
            bool: Whether or not the subject is curated correctly
        """
        return True

    def validate_session(self, session: flywheel.Session):  # pragma: no cover
        """Returns True if a session needs curation, False otherwise.

        Args:
            session (flywheel.Session): The session object to validate

        Returns:
            bool: Whether or not the session is curated correctly
        """
        return True

    def validate_acquisition(
        self, acquisition: flywheel.Acquisition
    ):  # pragma: no cover
        """Returns True if a acquisition needs curation, False otherwise.

        Args:
            acquisition (flywheel.Acquisition): The acquisition object to
                validate

        Returns:
            bool: Whether or not the acquisition is curated correctly
        """
        return True

    def validate_analysis(self, analysis: flywheel.AnalysisOutput):  # pragma: no cover
        """Returns True if a analysis needs curation, False otherwise.

        Args:
            analysis (flywheel.Analysis): The analysis object to validate

        Returns:
            bool: Whether or not the analysis is curated correctly
        """
        return True

    def validate_file(self, file_: flywheel.FileEntry):  # pragma: no cover
        """Returns True if a file_ needs curation, False otherwise.

        Args:
            file_ (flywheel.FileEntry): The file entry object to validate

        Returns:
            bool: Whether or not the file_ is curated correctly
        """
        return True


class FileCurator(Curator):
    def curate_container(self, container: Union[Container, Dict[str, Any]]) -> None:
        """Curates a generic container.
        Args:
            container (Dict or Container): A Flywheel file.
        """
        if self.validate_file(container):
            self.curate_file(container)

    def curate_file(
        self, file_: Union[flywheel.FileEntry, Dict[str, Any]]
    ) -> None:  # pragma: no cover
        """Curates a file.

        Args:
            file_ (Dict or flywheel.FileEntry):
                The file entry object to curate
        """
        pass

    def validate_file(
        self, file_: Union[flywheel.FileEntry, Dict[str, Any]]
    ) -> bool:  # pragma: no cover
        """Returns True if a file_ needs curation, False otherwise.

        Args:
            file_ (Dict or flywheel.FileEntry):
                The file entry object to validate

        Returns:
            bool: Whether or not the file_ is curated correctly
        """
        return True
