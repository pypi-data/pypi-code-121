CLI_CONFIG = {
    "api_version": {"subcommands": ["aws"], "dyne": "pop_create"},
    "region": {
        "subcommands": ["aws"],
        "dyne": "pop_create",
    },
    "services": {
        "subcommands": ["aws"],
        "dyne": "pop_create",
    },
}
CONFIG = {
    "api_version": {
        "default": None,
        "help": "The cloud api version to target",
        "dyne": "pop_create",
    },
    "region": {
        "default": "us-west-2",
        "help": "The cloud region to target",
        "dyne": "pop_create",
    },
    "services": {
        "default": [],
        "nargs": "*",
        "help": "The cloud services to target, defaults to all",
        "dyne": "pop_create",
    },
}
SUBCOMMANDS = {
    "aws": {
        "help": "Create idem_aws state modules by parsing boto3",
        "dyne": "pop_create",
    },
}
DYNE = {
    "acct": ["acct"],
    "exec": ["exec"],
    "pop_create": ["autogen"],
    "states": ["states"],
    "tool": ["tool"],
    "esm": ["esm"],
    "reconcile": ["reconcile"],
}
