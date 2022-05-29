import logging

from pytconf import Config, ParamCreator


class ConfigSudo(Config):
    """
    Parameters to control whether we use 'sudo' or not
    """
    sudo = ParamCreator.create_bool(
        help_string="use sudo?",
        default=True,
    )


class ConfigFlow(Config):
    """
    Parameters to configure the flow of pydmt
    """
    stop_after_error = ParamCreator.create_bool(
        help_string="Should pydmt stop after first error?",
        default=True,
    )


class ConfigTarget(Config):
    """
    Parameters to configure what is the target of the build
    """
    dev = ParamCreator.create_bool(
        help_string="Is the target to build a dev environment?",
        default=True,
    )


class ConfigOutput(Config):
    """
    Parameters to configure the output of pydmt
    """
    verbose = ParamCreator.create_bool(
        help_string="Should output be verbose?",
        default=True,
    )
    print_not = ParamCreator.create_bool(
        help_string="print out what we are not doing",
        default=False,
    )


class ConfigLogging(Config):
    """
    Parameters to control logging
    """
    loglevel = ParamCreator.create_choice(
        choice_list=[
            logging.getLevelName(logging.NOTSET),
            logging.getLevelName(logging.DEBUG),
            logging.getLevelName(logging.INFO),
            logging.getLevelName(logging.WARNING),
            logging.getLevelName(logging.WARN),
            logging.getLevelName(logging.ERROR),
            logging.getLevelName(logging.FATAL),
            logging.getLevelName(logging.CRITICAL),
        ],
        help_string="What log level to use?",
        default=logging.getLevelName(logging.INFO),
    )
