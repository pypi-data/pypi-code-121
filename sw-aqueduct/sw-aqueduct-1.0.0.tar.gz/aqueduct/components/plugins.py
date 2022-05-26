# -*- coding: utf-8 -*-
from packaging import version

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..utils.exceptions import GetComponentError


class Plugins(Base):

    """Used to sync plugins from a source instance to a destination instance of Swimlane"""

    def __download_plugin(self, name: str, id: str):
        try:
            self.log(f"Downloading plugin '{name}' from source.")
            return self.source_instance.download_plugin(id)
        except Exception as e:
            raise GetComponentError(type="Plugin", name=name, id=id)

    def sync_plugin(self, name: str, id: str):
        """This class syncs a single Swimlane plugin based on the provided name and ID.

        We first check to see if the provided name of the plugin exists in our destination instances plugin_dict.

        If it is, then we download the plugin from the source instance. If we are successful, we
        then add it to the destination instance.

        If the provided plugin name does not exist in our destination instance plugin_dict then we retrieve the
        plugin from both the source and destination instances. We compare their versions and if the source has
        a version greater than the destination we then add it to the destination instance by upgrading the plugin.

        Args:
            name (str): The name of a Swimlane plugin
            id (str): The internal ID of a Swimlane plugin
        """
        if not self._is_in_include_exclude_lists(name, "plugins"):
            self.log(f"Processing '{name}' plugin with id '{id}'")
            if not self.dest_plugin_dict.get(name):
                plugin = self.__download_plugin(name=name, id=id)
                if plugin:
                    if not Base.dry_run:
                        try:
                            self.log(f"Uploading plugin '{name}' to destination.")
                            resp = self.destination_instance.upload_plugin(name, plugin)
                            self.log(f"Successfully uploaded plugin '{name}' to destination.")
                        except Exception as e:
                            self.log(
                                f"Failed to upload plugin '{name}' to destination '{self.dest_host}'",
                                level="warning",
                            )
                    else:
                        self.add_to_diff_log(name, "added")
            else:
                self.log(
                    f"Plugin '{name}' already exists on destination '{self.dest_host}'. Checking for differences...."
                )
                dest_plugin = self.destination_instance.get_plugin(name=name)
                if not dest_plugin:
                    raise GetComponentError(type="Plugin", name=name)
                source_plugin = self.source_instance.get_plugin(name=name)
                if not source_plugin:
                    raise GetComponentError(type="Plugin", name=name)
                if version.parse(source_plugin.version) > version.parse(dest_plugin.version):
                    plugin = self.__download_plugin(name=name, id=id)
                    if plugin:
                        if not Base.dry_run:
                            self.log(f"Upgrading plugin '{name}' on destination.")
                            self.destination_instance.upgrade_plugin(filename=name, stream=plugin)
                            self.log(f"Successfully upgraded plugin '{name}' on destination.")
                        else:
                            self.add_to_diff_log(name, "upgraded")
                else:
                    self.log("Source and destination have the same version plugin. Skipping...")

    def sync(self):
        """This method is used to sync all plugins from a source instance to a destination instance"""
        self.log(f"Attempting to sync plugins from '{self.source_host}' to '{self.dest_host}'")
        self.dest_plugin_dict = self.destination_instance.plugin_dict
        plugin_dict = self.source_instance.plugin_dict
        if plugin_dict:
            for name, id in plugin_dict.items():
                self.sync_plugin(name=name, id=id)
