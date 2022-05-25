def logic_exists_brand(
    ripe_api = None,
    brand = None,
    model = None,
    method = None,
    version = None,
    **kwargs
):
    """
    Checks if a method exists in the 3DB logic scripts.

    :type ripe_api: RipeApi
    :param ripe_api: The ripe API instance.
    :type brand: String
    :param brand: The brand for the 3DB.
    :type model: String
    :param model: The model for the 3DB.
    :type model: String
    :param model: The version for the 3DB.
    :rtype: bool
    :return: Whether the method exists in the 3DB.
    """

    result = ripe_api.logic_exists_brand(
        brand,
        model,
        method,
        version = version
    )
    return result["exists"]

def logic_method_brand(
    ripe_api = None,
    brand = None,
    model = None,
    method = None,
    **kwargs
):
    """
    Executes a method existent in the 3DB logic scripts.
    Decodes byte type returns to strings.

    :type ripe_api: RipeApi
    :param ripe_api: The ripe API instance.
    :type brand: String
    :param brand: The brand for the 3DB.
    :type model: String
    :param model: The model for the 3DB.
    :type model: String
    :param model: The version for the 3DB.
    """

    result = ripe_api.logic_method_brand(
        brand,
        model,
        method,
        version = kwargs.get("version"),
        data_j = kwargs
    )

    # in case the result type is bytes we convert
    # it to a string as it was originally intended to be
    if isinstance(result, bytes): result = result.decode()

    return result

def try_execute_method(method, fallback = None, **kwargs):
    """
    Tries to execute a method with the kwargs provided. It gives
    priority to a method implementation in the kwargs, followed
    by an implementation in the 3DB logic script and finally
    to the default implementation given, returning `None`
    otherwise.

    :type method: String
    :param method: The method name to try to execute.
    :type fallback: Function
    :param fallback: The default function to execute.
    """

    if method in kwargs: return kwargs[method](**kwargs)

    logic_exists = logic_exists_brand(method = method, **kwargs)
    if logic_exists: return logic_method_brand(method = method, **kwargs)

    if fallback: return fallback(**kwargs)
    return None
