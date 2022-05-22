EMPTY_TOOL_CONF_FILE_PARAMETER_VALUES_ERROR = (
    'Error! Wrong configuration parameters values:\n{wrong_parameters_table}'
)

EMPTY_REQUIRED_TOOL_CONF_PARAMETER_VALUES_ERROR = (
    'Error! Wrong configuration parameters values:\n{wrong_parameters_table}'
)

WRONG_CONFIGURATION_FILE_FORMAT_ERROR = (
    'Error! Please, check --format parameter. Allowed values are conf or env.'
)

DIFFERENT_EXTENSION_CONFIGURATION_FILE_AND_FORMAT_ERROR = (
    'Error! Configuration file must have the same extension as the format.'
)

EMPTY_KEY_COLUMN_VALUES_ERROR = (
    'Error! Please set key_column_values parameter value.'
)

KEY_COLUMN_VALUES_ARE_NOT_INTEGER_ERROR = (
    'Key column ids are not integer. --key_column_ids is a string contains '
    'integers with comma delimiter.'
)

CONFIGURATION_DIRECTORY_DOES_NOT_EXIST = (
    'Configuration directory does not exist! Please, before running commands '
    'you need to configure "{tool_name}". Execute:\n$ {tool_name} configure'
)
CONFIGURATION_FILE_DOES_NOT_EXIST = (
    'Configuration file does not exist! Please, before running commands '
    'you need to configure "{tool_name}". Execute:\n$ {tool_name} configure'
)
CONFIGURATION_FILE_IS_DIRECTORY_ERROR = (
    'Error! Please, check --configuration_path, because this is a existing '
    'directory path! Path - "{path}"'
)
CONFIGURATION_FILE_ALREADY_EXISTS_WARNING = (
    'Configuration file already exists. It would be overwritten. Path - '
    '"{path}"'
)

WRONG_ARGUMENT_VALUE = (
    'Error! Please, check {argument_name} and set correct value.'
)

ARGUMENT_VALUE_WITHOUT_DIMENSION_ERROR = (
    'Error! Value of {argument_name} must be ends with dimension MB or GB.'
)

PROPERTY_NOT_FOUND_IN_REQUIRED_CONFIGS = (
    'Error! Section - {section} and option - {option} not found in required '
    'configs tools = {required_config_tool_names}.'
)

IMAGE_NOT_FOUND_ERROR = (
    'Error! Before running container you should build or pull image.'
)
