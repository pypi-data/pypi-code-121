import os
from typing import Any
from rich.tree import Tree

from dotpyle.utils import path
# from dotpyle.services import FileHandler, LocalFileHandler, Logger
# from dotpyle.services import FileHandler, LocalFileHandler
# from dotpyle.services import  Logger

from dotpyle.services.logger import Logger
from dotpyle.services.file_handler import FileHandler, LocalFileHandler
from dotpyle.exceptions import ConfigHandlerException
from dotpyle.objects.script import Script
from dotpyle.objects.dotfile import Dotfile
from dotpyle.objects.action import BaseAction
from dotpyle.objects.profile import Profile


class ConfigManager:
    """
    Methods to access and process Dotpyle configuration
    """

    __slots__ = (
        "_dotfiles",
        "_scripts",
        "_config_file_handler",
        "_local_file_handler",
        "_logger",
        "_version",
    )

    def __init__(self, file_handler: FileHandler, local_file_handler: LocalFileHandler, logger: Logger) -> None:
        self._logger = logger
        # self.checker = ConfigChecker()
        self._config_file_handler = file_handler
        self._local_file_handler = local_file_handler
        self._scripts: dict[str, Script] = {}
        self._dotfiles: dict[str, Dotfile] = {}
        self._load_config()

    def __del__(self):
        try:
            # First save config file
            self._save_config()
            self._run_pending_actions()
            # TODO rollback config file storage
            self._logger.log("Config file saved successfully")
        except:
            self._rollback_actions()
            self._logger.failure("Error... TODO")

    def _load_config(self) -> None:
        """Read dotpyle.yml config file and creates a OOP mapping of all fields"""
        self._load_general_config()

        """Read dotpyle.local.yml config file and set which dotfiles are linked"""
        self._load_local_config()

        # self._logger.log(*self._dotfiles.values())
        # for dotfile in self._dotfiles.values():
            # self._logger.log(dotfile._get_tree())

    def _load_general_config(self) -> None:
        """Read dotpyle.yml config file and creates a OOP mapping of all fields"""
        config_dict = self._config_file_handler.config
        try:
            self._version = config_dict["version"]
            if self._version != 0:
                raise ConfigHandlerException(
                    "Version '{}' of dotfile.yml file is currently unsupported"
                    .format(self._version)
                )
            if "scripts" in config_dict:
                self._scripts = {
                    alias: Script(alias, filename)
                    for alias, filename in config_dict["scripts"].items()
                }
                self._logger.log(*self._scripts.values())

            if "dotfiles" in config_dict:
                dotfiles_dict = {}
                raw_dotfiles = config_dict["dotfiles"].items()
                for (dotfile_name, raw_profiles) in raw_dotfiles:
                    profiles_dict = {}
                    for profile_name, profile_data in raw_profiles.items():
                        profile = Profile(
                            dotfile_name=dotfile_name,
                            profile_name=profile_name,
                            paths=profile_data.get("paths", []),
                            root=profile_data.get("root", '~'),
                            pre=profile_data.get("pre", []),
                            post=profile_data.get("post", []),
                        )
                        profiles_dict[profile_name] = profile
                    dotfiles_dict[dotfile_name] = Dotfile(
                        program_name=dotfile_name,
                        profiles=profiles_dict,
                    )

                self._dotfiles = dotfiles_dict

        except KeyError as e:
            print(e)  # TODO

    def _load_local_config(self) -> None:
        """Read dotpyle.local.yml config file and enrich current dotfiles with proper information"""
        local_dict = self._local_file_handler.config
        version = local_dict.get("version", None)
        if version != 0:
            raise ConfigHandlerException(
                "Version '{}' of dotfile.local.yml file is currently"
                " unsupported".format(version)
            )
        installed_profiles = local_dict.get("installed", {})
        for dotfile, profile in installed_profiles.items():
            self.get_dotfile(dotfile).get_profile(profile).linked = True

    def _get_linked_dotfiles(self) -> list[Dotfile]:
        """Auxiliar mothod to obtain current linked profiles"""
        linked_dotfiles = []
        for dotfile in self._dotfiles.values():
            if dotfile.linked_profile:
                linked_dotfiles.append(dotfile.linked_profile)
        return linked_dotfiles

    def _get_linked_profiles(self) -> dict[str, str]:
        """Auxiliar mothod to obtain current linked profiles"""
        linked_profiles = {}
        for dotfile in self._dotfiles.values():
            if dotfile.linked_profile:
                linked_profiles[
                    dotfile.program_name
                ] = dotfile.linked_profile.profile_name
        return linked_profiles

    def _serialize_general_config(self) -> dict[str, Any]:
        """Convert all objects back to dict format (dotpyle.yml)"""
        serialized_config = {
            "dotfiles": {
                dotfile_name: dotfile_data._serialize()
                for dotfile_name, dotfile_data in self._dotfiles.items()
            },
            "scripts": {
                script_name: script_data._serialize()
                for script_name, script_data in self._scripts.items()
            },
            "version": self._version,  # here could be updated to newer supported versions (future)
            "settings": self._config_file_handler.config["settings"],
        }
        self._logger.log(serialized_config)
        return serialized_config

    def _serialize_local_config(self) -> dict[str, Any]:
        """Convert all objects back to dict format (dotpyle.local.yml)"""
        serialized_local_config = {
            "installed": self._get_linked_profiles(),
            "version": self._version,  # here could be updated to newer supported versions (future)
        }
        self._logger.log(serialized_local_config)
        return serialized_local_config

    def _save_config(self) -> None:
        self._config_file_handler.save(self._serialize_general_config())
        self._local_file_handler.save(self._serialize_local_config())

    def _get_pending_actions(self) -> list[BaseAction]:
        pending_actions = []
        for dotfile in self._dotfiles.values():
            pending_actions.extend(dotfile._get_pending_actions())
        return pending_actions

    def _rollback_actions(self, actions: list[BaseAction] = None):
        if not actions:
            actions = self._get_pending_actions()
        # Iterate over all executed actions backwards, rollbacking them
        for action in actions[::-1]:
            action.rollback()
        pass

    def _run_pending_actions(self) -> None:
        run_actions: list[BaseAction] = []
        try:
            for action in self._get_pending_actions():
                self._logger.log(action)
                run_actions.append(action)
                action.run()
        except:
            # Rollback executed actions
            self._rollback_actions(run_actions)

    def query_dotfiles(self, program_name: str) -> list[Dotfile]:
        match = []
        if program_name:
            match = [dotfile_data for dotfile_name, dotfile_data in self._dotfiles.items() if dotfile_name == program_name]
        else:
            match.extend(self._dotfiles.values())
        return match

    # def get_tree(self, program_name: str, profile_name: str, only_linked: bool):
        # for dotfile in self.query_dotfiles(program_name):
            # profile_tree = dotfile.get_tree(profile_filter=profile_name, only_linked=only_linked)
            # if len(profile_tree.children) > 0:
                # tree.add(dotfile.get_tree(profile_filter=name, only_linked=only_linked))

    def get_dotfile(self, program_name: str) -> Dotfile:
        if program_name in self._dotfiles:
            return self._dotfiles[program_name]
        raise ConfigHandlerException(
            'Dotfile "{}" does not exist'.format(program_name)
        )

    def set_dotfile(self, dotfile: Dotfile) -> None:
        self._dotfiles[dotfile.program_name] = dotfile

    def edit_dotfile(self, program_name: str):
        pass

    def remove_dotfile(self):
        pass
