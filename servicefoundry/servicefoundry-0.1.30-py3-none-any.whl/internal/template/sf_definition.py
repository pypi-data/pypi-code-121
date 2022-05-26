import yaml

from ..exceptions import ConfigurationException

TEMPLATE = "template"
PARAMETERS = "parameters"
OVERWRITES = "overwrites"


class SFDefinition:
    def __init__(self, template, parameters, overwrites):
        self.template = template
        self.parameters = parameters
        self.overwrites = overwrites

    @classmethod
    def create(cls, file):
        with open(file) as f:
            try:
                definition = yaml.full_load(f)
                if TEMPLATE not in definition:
                    raise ConfigurationException(
                        f"File {file} has missing field '{TEMPLATE}'."
                    )
                template = definition[TEMPLATE]
                if PARAMETERS not in definition:
                    raise ConfigurationException(
                        f"File {file} has missing field '{PARAMETERS}'."
                    )
                parameters = definition[PARAMETERS]
                overwrites = (
                    definition[OVERWRITES] if OVERWRITES in definition else None
                )
            except yaml.YAMLError as exc:
                raise ConfigurationException(f"File {file} is not in yaml format.")
            return cls(template, parameters, overwrites)
