import os
import yaml

sources_directory = os.getcwd() + "/src"


def get_config(directory):
    deps_filename = directory + "/wks.yml"
    if os.path.exists(deps_filename):
        f = open(deps_filename, "r")
        deps = yaml.load(f, Loader=yaml.Loader)

        return deps

    return None
