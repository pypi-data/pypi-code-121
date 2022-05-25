import yaml

from ..exceptions import ConfigurationException

TEMPLATE = "template"
PARAMETERS = "parameters"
OVERWRITES = "overwrites"


class SFDefinition:
    def __init__(self, definition, file_name):
        if TEMPLATE not in definition:
            raise ConfigurationException(
                f"File {file_name} has missing field '{TEMPLATE}'."
            )
        self.template = definition[TEMPLATE]
        if PARAMETERS not in definition:
            raise ConfigurationException(
                f"File {file_name} has missing field '{PARAMETERS}'."
            )
        self.parameters = definition[PARAMETERS]
        self.overwrites = definition[OVERWRITES] if OVERWRITES in definition else None

    @classmethod
    def create(cls, file):
        with open(file) as f:
            try:
                service_foundry = yaml.full_load(f)
            except yaml.YAMLError as exc:
                raise ConfigurationException(f"File {file} is not in yaml format.")
            return cls(service_foundry, file)
