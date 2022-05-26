# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..models import Workspace
from ..utils.exceptions import AddComponentError, UpdateComponentError


class Workspaces(Base):

    """Used to sync workspaces from a source instance to a destination instance of Swimlane"""

    def sync_workspace(self, workspace: Workspace):
        if not self._is_in_include_exclude_lists(workspace.name, "workspaces"):
            self.log(f"Processing workspace '{workspace.name}'")
            dest_workspace = self.destination_instance.get_workspace(workspace.id)
            if not dest_workspace:
                if not Base.dry_run:
                    self.log(f"Adding workspace '{workspace.name}' to destination.")
                    # ensuring that applications and dashboards are unique in the workspace components lists
                    try:
                        for key in ["applications", "dashboards"]:
                            if getattr(workspace, key):
                                values = list(set(getattr(workspace, key)))
                                setattr(workspace, key, values)
                    except Exception as e:
                        self.log(
                            "Error when forcing applications and dashboards lists to be unique. "
                            "Continuing anyways..."
                        )
                    dest_workspace = self.destination_instance.add_workspace(workspace)
                    if not dest_workspace:
                        raise AddComponentError(model=workspace, name=workspace.name)
                    self.log(f"Successfully added workspace '{workspace.name}' to destination.")
                else:
                    self.add_to_diff_log(workspace.name, "added")
            else:
                self.log(f"Workspace '{workspace.name}' already exists on destination. Checking differences...")
                if not Base.dry_run:
                    dashboards = []
                    for dashboard in workspace.dashboards:
                        for key, val in self.source_instance.dashboard_dict.items():
                            if dashboard == val and self.destination_instance.dashboard_dict.get(key):
                                self.log(
                                    f"Found {key} in dest dashboard with value of"
                                    f" {self.destination_instance.dashboard_dict[key]}"
                                )
                                dashboards.append(self.destination_instance.dashboard_dict[key])
                    workspace.dashboards = dashboards
                    from .applications import Applications

                    for application_id in workspace.applications:
                        if application_id and application_id not in self.destination_instance.application_id_list:
                            Applications().sync_application(application_id=application_id)
                    resp = self.destination_instance.update_workspace(workspace_id=workspace.id, workspace=workspace)
                    if not resp:
                        raise UpdateComponentError(model=workspace, name=workspace.name)
                    self.log(f"Successfully updated workspace '{workspace.name}' on destination.")
                else:
                    self.add_to_diff_log(workspace.name, "updated")

    def sync(self):
        """This method is used to sync all workspaces from a source instance to a destination instance"""
        self.log(f"Starting to sync workspaces from '{self.source_host}' to '{self.dest_host}'")
        workspaces = self.source_instance.get_workspaces()
        if workspaces:
            for workspace in workspaces:
                self.sync_workspace(workspace=workspace)
