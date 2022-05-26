import logging
from typing import Any, List, Union, Sequence, Dict

logger = logging.getLogger(__name__)


def pull_variables(
    child: "cosapp.systems.System", 
    pulling: Union[str, List[str], Dict[str, str]],
):
    """Pull variables from child to the parent.

    Parameters
    ----------
    child: System
        `System` asking to pull variables to its parent
    pulling: str or List[str] or Dict[str, str]
        Map of child ports to pulled ports at the parent system level
    selection: str or List[str] or Dict[str, str]

    """
    from cosapp.systems import System
    from cosapp.ports.port import BasePort, Port
    from cosapp.utils.naming import CommonPorts

    parent: System = child.parent
    if parent is None:
        raise AttributeError(
            f"Can't pull variables from orphan System {child.name!r}"
        )
    method_map = {
        CommonPorts.INWARDS.value: 'add_inward',
        CommonPorts.OUTWARDS.value: 'add_outward',
        CommonPorts.MODEVARS_IN.value: 'add_inward_modevar',
        CommonPorts.MODEVARS_OUT.value: 'add_outward_modevar',
    }
    def copy_variable(
        child: System,
        port_name: str,
        child_var: str,
        parent_var: str,
        value: Any,
    ) -> None:
        """Copy variable `child_var` from `child` into `parent`, as `parent_var`."""
        child_port: BasePort = child[port_name]
        parent_port: BasePort = parent[port_name]
        lock_status = parent._locked
        parent._locked = False
        # Call `add_inward`, `add_outward`, etc., depending on context
        method = getattr(parent, method_map[port_name])
        method(parent_var, value)
        parent._locked = lock_status
        # Copy full variable detail in parent port
        parent_port.copy_variable_from(child_port, child_var, parent_var)
        logger.debug(
            "{}.{} has been duplicated from {}.{} - including "
            "validation range and scope.".format(
                parent.name, parent_var, child.name, child_var
            )
        )

    if isinstance(pulling, str):
        pulling = [pulling]
    if isinstance(pulling, Sequence):
        pulling = dict(zip(pulling, pulling))

    for child_attr_name, parent_attr_name in pulling.items():
        child_port = child[child_attr_name]

        if isinstance(child_port, Port):
            if parent_attr_name not in parent:
                pulled_port = child_port.copy(parent_attr_name)
                parent._add_port(pulled_port)
                logger.debug(
                    f"Port {pulled_port.contextual_name} has been duplicated from"
                    f" {child_port.contextual_name} - including validation range and scope."
                )
            else:
                pulled_port = parent[parent_attr_name]
            
            parent.connect(child_port, pulled_port)

        else:  # ExtensiblePort (inwards or outwards)
            if isinstance(child_port, BasePort):  # Pulling all inwards or outwards
                port_name = child_port.name
                parent_port = parent[port_name]

                for varname in child_port:
                    if varname not in parent_port:
                        value = child_port[varname]
                        copy_variable(child, port_name, varname, varname, value)

                parent.connect(child_port, parent_port, list(child_port))

            else:  # Pulling individual variable
                var = child.name2variable[child_attr_name]
                port_name = var.mapping.name

                if parent_attr_name not in parent[port_name]:
                    copy_variable(child, port_name, child_attr_name, parent_attr_name, child_port)

                parent.connect(child[port_name], parent[port_name], {child_attr_name: parent_attr_name})
