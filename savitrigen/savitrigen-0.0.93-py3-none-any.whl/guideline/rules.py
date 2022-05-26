import re

MODULE_NAMING = [
    (lambda name: re.search(r'^[0-9]', name), 'module name cannot start with a number'),
    (lambda name: re.search(r'[A-Z]', name), 'module name must use snake_case'),
    (lambda name: name[-1:] == 's' and name[-2:] != 's', 'module name must be in singular')
]

FIELD_NAMING = [
    (lambda name: re.search(r'^[0-9]', name), 'field name cannot start with a number'),
    (lambda name: re.search(r'[A-Z]', name), 'field name must use snake_case'),
]

PLUGIN_NAMING = [
    (lambda name: not re.search(r'plugin-([a-z]+)$', name), 'module must follow "plugin-name" format')
]
