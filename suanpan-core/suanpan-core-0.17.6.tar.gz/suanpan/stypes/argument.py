import abc


class ArgumentT(object):
    @abc.abstractmethod
    def __init__(self, key, alias=None, label=None, required=False, default=None, choices=[], type=str):
        """init an argument

        Arguments:
            key: the key of the argument
            alias: the alias name of the argument
            label: the label of the argument
            required: is this argument required
            default: default value of the argument
            choices: choices of the argument if have
            type: argument type

        Example:
            String(key="formula", default="")
        """
        ...
