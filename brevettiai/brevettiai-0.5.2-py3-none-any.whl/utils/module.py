import inspect
import logging


log = logging.getLogger(__name__)


def get_parameter_type(parameter):
    if parameter.annotation is not parameter.empty:
        return parameter.annotation
    elif parameter.default is not parameter.empty:
        return type(parameter.default)
    else:
        return type(None)


class Module:
    """
    Base class for serializable modules
    """
    def get_config(self):
        signature = inspect.signature(self.__init__)
        # Extract parameters
        config = {x: getattr(self, x) for x in signature.parameters.keys() if hasattr(self, x)}

        # Map sub modules
        for k, v in config.items():
            if isinstance(v, Module):
                config[k] = v.get_config()
            else:
                if hasattr(config[k], "numpy"):
                    config[k] = config[k].numpy()
                if hasattr(config[k], "tolist"):
                    config[k] = config[k].tolist()

        return config

    @classmethod
    def from_config(cls, config):
        if config is None:
            return None
        valid_config: dict = {}
        signature = inspect.signature(cls.__init__)
        for k, v in signature.parameters.items():
            ptype = get_parameter_type(v)
            if k in config:
                if issubclass(ptype, Module):
                    valid_config[k] = ptype.from_config(config[k])
                else:
                    valid_config[k] = config[k]
            if v.kind==inspect._ParameterKind.VAR_KEYWORD:
                for k in config.keys():
                    if k not in valid_config:
                        valid_config[k] = config[k]

        if len(config) != len(valid_config):
            log.warning("Invalid config keys: " + ", ".join(list(set(config) - set(valid_config))))
        return cls(**valid_config)

    def copy(self):
        return self.from_config(self.get_config())

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validator

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            type=cls.__name__
        )

    @classmethod
    def validator(cls, x):
        if isinstance(x, cls):
            return x
        return cls.from_config(x)
