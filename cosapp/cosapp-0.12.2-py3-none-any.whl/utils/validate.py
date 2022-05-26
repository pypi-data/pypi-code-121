from typing import Dict, Tuple


def validate(model: "System") -> Tuple[Dict[str, str], Dict[str, str]]:
    """Check the validity of the provided `System`.
    
    Parameters
    ----------
    model : cosapp.systems.System
        The system to be validated

    Returns
    -------
    Tuple[Dict[str, str], Dict[str, str]]
        Warnings and errors dictionaries - key is the variable name and value the error reason.
    
    """
    from cosapp.ports.enum import Validity

    results = model.check()

    def value_str(value) -> str:
        try:
            return f"{value:.5g}"
        except:
            return str(value)

    def msg_dict(level) -> Dict[str, str]:
        def validity_filter(items) -> bool:
            name, validity = items
            # Second condition below filters inwards and outwards in short name
            return validity == level and "." in name
        output = dict()
        for variable, _ in filter(validity_filter, results.items()):
            port_name, variable_name = variable.rsplit(".", maxsplit=1)
            port = model[port_name]
            ground = port.get_validity_ground(level, variable_name)
            output[variable] = f" = {value_str(port[variable_name])} not in {ground}"
        return output

    return msg_dict(Validity.WARNING), msg_dict(Validity.ERROR)
