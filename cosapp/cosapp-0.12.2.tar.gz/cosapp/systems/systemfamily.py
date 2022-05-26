from enum import Enum
import logging
from typing import List, Optional

from cosapp.systems.system import System, ConversionType
from cosapp.utils.helpers import check_arg

logger = logging.getLogger(__name__)


class SystemFamily(System):
    # TODO clarify why its a System and why System has `convert_to`
    # Is it abstract?
    """Abstract class defining a family of `System` convertible in one another."""

    __slots__ = ('family_name', 'modelings')

    def __init__(self, name: str, **kwargs):
        self.modelings = SystemFamilyModelings()  # type: SystemFamilyModelings
        self.family_name = "not_defined"  # type: str
        super(SystemFamily, self).__init__(name, **kwargs)

    def possible_conversions(self) -> List[str]:
        """Get the list of possible conversions between `System` type inside the `SystemFamily`.

        Returns
        -------
        List[str]
            List of conversion methods available
        """
        rtn = [meth for meth in dir(self) if type(self).__name__ + "_to_" in meth]
        return rtn

    def convert_to(self, to_type: str, auto: ConversionType = ConversionType.manual):
        """Convert the current `System` in the provided to_type class.

        Parameters
        ----------
        to_type : str
            Type name of the target new class
        auto : ConversionType, optional
            Type of conversion; default manual
        """
        check_arg(to_type, "to_type", str, lambda s: len(s) > 0)
        check_arg(auto, "auto", ConversionType)

        self_type = self.__class__.__name__

        if auto != ConversionType.manual:
            to_type = getattr(self.modelings, auto.value)()

        if self_type == to_type:
            raise ValueError(
                'Failed to convert "{}" #{} to #{}: same classes'.format(
                    self.name, self_type, to_type
                )
            )

        method_name = f"{self_type}_to_{to_type}"

        if method_name in self.possible_conversions():
            converter = getattr(self, method_name)
        else:
            raise ValueError(
                'Failed to convert "{}" #{} to #{}: method does not exist'.format(
                    self.name, self_type, to_type
                )
            )

        parent = self.parent
        if parent is None:
            raise ValueError(
                'Failed to convert "{}" #{} to #{}: parent system is immutable'.format(
                    self.name, self_type, to_type
                )
            )

        # Restore connections
        to_restore = list(filter(lambda c: c.sink.owner is self, parent.connectors.values()))
        new_obj = converter()
        new_obj.name = name = self.name
        # TODO this is really ugly and should be done by the parent...
        execution_idx = list(parent.exec_order).index(name)
        parent.pop_child(name)
        parent.add_child(new_obj, execution_index=execution_idx)
        for c in to_restore:
            parent.connect(c.sink, c.source, c.mapping)

    def update_connections(self, new_system: System) -> None:
        # TODO this should be called automatically and not in the _to_ user method?
        """Update connections after conversion of this `System` into the `new_system`.

        New connections are created for input port. But for output port, the port
        reference in the existing connections are updated.

        Parameters
        ----------
        new_system : System
            The new type `System` in which the current `System` has been converted into
        """
        for name, port in self.inputs.items():
            if name in new_system.inputs:
                new_system.inputs[name].morph(port)
                port.owner = new_system
                new_system.inputs[name] = port
            else:
                logger.warning(
                    '"{}" conversion: "{}" not found in #{}'
                    ''.format(self.name, name, type(new_system).__name__)
                )

        for name, port in self.outputs.items():
            if name in new_system.outputs:
                # Convert existing output ports to keep existing connections
                new_system.outputs[name].morph(port)
                port.owner = new_system
                new_system.outputs[name] = port
            else:
                logger.warning(
                    '"{}" conversion: "{}" not found in #{}'
                    ''.format(self.name, name, type(new_system).__name__)
                )


class SystemFamilyModelings(list):
    # TODO documentation
    def __init__(self):
        super().__init__()

    def add(self, name, fidelity, cost):
        self.append((name, fidelity, cost))

    def delete(self, name):
        rtn = [idx for idx, tup in enumerate(self) if tup[0] == name]
        for idx in rtn:
            del self[idx]

    def exists(self, name):
        l = [idx for idx, tup in enumerate(self) if tup[0] == name]
        return len(l) > 0

    def best_fidelity_to_cost_ratio(self):
        self.sort(key=lambda tup: tup[2] / tup[1])
        return self[0][0]

    def highest_fidelity(self):
        self.sort(key=lambda tup: tup[1])
        return self[-1][0]

    def lowest_fidelity(self):
        self.sort(key=lambda tup: tup[1])
        return self[0][0]

    def highest_cost(self):
        self.sort(key=lambda tup: tup[2])
        return self[-1][0]

    def lowest_cost(self):
        self.sort(key=lambda tup: tup[2])
        return self[0][0]
