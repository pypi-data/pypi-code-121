import numpy
import collections
import pickle
import pandas
import logging
import warnings
from numbers import Number
from collections import OrderedDict
from typing import (
    NoReturn, Any, Dict, List,
    Iterable, NamedTuple, Union,
    Optional, Type,
)

from cosapp.utils.surrogate_models.base import SurrogateModel
from cosapp.ports.enum import PortType
from cosapp.utils.logging import LogLevel
from cosapp.utils.helpers import check_arg
from cosapp.utils.find_variables import find_variables, make_wishlist, natural_varname


logger = logging.getLogger(__name__)


class SurrogateModelProxy(SurrogateModel):
    """Surrogate model proxy used in `SystemSurrogate`.
    Adds an internal property `trained`, and check that model
    has been trained before each prediction.
    """
    def __init__(self, model):
        if not isinstance(model, SurrogateModel):
            raise TypeError(
                "`SurrogateModelProxy` can only wrap `SurrogateModel` instances."
            )
        self.__wrappee = model
        self.__trained = False

    @property
    def trained(self) -> bool:
        return self.__trained

    def train(self, x, y) -> None:
        """Trains surrogate model with inputs `x` and outputs `y`.

        Parameters
        ----------
        x : array-like
            Training input locations
        y : array-like
            Model responses at given inputs.
        """
        model = self.__wrappee
        logger.debug(f"Training model {model} with \n\tX = {x}\n\tY = {y}")
        model.train(x, y)
        self.__trained = True
        logger.debug(f"Model {model} trained")

    def predict(self, x) -> numpy.ndarray:
        """Calculates a predicted value of the response based on the current trained model.

        Parameters
        ----------
        x : array-like
            Point(s) at which the surrogate is evaluated.
        """
        model = self.__wrappee
        if not self.__trained:
            raise RuntimeError(
                f"{type(model).__name__} has not been trained, so no prediction can be made."
            )
        return model.predict(x)

    def get_type(self) -> Type[SurrogateModel]:
        """Returns wrapped model type"""
        return type(self.__wrappee)


class SystemSurrogateState(NamedTuple):
    """Named tuple containing internal state data of a SystemSurrogate object"""
    doe_in: pandas.DataFrame
    doe_out: Union[pandas.DataFrame, OrderedDict]
    model: SurrogateModelProxy
    doe_out_sizes: OrderedDict


class SystemSurrogate:
    """
    Class representing a surrogate model trained from the outputs of an owner system.
    Once the surrogate is created, it supersedes (whenever activated) the behaviour of
    `System.compute()`. 
    """
    __slots__ = ('__owner', '__state', '__need_doe')

    def __init__(self,
        owner: "cosapp.systems.System",
        data_in: Union[pandas.DataFrame, Dict[str, Any]],
        model: Type[SurrogateModel],
        data_out: Optional[Union[pandas.DataFrame, Dict[str, Any]]] = None,
        postsynch: Union[str, List[str]] = '*',
        *args, **kwargs
    ):
        # CHECK ARGS
        from cosapp.systems import System
        check_arg(owner, 'owner', System)
        check_arg(data_in, 'data_in', (pandas.DataFrame, dict))
        check_arg(data_out, 'data_out', (pandas.DataFrame, dict, type(None)))
        if model is not None:
            try:
                check_arg(model, 'model', type, lambda m: issubclass(m, SurrogateModel))
            except ValueError as error:
                error.args = (
                    f"`model` must be a concrete implementation of `SurrogateModel`"
                    f"; got `{model.__name__}`",
                )
                raise
        postsynch = make_wishlist(postsynch, 'postsynch')
        
        # BUILD INTERN DATA
        self.__owner = owner
        self.__need_doe = (data_out is None)
        
        doe_in = pandas.DataFrame.from_dict(data_in) if isinstance(data_in, dict) else data_in
        doe_out = self.__init_doe_out(data_out, postsynch)
        model_obj = None if model is None else SurrogateModelProxy(model(*args, **kwargs))
        self.__state = SystemSurrogateState(doe_in, doe_out, model_obj, OrderedDict())

        # TRAINING
        empty = owner is None or model_obj is None or len(data_in) == 0
        if not empty:
            logger.debug(
                f"Initialize {model.__name__} surrogate for System {owner.name!r}"
                f", with {len(doe_in)} samples of {list(doe_in.columns)}"
            )
            self.__check_unknowns_and_transients()
            self.__prepare_and_train()

        logger.debug(f"System surrogate initialized")

    @property
    def owner(self)-> "cosapp.systems.System":
        return self.__owner

    @property
    def state(self)-> SystemSurrogateState:
        """SystemSurrogateState: inner state of system surrogate"""
        return self.__state

    @property
    def model_type(self)-> Type[SurrogateModel]:
        return self.__state.model.get_type()

    @property
    def trained(self) -> bool:
        return self.__state.model.trained

    @property
    def synched_outputs(self) -> List[str]:
        """List[str]: list of synchronized output variable names"""
        return list(self.__state.doe_out_sizes)

    def __init_doe_out(self, data_out, postsynch) -> "OrderedDict[str, List]":
        doe_out = OrderedDict()
        if isinstance(data_out, pandas.DataFrame):
            doe_out = data_out.to_dict(into=OrderedDict)
        elif data_out is not None:
            doe_out = OrderedDict(data_out)
        elif self.owner is not None:
            watched = self.__get_owner_connections()
            varlist = watched.keys()
            if '*' not in postsynch:
                owner = self.owner
                def writeable(var) -> bool:
                    try:
                        owner[var] = owner[var]
                    except AttributeError:
                        return False
                    else:
                        return True
                varlist = find_variables(owner,
                        includes=postsynch,
                        excludes=None,
                        inputs=False,
                    )
                varlist = set(filter(writeable, varlist))
                # Make sure varlist contains at least owner system outputs
                for port, output in owner.outputs.items():
                    varlist |= set(natural_varname(f"{port}.{var}") for var in output)
            doe_out = OrderedDict((var, []) for var in varlist)
        return doe_out

    def __get_doe_out_sizes(self) -> None:
        state = self.__state
        owner = self.__owner
        doe_out_sizes = OrderedDict.fromkeys(state.doe_out.keys(), None)
        pos = 0
        for var in doe_out_sizes:
            size = 0
            value = owner[var]
            if isinstance(value, Number):
                size = 1
            elif isinstance(value, numpy.ndarray):
                size = value.size
            else:
                raise TypeError(
                    f"Unsupported data type {type(value).__name__} for {owner.name}.{var}"
                )
            doe_out_sizes[var] = (pos, size)
            pos += size
        self.__state = SystemSurrogateState(
            state.doe_in,
            state.doe_out,
            state.model,
            doe_out_sizes,
        )

    def __format_outputs(self) -> numpy.ndarray:
        logger.debug(f"Reshaping outputs")
        state = self.__state
        reshaped_outputs = []
        for k in range(len(state.doe_in)):
            reshaped_outputs.append(
                list(value[k] for value in state.doe_out.values())
            )
        reshaped_outputs = numpy.asarray(list(list(flatten(el)) for el in reshaped_outputs))
        # logger.debug(f"Reshaped outputs are now numpy.ndarray and are: {reshaped_outputs}")
        return reshaped_outputs

    def __format_inputs(self) -> numpy.ndarray:
        logger.debug(f"Reshaping input data")
        res = []
        for couple_values in self.__state.doe_in.values:
            res.append(list(flatten(couple_values)))
        return numpy.asarray(res)

    def __set_and_execute(self) -> None:
        logger.debug(f"Setting and executing in order to build data for training")
        owner = self.__owner
        state = self.__state
        for i, row in state.doe_in.iterrows():
            logger.log(LogLevel.FULL_DEBUG, f"Setting {owner.name!r} input values (DOE row #{i})")
            for var, value in row.items():
                owner[var] = value
            owner.run_drivers()
            # add tracked output data to doe_out
            for var in state.doe_out:
                state.doe_out[var].append(owner[var])

    def add_data(self, newdoe: pandas.DataFrame) -> NoReturn:
        # TODO: Should merge input lists when matching names (not working yet)
        # self.__state = SystemSurrogateState(
        #     self.__state.doe_in,
        #     self.__state.doe_out,
        #     self.__state.model,
        #     OrderedDict(),
        # )
        raise NotImplementedError()

    def __prepare_and_train(self) -> None:
        logger.debug(f"Preparing and training function")
        if len(self.__state.doe_out) == 0:
            raise ValueError(
                f"Cannot train surrogate model: no output found in System {self.owner.name!r}"
            )
        self.__get_doe_out_sizes()
        if self.__need_doe:
            self.__set_and_execute()
        x = self.__format_inputs()
        y = self.__format_outputs()
        self.__train_model(x, y)

    def __train_model(self, x, y) -> None:
        self.__state.model.train(x, y)

    def predict(self, x):
        return self.__state.model.predict(x).reshape(1, -1)[0]

    def compute(self) -> None:
        logger.debug(f"Start meta_compute() instead of {self.owner.name}.compute().")
        inputs = self.__get_owner_inputs()
        outputs = self.predict(inputs)
        self.__set_owner_outputs(outputs)
        logger.debug(f"meta_compute() done")

    def __get_owner_inputs(self) -> numpy.ndarray:
        owner = self.owner
        logger.debug(f"Getting current inputs of system {owner.name}")
        inputs = list(flatten(owner[var] for var in self.__state.doe_in.columns))
        logger.debug(f"Detected input values: {inputs}")
        return numpy.asarray(inputs)

    def __set_owner_outputs(self, np_outputs: numpy.ndarray) -> None:
        owner = self.__owner
        logger.log(LogLevel.FULL_DEBUG, f"Post-synchronize outputs of {owner.name}")
        for var, (pos, size) in self.__state.doe_out_sizes.items():
            if size == 1:
                owner[var] = np_outputs[pos]
            elif size > 1:
                owner[var].ravel()[:] = np_outputs[pos : pos + size]

    def dump(self, filename: str) -> None:
        """Dump current state to file"""
        logger.debug(f"Dumping metamodel in {filename}")
        with open(filename, 'wb') as fp:
            pickle.dump(self.__state, fp)

    @classmethod
    def load(cls, owner: "cosapp.systems.System", filename: str) -> "SystemSurrogate":
        """Load system surrogate from file"""
        logger.debug(f"Loading metamodel from {filename}")
        from cosapp.systems import System
        check_arg(owner, 'owner', System)
        with open(filename, 'rb') as fp:
            state = pickle.load(fp)
        if not isinstance(state, SystemSurrogateState):
            raise TypeError("cannot load object")
        obj = cls(owner, data_in={}, model=None)
        obj.__state = state
        return obj

    def __check_unknowns_and_transients(self) -> None:
        state = self.__state
        unknowns = get_unknowns_transients(self.__owner)
        unsolvable_unknowns = set(unknowns).difference(state.doe_out)
        trained_unknowns = unsolvable_unknowns.issubset(state.doe_in)
        if not trained_unknowns:
            message = "The following unknowns/transients are not part of the training set; "\
                "future attempts to compute them with a driver may fail:"
            for name in unknowns.difference(state.doe_in):
                message += f"\n\t- {name}"
            warnings.warn(message)

    def __get_owner_connections(self) -> "OrderedDict[str, list]":
        return get_dependent_connections(self.__owner)


def flatten(iterable: Iterable) -> Iterable:
    for elem in iterable:
        if isinstance(elem, collections.abc.Iterable) and not isinstance(elem, str): 
            yield from flatten(elem)
        else:
            yield elem


def get_dependent_connections(system: "cosapp.systems.System") -> Dict[str, PortType]:
    """
    This function returns a dictionnary mapping variable names to a port direction.
    Keys are absolute paths to connected inputs and all outputs.
    Values are owner port direction.
    """
    logger.debug(f"Starting recursive search of connected inputs and all outputs on {system.name}")

    def get_connections(system, head_system) -> Dict[str, PortType]:
        """Recursive inner version of `get_dependent_connections`"""
        result = dict()
        prefix = ""
        if system is not head_system:
            prefix = f"{head_system.get_path_to_child(system)}."
            connectors = system.parent.systems_connectors.get(system.name, [])
            for connector in connectors:
                sink = connector.sink
                logger.debug(f"Detecting connector {connector} with sink {sink.name!r}")
                if sink.is_input:
                    for var in connector.sink_variables():
                        key = f"{prefix}{sink.name}.{var}"
                        result[key] = PortType.IN
                        logger.debug(f"Add {key} to list of connected inputs")

        for output in system.outputs.values():
            logger.debug(f"Checking output {output}.")
            for var in output:
                key = f"{prefix}{output.name}.{var}"
                result[key] = PortType.OUT
                logger.debug(f"Add {key} to list of outputs")
        if system.is_standalone():
            unknowns = system.get_unsolved_problem().unknowns
            for unknown in unknowns:
                key = f"{prefix}{unknown}"
                result[key] = PortType.IN
                logger.debug(f"Add {key} to list of unknowns")
        for child in system.children.values():
            logger.debug(f"Targeted child of recursive getter of connected inputs and all outputs is {child}")
            result.update(get_connections(child, head_system))
        return result

    return get_connections(system, system)


def get_unknowns_transients(system: "cosapp.systems.System") -> set:
    res = set()
    problem = system.get_unsolved_problem()
    for collection in (problem.unknowns, problem.transients):
        res |= set(collection)
    return res
