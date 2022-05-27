# https://pop.readthedocs.io/en/latest/tutorial/quickstart.html#adding-configuration-data
# In this dictionary goes all the immutable values you want to show up under hub.OPT.tf_idem_auto
CONFIG = {
    "config": {
        "default": None,
        "help": "Load extra options from a configuration file onto hub.OPT.tf_idem_auto",
    },
    "tf_state_bucket_name": {"default": "", "help": "Name of S3 bucket"},
    "tf_state_key": {"default": "", "help": "S3 bucket key name"},
    "idem_describe": {"default": False, "help": "Flag to control IDEM describe step"},
    "get_tf_state_from_s3": {
        "default": False,
        "help": "If true, download the tf_state json file from s3 bucket",
    },
    "output_directory_path": {
        "default": "",
        "help": "Path of the output directory where converted files will be generated",
    },
    "idem_describe_path": {
        "default": "",
        "help": "The sls data collected from IDEM describe command.",
    },
    "tf_state_file_path": {
        "default": "",
        "help": "The terraform state file fetched from s3 bucket. Variable is only used when tf_state is taken as input",
    },
}

# The selected subcommand for your cli tool will show up under hub.SUBPARSER
# The value for a subcommand is a dictionary that will be passed as kwargs to argparse.ArgumentParser.add_subparsers
SUBCOMMANDS = {
    # "my_sub_command": {}
}

# Include keys from the CONFIG dictionary that you want to expose on the cli
# The values for these keys are a dictionaries that will be passed as kwargs to argparse.ArgumentParser.add_option
CLI_CONFIG = {
    "config": {"options": ["-c"]},
    "tf_state_bucket_name": {"options": ["-b", "--s3-bucket-name"]},
    "tf_state_key": {"options": ["-k", "--s3-state-key"]},
    "idem_describe": {"options": ["-d", "--des-flag"]},
    "get_tf_state_from_s3": {"options": ["-s", "--use-s3"]},
    "output_directory_path": {"options": ["-o", "--out"]},
    "idem_describe_path": {"options": ["i", "--idem-desc"]},
    "tf_state_file_path": {"options": ["-t", "--tf-state"]},
    # "my_option1": {"subcommands": ["A list of subcommands that exclusively extend this option"]},
    # This option will be available under all subcommands and the root command
    # "my_option2": {"subcommands": ["_global_"]},
}

# These are the namespaces that your project extends
# The hub will extend these keys with the modules listed in the values
DYNE = {"tf_idem_auto": ["tf_idem_auto"]}
