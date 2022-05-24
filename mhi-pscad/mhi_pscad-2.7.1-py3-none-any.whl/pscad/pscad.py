#===============================================================================
# PSCAD Application object
#===============================================================================

"""
The PSCAD Application Proxy Object
"""

#===============================================================================
# Imports
#===============================================================================

import os, string, re, logging, time

from warnings import warn
from xml.etree import ElementTree as ET
from contextlib import contextmanager
from typing import Dict, List, Optional, Set, Tuple, Union

from mhi.common.remote import Application

import mhi.common.path
import mhi.common.cdata

from .remote import Remotable, rmi, rmi_property, deprecated
from .types import Parameters, Message, ProjectType
from .project import Project
from .simset import SimulationSet
from .form import FormCodec
from .certificate import Certificate
from .resource import RES_ID
from .unit import UnitSystem


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# PSCAD Application
#===============================================================================

class PSCAD(Application, Remotable):
    """
    The PSCAD Application

    This proxy is used to communicate with a running PSCAD Application,
    and may only be created via one of the following methods:

    * :func:`mhi.pscad.launch()`
    * :func:`mhi.pscad.connect()`
    * :func:`mhi.pscad.application()`
    """

    _certs = None # Dict[int, Certificate]



    #===========================================================================
    # Initialization
    #===========================================================================

    def _initialize(self):
        xml = self._xml(RES_ID['IDR_UNIT_SYSTEM'])
        UnitSystem.parse(xml)


    #===========================================================================
    # Properties
    #===========================================================================

    @rmi_property
    def version(self) -> str: # type: ignore
        """
        The PSCAD version string. (Read-only)
        """


    @rmi_property
    def examples_folder(self) -> str:
        """
        The PSCAD "Examples Directory". (Read-only)
        """


    #===========================================================================
    # Subscriptions
    #===========================================================================

    #---------------------------------------------------------------------------
    # What can be subscribed to
    #---------------------------------------------------------------------------

    @rmi
    def subscriptions(self) -> Set[str]:
        """
        Returns the set of event-names which can be
        :meth:`subscribed <.subscribe>` to.

        Returns:
            Set[str]: Event names which can be subscribed to.

        .. versionadded:: 2.0
        """

    #---------------------------------------------------------------------------
    # What has been subscribed to
    #---------------------------------------------------------------------------

    @property
    def _subscribed(self):
        if '_subscription' not in self.__dict__:
            self._subscription = {} # pylint: disable=attribute-defined-outside-init
        return self._subscription

    def subscribed(self, name: str) -> bool:
        """
        Determine if the given event is being subscribed to.

        Returns:
            `True` if the given event is subscribed to, `False` otherwise.
        """

        return name in self._subscribed

    #---------------------------------------------------------------------------
    # Subscribe
    #---------------------------------------------------------------------------

    @rmi
    def _subscribe(self, name):
        pass

    def subscribe(self, name: str, handler=None) -> None:
        """
        Start receiving `name` events.

        Parameters:
            name (str): Name of event being subscribed to, such as
                        `"load-events"` or `"build-events"`
            handler: Function to call when event is received.
        """

        if handler:
            self._subscribe(name)
            self._subscribed[name] = handler
        else:
            warn("Subscriptions without a handler are no longer supported",
                 DeprecationWarning, stacklevel=2)

    #---------------------------------------------------------------------------
    # Unsubscribe
    #---------------------------------------------------------------------------

    @rmi
    def _unsubscribe(self, name):
        pass

    def unsubscribe(self, name: str) -> bool:
        """
        Stop receiving and processing `name` events.

        Parameters:
            name (str): Name of event being unsubscribed from.
        """

        handler = self._subscribed.pop(name, None)
        if handler:
            handler.close()
            return self._unsubscribe(name)

        LOG.warning("Not currently subscribed to %s events", name)
        return False

    def unsubscribe_all(self) -> None:
        """
        Stop receiving all events

        .. versionadded:: 2.0
        """

        for handler in self._subscribed.values():
            handler.close()

        self._unsubscribe(None)


    #---------------------------------------------------------------------------
    # Temporary subscription
    #---------------------------------------------------------------------------

    @contextmanager
    def subscription(self, name: str, handler):
        """
        Subscription context manager

        Usage::

            with pscad.subscription(event_name, handler):
                # subscription is active in this "with-statement"

            # handler is auto-unsubscribed when "with-statement" exits

        .. versionadded:: 2.0
        """

        try:
            if handler:
                self.subscribe(name, handler)
            yield None
        finally:
            if handler and name in self._subscribed:
                self.unsubscribe(name)


    #---------------------------------------------------------------------------
    # Subscription handler
    #---------------------------------------------------------------------------

    def _broadcast(self, channel, msg):
        handler = self._subscribed.get(channel, None)
        if handler:
            try:
                handler.send(msg)
            except StopIteration:
                self._subscribed.pop(channel, None)

        else:
            LOG.warning("Broadcast w/o subscription: %s %r", channel, msg)


    #===========================================================================
    # Flags
    #===========================================================================

    @rmi
    def _flags(self, *args):
        pass

    def flags(self, flags: Dict[str, bool] = None, **kwargs
              ) -> Optional[Dict[str, bool]]:
        """
        Retrieve or set application flags

        If no flags are given, the value of all flags is returned.
        Otherwise, the specified flags are set or cleared.

        Parameters:
            flags (dict): The flags to set or clear (optional).
            **kwargs: Flags to set or clear as key=value pairs (optional)

        Examples::

            pscad.flags({"silence": True, "load-meta-files": False})
            pscad.flags(silence=True, load_meta_files=False)
        """

        flags = dict(flags, **kwargs) if flags else kwargs
        flags = {key.replace('_', '-'): val for key, val in flags.items()}
        return self._flags(flags)

    @deprecated("Use PSCAD.flags()")
    def set_flags(self, flags=None, **kwargs):
        """
        Set or clear one or more application flags

        Parameters:
            flags (dict): The flags to set or clear.
            **kwargs: Flags to set or clear as key=value pairs

        Examples::

            pscad.set_flags({"silence": True, "load-meta-files": False})
            pscad.set_flags(silence=True, load_meta_files=False)
        """

        return self.flags(flags, **kwargs)

    @deprecated("Use PSCAD.flags()")
    def get_flags(self):
        """
        Retrieve the current application flags

        Returns:
            Dict[str, bool]: A dictionary of the current application flags.

        Example::

            >>> pscad.get_flags()
            {'silence': True, 'load-meta-files': True}

        """

        return self._flags()


    #===========================================================================
    # Busy
    #===========================================================================

    @rmi
    def is_busy(self) -> bool:
        """
        Determine whether the PSCAD application is "busy" or not.

        Returns:
            `True` if the application is presently busy, `False` otherwise.
        """

    def wait_for_idle(self, poll_interval: float = 0.1) -> None:
        """
        Wait until the PSCAD application is no longer "busy".
        """

        while self.is_busy():
            time.sleep(poll_interval)


    #===========================================================================
    # Fetch internal XML document
    #===========================================================================

    @rmi
    def _xml(self, iid):
        pass

    #===========================================================================
    # Expand
    #===========================================================================

    @rmi
    def _substitute(self, value):
        pass

    def substitute(self, value: str) -> str:
        """
        Substitute PSCAD workspace and environment variables in the given
        string

        Returns:
            str: The string with known variables substituted.

        Example::

            >>> pscad.substitute('Running PSCAD version $(Version)')
            'Running PSCAD version 5.0'
        """
        return self._substitute(value)


    #===========================================================================
    # Settings
    #===========================================================================

    @rmi
    def _settings(self, settings):
        pass

    def _settings_codec(self):
        if '_setting_codec' not in PSCAD.__dict__:
            PSCAD._setting_codec = FormCodec.application(self)
            # pylint: disable=protected-access
            PSCAD._setting_codec._coding['fortran_version'] = mhi.pscad.fortran_codec()
            PSCAD._setting_codec._coding['matlab_version'] = mhi.pscad.matlab_codec()
            # pylint: enable=protected-access

        return PSCAD._setting_codec


    def settings(self, settings: Parameters = None,
                 **kwargs) -> Optional[Parameters]:
        """
        Set or retrieve PSCAD's settings.

        Parameters:
            settings (dict): A dictionary of setting key-values pairs
            **kwargs: individual setting key-value pairs

        If called without providing any key-value pairs, the current settings
        are returned.  Otherwise, the given key-value pairs are set in the
        application's settings.

        Any unknown keys are silently ignored.  The effect of setting an known
        key to an invalid value is undefined.
        """

        codec = self._settings_codec()

        # Combined settings & **kwargs into one combined dictionary
        settings = dict(settings, **kwargs) if settings else kwargs

        if settings:
            try:
                settings = codec.encode(settings)
            except KeyError as err:
                msg = "{!r} not valid for {!r} setting".format(*err.args)
                raise KeyError(msg) from None

            self._settings(settings)
            settings = None

        else:
            # Get settings
            settings = self._settings(settings)
            settings = codec.decode(settings)

        return settings

    def setting_range(self, setting: str):
        """
        Get legal values for a setting.

        The function may return:

        * a ``tuple`` or a ``frozenset`` of legal values,
        * a ``range()`` of legal values (integer settings),
        * a ``Tuple[float, float]`` representing minimum and maximum values \
            (real & complex settings),
        * an exception if the setting does not have a defined range

        Parameters:
            setting (str): A PSCAD setting name

        Returns:
            The valid values or range the setting may take on.

        Examples::

            >>> pscad.setting_range('agent_show')
            (False, True)

            >>> pscad.settings_range('backup_freq')
            (10, 15, 20, 30, 60)

            >>> pscad.settings_range('active_graphics')
            frozenset({'2_SEC', '5_SEC', '10_SEC'})

            >>> pscad.settings_range('backup_folder')
                ...
            ValueError: No defined range for setting

        .. versionadded:: 2.1
        """

        codec = self._settings_codec()

        try:
            return codec.range(setting)
        except KeyError:
            raise ValueError("No such setting") from None
        except AttributeError:
            raise ValueError("No defined range for setting") from None


    #===========================================================================
    # Licensing
    #===========================================================================

    @rmi
    def _certificates(self):
        pass

    @rmi
    def _certificate(self, *args):
        pass

    @rmi
    def _release_all_certs(self, *args):
        pass

    #---------------------------------------------------------------------------
    # Login
    #---------------------------------------------------------------------------

    @rmi
    def login(self, username: str, password: str, remember: bool = False):
        """
        Attempt to log in to a My Center account, for licensing.

        Parameters:
            username (str): The account's My Center user name
            password (str): The account's My Center password
            remember (bool): Set to ``True`` to check the "Remember me" checkbox
        """

    def logout(self) -> None:
        """
        Log out of the My Center account
        """

        self.login(None, None)


    #---------------------------------------------------------------------------
    # Is the User logged in?
    #---------------------------------------------------------------------------

    @rmi
    def logged_in(self) -> bool:
        """
        Returns whether or not the user is "Logged in"

        Returns:
            `True` if the user is logged in, `False` otherwise.

        Example:
            >>> pscad.logged_in()
            True
        """

    #---------------------------------------------------------------------------
    # Does PSCAD hold a license certificate?
    #---------------------------------------------------------------------------

    @rmi
    def licensed(self) -> bool:
        """
        Determine whether a valid license is being held.

        Returns:
            `True` if the a license is held, `False` otherwise.

        Example:
            >>> pscad.licensed()
            True
        """

    #---------------------------------------------------------------------------
    # What license certificates are available?
    #---------------------------------------------------------------------------

    def get_available_certificates(self, *, refresh: bool = False
                                   ) -> Dict[int, Certificate]:
        """
        Retrieve a list of license certificates available to the user.

        Returns:
            A dictionary of :class:`certificates <.Certificate>`,
            keyed by :meth:`.Certificate.id`.
        """

        if not refresh and self._certs is not None:
            return self._certs

        self._certs = Certificate.parse(self._certificates())

        return self._certs


    #---------------------------------------------------------------------------
    # What license certificates do we currently hold?
    #---------------------------------------------------------------------------

    def get_current_certificate(self) -> Optional[Certificate]:
        """
        Retrieve the Certificate currently being held.

        Returns:
            The :class:`.Certificate` being held, or `None`
        """

        if self.licensed():
            certs = self.get_available_certificates()
            xml = self._certificate()

            return Certificate.find_cert(certs, xml)

        return None


    #---------------------------------------------------------------------------
    # Acquire a license certificate
    #---------------------------------------------------------------------------

    def get_certificate(self, certificate: Certificate) -> int:
        """
        Attempt to acquire the given license certificate.

        Parameters:
            certificate: the :class:`.Certificate` to be acquired.
        """

        return self._certificate(str(certificate.id()))


    #---------------------------------------------------------------------------
    # Release certificates
    #---------------------------------------------------------------------------

    def release_certificate(self) -> None:
        """
        Releases the currently held certificate.
        """

        return self._certificate("")

    def release_all_certificates(self) -> None:
        """
        Releases all currently held certificates.

        .. versionadded:: 2.1.1
        """

        return self._release_all_certs()


    #---------------------------------------------------------------------------
    # Activate Legacy Professional/Educational license
    #---------------------------------------------------------------------------

    @rmi
    def _activate_legacy(self, professional):
        pass

    def activate_pro_license(self) -> bool:
        """
        Activate Professional Legacy License
        """
        return self._activate_legacy(True)

    def activate_edu_license(self) -> bool:
        """
        Activate Educational Legacy License
        """
        return self._activate_legacy(False)

    @rmi
    def _license_host(self, host):
        pass

    def set_license_host(self, host: str) -> None:
        """
        Set license host
        """
        return self._license_host(host)


    #===========================================================================
    # Workspace commands
    #===========================================================================

    @staticmethod
    def _validate_workspace_name(name: str) -> None:
        if not re.fullmatch("[a-zA-Z][a-zA-Z0-9_]*", name):
            raise ValueError("Name must start with a letter, and "
                             "may only contain letters, numbers & underscores.")

    @classmethod
    def _validate_workspace_filename(cls, filename: str) -> None:
        _, file = os.path.split(filename)
        name, _ = os.path.splitext(file)
        cls._validate_workspace_name(name)


    #---------------------------------------------------------------------------
    # Workspace options
    #---------------------------------------------------------------------------

    @deprecated("Use the pscad.settings() method")
    def parameters(self, parameters=None, **kwargs): # pylint: disable=missing-function-docstring
        return self.settings(parameters, **kwargs)


    #---------------------------------------------------------------------------
    # New Workspace
    #---------------------------------------------------------------------------

    @rmi
    def _new_workspace(self, filename, name):
        pass

    def new_workspace(self, filename: str = r"~\Documents\NewWorkspace.pswx",
                      folder: str = None) -> None:
        """
        Unload the current workspace, and create a new one.

        Parameters:
            filename (str): filename of new workspace
            folder (str): If provided, the path to the filename is resolved
                relative to this folder.

        Warning:
            If popup dialogs are being silenced,
            **all unsaved changes will be unconditionally lost**.

        .. versionchanged:: 2.0
            Added ``filename`` & ``folder`` parameters.
        """

        name, ext = os.path.splitext(filename)
        if ext != '.pswx':
            filename = name + '.pswx'

        filename = mhi.common.path.expand_path(filename, abspath=True,
                                               folder=folder)

        name = os.path.splitext(os.path.split(filename)[1])[0]
        self._validate_workspace_name(name)

        self._new_workspace(filename, name)


    #---------------------------------------------------------------------------
    # Save Workspace
    #---------------------------------------------------------------------------

    @rmi
    def _save_workspace(self, filename, save_projects):
        pass

    def save_workspace(self, filename: str = None, folder: str = None,
                       save_projects: bool = True) -> None:
        """
        Save the current workspace, possibly as a new workspace.
        """

        if folder and not filename:
            raise ValueError("Filename is required when folder is given")

        if filename:
            name, ext = os.path.splitext(filename)
            if ext != '.pswx':
                filename = name + '.pswx'

            filename = mhi.common.path.expand_path(filename, abspath=True,
                                                   folder=folder)

            directory, file = os.path.split(filename)
            name = os.path.splitext(file)[0]
            if not os.path.isdir(directory):
                raise FileNotFoundError("No such directory: "+directory)
            self._validate_workspace_name(name)

        self._save_workspace(filename, save_projects)


    #---------------------------------------------------------------------------
    # Workspace directory/name/path
    #---------------------------------------------------------------------------

    @property
    def workspace_dir(self) -> str:
        """
        Return the current workspace directory
        """
        return self.substitute('$(WorkspaceDir)')

    @property
    def workspace_name(self) -> str:
        """
        Return the current workspace name
        """
        return self.substitute('$(WorkspaceName)')

    @property
    def workspace_path(self) -> str:
        """
        Return the current workspace path
        """
        return self.substitute(r'$(WorkspaceDir)\$(WorkspaceName).pswx')


    #---------------------------------------------------------------------------
    # Is Dirty
    #---------------------------------------------------------------------------

    @rmi
    def is_dirty(self) -> bool:
        """
        Determine whether the workspace has been modified since the last time
        it was saved.

        Returns:
            `True` if the workspace has unsaved changes, `False` otherwise.
        """

    #---------------------------------------------------------------------------
    # List Projects
    #---------------------------------------------------------------------------

    @rmi
    def _projects(self):
        pass

    def projects(self) -> List[Dict[str, str]]:
        """
        List all currently loaded libraries and cases.

        Returns:
           List[dict]: The ``name``, ``type`` and ``description`` of each
           project in the workspace.

        With only the master library loaded:

        >>> pscad.new_workspace()
        >>> pscad.projects()
        [{'name': 'master', 'type': 'Library', 'description': 'Master Library'}]

        Instead of a ``name``, ``type``, and ``description`` dictionary,
        :meth:`.cases` may be used to retrieve all the case projects,
        and :meth:`.libraries` to retrieve all the library projects.

        .. versionchanged:: 2.0
            Was ``PSCAD.list_projects()``.
        """

        return [{'name': name, 'type': kind, 'description': descr}
                for name, kind, descr in self._projects()]


    @deprecated('list_projects() will be removed; use projects()')
    def list_projects(self):        # pylint: disable=missing-function-docstring
        return self.projects()


    @deprecated('list_cases() will be removed; use projects()')
    def list_cases(self):           # pylint: disable=missing-function-docstring
        return self.projects()

    def cases(self) -> List[Project]:
        """
        List all currently loaded cases.

        Returns:
           List[Project]: A list of case projects.

        .. versionadded:: 2.6
        """

        return [self.project(name) for name, prj_type, _ in self._projects()
                if prj_type == 'Case']

    def libraries(self) -> List[Project]:
        """
        List all currently loaded libraries.

        Returns:
           List[Project]: A list of library projects.

        .. versionadded:: 2.6
        """

        return [self.project(name) for name, prj_type, _ in self._projects()
                if prj_type == 'Library']


    #---------------------------------------------------------------------------
    # Get Project
    #---------------------------------------------------------------------------

    @rmi
    def _project(self, name):
        pass

    def project(self, name: str) -> Project:
        """
        Retrieve a controller for a named project in the workspace.

        Parameters:
            name (str): The name of the library or case. \
                The directory and filename extension must not be included.

        Returns:
            A :class:`project <.ProjectCommands>` controller.

        >>> master = pscad.project('master')
        >>> master.parameters()['description']
        'Master Library'
        """
        Project.validate_name(name)
        return self._project(name)

    def focused(self) -> Project:
        """
        Return the currently focused project
        """

        return self._project(None)


    #---------------------------------------------------------------------------
    # Create Project
    #---------------------------------------------------------------------------

    @rmi
    def _create_project(self, prj_type, filename):
        pass

    @deprecated("Use pscad.create_case() or pscad.create_library")
    def create_project(self, prj_type, name, folder):
        """
        Create a new project in the workspace.

        Parameters:
           prj_type (int): Project type.  Use 1 -> case, 2 -> library
           name (str): Name of the project.
           folder (str): Path to directory where project will be stored.

        Returns:
            A project controller for the newly created project.
        """

        LOG.info("Create project %r in %r", name, folder)

        Project.validate_name(name)

        try:
            prj_type = ProjectType(prj_type).value
        except ValueError:
            raise ValueError("Invalid type: {!r}".format(prj_type)) from None

        path = mhi.common.path.expand_path(name, True, folder)

        self._create_project(prj_type, path)
        return self._project(name)


    #---------------------------------------------------------------------------
    # Create Case
    #---------------------------------------------------------------------------

    def create_case(self, filename: str, folder: str = None) -> Project:
        """
        Create a new project case in the workspace.

        Parameters:
           filename (str): Name or filename of the project.
           folder (str): Folder where project will be stored. (optional)

        Returns:
            The newly created project case.

        .. versionadded:: 2.0
            Replaces ``PSCAD.create_project(1, name, folder)``
        """

        name, ext = os.path.splitext(filename)
        if ext == '':
            filename = name + '.pscx'
        elif ext != '.pscx':
            raise ValueError("Invalid extension for case: "+ext)

        filename = mhi.common.path.expand_path(filename, abspath=True,
                                               folder=folder)

        name = os.path.splitext(os.path.split(filename)[1])[0]
        Project.validate_name(name)

        self._create_project(ProjectType.CASE.value, filename)
        return self._project(name)


    #---------------------------------------------------------------------------
    # Create Case
    #---------------------------------------------------------------------------

    def create_library(self, filename: str, folder: str = None) -> Project:
        """
        Create a new library project in the workspace.

        Parameters:
           filename (str): Name or filename of the library.
           folder (str): Folder where library will be stored. (optional)

        Returns:
            The newly created library.

        .. versionadded:: 2.0
            Replaces ``PSCAD.create_project(2, name, folder)``
        """

        name, ext = os.path.splitext(filename)
        if ext == '':
            filename = name + '.pslx'
        elif ext != '.pslx':
            raise ValueError("Invalid extension for library: "+ext)

        filename = mhi.common.path.expand_path(filename, abspath=True,
                                               folder=folder)

        name = os.path.splitext(os.path.split(filename)[1])[0]
        Project.validate_name(name)

        self._create_project(ProjectType.LIBRARY.value, filename)
        return self._project(name)


    #===========================================================================
    # Load commands
    #===========================================================================

    #---------------------------------------------------------------------------
    # Load Project(s)/Workspace
    #---------------------------------------------------------------------------

    @rmi
    def _load(self, *filenames):
        pass

    def load(self, *filenames: str, handler=None, folder: str = None) -> None:
        """
        Load a workspace, or one or more projects into the current workspace.

        Parameters:
            *filenames (str): a list of filenames to load.
            folder (str): If provided, the path to the filenames are resolved
                relative to this folder.
            handler: If provided, the given handler is automatically added for\
                the duration of the load operation.  Defaults to `None`.

        If a workspace file (`*.pswx`) is given, it must be the only file.
        Otherwise, more than one library (`*.pslx`) and/or case (`*.pscx`) may
        be given.

        >>> pscad.load(os.path.join(pscad.examples_folder, r'tutorial\\vdiv.pscx'))
        >>> vdiv = pscad.project('vdiv')
        >>> vdiv.parameters()['description']
        'Single Phase Voltage Divider'

        .. versionchanged:: 2.0
            Added ``folder`` parameter.
        """

        if len(filenames) == 1  and  isinstance(filenames[0], list):
            filenames = filenames[0]

        if len(filenames) == 0:
            LOG.info("No files given")
            raise ValueError("No files given")

        if any(os.path.splitext(file)[1].lower() == ".pswx" for file in filenames
               ) and len(filenames) != 1:
            raise ValueError("A workspace must be the only file given")

        file_names = mhi.common.path.expand_paths(filenames, abspath=True,
                                                  folder=folder)

        LOG.info("Loading %s", file_names)

        with self.subscription('load-events', handler):
            return self._load(*file_names)


    #---------------------------------------------------------------------------
    # Reload Workspace
    #---------------------------------------------------------------------------

    @rmi
    def reload(self) -> None:
        """
        Reload the workspace

        Discard all unsaved changes and reload the workspace.
        """


    #---------------------------------------------------------------------------
    # Consolidate Workspace
    #---------------------------------------------------------------------------

    @rmi
    def _consolidate(self, folder):
        pass

    def consolidate(self, folder: str) -> None:
        """
        Consolidate the workspace

        Package all workspace projects & resources into one folder.
        Any existing files in the folder will be removed.
        """

        if os.path.exists(folder) and not os.path.isdir(folder):
            raise ValueError("Not a directory: "+folder)

        if not os.path.isdir(folder):
            os.makedirs(folder)

        return self._consolidate(folder)


    #===========================================================================
    # Generic Command
    #===========================================================================

    def _command(self, cmd: str) -> None:

        if cmd not in RES_ID:
            raise ValueError("Unknown command: " + cmd)
        cmd_id = RES_ID[cmd]

        self._generic_cmd(cmd_id)


    #===========================================================================
    # Build / Run suite
    #===========================================================================

    @rmi
    def _launch(self, *args, **kwargs):
        pass

    _CURRENT = 1
    _ALL = 2
    _SIM_SETS = 3

    @deprecated('This method is obsolete')
    def execute_build_run_cmd(self, cmd, handler=None): # pylint: disable=missing-function-docstring
        raise NotImplementedError()

    def clean_all(self) -> None:
        """
        Remove all temporary files used to build the case.
        """

        LOG.info("Clean All")

        return self._launch(clean=self._ALL)

    def build_all(self, handler=None) -> None:
        """
        Build all projects
        """

        LOG.info("Build all")

        with self.subscription('build-event', handler):
            return self._launch(clean=self._ALL, build=self._ALL)

    def build_modified(self, handler=None) -> None:
        """
        Build any modified projects
        """

        LOG.info("Build modified")

        with self.subscription('build-event', handler):
            return self._launch(build=self._ALL)

    def build_current(self, handler=None) -> None:
        """
        Build only the current project
        """

        LOG.info("Build current")

        with self.subscription('build-event', handler):
            return self._launch(clean=self._CURRENT, build=self._CURRENT)

    def run_simulation_sets(self, *simulation_sets: SimulationSet,
                            handler=None) -> None:
        """
        Run the given simulations sets.

        Any modified projects will be built as necessary.
        """

        LOG.info("Run simulation sets")

        with self.subscription('build-event', handler):
            return self._launch(*simulation_sets, run=self._SIM_SETS)

    def run_all_simulation_sets(self, handler=None) -> None:
        """
        Run all simulations sets.

        Any modified projects will be built as necessary.
        """

        LOG.info("Run all simulation sets")

        with self.subscription('build-event', handler):
            return self._launch(run=self._SIM_SETS)

    def pause_run(self) -> None:
        """
        Pause the currently running projects.
        """

        LOG.info("Pause Run")

        self._command("ID_RIBBON_HOME_RUN_PAUSE")

    def stop_run(self) -> None:
        """
        End the currently running projects.
        """

        LOG.info("Stop Run")

        self._command("ID_RIBBON_HOME_RUN_STOP")

    @rmi
    def stop_single_project(self, project: Project) -> bool:
        """
        Terminate the execution of one project task.
        """

    def skip_run(self) -> None:
        """
        Skip the currently run, and continue with next.
        """

        LOG.info("Skip Run")

        self._command("ID_RIBBON_HOME_RUN_SKIP")

    def next_step(self) -> None:
        """
        Advance the running simulation by one step.
        """

        LOG.info("Next step")

        self._command("ID_RIBBON_HOME_RUN_STEP")

    def snapshot(self) -> None:
        """
        Take a snapshot.
        """

        LOG.info("Snapshot")

        self._command("ID_RIBBON_HOME_RUN_SNAPSHOT")

    @rmi
    def slow(self, factor: int) -> None:
        """
        Set the simulation speed slow-down factor.
        """


    #===========================================================================
    # Simulations Sets
    #===========================================================================

    @rmi
    def simulation_sets(self) -> List[str]:
        """
        List all simulations set names.

        Returns:
            List[str]: A names of all simulation sets in the workspace.

        .. versionchanged:: 2.0
            Replaces ``Workspace.list_simulation_sets()``
        """

    @deprecated('list_simulation_sets() will be removed; use simulation_sets()')
    def list_simulation_sets(self): # pylint: disable=missing-function-docstring
        return self.simulation_sets()

    @rmi
    def _simulation_set(self, set_name, **kwargs):
        pass

    def create_simulation_set(self, set_name: str) -> SimulationSet:
        """
        Create a new simulation set.

        Parameters:
            set_name (str): Name of the new simulation set.
        """

        LOG.info("Create simulation set '%s'", set_name)

        SimulationSet.validate_name(set_name)

        return self._simulation_set(set_name, action='create')

    def remove_simulation_set(self, set_name: str) -> None:
        """
        Remove an existing simulation set.

        Parameters:
            set_name (str): Name of the simulation set to remove.
        """

        SimulationSet.validate_name(set_name)

        LOG.info("Remove simulation set '%s'", set_name)

        return self._simulation_set(set_name, action='remove')

    @rmi
    def remove_all_simulation_sets(self) -> None:
        """
        Remove all simulation sets.
        """

    def simulation_set(self, set_name: str) -> SimulationSet:
        """
        Retrieve a controller proxy for the given simulation set.

        Parameters:
            set_name (str): Name of the simulation set.

        Returns:
            SimulationSet: The named simulation set.

        .. versionchanged:: 2.0
            Replaces ``Workspace.simulation_set(set_name)``
        """

        SimulationSet.validate_name(set_name)

        return self._simulation_set(set_name)


    #===========================================================================
    # Navigate
    #===========================================================================

    @rmi
    def _navigate(self, msg):
        pass

    def navigate_to(self, scope: str, name: str, link: int, text: str = '',
                    status: str = 'normal') -> bool:
        """
        Navigate to a component, highlight it, and show a message next to it.

        Parameters:
            scope (str): The project component is in.
            name (str): The canvas the component is on.
            link (int): The component Id number
            text (str): Message to display
            status (str): `'normal'`, `'warning'`, or `'error'`
        """

        message = ET.Element('message')
        message.set('status', status)
        message.set('label', 'build')
        message.set('groupid', '0')

        ET.CDATA(message, text) # type: ignore

        user = ET.SubElement(message, 'User')
        user.set('scope', scope)
        user.set('name', name)
        user.set('link', str(link))
        user.set('status', status)

        msg = ET.tostring(message, encoding='unicode')
        return self._navigate(msg)

    def navigate(self, msg: Message) -> bool:
        """
        Navigate to a component, highlight it, and show a message next to it.

        Parameters:
            msg: A message returned from Project.messages()
        """

        if msg.classid == 'CmpNavigator':
            return self.navigate_to(msg.scope, msg.name, msg.link,
                                    msg.text, msg.status)
        raise ValueError("Cannot navigate to {}".format(msg))

    def navigate_dismiss(self) -> bool:
        """
        Dismiss a popup message shown for a previous navigate command
        """

        return self._navigate(None)

    def navigate_up(self) -> None:
        """
        Return to the page which contains the object currently
        being viewed.
        """

        LOG.info("Navigate Up")

        self._command("ID_RIBBON_HOME_NAVIGATION_UP")


    #===========================================================================
    # Copy Definition(s)
    #===========================================================================

    @rmi
    def _copy_definitions(self, *defns):
        pass

    def copy_definitions(self, *defns: "Definition") -> None:
        """
        Copy a definition to the clipboard
        """

        if not defns:
            raise ValueError("No definition selected")

        return self._copy_definitions(*defns)


    #===========================================================================
    # Keystrokes
    #===========================================================================

    @rmi
    def key(self, vktype: str, vkcode: int) -> None:
        """
        Generate a keyboard key event
        """

    @rmi
    def _keystrokes(self, data: str) -> None:
        pass

    @deprecated("Use PSCAD object to send keystrokes directly.")
    def keystroke(self):            # pylint: disable=missing-function-docstring
        return self

    def keystrokes(self, *strokes: Union[str, int]):
        """
        Type a series of strings and/or virtual key strokes.
        """
        for stroke in strokes:
            if isinstance(stroke, int):
                self.stroke(stroke)
            elif isinstance(stroke, str):
                self.typing(stroke)
            else:
                LOG.error("Invalid keystrokes: %r", stroke)

    def key_down(self, vkcode: int):
        """
        Simulate keyboard key press
        """

        self.key('down', vkcode)
        return self

    def stroke(self, vkcode: int):
        """
        Simulate keyboard keystroke
        """

        self.key('stroke', vkcode)
        return self

    def key_up(self, vkcode: int):
        """
        Simulate keyboard key release
        """

        self.key('up', vkcode)
        return self

    def typing(self, data: str, cooked: bool = False):
        """
        Send a series of keystrokes to type in the application.

        Since pressing and holding certain keys will change the meaning of other
        keypresses, modifier prefixes are used to indicate which keys must be
        pressed and released around another key: '!' is for SHIFT, '@' is
        for ALT, and '#' is for CTRL.

        By default, this method will "cook" strings, adding the appropriate
        modifiers to turn a character into a series of modified keypress.
        If `cooked=True` is specified, the given string must already contain
        the required modifiers.

        .. table::
            :widths: auto

            =====================  =========================
            Raw                    Cooked
            =====================  =========================
            He said, 'How & why?'  !he said, '!how !7 why!/'
            =====================  =========================
        """

        if not cooked:
            data = self._cook(data)
        print("Typing:", data)
        return self._keystrokes(data)

    @staticmethod
    def _cook(data: str) -> str:
        """Translate generic ASCII into magic keystroke string"""

        cooked = ''
        for char in data:
            if char in "abcdefghijklmnopqrstuvwxyz 0123456789`-=[]\\;',./":
                cooked += char
            elif char in string.ascii_uppercase:
                cooked += '!'
                cooked += char     # Send uppercase letter, just because
            else:
                # Translate from:
                #       ~!@#$%^&*()_+{}|:"<>?
                # To:
                #       `1234567890-=[]\;',./
                pos = "~!@#$%^&*()_+{}|:\"<>?".find(char)
                if pos >= 0:
                    cooked += '!'
                    cooked += "`1234567890-=[]\\;',./"[pos]
                else:
                    LOG.error("Unknown character: %s", char)

        return cooked


    #===========================================================================
    # Mouse
    #===========================================================================

    @deprecated("Use PSCAD object to send mouse events directly.")
    def mouse(self):                # pylint: disable=missing-function-docstring
        return self

    @rmi
    def _mouse(self, *args):
        pass

    def move(self, x: int, y: int):
        """
        Simulate mouse movement
        """

        self._mouse('move', x, y)
        return self

    #---------------------------------------------------------------------------
    # Left mouse button down/up/click
    #---------------------------------------------------------------------------

    def leftdown(self, x: int, y: int):
        """
        Simulate left mouse button press
        """

        self.move(x, y)
        self._mouse('leftdown')
        return self

    def leftup(self, x: int, y: int):
        """
        Simulate left mouse button release
        """

        self.move(x, y)
        self._mouse('leftup')
        return self

    def leftclick(self, x: int, y: int):
        """
        Simulate left mouse button click
        """

        self.move(x, y)
        self._mouse('leftclick')
        return self

    #---------------------------------------------------------------------------
    # Middle mouse button down/up/click
    #---------------------------------------------------------------------------

    def middledown(self, x: int, y: int):
        """
        Simulate middle mouse button press
        """

        self.move(x, y)
        self._mouse('middledown')
        return self

    def middleup(self, x: int, y: int):
        """
        Simulate middle mouse button release
        """

        self.move(x, y)
        self._mouse('middleup')
        return self

    def middleclick(self, x: int, y: int):
        """
        Simulate middle mouse button click
        """

        self.move(x, y)
        self._mouse('middleclick')
        return self

    #---------------------------------------------------------------------------
    # Right mouse button down/up/click
    #---------------------------------------------------------------------------

    def rightdown(self, x: int, y: int):
        """
        Simulate right mouse button press
        """

        self.move(x, y)
        self._mouse('rightdown')
        return self

    def rightup(self, x: int, y: int):
        """
        Simulate right mouse button release
        """

        self.move(x, y)
        self._mouse('rightup')
        return self

    def rightclick(self, x: int, y: int):
        """
        Simulate right mouse button click
        """

        self.move(x, y)
        self._mouse('rightclick')
        return self

    #---------------------------------------------------------------------------
    # Scroll Wheel
    #---------------------------------------------------------------------------

    def wheel(self, delta: int):
        """
        Simulate mouse scroll wheel movement
        """

        self._mouse('wheel', delta)
        return self


    #===========================================================================
    # Deprecated and uncomplete commands
    #===========================================================================

    @deprecated
    def command(self, cmd_name, scope=None, **kwargs): # pylint: disable=unused-argument,missing-function-docstring
        raise NotImplementedError("Use official documented methods.")

    @deprecated("Use official documented methods.")
    def command_id(self, cmd_name, **kwargs): # pylint: disable=unused-argument,missing-function-docstring
        return self._command(cmd_name)

    @deprecated("Use PSCAD application methods directly")
    def workspace(self):            # pylint: disable=missing-function-docstring
        return self


#===============================================================================
# Typing requires complete types at the end of the module
#===============================================================================

# pylint: disable=wrong-import-order, wrong-import-position, ungrouped-imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .definition import Definition
