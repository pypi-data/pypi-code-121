# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..models import Task, TaskLight
from ..utils.exceptions import GetComponentError, UpdateComponentError


class Tasks(Base):

    """Used to sync tasks from a source instance to a destination instance of Swimlane"""

    _plugin_dict = {}

    def _get_dest_plugin_dict(self):
        if not self._plugin_dict:
            for plugin in self.destination_instance.get_plugins():
                if plugin:
                    action_dict = {}
                    _plugin = self.destination_instance.get_plugin(plugin.id)
                    if _plugin.availableActionDescriptors:
                        for action in _plugin.availableActionDescriptors:
                            if action.actionType not in action_dict:
                                action_dict[action.actionType] = {}
                            action_dict[action.actionType].update({"id": action.id, "imageId": action.imageId})
                    if _plugin.name not in self._plugin_dict:
                        self._plugin_dict[_plugin.name] = action_dict
                    self._plugin_dict[_plugin.name].update({"fileId": _plugin.fileId})
        return self._plugin_dict

    def update_task_plugin_ids(self, task: Task):
        # getting a dict of destination plugins so we can update our
        # tasks with the correct fileId and actions IDs
        self.log("Retrieving plugins from destination instance", level="debug")
        self._get_dest_plugin_dict()
        if "python" not in task.action.descriptor.actionType:
            task_name = task.action.descriptor.packageDescriptor.name
            action_type = task.action.descriptor.actionType
            self.log(f"Updating task '{task.name}' with correct plugin IDs")
            if self._plugin_dict.get(task_name):
                if self._plugin_dict[task_name].get(action_type):
                    # We are updating the current source task_ so that it contains the correct Ids for the
                    # destination plugin
                    self.log(
                        f"Updating task '{task.name}' with correct packageDescriptor fileId "
                        f"'{self._plugin_dict[task_name]['fileId']}'"
                    )
                    task.action.descriptor.packageDescriptor.fileId = self._plugin_dict[task_name]["fileId"]
                    self.log(
                        f"Updating task '{task.name}' with correct imageId "
                        f"'{self._plugin_dict[task_name][action_type]['imageId']}'"
                    )
                    task.action.descriptor.imageId = self._plugin_dict[task_name][action_type]["imageId"]
                    self.log(
                        f"Updating task '{task.name}' with correct packageDescriptorId "
                        f"'{self._plugin_dict[task_name][action_type]['id']}'"
                    )
                    task.action.packageDescriptorId = self._plugin_dict[task_name][action_type]["id"]
        return task

    def _check_tasks_using_tracking_id(self, task):
        if hasattr(task, "inputMapping") and task.inputMapping:
            for mapping in task.inputMapping:
                if hasattr(mapping, "value") and isinstance(mapping.value, str):
                    if self.tracking_id_map.get(mapping.value):
                        mapping.value = self.tracking_id_map[mapping.value]
        if hasattr(task, "outputs") and task.outputs:
            for output in task.outputs:
                if hasattr(output, "backReferenceFieldId") and isinstance(output.backReferenceFieldId, str):
                    if self.tracking_id_map.get(output.backReferenceFieldId):
                        output.backReferenceFieldId = self.tracking_id_map[output.backReferenceFieldId]
                if hasattr(output, "mappings"):
                    for mapping in output.mappings:
                        if hasattr(mapping, "value") and isinstance(mapping.value, str):
                            if self.tracking_id_map.get(mapping.value):
                                mapping.value = self.tracking_id_map[mapping.value]
        return task

    def sync_task(self, task: Task or TaskLight):
        """This method syncs a single task from a source Swimlane instance to a destination instance.

        Using the provided task dictionary from Swimlane source instance we first get the actual task
        object from the source.

        Next, we attempt to retrieve the task from the destination system. If the task does not exist
        on the destination instance, we add it. If it does exist, we check if the `uid` and the `version` are the same.
        If they are the same we skip updating the task. If they are different, we update the task on the destination
        instance.

        Args:
            task (dict): A Swimlane task object from a source system.

        Returns:
            Task or TaskLight: If we failed to add a task we return it so we can try again.
                               Only if called using the sync method.
        """
        if not self._is_in_include_exclude_lists(task.name, "tasks"):
            self.log(f"Processing task '{task.name}'.")
            task_ = self.source_instance.get_task(task.id)
            if not task_:
                raise GetComponentError(type="task", name=task.name, id="")
            task_ = self.update_task_plugin_ids(task=task_)
            dest_task = self.destination_instance.get_task(task_.id)
            if not dest_task:
                if not Base.dry_run:
                    self.log(f"Creating task '{task_.name}' on destination.")
                    try:
                        # checking tasks for inputs and outputs mapped to source application
                        # tracking-ids and replacing them with the new ones
                        task_ = self._check_tasks_using_tracking_id(task=task_)
                        dest_task = self.destination_instance.add_task(task_)
                        self.log(f"Successfully added task '{task_.name}' to destination.")
                    except Exception as e:
                        self.log(
                            f"Failed to add task '{task_.name}' to destination.",
                            level="warning",
                        )
                        self.log("Will attempt again before finalizing.")
                        return task_
                else:
                    self.add_to_diff_log(task_.name, "added")
            else:
                self.log(f"Task '{task_.name}' already exists on destination.")
                if task_.uid == dest_task.uid:
                    if task_.version == dest_task.version:
                        self.log(f"Task '{task_.name}' has not changed on destination. Skipping...")
                    else:
                        if not Base.dry_run:
                            if task_.name in self._processed_task_list:
                                self.log(f"Task '{task_.name}' already updated by applications component. Skipping...")
                            else:
                                self.log(f"Task '{task_.name}' has changed. Updating...")
                                try:
                                    dest_task = self.destination_instance.update_task(dest_task.id, task_)
                                    if not dest_task:
                                        raise UpdateComponentError(model=task_, name=task_.name)
                                    self.log(f"Successfully updated task '{task_.name}' on destination.")
                                except Exception as e:
                                    raise UpdateComponentError(model=task_)
                        else:
                            self.add_to_diff_log(task_.name, "updated")

    def sync(self):
        """This method is used to sync all tasks from a source instance to a destination instance"""
        self.log(f"Starting to sync tasks from '{self.source_host}' to '{self.dest_host}'")
        failed_task_list = []
        tasks = self.source_instance.get_tasks()
        if tasks:
            for task in tasks:
                resp = self.sync_task(task=task)
                if resp:
                    failed_task_list.append(resp)

        self.log(f"The following tasks failed to process: {[x.name for x in failed_task_list]}")
        if failed_task_list:
            count = 1
            self.log("Retrying failed task migration from host to destination.")
            while count < 3:
                for task_ in failed_task_list:
                    self.log(f"Attempt {count}: Processing task '{task_.name}'.")
                    self.log(f"Creating task '{task_.name}' on destination.")
                    try:
                        dest_task = self.destination_instance.add_task(task_)
                        self.log(f"Successfully added task '{task_.name}' to destination.")
                        failed_task_list.remove(task_)
                    except Exception as e:
                        self.log(
                            f"Failed to add task '{task_.name}' to destination.",
                            level="warning",
                        )
                count += 1

            if len(failed_task_list) > 0:
                self.log(
                    f"The following task were unable to be added to destination! {[x.name for x in failed_task_list]}",
                    level="critical",
                )
                if not self.continue_on_error:
                    task_names = [x.name for x in failed_task_list]
                    raise Exception(f"The following task were unable to be added to destination! {task_names}")
