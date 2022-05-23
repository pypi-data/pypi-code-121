from kolibri.data.text.resources import resources
from pathlib import Path
from kdmt.file import read_json_file
from kolibri.tools._regex import Regex

try:
    patterns_file=resources.get(str(Path('modules', 'regexes', 'defaults.json'))).path
    patterns=read_json_file(patterns_file)
except:
    print("Couldnot Find ressources. Dig you download them?")


# Programmatically compile regex regexes and put them in the global scope
__g = globals()


def compile_patterns_in_dictionary(parent_name, dictionary):
    """
    Replace all strings in dictionary with compiled
    version of themselves and return dictionary.
    """
    for name, regex_str in dictionary.items():
        if isinstance(regex_str, dict) and ("value" in regex_str):
            dictionary[name] = Regex(parent_name, regex_str["value"], regex_str["flags"])
        if isinstance(regex_str, str):
            dictionary[name] = Regex(parent_name, regex_str)
        elif isinstance(regex_str, dict) and "value" not in regex_str:
            compile_patterns_in_dictionary(regex_str)
    return dictionary
try:
    for (name, regex_variable) in patterns.items():
        if isinstance(regex_variable, str):
            # The regex variable is a string, compile it and put it in the
            # global scope
            __g[name] = Regex(name, regex_variable)
        elif isinstance(regex_variable, dict) and "value" in regex_variable:
            __g[name] = Regex(name, regex_variable["value"], regex_variable["flags"])
        elif isinstance(regex_variable, dict):
            # The regex variable is a dictionary, convert all regex strings
            # in the dictionary to their compiled versions and put the variable
            # in the global scope
            __g[name] = compile_patterns_in_dictionary(name, regex_variable)
except:
    pass



