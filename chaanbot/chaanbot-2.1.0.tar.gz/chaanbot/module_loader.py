import importlib
import logging
from typing import List, Any

import pkg_resources

logger = logging.getLogger("module_loader")


class ModuleLoader:
    """ Responsible for loading modules """

    def __init__(self, config, database, requests):
        self.database = database
        self.requests = requests

        enabled_modules = config.get("modules", "enabled", fallback=None)
        if enabled_modules:
            self.enabled_modules = [str.strip(module_name) for module_name in enabled_modules.split(",")]
            logger.debug("Enabled modules: {}".format(self.enabled_modules))

        disabled_modules = config.get("modules", "disabled", fallback=None)
        if disabled_modules:
            self.disabled_modules = [str.strip(module_name) for module_name in disabled_modules.split(",")]
            logger.debug("Disabled modules: {}".format(self.disabled_modules))

    def load_modules(self, config, matrix) -> List[Any]:
        """ Load modules in the module package, as specified by enabled and disabled in config file,
        and return a list of instantiated module classes """
        files = self._get_files_in_module_dirs()
        modules = [file.replace('.py', '') for file in files if file.endswith('.py') and '__' not in file]
        logger.info("Existing modules: {}".format(modules))
        modules_to_load = list(filter(lambda cur_module_file: self._is_enabled(cur_module_file), modules))
        if len(modules_to_load) == len(modules):
            logger.info("Loading all modules")
        else:
            logger.info("Loading modules: {}. Others are not enabled or explicitly disabled.".format(modules_to_load))

        loaded_modules = []
        for module_to_load in modules_to_load:
            loaded_modules.append(self._load_module(config, matrix, module_to_load))
        return loaded_modules

    @staticmethod
    def _get_files_in_module_dirs() -> List[str]:
        """ Get files in the chaanbot/module folder and its subfolders"""
        files = pkg_resources.resource_listdir("chaanbot", "modules")
        all_files = files.copy()
        logger.debug("All files in modules folder are: {}".format(all_files))
        for file in files:
            if pkg_resources.isdir("chaanbot/modules/{}".format(file)):
                logger.debug("{} is a folder".format(file))
                subfolder_modules = pkg_resources.resource_listdir("chaanbot", "modules/{}".format(file))
                logger.debug("Got files from inside folder: {}".format(subfolder_modules))
                for subfolder_module in subfolder_modules:
                    all_files.append("{}/{}".format(file, subfolder_module))
        return all_files

    def _load_module(self, config, matrix, relative_module_path) -> Any:
        """ Load a module and return the instantiated module class """
        logger.debug("Importing module: {}".format(relative_module_path))
        module = importlib.import_module("chaanbot.modules." + relative_module_path.replace("/", "."))
        module_class = getattr(module, self._get_class_name(relative_module_path))
        instance = self._instantiate_module_class(module_class, config, matrix)
        instance.always_run = instance.always_run if hasattr(instance, "always_run") else False
        return instance

    def _get_class_name(self, relative_module_path) -> str:
        module_name = self._get_module_name(relative_module_path)
        class_name = ''.join(word.title() for word in module_name.split('_'))
        return class_name

    def _is_enabled(self, relative_module_path) -> bool:
        module_name = self._get_module_name(relative_module_path)
        if hasattr(self, "disabled_modules"):
            if module_name in self.disabled_modules:
                return False
        if hasattr(self, "enabled_modules"):
            return module_name in self.enabled_modules
        return True

    @staticmethod
    def _get_module_name(relative_module_path):
        module_name = relative_module_path.split("/", 1).pop() if "/" in relative_module_path else relative_module_path
        return module_name

    def _instantiate_module_class(self, module_class, config, matrix):
        try:
            return module_class(config, matrix, self.database, self.requests)
        except TypeError:  # Module might not require any parameters, try without
            return module_class()
