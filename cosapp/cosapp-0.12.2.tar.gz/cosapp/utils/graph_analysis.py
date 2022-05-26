from cosapp.systems import System
from cosapp.ports.port import BasePort
from cosapp.core.variableref import VariableReference
from cosapp.utils.naming import natural_varname
from cosapp.utils.helpers import check_arg

from typing import Dict, Set, Tuple


def get_free_inputs(system: System) -> Dict[str, VariableReference]:
    """Searches all free inputs within `system`, and returns a dictionary
    mapping each input to their source variable (may differ from input,
    in case of pulling).

    Returns:
    --------
    mapping: Dict[str, str]
        Dictionary of the kind `input_name`: `free_input_name`.
    """
    check_arg(system, 'system', System)

    def recursive_search(system: System, head: System) -> Tuple[Dict[str, str], Set[str]]:
        """Recursive inner version of `get_dependent_connections`"""
        inputs = dict()
        bound_inputs = set()  # type: Set[str]
        prefix = "" if system is head else f"{head.get_path_to_child(system)}."

        def get_portname(port: BasePort) -> str:
            if port.owner is system:
                return f"{prefix}{port.name}"  # avoid unnecessary path search
            return port.full_name(trim_root=True)

        for port in system.inputs.values():
            portname = get_portname(port)
            inputs.update({
                f"{portname}.{name}": f"{portname}.{name}"
                for name in port
            })

        for connector in system.incoming_connectors():
            if not connector.is_active:
                continue
            sink, source = connector.sink, connector.source
            if sink.is_output:
                continue
            sink_name = get_portname(sink)
            if source.is_output:
                bound_inputs |= set(
                    f"{sink_name}.{target}"
                    for target in connector.sink_variables()
                )
            else:
                source_name = get_portname(source)
                inputs.update({
                    f"{sink_name}.{target}": f"{source_name}.{origin}"
                    for target, origin in connector.mapping.items()
                })

        for child in system.children.values():
            child_inputs, child_bound_inputs = recursive_search(child, head)
            bound_inputs |= child_bound_inputs
            for key, alias in child_inputs.items():
                try:
                    # Check if `ref` is already mapped in parent
                    inputs[key] = inputs[alias]
                except KeyError:
                    inputs[key] = alias

        return inputs, bound_inputs

    root = system.root()
    
    if system is root or system.parent is root:
        # Most likely case
        start = system
    else:
        # If system is neither root nor a child of root,
        # the search must start just below root, to make sure
        # highest-level aliases are not connected to an output.
        # This is slow, and should be avoided.
        start = system.path()[1]

    inputs, bound_inputs = recursive_search(start, root)
    bound_inputs &= set(inputs.values())

    name2variable = root.name2variable
    result = dict()

    for key, src in inputs.items():
        if src in bound_inputs:
            continue
        ref = name2variable[key]
        try:
            context = system.get_path_to_child(ref.context)
        except:
            # context is not in system tree - skip key
            continue
        new_key = f"{ref.mapping.name}.{ref.key}"
        if context:
            new_key = f"{context}.{new_key}"
        result[natural_varname(new_key)] = result[new_key] = name2variable[src]

    return result
