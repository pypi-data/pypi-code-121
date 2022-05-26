"""
Classes connecting `Port` of foreign `System` to transfer variable values.
"""
import abc
import copy
import logging
import weakref
from types import MappingProxyType
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple, Union, Any

from cosapp.ports import units
from cosapp.ports.port import BasePort, Port
from cosapp.utils.helpers import check_arg, is_numerical

logger = logging.getLogger(__name__)


class ConnectorError(Exception):
    """Raised if a connector cannot be created between two `Port`.

    Attributes
    ----------
    message : str
        Error message
    """

    def __init__(self, message: str):
        """Instantiate a error object from the error descriptive message.

        Parameters
        ----------
        message : str
            Error message
        """
        self.message = message


class BaseConnector(abc.ABC):
    """This class connect two ports without enforcing that all port variables are connected.

    The link is oriented from the source to the sink.

    Parameters
    ----------
    name : str
        Name of the connector
    source : BasePort
        Port from which originate the variables
    mapping : str or List[str] or Dict[str, str]
        (List of) common name(s) or mapping name dictionary
    sink : BasePort
        Port to which the variables are transferred
    """

    def __init__(
        self,
        name: str,
        sink: BasePort,
        source: BasePort,
        mapping: Union[str, List[str], Dict[str, str], None] = None,
    ):
        """Connector constructor from the two `BasePort` to link and the list of variables to map.

        If no mapping is provided, connection will be made between variables based on their names. 
        If a name mapping is provided as a list, the name should be present in both port. And if 
        the mapping is specified as a dictionary, the keys belong to the sink port and the values
        to the source port.

        Parameters
        ----------
        name : str
            Name of the connector
        sink : BasePort
            Port to which the variables are transferred.
        source : BasePort
            Port from which originate the variables.
        mapping : str or List[str] or Dict[str, str], optional
            (List of) common name(s) or mapping name dictionary; default None (i.e. no mapping).
        
        Raises
        ------
        ConnectorError
            If the connection between the `source` and the `sink` is not possible to establish.
        """
        self.__check_port(sink, 'sink')
        self.__check_port(source, 'source')
        check_arg(name, 'name', str, lambda s: len(s.strip()) > 0)

        if source is sink:
            raise ConnectorError("Source and sink cannot be the same object.")

        # Generate mapping dictionary
        if mapping is None:
            mapping = dict((v, v) for v in sink if v in source)
        else:
            mapping = self.format_mapping(mapping)

        self._name = name  # type: str
        self._mapping = mapping  # type: Dict[str, str]
        self._source = self.__get_port(source, sink=False, check=False)  # type: weakref.ReferenceType[BasePort]
        self._sink = self.__get_port(sink, sink=True, check=False)  # type: weakref.ReferenceType[BasePort]

    @abc.abstractmethod
    def transfer(self) -> None:
        """Transfer values from `source` to `sink`."""
        pass

    def __repr__(self) -> str:
        mapping = self._mapping
        if self.preserves_names():
            mapping = list(mapping)
        return "{}({} <- {}, {})".format(
            type(self).__qualname__,
            self.sink.contextual_name,
            self.source.contextual_name,
            mapping,
        )

    @property
    def name(self) -> str:
        """str : name of the connector."""
        return self._name

    @property
    def source(self) -> BasePort:
        """`BasePort`: Port from which transferred values originate."""
        return self._source()

    @source.setter
    def source(self, port: BasePort) -> None:
        self._source = self.__get_port(port, sink=False, check=True)

    @property
    def sink(self) -> BasePort:
        """`BasePort`: Port to which values are transferred."""
        return self._sink()

    @sink.setter
    def sink(self, port: BasePort) -> None:
        self._sink = self.__get_port(port, sink=True, check=True)

    def __get_port(self, port: BasePort, sink: bool, check=True) -> "weakref.ref[BasePort]":
        """Returns a weakref to `port`, after compatibility check with internal mapping."""
        if sink:
            name = 'sink'
            variables = self.sink_variables()
        else:
            name = 'source'
            variables = self.source_variables()

        if check:
            self.__check_port(port, name)

        for variable in variables:
            if variable not in port:
                raise ConnectorError(
                    f"{name.title()} variable {variable!r} does not exist in port {port}."
                )
        
        return weakref.ref(port)

    @staticmethod
    def __check_port(port: BasePort, name: str) -> None:
        check_arg(port, name, BasePort, stack_shift=1)

        if not port.owner:
            raise ConnectorError(f"{name.title()} owner is undefined.")

    def __len__(self) -> int:
        return len(self._mapping)

    @property
    def mapping(self) -> Dict[str, str]:
        """Dict[str, str] : Variable name mapping between the sink (key) and the source (value)."""
        return MappingProxyType(self._mapping)

    def sink_variables(self) -> Iterator[str]:
        return self._mapping.keys()

    def source_variables(self) -> Iterator[str]:
        return self._mapping.values()

    def sink_variable(self, source_variable: str) -> str:
        """Returns the name of the sink variable associated to `source_variable`"""
        for sink, source in self._mapping.items():
            if source == source_variable:
                return sink
        raise KeyError(source_variable)

    def source_variable(self, sink_variable: str) -> str:
        """Returns the name of the source variable associated to `sink_variable`"""
        return self._mapping[sink_variable]

    def preserves_names(self) -> bool:
        """Returns `True` if connector mapping preserves variable names,
        `False` otherwise."""
        return all(target == origin for target, origin in self._mapping.items())

    def is_mirror(self) -> bool:
        """Returns `True` if connector is an identical, one-to-one mapping
        between two ports of the same kind; `False` otherwise."""
        sink, source = self.sink, self.source
        return (
            type(sink) is type(source)
            and isinstance(sink, Port)
            and len(self) == len(sink)
            and self.preserves_names()
        )

    def update_mapping(self, mapping: Dict[str, str]) -> None:
        """Extend current mapping with additional dictionary.

        Parameters
        ----------
        mapping : Dict[str, str]
            Variable name mapping extending current mapping.
        """
        self._mapping.update(mapping)

    def remove_variables(self, names: Iterable[str]) -> None:
        """Remove the provided variables from this connection.

        The provided names should be sink names.

        Parameters
        ----------
        names : Iterable[str]
            Collection of sink variable names to be removed.
        """
        for variable in names:
            del self._mapping[variable]

    def info(self) -> Union[Tuple[str, str], Tuple[str, str, Dict[str, str]]]:
        """Returns connector information in a tuple.

        If the name mapping is complete, with identical names,
        it is omitted, and the output tuple is formatted as:
            (target_name, source_name)

        Otherwise, output is formatted as:
            (target_name, source_name, name_mapping)

        Returns
        -------
        tuple
            Tuple representing connector
        """
        # If the mapping is full and with the same nomenclature
        target, origin = self.port_names()
        same_nomenclature = False
        if len(self._mapping) == len(self.source) == len(self.sink):
            same_nomenclature = self.preserves_names()
        if same_nomenclature:
            info = (target, origin)
        else:
            info = (target, origin, self._mapping.copy())
        return info

    def to_dict(self) -> Dict[str, Union[Tuple[str, str], Tuple[str, str, Dict[str, str]]]]:
        """Converts connector into a single-key dictionary.
        The key is the connector name; associated value
        is the tuple returned by method `info()`.

        Returns
        -------
        dict
            Dictionary {name: info_tuple} representing connector
        """
        return {self.name: self.info()}

    def port_names(self) -> Tuple[str, str]:
        """Returns source and sink contextual names as a str tuple.

        Returns
        -------
        tuple
            (source_name, sink_name) tuple
        """
        source, sink = self.source, self.sink

        if source.owner is sink.owner.parent:
            origin = source.name
        else:
            origin = source.contextual_name

        if sink.owner is source.owner.parent:
            target = sink.name
        else:
            target = sink.contextual_name
        
        return target, origin

    @staticmethod
    def format_mapping(mapping: Union[str, List[str], Dict[str, str]]) -> Dict[str, str]:
        """Returns suitable name mapping for connectors,
        from different kinds of argument `mapping`.

        Parameters:
        -----------
        - mapping, Union[str, List[str], Dict[str, str]]:
            Name mapping, given as either a string (single variable),
            a list of strings, or a full name mapping, as a dictionary.
        
        Returns:
        --------
        Dict[str, str]: suitable mapping for connectors.
        """
        if isinstance(mapping, str):
            mapping = {mapping: mapping}
        elif isinstance(mapping, MappingProxyType):
            mapping = dict(mapping)
        elif not isinstance(mapping, dict):
            mapping = dict(zip(mapping, mapping))
        return mapping


class Connector(BaseConnector):
    """Shallow copy connector.
    See `BaseConnector` for base class details.
    """
    def __init__(
        self,
        name: str,
        sink: BasePort,
        source: BasePort,
        mapping: Union[str, List[str], Dict[str, str], None] = None,
    ):
        super().__init__(name, sink, source, mapping)

        self._unit_conversions = {} # type: Dict[str, Optional[Tuple[float, float]]]
        self._transfer_func = {}  # type: Dict[str, Callable[[Any], Any]]
        self.update_unit_conversion()

    @BaseConnector.source.setter
    def source(self, port: BasePort) -> None:
        cls = self.__class__
        super(cls, cls).source.__set__(self, port)
        self.update_unit_conversion()

    @BaseConnector.sink.setter
    def sink(self, port: BasePort) -> None:
        cls = self.__class__
        super(cls, cls).sink.__set__(self, port)
        self.update_unit_conversion()

    def update_mapping(self, mapping: Dict[str, str]) -> None:
        super().update_mapping(mapping)
        self.update_unit_conversion()

    def remove_variables(self, names: Iterable[str]) -> None:
        super().remove_variables(names)
        for variable in names:
            del self._unit_conversions[variable]
            del self._transfer_func[variable]

    def update_unit_conversion(self, name: Optional[str] = None) -> None:
        """Update the physical unit conversion on the connector.

        If `name` is not `None`, update the conversion only for the connexion towards that variable.

        Parameters
        ----------
        name : str, optional
            Name of the variable for which unit conversion needs an update; default None (i.e. all
            conversions will be updated).

        Raises
        ------
        UnitError
            If unit conversion from source to sink is not possible
        """
        source, sink = self.source, self.sink
        mapping = self.mapping

        def update_one_connection(key: str) -> None:
            """Update the unit converter of the connected key.

            Parameters
            ----------
            key : str
                Name of the connected variable for which the unit converter should be updated.
            """
            target = sink.get_details(key)
            origin = source.get_details(mapping[key])
            has_unit = {
                'target': bool(target.unit),
                'origin': bool(origin.unit),
            }
            if has_unit['origin'] != has_unit['target']:
                # Send a warning if one end of the connector
                # has a physical unit and the other is dimensionless
                message = lambda origin_status, target_status: (
                    f"Connector source {origin.full_name!r} {origin_status}, but target {target.full_name!r} {target_status}."
                )
                if has_unit['origin']:
                    logger.warning(
                        message(f"has physical unit {origin.unit}", "is dimensionless")
                    )
                else:
                    logger.warning(
                        message("is dimensionless", f"has physical unit {target.unit}")
                    )
            # Get conversion constants between units
            constants = units.get_conversion(origin.unit, target.unit)
            if constants is None and is_numerical(sink[key]):
                constants = (1.0, 0.0)  # legacy - tests be must changed if suppressed
            self._unit_conversions[key] = constants

            # Get transfer function
            transfer = copy.copy  # fallback
            try:
                factor, offset = self._unit_conversions[key]
            except:
                pass
            else:
                if factor != 1 or offset != 0:
                    transfer = lambda value: factor * (value + offset)
            self._transfer_func[key] = transfer

        if name is None:
            for name in mapping:
                update_one_connection(name)
        else:
            update_one_connection(name)

    def transfer(self) -> None:
        fallback = copy.copy
        source, sink = self.source, self.sink

        for target, origin in self._mapping.items():
            # get/setattr faster for Port
            value = getattr(source, origin)
            transfer = self._transfer_func[target]
            try:
                setattr(sink, target, transfer(value))
            except TypeError:
                setattr(sink, target, fallback(value))


class DeepCopyConnector(BaseConnector):
    """Deep copy connector.
    See `BaseConnector` for base class details.
    """
    def transfer(self) -> None:
        source, sink = self.source, self.sink

        for target, origin in self._mapping.items():
            value = getattr(source, origin)
            setattr(sink, target, copy.deepcopy(value))
