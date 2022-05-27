def get_updated_cache_parameter_group(hub, old_paramaters, parameter_name_values):

    r"""
    Checks if the input ParameterNamesValues needs to be updated and returns a list of parameters that needs to be modified.

    Args:

        old_parameters: The detailed parameter list for a particular cache parameter group.
        parameter_name_values: Parameters Values as needed by the user.

    Returns:
        [
            {
                "ParameterName": "Text",
                "ParameterValue": "Text"
            },
        ]
    """
    final_parameters = []
    old_parameter_map = {
        params.get("ParameterName"): params for params in old_paramaters
    }
    if parameter_name_values:
        for new_parameters in parameter_name_values:
            if new_parameters.get("ParameterName") in old_parameter_map:
                if not new_parameters.get("ParameterValue") == old_parameter_map.get(
                    new_parameters.get("ParameterName")
                ).get("ParameterValue"):
                    final_parameters.append(new_parameters)
    return final_parameters
