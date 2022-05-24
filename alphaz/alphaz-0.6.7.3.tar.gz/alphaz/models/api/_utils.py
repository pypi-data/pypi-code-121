import jwt

MAIL_PARAMETERS_PATTERN = '[[%s]]'

def fill_config(configuration,source_configuration):
    for key, value in configuration.items():
        for key2, value2 in source_configuration.items():
            if type(value) != dict and MAIL_PARAMETERS_PATTERN%key2 in str(value):
                value = str(value).replace(MAIL_PARAMETERS_PATTERN%key2,value2)
        configuration[key] = value


def merge_configuration(configuration,source_configuration,replace=False):
    for key2, value2 in source_configuration.items():
        if (not key2 in configuration or replace) and type(value2) != dict:
            configuration[key2] = value2

