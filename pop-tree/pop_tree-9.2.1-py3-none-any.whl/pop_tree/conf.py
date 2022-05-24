CLI_CONFIG = {
    "output": {
        "source": "rend",
        "default": None,
    },
    "ref": {
        "positional": True,
        "nargs": "?",
    },
    "recurse": {
        "action": "store_true",
    },
    "graph": {},
    "graph_layout": {},
    "hide": {"nargs": "*"},
    "pypaths": {"nargs": "*"},
}

CONFIG = {
    "ref": {
        "type": str,
        "help": "The ref on the hub to show",
        "default": None,
    },
    "pypaths": {
        "help": "A space delimited list of pypaths to add to the hub",
        "default": [],
    },
    "graph": {
        "help": "Plugin to use for generating a graph, (I.E. 'simple', 'details', 'json')",
        "default": None,
    },
    "graph_layout": {
        "help": "They layout to use with the graph plugin",
        "default": None,
    },
    "hide": {
        "help": "Hide teh named node types from the graph. I.e. functions, contracts, variables",
        "default": [],
    },
}

DYNE = {
    "graph": ["graph"],
    "tree": ["tree"],
}
