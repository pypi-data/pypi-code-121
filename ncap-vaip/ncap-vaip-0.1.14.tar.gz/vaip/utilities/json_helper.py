from functools import reduce
import logging

logger = logging.getLogger()

def get_nested_value(dictionary, keys, default=None):
    """
    Get a value from a (probably nested) JSON element given a '.'-separated
    string to navigate to the element.

    :param dictionary: Dict to look through.
    :param keys: '.'-separated keys in the dict.
    :param default: Default return value if keys is not found.
    :return: Value if one is found.
    """
    # Skip the initial "$"
    if keys.startswith('$.'):
        keys = keys[2:]

    value = reduce(
        lambda d,
        key: d.get(key, default)
        if isinstance(d, dict) else default, keys.split("."), dictionary
    )
    if value is None:
        logger.warning("Could not find {0} in the dict".format(keys))

    return value


def find_and_fill_placeholders(template, event):
    """
    Step through nested layers of template. If you find a placeholder,
    replace it with the path in event.

    TODO: Make tail-recursive. 'Accumulate' the template and pass the
        subtemplate separately.
    :param template: Dict to step through and identify placeholders in.
    :param event: (usually) superset of template containing values to
    replace the placeholders with.
    :return: The filled-out template (or subset of it) since Python would
    otherwise update local variables.
    """
    for i, (k, v) in enumerate(template.items()):
        if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
            template[k] = get_nested_value(event, v[2:-2])
        elif isinstance(v, dict):
            template[k] = find_and_fill_placeholders(v, event)

    return template


def merge_dicts(event, template_key):
    """
    Top-level function that finds placeholders in event[template_key] and
    replaces them with the values at the paths indexed by the placeholders
    themselves.

    e.g., if event[template_key] = {"placeholder": "{{$.detail.source_key}}"},
    this function would render event[template_key]["placeholder"] = event[
    "detail"]["source_key"].

    template_key and the placeholders can support nested keys in the event
    dict. See the default value for template_key for usage. "$" is an AWS
    SAM convention for the root of the dict.

    :return: event[template_key] with placeholders replaced.
    """
    template = get_nested_value(event, template_key)

    # Find and replace placeholders recursively
    return find_and_fill_placeholders(template, event)


def generate_placeholder_mapping(placeholder_rows, source_payload):
    """
    Produces a dictionary that maps raw placeholder strings to their equivalent
    filled-in value, based on the dictionary structure of the incoming source_payload.

    eg., if source_payload = { "key": { "to": { "value": "foo" }}},
    and there was a placeholder in the query results = "{{$.key.to.value}}",
    this function would output a dictonary = { "{{$.key.to.value}}": "foo" }

    :param placeholder_rows: an iterable produced by a SPARQL query. Assumed that the second bound variable in a result row is the placeholder literal string.
    :param source_payload: dictionary containing the key paths referenced by the placeholders
    :return: a dictionary with keys corresponding to the raw placeholder string, and values equal to their replaced value
    """
    placeholder_output = {}
    for row in placeholder_rows:
        key = str(row[1])
        value = str(row[1])
        placeholder_output[key] = value
    
    filled_placeholders = find_and_fill_placeholders(placeholder_output, source_payload)
    return filled_placeholders
