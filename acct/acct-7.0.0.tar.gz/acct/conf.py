CLI_CONFIG = {
    "input_file": {
        "positional": True,
        "subcommands": ["encrypt", "decrypt"],
    },
    "acct_key": {"os": "ACCT_KEY", "subcommands": ["encrypt", "decrypt"]},
    "acct_file": {"os": "ACCT_FILE", "subcommands": ["encrypt", "decrypt"]},
    "extras": {
        "render": "json",
    },
    "render_pipe": {},
    "crypto_plugin": {"subcommands": ["encrypt", "decrypt"]},
    "output": {"source": "rend", "subcommands": ["decrypt"]},
    "output_file": {"subcommands": ["encrypt"]},
}
CONFIG = {
    "acct_file": {
        "default": None,
        "help": "An encrypted acct file",
    },
    "acct_key": {
        "default": None,
        "help": "The key to encrypt the file with, if no key is passed a key will be generated and displayed on after the encrypted file is created",
    },
    "extras": {
        "default": None,
        "help": "Additional arbitrary configuration values as a json string",
    },
    "crypto_plugin": {
        "default": "fernet",
        "help": "The crypto plugin to use with acct",
    },
    "render_pipe": {
        "default": "jinja|yaml",
        "help": "The render pipe to use to parse input files before they are encrypted",
    },
    "serial_plugin": {
        "default": "msgpack",
        "help": "The pop-serial plugin to use to serialize data before it is encrypted",
    },
    "allowed_backend_profiles": {
        "default": None,
        "help": "A list of backend profile names to allow, defaults to ALL",
    },
    "output_file": {"default": None, "help": "The output file name when encrypting"},
}
SUBCOMMANDS = {
    "encrypt": {x: "Use the acct command to encrypt data" for x in ("desc", "help")},
    "decrypt": {x: "Use the acct command to decrypt data" for x in ("desc", "help")},
}
DYNE = {
    "acct": ["acct"],
    "crypto": ["crypto"],
}
