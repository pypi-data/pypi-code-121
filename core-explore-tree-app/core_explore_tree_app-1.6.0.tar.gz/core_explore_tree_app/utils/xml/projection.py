# from exceptions import CDCSError
# FIXME: pymongo syntax. Check why we need that and translate to mongoengine if needed.


def get_projection(document):
    """Get the value returned by the projection

    Args:
        document: Data Object

    Returns:
    """
    keys = list(document.dict_content.keys())
    if len(keys) == 0:
        return document.id
    for key in keys:
        return get_projection_value(document.dict_content[key])


def get_projection_value(document):
    """Get the value returned by the projection

    Args:
        document:

    Returns:
    """
    value = document[list(document.keys())[0]]
    if isinstance(value, dict):
        return get_projection_value(value)
    else:
        return value
