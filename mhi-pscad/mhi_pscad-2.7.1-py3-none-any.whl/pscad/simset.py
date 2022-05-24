#===============================================================================
# PSCAD Simulation Set
#===============================================================================
"""
**************
Simulation Set
**************

.. autoclass:: SimulationSet


Management
----------

.. automethod:: SimulationSet.name


Tasks
-----

.. automethod:: SimulationSet.list_tasks
.. automethod:: SimulationSet.add_tasks
.. automethod:: SimulationSet.remove_tasks
.. automethod:: SimulationSet.task


Build & Run
-----------

.. automethod:: SimulationSet.run

"""

#===============================================================================
# Imports
#===============================================================================

import re, logging, os
from typing import List, Tuple, Dict, Optional, Union

import mhi.common.path

from .remote import Remotable, rmi, rmi_property, deprecated
from .form import FormCodec

from .types import Parameters

#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# SimulationSet
#===============================================================================

class SimulationSet(Remotable):
    """
    Simulation Set

    A container of Project and External Simulation Set Tasks
    """

    #===========================================================================
    # Validate Simulation Set Name
    #===========================================================================

    @staticmethod
    def validate_name(name: str):
        """
        The ``name`` must conform to PSCAD naming convensions:

        * should start with a letter,
        * remaining characters must be alphanumeric or the underscore ``_``,
        * cannot exceed 30 characters.

        Raises a ``ValueError`` is an invalid name is given.
        """

        if not name  or  not re.fullmatch(r"\w{1,31}", name):
            LOG.error("Invalid simulation set name: %r", name)
            raise ValueError("Name may only contain letters, numbers & "
                             "underscores, and must be less than 30 characters")


    #===========================================================================
    # Identity
    #===========================================================================

    def __repr__(self):
        return "SimulationSet[{}]".format(self._name)


    #===========================================================================
    # Name
    #===========================================================================

    _name = rmi_property(True, True, name='_name')

    def name(self, new_name: str = None) -> str:
        """
        Get or set the simulation set name.

        Parameters:
            new_name (str): New name for the simulation set (optional)

        Returns:
            The name of the simulation set
        """

        if new_name:
            self.validate_name(new_name)
            self._name = new_name

        return self._name


    #===========================================================================
    # Depends On
    #===========================================================================

    @deprecated("Not supported")
    def depends_on(self, name=None): # pylint: disable=no-self-use,unused-argument,missing-function-docstring
        return ""


    #===========================================================================
    # Clone
    #===========================================================================

    @rmi
    def clone(self):
        """
        Duplicate this simulation set
        """


    #===========================================================================
    # Parameters
    #===========================================================================

    @rmi
    def _parameters(self, parameters=None):
        pass

    def parameters(self, parameters: Parameters = None,
                   **kwargs) -> Optional[Parameters]:
        """
        Get/Set simulation set parameters
        """

        codec = FormCodec.simulation_set(self)

        parameters = dict(parameters, **kwargs) if parameters else kwargs
        parameters = codec.encode(parameters)
        parameters = self._parameters(parameters)
        parameters = codec.decode(parameters)

        return parameters


    #===========================================================================
    # Tasks (Projects/External)
    #===========================================================================

    @rmi
    def tasks(self) -> List["ProjectTask"]:
        """
        List projects included in the simulation set.

        Returns:
            List[ProjectTask]: The tasks included in the simulation set.
        """

    def list_tasks(self) -> List[str]:
        """
        List task names included in the simulation set.

        Returns:
            List[str]: The names of the tasks in the simulation set.
        """
        return [task.name for task in self.tasks()]

    @rmi
    def add_task(self, task: Union[str, "Project"]) -> "ProjectTask":
        """
        Add a project task to the simulation set.

        Parameters:
            task: The project to add as a project task to the simulation set.

        Returns:
            ProjectTask: The project task
        """

    @rmi
    def add_tasks(self, *tasks: Union[str, "Project"]) -> None:
        """
        Add one or more tasks (projects) to the simulation set.

        Parameters:
            *tasks: The tasks (projects) to add to the simulation set.
        """

    @rmi
    def _add_ext_task(self, filename):
        pass

    def add_external_task(self, filename: str, folder: str = None
                          ) -> "ExternalTask":
        """
        Add an external task (executable) to the simulation set.

        Parameters:
            filename (str): The executable's filename
            folder (str): Folder of the executable (optional)

        Returns:
            ExternalTask: The external task
        """
        filename = mhi.common.path.expand_path(filename, abspath=True,
                                               folder=folder)
        if not os.path.isfile(filename):
            raise FileNotFoundError("No such executable: "+filename)

        return self._add_ext_task(filename)

    @rmi
    def remove_tasks(self,
                     *tasks: Union[str, "Project", "ProjectTask", "ExternalTask"]
                     ) -> None:
        """
        Remove one or more tasks (projects) from the simulation set.

        Parameters:
            *tasks: The tasks (projects) to remove from the simulation set.
        """

    @rmi
    def task(self, name: str) -> "ProjectTask":
        """
        Retrieve an individual task in the simulation set.

        Parameters:
            task_name (str): Name of task

        Returns:
            ProjectTask: The identified task
        """


    #===========================================================================
    # Move Up/Down/First/Last
    #===========================================================================

    @rmi
    def _move(self, delta):
        pass

    def move_up(self) -> None:
        """
        Move Simulation Set to up one position in list
        """

        self._move(-1)

    def move_down(self) -> None:
        """
        Move Simulation Set to up down position in list
        """

        self._move(+1)

    def to_top(self) -> None:
        """
        Move Simulation Set to start of list
        """

        self._move(-0x80000000)

    def to_bottom(self) -> None:
        """
        Move Simulation Set to end of list
        """

        self._move(+0x7fffffff)


    #===========================================================================
    # Build / Run / Pause / Stop
    #===========================================================================

    #---------------------------------------------------------------------------
    # Clean
    #---------------------------------------------------------------------------

    def clean(self) -> None:
        """
        Remove temporary files created during build/run
        """

        pscad = self._pscad
        pscad._launch(self, clean=pscad._SIM_SETS) # pylint: disable=protected-access


    #---------------------------------------------------------------------------
    # Build
    #---------------------------------------------------------------------------

    def build(self) -> None:
        """
        Build all projects in the simulation set
        """

        pscad = self._pscad
        pscad._launch(self, clean=pscad._SIM_SETS, build=pscad._SIM_SETS) # pylint: disable=protected-access

    def build_modified(self) -> None:
        """
        Build any modified projects in the simulation set
        """

        pscad = self._pscad
        pscad._launch(self, build=pscad._SIM_SETS) # pylint: disable=protected-access


    #---------------------------------------------------------------------------
    # Run
    #---------------------------------------------------------------------------

    @rmi
    def _run(self):
        pass

    def run(self, consumer=None) -> None:
        """
        Run this simulation set.

        Parameters:
            consumer: handler for events generated by the build/run (optional).
        """

        with self._pscad.subscription('build-events', consumer):
            self._run()


#===============================================================================
# SimsetTask
# - For ProjectTask (and perhaps ExternalTask)
#===============================================================================

class SimsetTask(Remotable):
    """
    Simulation Set Task (Abstract)
    """

    def __str__(self):
        return self.name

    @rmi_property
    def name(self):
        """Name of this project task"""

    @rmi_property
    def simulation_set(self):
        """Simulation set the task is part of"""

    @rmi
    def _move(self, delta):
        pass

    def move_up(self) -> None:
        """
        Move the task up one spot in the the task list of the simulation
        """
        self._move(-1)

    def move_down(self) -> None:
        """
        Move the task down one spot in the the task list of the simulation
        """
        self._move(1)

    def to_top(self) -> None:
        """
        Move the task to the top of the task list of the simulation
        """
        self._move(-0x80000000)

    def to_bottom(self) -> None:
        """
        Move the task to the bottom of the task list of the simulation
        """
        self._move(0x7FFFFFFF)


#===============================================================================
# SimulationTask
#===============================================================================

class ProjectTask(SimsetTask):
    """
    Project Simulation Set Task
    """

    def __repr__(self):
        return "ProjectTask[{}]".format(self.name)

    @rmi
    def _parameters(self, parameters):
        pass

    def parameters(self, parameters: Parameters = None, **kwargs
                   ) -> Optional[Parameters]:
        """parameters(parameter=value, ...)
        Get/set simulation set task parameters

        .. table:: Project Task Parameters

           ============= ===== ============================================
           Param Name    Type  Description
           ============= ===== ============================================
           namespace     str   Namespace of project (read-only)
           name          str   Display Name
           ammunition    int   Task count
           volley        int   Maximum Volley
           affinity      int   Trace Affinity
           rank_snap     bool  Specify snapshot file by rank #?
           substitutions str   Substitution set
           clean         bool  Force Re-Build
           ============= ===== ============================================
        """

        codec = FormCodec.simset_project_task(self)

        parameters = dict(parameters, **kwargs) if parameters else kwargs

        if 'namespace' in parameters:
            raise ValueError('Task namespace is read-only')
        parameters = codec.encode(parameters)
        parameters = self._parameters(parameters)
        parameters = codec.decode(parameters)

        return parameters

    @rmi
    def _layers(self, parameters):
        pass

    def layers(self, layer_states=None, **kwargs):
        """layers(layer_name=state, ...)
        Get / set layer overrides for this Simulation Task.

        Each layer can be forced into state different from the project's
        default state.

        .. table:: Layer State Overrides

           ============ ========================================================
           State        Description
           ============ ========================================================
           ``None``     Inherit from the project's layer state
           ``True``     Force the layer to be enabled
           ``False``    Force the layer to be disabled
           ``"Custom"`` Force the layer into the configuration named "Custom"
           ============ ========================================================

        Returns:
            dict: The current simulation task's layer overrides.

        Example::

            # When this simulation set task runs, force the "region1" layer
            # to be enabled, the "region2" layer to be disabled, and the
            # "region3" layer into a custom layer configuration.  Remove any
            # override that was previously applied to "region4" in this task.

            task.layers(region1=True, region2=False, region3="Special",
                        region4=None)
        """

        layer_states = dict(layer_states, **kwargs) if layer_states else kwargs

        if layer_states:                        # pylint: disable=no-else-return
            states = {}
            for name, state in layer_states.items():
                if isinstance(state, str):
                    state = "C_" + state
                elif isinstance(state, bool):
                    state = "1" if state else "2"
                elif state is None:
                    state = "0"
                else:
                    raise TypeError("Invalid state {!r} for layer {}".format(
                        state, name))
                states[name] = state

            return self._layers(states)

        else:
            states = self._layers({})
            for name, state in states.items():
                if state.startswith('C_'):
                    state = state[2:]
                elif state == "0":
                    state = None
                else:
                    state = state == "1"
                layer_states[name] = state

            return layer_states

    @rmi
    def _overrides(self, parameters):
        pass

    def overrides(self, parameters: Parameters = None, **kwargs
                  ) -> Optional[Parameters]:
        """overrides(parameter=value, ...)
        Get / set override parameters for this Simulation Task.

        .. table:: Project Task Override Parameters

            ======================= ===== =============================================
            Parameter Name          Type  Description
            ======================= ===== =============================================
            duration                float Duration of run (sec)
            time_step               float Simulation time-step (µs)
            plot_step               float Output channel plot step
            start_method            int   Startup Method.  0=Standard, 1=From Snapshot
            startup_inputfile       str   Input filename
            save_channels_file      str   Output filename
            save_channels           int   0=Do not save, 1=Legacy Format (``*.out``), \
                                            2=Advanced Format (``*.psout``)
            timed_snapshots         int   0=None, 1=Single, 2=Incremental (Same File), \
                                            3=Incremental (Many Files)
            snapshot_file           str   Snapshot filename
            snap_time               float Snapshot time
            run_config              int   0=Standalone, 1=Master, 2=Slave
            run_count               int   Number of runs
            remove_snapshot_offset  bool  Remove snapshot time offset
            only_in_use_channels    bool  Only send "in use" channels
            state_animation         bool  Enable animation
            manual_start            bool  Manual Start
            ======================= ===== =============================================

        For each of the above parameters, there is an additional parameter,
        prefixed with ``override_``, which controls whether this parameter is used.
        It is automatically set to ``"true"`` if a value other than ``None`` is given,
        and to ``"false"`` if the `None` value is given.
        """

        codec = FormCodec.simset_project_overrides(self)

        parameters = dict(parameters, **kwargs) if parameters else kwargs

        if parameters:                          # pylint: disable=no-else-return
            overrides = {}
            for key, value in parameters.items():
                if key.startswith('override_'):
                    value = "true" if value and str(value).lower() != "false" else "false"
                    overrides[key] = value
                else:
                    if value is not None:
                        overrides[key] = str(value)
                        overrides["override_"+key] = "true"
                    else:
                        overrides["override_"+key] = "false"

            return self._overrides(overrides)

        else:
            overrides = self._overrides(parameters)
            overrides = codec.decode(overrides)
            return overrides

    def __getitem__(self, key):
        parameters = self.parameters()
        return parameters[key]

    def namespace(self) -> str:
        """
        Get the namespace of the task
        """

        return self['namespace']

    @deprecated
    def controlgroup(self, controlgroup=None): # pylint: disable=missing-function-docstring
        raise NotImplementedError()

    @deprecated("Use simulation_task.parameters()")
    def volley(self, volley=None):
        """Get or set the volley count"""
        if volley is None:
            return self['volley']
        return self.parameters(volley=volley)

    @deprecated("Use simulation_task.parameters()")
    def affinity(self, affinity=None):
        """Get or set the affinity"""
        if affinity is None:
            return self['affinity']
        return self.parameters(affinity=affinity)


#===============================================================================
# ExternalTask
#===============================================================================

class ExternalTask(SimsetTask):
    """
    External Simulation Set Task
    """

    def __repr__(self):
        return "ExternalTask[{}]".format(self.name)

    @rmi
    def _parameters(self, parameters):
        pass

    def parameters(self, parameters: Parameters = None, **kwargs
                   ) -> Optional[Parameters]:
        """parameters(parameter=value, ...)
        Get/set External Task Settings

        .. table:: External Task Settings

           ============= ====== ===========================================
           Param Name    Type   Description
           ============= ====== ===========================================
           name          Text   Name
           path          Path   Process to Launch
           args          Text   Arguments
           platform      Choice Platform: X86, X64
           ============= ====== ===========================================
        """

        codec = FormCodec.simset_external_task(self)

        parameters = dict(parameters, **kwargs) if parameters else kwargs

        parameters = codec.encode(parameters)
        parameters = self._parameters(parameters)
        parameters = codec.decode(parameters)

        return parameters

    @rmi
    def stop(self) -> None:
        """
        Unconditionally stop the external task
        """


#===============================================================================
# Typing requires complete types at the end of the module
#===============================================================================

# pylint: disable=wrong-import-order, wrong-import-position, ungrouped-imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .project import Project
