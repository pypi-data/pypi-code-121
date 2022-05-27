import re
from types import ModuleType


def convert_local_ns(query_string, local_ns) -> str:
    # remove local_ns items with ModuleType
    local_ns = {
        key: val for key, val in local_ns.items() if not isinstance(val, ModuleType)
    }

    # variables need to be converted
    var_list = list(set(map(str.strip, re.findall(r"=( *?\w+)", query_string))))

    # modifying query_string
    for i in range(len(var_list)):
        var = local_ns.get(var_list[i])
        if var:
            query_string = query_string.replace(var_list[i], f"'{str(var)}'")

    return query_string


def is_url(s):
    p = re.compile(r"^\s*\w*://\w*")
    if p.match(s):
        return True
    else:
        return False


def is_api_token(s):
    p = re.compile(r"^\s*API_TOKEN=\w*")
    if p.match(s):
        return True
    else:
        return False


def is_multiple_queries(s):
    return ";" in s


# deprecated.
def split_string_to_query_list(s: str) -> list:
    """
    Split semi-colon containing string to query list and exclude empty string('').
    """
    return list(filter(None, map(lambda x: x.strip(), s.split(";"))))
