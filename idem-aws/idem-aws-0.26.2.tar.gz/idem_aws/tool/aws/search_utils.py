from typing import Dict
from typing import List


def search_filter_syntax_validation(hub, filters: List) -> Dict:
    """
    Validate if the filter syntax is correct. A filter should contain both "name" and "values" parameter.

    Args:
        hub: The redistributed pop central hub.
        filters: filters input from sls file

    Returns:
        Validation result and error message if the validation fails
    """
    result = {"result": True, "comment": ()}
    if filters is not None:
        for fil in filters:
            if "name" not in fil or "values" not in fil:
                result["comment"] = (f"A filter requires 'name' and 'values'",)
                result["result"] = False
                return result
    return result


def convert_search_filter_to_boto3(hub, filters: List) -> List:
    """
    Convert a filters list in the sls format to the boto3 format. Boto3 uses "Name" and "Values" as parameters.

    Args:
        hub: The redistributed pop central hub.
        filters: A filters list in the sls format

    Returns:
        A filters list in the boto3 format
    """
    result = []
    if filters is not None:
        for fil in filters:
            result.append({"Name": fil["name"], "Values": fil["values"]})
    return result
