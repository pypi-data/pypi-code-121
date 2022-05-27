from typing import List


def mask_infs(x):
    return f"CASE WHEN {x} > apoc.math.maxLong() THEN null ELSE {x} END"

def is_regex(other):
    """
    Regex is defined either by:
     1. starting and ending the string with '/'
        OR
     2. When the string contains * and the string doesn't start and end with '"'
    """
    return (other.startswith('/') and other.endswith('/')) or \
           ('*' in other and not (other.startswith('"') and other.endswith('"')))


def remove_successive_duplicate_lines(cypher: List[str]):
    """
    Given a list of cypher statements, remove any lines that appear more than once in succession only
    """
    if not cypher:
        return []
    deduplicated = [cypher[0]]
    for line in cypher[1:]:
        if line != deduplicated[-1]:
            deduplicated.append(line)
    return deduplicated


def safe_name(name):
    if name is None:
        return name
    return '__dot__'.join(name.split('.'))


special_dtypes = {
    ('boolean', 'float'): 'tointeger(tofloat({}))',
    ('float', 'boolean'): 'toboolean(tointeger({}))',
    ('boolean', 'number'): 'tointeger({})',
    ('number', 'boolean'): 'toboolean(tointeger({}))',
}

def dtype_conversion(from_dtype, to_dtype, string, *replacements):
    if from_dtype == to_dtype:
        return string
    if from_dtype is None or to_dtype is None:
        return string
    func = special_dtypes.get((from_dtype, to_dtype), f'to{to_dtype}({{}})')
    for replacement in replacements:
        string = string.replace(replacement, func.format(replacement))
    return string
