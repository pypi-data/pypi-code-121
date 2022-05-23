import os.path
import os
import configparser
from ..core.command import Command
from ..utils.utils import *


class ConfigCommand(Command):
    LOCAL_CONFIG_FILE = "flutter_gen.config"

    __instance = None

    @staticmethod
    def getInstance():
        if ConfigCommand.__instance == None:
            return ConfigCommand()
        return ConfigCommand.__instance

    @property
    def default_local_config_file_path(self):
        return "./{}".format(self.LOCAL_CONFIG_FILE)

    @property
    def local_config_exists(self):
        return os.path.isfile(self.default_local_config_file_path)

    @property
    def config_file_path(self):
        return self.default_local_config_file_path

    def read_config(self, name):
        try:
            (section, section_item) = name.split(".")
            config = configparser.ConfigParser()
            config.read(self.config_file_path)
            return config[section][section_item]
        except Exception:
            logError("Can't read config file in %s" % name)
            exit(0)

    def update_project_info(self):
        project_name = input('Enter project name (e.g. Flutter App): ')
        package_name = input('Enter package name (e.g. flutter_app): ')
        bundle_name = input(
            'Enter bundle name  (e.g. com.example.flutter_app):')

        if project_name and package_name and bundle_name:
            config = configparser.ConfigParser()
            config.read(self.config_file_path)

            if 'project' not in config:
                config['project'] = {}

            config["project"]["application_name"] = project_name
            config["project"]["package_name"] = package_name
            config["project"]["bundle_name"] = bundle_name

            # write to file
            with open(self.config_file_path, "w") as f:
                config.write(f)
        return (project_name, package_name, bundle_name)

    def create_config(self):
        if self.local_config_exists:
            log("Config file is exist")
            return
        config = configparser.ConfigParser()
        config.read(self.config_file_path)

        if "project" not in config:
            config["project"] = {}
        if "localization" not in config:
            config["localization"] = {}

        config["project"]["application_name"] = "Example"
        config["project"]["package_name"] = "example"
        config["project"]["bundle_name"] = "com.example.app"
        config["localization"]["input_path"] = "lib/assets/i18n"
        config["localization"]["output_path"] = "lib/generated"
        config["localization"]["file_name"] = "i18n.g.dart"

        # write to file
        with open(self.config_file_path, "w") as f:
            config.write(f)

    def info(self):
        try:
            with open(self.config_file_path, "r") as f:
                content = f.readlines()
                print("Local configuration:\n")
                print("".join(content))
        except Exception:
            print("The configuration file does not exist.")
