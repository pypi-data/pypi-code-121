"""Export a System as FMU."""
import itertools
import logging
import os
import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Union
from collections.abc import Collection

import numpy

from cosapp.core import __version__ as cosapp_version
from cosapp.drivers import RunSingleCase
from cosapp.drivers.abstractsolver import AbstractSolver
from cosapp.ports.port import BasePort
from cosapp.systems import System
from cosapp.utils.helpers import check_arg
from cosapp.utils.naming import natural_varname

try:
    from pythonfmu import Fmi2Causality, Fmi2Variability, FmuBuilder as PyFmuBuilder
except ImportError:

    class Fmi2Causality(Enum):
        parameter = 0
        calculatedParameter = 1
        input = 2
        output = 3
        local = 4

    class Fmi2Variability(Enum):
        constant = 0
        fixed = 1
        tunable = 2
        discrete = 3
        continuous = 4

    PyFmuBuilder = None


logger = logging.getLogger(__name__)

DECK_FILE_NAME = "system.json"
THIS_YEAR = datetime.now().year


class TimeIntegrator(Enum):
    """Available time integrator for FMU export."""

    EulerExplicit = "Euler explicit"
    RK2 = "Runge-Kutta 2"
    RK3 = "Runge-Kutta 3"
    RK4 = "Runge-Kutta 4"

    @property
    def driver(self) -> str:
        if self.name.startswith("RK"):
            return "RungeKutta"
        else:
            return self.name

    @property
    def options(self) -> Dict[str, str]:
        if self.name.startswith("RK"):
            return dict(order=int(self.name[2:]))
        else:
            return dict()


class VariableType(Enum):
    Boolean = "bool"
    Integer = "int"
    Real = "float"
    String = "bytes"


class Variable(NamedTuple):
    """Variable attributes"""

    name: str
    pytype: str  # Python type
    fmutype: str  # FMU type
    causality: Fmi2Causality
    variability: Optional[Fmi2Variability] = None


class FmuBuilder:
    """CoSApp FMU builder"""

    @staticmethod
    def _add_variables(
        vars: Dict[str, Any],
        causality: Fmi2Causality,
        variability: Optional[Fmi2Variability] = None,
    ) -> List[Variable]:
        """Transforms the to-included variable dictionary in 
        a list of Variable object for injection in the Jinja2 template.
        
        Parameters
        ----------
        vars : Dict[str, Any]
            Dictionary of the to-be-included variables
        causality : Fmi2Causality
            Causality of the variables
        variablility : Fmi2Variablity or None
            Variability of the variables; default not specified

        Returns
        -------
        List[Variable]
            List of Variable object to be injected in the template.
        """
        l_vars = list()
        for name, value in vars.items():
            try:
                dtype = FmuBuilder._get_variable_type(value)
            except TypeError as e:
                raise TypeError(f"{e!s} for variable {name}")

            l_vars.append(
                Variable(
                    name,
                    dtype.value,
                    dtype.name,
                    causality.name,
                    getattr(variability, "name", None),
                )
            )

        return l_vars

    @staticmethod
    def _get_default_value(names: Iterable[str], system: System) -> Dict[str, Any]:
        """Read the default value of the variable in the system.
        
        Parameters
        ----------
        names: Iterable[str]
            Variable to look for
        system: System
            CoSApp system in from which the values need to be taken

        Returns
        -------
        Dict[str, Any] : Dictionary of the variable name (key) with their value (value)
        """
        values = dict()
        for name in names:
            try:
                values[name] = eval(f"master.{name}", {"master": system})
            except (AttributeError, IndexError, KeyError):
                raise ValueError(
                    f"Variable {name} not found in the system '{system.name}'."
                )

        return values

    @staticmethod
    def _get_default_variables(
        ports: Dict[str, BasePort], to_skip: Iterable[str]
    ) -> Dict[str, Any]:
        """Get the default variable list from a port list.

        Variable names will be `port`.`variable_name` except for
        inwards and outwards (it will be `variable_name` directly).

        Only variables of type supported by FMI are listed.

        Parameters
        ----------
        ports : Dict[str, BasePort]
            List of port to extract variables from
        to_skip : Iterable[str]
            List of variable names to ignore

        Returns
        -------
        Dict[str, Any]
            Return a dictionary of the variables to be included with their
            default value.
        """
        vars = dict()
        for port_name, port in ports.items():
            for name in port:
                full_name = natural_varname(f"{port_name}.{name}")
                if full_name in to_skip:
                    continue

                value = port[name]
                try:
                    FmuBuilder._get_variable_type(value)
                except TypeError:
                    logger.debug(
                        f"Variable {full_name!r} has unsupported type for FMI."
                    )
                else:
                    vars[full_name] = value
        return vars

    @staticmethod
    def _get_documentation_folder(dest: Path) -> Path:
        """Path: The subfolder containing the documentation files."""
        doc_folder = dest / "documentation"
        doc_folder.mkdir(parents=True, exist_ok=True)
        return doc_folder

    @staticmethod
    def _get_project_folder(dest: Path) -> Path:
        """Path: The subfolder containing the project files."""
        project_folder = dest / "project_files"
        project_folder.mkdir(parents=True, exist_ok=True)
        return project_folder

    @staticmethod
    def _get_script_file(dest: Path, system: System, suffix: str) -> Path:
        """Path: Facade module file path."""
        class_name = type(system).__name__
        path = FmuBuilder._get_project_folder(dest)
        filename = path / f"{class_name.lower()}{suffix}.py"
        filename.parent.mkdir(parents=True, exist_ok=True)
        return filename

    @staticmethod
    def _get_variable_type(value: Any) -> VariableType:
        """Get the FMI variable type of a value.
        
        Parameters
        ----------
        value : Any
            Value to test
        
        Returns
        -------
        VariableType
            Type of the variable

        Raises
        ------
        TypeError
            For unsupported variable types.
        """

        if isinstance(value, (bool, numpy.bool_)):
            dtype = VariableType.Boolean
        elif isinstance(value, (int, numpy.int_)):
            dtype = VariableType.Integer
        elif isinstance(value, (float, numpy.float_)):
            dtype = VariableType.Real
        elif isinstance(value, (str, numpy.str_)):
            dtype = VariableType.String
        elif isinstance(value, numpy.ndarray):
            if value.ndim != 0:
                raise TypeError("Unsupported numpy array")
            if numpy.issubdtype(value.dtype, numpy.dtype(bool)):
                dtype = VariableType.Boolean
            elif numpy.issubdtype(value.dtype, numpy.dtype(int)):
                dtype = VariableType.Integer
            elif numpy.issubdtype(value.dtype, numpy.dtype(float)):
                dtype = VariableType.Real
            elif numpy.issubdtype(value.dtype, numpy.dtype(str)):
                dtype = VariableType.String
            else:
                raise TypeError(f"Unsupported numpy dtype {value.dtype}")
        else:
            dtype = type(value)
            raise TypeError(f"Unsupported type {dtype.__qualname__}")

        return dtype

    @staticmethod
    def generate_fmu_facade(
        system: System,
        inputs: Iterable[str] = None,
        parameters: Iterable[str] = None,
        outputs: Iterable[str] = None,
        locals: Iterable[str] = None,
        time_integrator: Union[TimeIntegrator, str] = TimeIntegrator.RK4,
        nonlinear_solver: Optional[AbstractSolver] = None,
        dest: Union[Path, str] = os.curdir,
        python_env: Union[Path, str, None] = None,
        version: Optional[str] = None,
        author: Optional[str] = None,
        description: Optional[str] = None,
        copyright: Optional[str] = "",
        license: Optional[str] = "",
        fmu_name_suffix: str = "",
    ) -> Path:
        """Export a system as CoSimulation FMU respecting FMI 2.0.

        Inputs, parameters, outputs and locals are by default taken from inputs,
        inwards, outputs and outwards variables of the CoSApp system, respectively. If you wish
        to set an empty list, set the corresponding argument with a empty dictionary.

        You can add a mathematical problem to the system by passing the proper
        nonlinear_solver. If it contains a RunSingleCase, its equations will be
        passed to the FMU. 
        
        Parameters
        ----------
        - system : System
            System to be exported
        - inputs : Iterable[str], optional
            List of input variables with initial values; default None
        - parameters : Iterable[str], optional
            List of parameter variables with initial values; default None
        - outputs : Iterable[str], optional
            List of output variables with initial values; default None
        - locals : Iterable[str], optional
            List of local variables with initial values; default None
        - time_integrator : TimeIntegrator, optional
            Time integrator algorithm; default Runge-Kutta 4th order
        - nonlinear_solver : AbstractSolver, optional
            Non linear Driver to use for solving the system at a given instant
        - dest : str or Path, optional
            Destination folder; default current directory
        - python_env : str or Path, optional
            File listing the python dependency; default None
        - version : str, optional
            FMU version; default None
        - author : str, optional
            FMU author; default None
        - description : str, optional
            System description; default None
        - license : str, optional
            FMU license; default ""
        - copyright : str, optional
            FMU copyright; default ""
        - fmu_name_suffix : str, optional
            FMU name; default ""

        Returns
        -------
        pathlib.Path
            Folder path containing FMU facade files
        """
        # Optional dependencies
        try:
            from jinja2 import Environment, PackageLoader
        except ImportError:
            raise ImportError("jinja2 needs to be installed to export a System as FMU.")

        # Check the arguments
        nonetype = type(None)
        check_arg(system, "system", System)
        check_arg(inputs, "inputs", (Collection, nonetype))
        check_arg(parameters, "parameters", (Collection, nonetype))
        check_arg(outputs, "outputs", (Collection, nonetype))
        check_arg(locals, "locals", (Collection, nonetype))
        check_arg(time_integrator, "time_integrator", (TimeIntegrator, str))
        check_arg(nonlinear_solver, "nonlinear_solver", (AbstractSolver, nonetype))
        check_arg(dest, "dest", (Path, str))
        check_arg(python_env, "python_env", (Path, str, nonetype))
        local_vars = dict()
        options = {
            "version": version,
            "author": author,
            "description": description,
            "copyright": copyright,
            "license": license,
        }
        for name, value in options.items():
            if value is not None:
                check_arg(value, name, str)
                local_vars[name] = value

        # Convert argument
        time_integrator = TimeIntegrator(time_integrator)
        temp_dest = Path(dest)

        # Generate the parameters
        system_type = type(system)
        params = {
            "module_name": system_type.__module__,
            "class_name": system_type.__qualname__,
            "driver": time_integrator.driver,
            "time_options": time_integrator.options,
            # TODO 'nl_options': dict(),
            "variables": list(),
            "class_attrs": dict(),
            "system_file": DECK_FILE_NAME,
        }

        for name, value in local_vars.items():
            params["class_attrs"][name] = value

        # TODO FMI supports to set for CoSimulation the DefaultExperiment.stepSize
        # that defines the preferred communicationStepSize

        user_list = set(
            itertools.chain(inputs or [], parameters or [], outputs or [], locals or [])
        )

        if inputs is None:
            inward_port = system.inputs.pop(System.INWARDS)
            inputs = FmuBuilder._get_default_variables(system.inputs, user_list)
            system.inputs[System.INWARDS] = inward_port  # Restore popped port
        else:
            inputs = FmuBuilder._get_default_value(inputs, system)
        if parameters is None:
            parameters = FmuBuilder._get_default_variables(
                {System.INWARDS: system.inputs[System.INWARDS]}, user_list
            )
        else:
            parameters = FmuBuilder._get_default_value(parameters, system)

        if outputs is None:
            outward_port = system.outputs.pop(System.OUTWARDS)
            outputs = FmuBuilder._get_default_variables(system.outputs, user_list)
            system.outputs[System.OUTWARDS] = outward_port
        else:
            outputs = FmuBuilder._get_default_value(outputs, system)

        if locals is None:
            locals = FmuBuilder._get_default_variables(
                {System.OUTWARDS: system.outputs[System.OUTWARDS]}, user_list
            )
        else:
            locals = FmuBuilder._get_default_value(locals, system)

        params["variables"].extend(
            FmuBuilder._add_variables(inputs, Fmi2Causality.input)
        )
        params["variables"].extend(
            FmuBuilder._add_variables(
                parameters, Fmi2Causality.parameter, Fmi2Variability.tunable
            )
        )
        params["variables"].extend(
            FmuBuilder._add_variables(outputs, Fmi2Causality.output)
        )
        params["variables"].extend(
            FmuBuilder._add_variables(locals, Fmi2Causality.local)
        )

        if nonlinear_solver is not None:
            children_driver = list(nonlinear_solver.children.values())
            if len(children_driver) > 1:
                raise ValueError("The nonlinear solver can only have one child.")
            runSingleCase = children_driver[0]
            if not isinstance(runSingleCase, RunSingleCase):
                raise TypeError(
                    "The nonlinear solver child must be of type RunSingleCase."
                )
            # Note:
            #   Since `RunSingleCase` child is unique, a simple merging
            #   of the various mathematical problems by extension works.
            #   It would not be the case in a multi-point design problem,
            #   for example, where off-design, design and local problems
            #   must be assembled with care.
            problem = nonlinear_solver.raw_problem.copy()
            problem.extend(runSingleCase.offdesign)
            problem.extend(runSingleCase.design)
            params["problem"] = problem.to_dict()

        env = Environment(
            loader=PackageLoader("cosapp.tools", "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("pythonfmu.j2")

        rendered_script = template.render(params)

        filename = FmuBuilder._get_script_file(temp_dest, system, fmu_name_suffix)
        with open(filename, mode="w", encoding="utf-8") as f:
            f.write(rendered_script)

        project_folder = FmuBuilder._get_project_folder(temp_dest)
        deck_file = project_folder / DECK_FILE_NAME
        system.save(deck_file)  # Save the customized system

        # Create default environment if it is not provided
        if python_env is None:
            python_env = project_folder / "requirements.txt"

        python_env = Path(python_env)

        if not python_env.exists():
            logger.info("Create default package list.")

            package_list = {"cosapp": cosapp_version}

            python_env.write_text(
                "\n".join(
                    f"{name}~={version}" for name, version in package_list.items()
                )
            )

        doc_folder = FmuBuilder._get_documentation_folder(temp_dest)
        license_file = None
        if license is not None and license.endswith("Proprietary"):
            company = license[: -len("Proprietary")].strip()
            license_file = doc_folder / "licenses" / "license.txt"
            license_file.parent.mkdir(parents=True, exist_ok=True)
            license_file.write_text(
                f"Copyright © {THIS_YEAR} {company} - All Rights Reserved\n"
                f"Unauthorized copying and/or distribution of this source-code, via any medium "
                f"is strictly prohibited\nwithout the express permission of {company}.\n"
                "Proprietary and confidential"
            )

        return temp_dest

    @staticmethod
    def to_fmu(
        system: System,
        inputs: Iterable[str] = None,
        parameters: Iterable[str] = None,
        outputs: Iterable[str] = None,
        locals: Iterable[str] = None,
        time_integrator: Union[TimeIntegrator, str] = TimeIntegrator.RK4,
        nonlinear_solver: Optional[AbstractSolver] = None,
        dest: Union[Path, str] = os.curdir,
        python_env: Union[Path, str, None] = None,
        project_files: Iterable[Union[Path, str]] = set(),
        version: Optional[str] = None,
        author: Optional[str] = None,
        description: Optional[str] = None,
        copyright: Optional[str] = "",
        license: Optional[str] = "",
        fmu_name_suffix: str = "",
    ) -> Path:
        """Export a system as CoSimulation FMU respecting FMI 2.0.

        Inputs, parameters, outputs and locals are by default taken from inputs,
        inwards, outputs and outwards variables of the CoSApp system, respectively. If you wish
        to set an empty list, set the corresponding argument with a empty dictionary.

        You can add a mathematical problem to the system by passing the proper
        nonlinear_solver. If it contains a RunSingleCase, its equations will be
        passed to the FMU. 
        
        Parameters
        ----------
        system : System
            System to be exported
        inputs : Iterable[str], optional
            List of input variables with initial values; default None
        parameters : Iterable[str], optional
            List of parameter variables with initial values; default None
        outputs : Iterable[str], optional
            List of output variables with initial values; default None
        locals : Iterable[str], optional
            List of local variables with initial values; default None
        time_integrator : TimeIntegrator, optional
            Time integrator algorithm; default Runge-Kutta 4th order
        nonlinear_solver : AbstractSolver, optional
            Non linear Driver to use for solving the system at a given instant
        dest : str or Path, optional
            Destination folder; default current directory
        python_env : str or Path, optional
            File listing the python dependency; default None
        project_files : Iterable of str or Path, optional
            List of additional files to be included in the FMU; default no additional files
        version : str, optional
            FMU version; default None
        author : str, optional
            FMU author; default None
        description : str, optional
            System description; default None
        license : str, optional
            FMU license; default ""
        copyright : str, optional
            FMU copyright; default ""
        fmu_name_suffix : str, optional
            FMU name suffix; default ""

        Returns
        -------
        pathlib.Path
            FMU file path object
        """
        dest = Path(dest)
        temp_dest = dest / "tmp"

        temp_dest = FmuBuilder.generate_fmu_facade(
            system,
            inputs,
            parameters,
            outputs,
            locals,
            time_integrator,
            nonlinear_solver,
            temp_dest,
            python_env,
            version,
            author,
            description,
            copyright,
            license,
            fmu_name_suffix,
        )

        if PyFmuBuilder is None:
            logger.warning(
                "pythonfmu needs to be installed to package the simulation as FMU."
            )
            return dest

        project_folder = FmuBuilder._get_project_folder(temp_dest)
        project_files = set([Path(f) for f in project_files])
        project_files.update(project_folder.glob("*"))

        documentation_folder = FmuBuilder._get_documentation_folder(temp_dest)
        PyFmuBuilder.build_FMU(
            FmuBuilder._get_script_file(temp_dest, system, fmu_name_suffix),
            dest=dest,
            project_files=project_files,
            documentation_folder=documentation_folder,
            needsExecutionTool="false",
            canGetAndSetFMUstate="false",
        )

        shutil.rmtree(temp_dest)

        return dest / f"{type(system).__name__}.fmu"


to_fmu = FmuBuilder.to_fmu
