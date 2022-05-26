# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..models import Dashboard
from ..utils.exceptions import AddComponentError, UpdateComponentError
from .reports import Reports


class Dashboards(Base):

    """Used to sync dashboards from a source instance to a destination instance of Swimlane"""

    def __process_reports(self, dashboard: Dashboard):
        self.log(f"Processing dashboard '{dashboard.name}' reports.")
        for item in dashboard.items:
            report = self.source_instance.get_report(report_id=item.reportId)
            Reports().sync_report(report=report)

    def sync_dashboard(self, dashboard: Dashboard):
        """This method syncs a single dashboard from a source instance to a destination instance.

        This class first checks to see if the provided dashboard already exists on the destination instance.
        If it does not exist then we attempt to add the dashboard to the destination instance.

        If the dashboard already exists on the destination instance, we first check it against all destination
        instance dashboards. This check involves comparing the provided source dashboard dict with
        the `uid` and `name` of a destination instance dashboard.

        If a match is found, we then check if the version is the same.
        If it is we simply skip processing this dashboard.

        If a match is found but the versions are different, we first ensure that all the reports in the dashboard are on
        the destination instance. Once that is complete, we modify the dashboard to remove unneeded keys and then update
        it as provided by the source instance.

        Args:
            dashboard (dict): A source instance dashboard dictionary.
        """
        if not self._is_in_include_exclude_lists(dashboard.name, "dashboards"):
            self.log(f"Processing dashboard '{dashboard.name}' ({dashboard.id})")
            self.__process_reports(dashboard=dashboard)
            dest_dashboard = None
            dest_dashboards = self.destination_instance.get_dashboards()
            if dest_dashboards:
                for d in dest_dashboards:
                    if d.uid == dashboard.uid:
                        dest_dashboard = d
            if not dest_dashboard:
                if not Base.dry_run:
                    self.log(
                        f"Adding dashboard '{dashboard.name}' for workspaces '{dashboard.workspaces}' on destination"
                    )
                    dashboard.permissions = {}
                    dashboard.createdByUser = {}
                    dashboard.modifiedByUser = {}
                    dest_dashboard = self.destination_instance.add_dashboard(dashboard)
                    if not dest_dashboard:
                        raise AddComponentError(model=dashboard, name=dashboard.name)
                    self.log(f"Successfully added dashboard '{dashboard.name}' to destination.")
                else:
                    self.add_to_diff_log(dashboard.name, "added")
            else:
                if self.update_dashboards:
                    self.log(
                        f"Dashboard '{dashboard.name}' for workspaces '{dashboard.workspaces}' was found."
                        " Checking differences..."
                    )
                    dest_dashboard.workspaces = dashboard.workspaces
                    dest_dashboard.items = dashboard.items
                    dest_dashboard.description = dashboard.description
                    dest_dashboard.timelineFilters = dashboard.timelineFilters
                    if not Base.dry_run:
                        self.log(f"Updating '{dashboard.name}' now.")
                        dest_dashboard = self.destination_instance.update_dashboard(dest_dashboard)
                        if not dest_dashboard:
                            raise UpdateComponentError(model=dashboard, name=dashboard.name)
                        self.log(f"Successfully updated dashboard '{dashboard.name}'.")
                    else:
                        self.add_to_diff_log(dashboard.name, "updated")
                else:
                    self.log(
                        f"Skipping check of dashboard '{dashboard.name}' for changes since update_dashboards is False."
                    )

    def sync(self):
        """This method is used to sync all dashboards from a source instance to a destination instance"""
        self.log(f"Attempting to sync dashboards from '{self.source_host}' to '{self.dest_host}'")
        dashboards = self.source_instance.get_dashboards()
        if dashboards:
            for dashboard in dashboards:
                self.sync_dashboard(dashboard=dashboard)
