# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..models import Report
from ..utils.exceptions import AddComponentError


class Reports(Base):

    """Used to sync reports from a source instance to a destination instance of Swimlane"""

    def __update_destination_report(self, source: Report, destination: Report, application_name=None):
        if source.columns and destination.columns and source.columns != destination.columns:
            for scolumn in source.columns:
                if scolumn not in destination.columns:
                    destination.columns.append(scolumn)
                    self.add_to_diff_log(
                        f"{application_name if application_name else ''} - {destination.name} Report",
                        "updated",
                        subcomponent="columns",
                    )
        if source.filters and not destination.filters:
            self.log(
                "Updating filters on destination since source has some but destination does not.",
                level="debug",
            )
            for sfilter in source.filters:
                if sfilter not in destination.filters:
                    destination.filters.append(sfilter)
                    self.add_to_diff_log(
                        f"{application_name if application_name else ''} - {destination.name} Report",
                        "updated",
                        subcomponent="filters",
                    )
        if source.keywords and not destination.keywords:
            self.log(
                "Updating keywords on destination since source has keywords and destination does not.",
                level="debug",
            )
            destination.keywords = source.keywords
            self.add_to_diff_log(
                f"{application_name if application_name else ''} - {destination.name} Report",
                "updated",
                subcomponent="keywords",
            )
        return destination

    def __update_default_report(self, sreport: Report, dreport: Report):
        self.log("Updating 'Default' report.")
        dest_application = self.destination_instance.get_application(sreport.applicationIds[0])
        if dest_application:
            self.log(
                f"Getting source default report and application for application ID '{sreport.applicationIds[0]}'",
                level="debug",
            )
            source_default_report = self.source_instance.get_default_report_by_application_id(sreport.applicationIds[0])
            source_application = self.source_instance.get_application(sreport.applicationIds[0])

            self.log(
                f"Getting destination application '{dest_application['name']}' Tracking ID field ID",
                level="debug",
            )
            dest_tracking_field = None
            for field in dest_application.get("fields"):
                if field.get("fieldType") and field["fieldType"].lower() == "tracking":
                    dest_tracking_field = field.get("id")
            self.log(
                f"Destination application '{dest_application['name']}' Tracking ID field ID is '{dest_tracking_field}'",
                level="debug",
            )
            self.log(
                f"Getting source application '{source_application['name']}' Tracking ID field ID",
                level="debug",
            )
            source_tracking_field = None
            for field in source_application.get("fields"):
                if field.get("fieldType") and field["fieldType"].lower() == "tracking":
                    source_tracking_field = field.get("id")
            self.log(
                f"Source application '{source_application['name']}' Tracking ID field ID is '{source_tracking_field}'",
                level="debug",
            )

            if source_tracking_field in source_default_report.columns:
                self.log(
                    "Updating columns in default report to match tracking IDs",
                    level="debug",
                )
                source_default_report.columns.remove(source_tracking_field)
                source_default_report.columns.append(dest_tracking_field)
                self.add_to_diff_log(
                    f"{dest_application['name']} - Default Report",
                    "updated",
                    subcomponent="tracking-id",
                )

            if source_default_report.sorts and source_default_report.sorts.get(source_tracking_field):
                self.log(
                    "Updating sorts in default report to match tracking IDs",
                    level="debug",
                )
                val = source_default_report.sorts[source_tracking_field]
                source_default_report.sorts.pop(source_tracking_field)
                source_default_report.sorts.update({dest_tracking_field: val})
                self.add_to_diff_log(
                    f"{dest_application['name']} - Default Report",
                    "updated",
                    subcomponent="sorts",
                )
            self.log("Updating default report id, uid, and version strings.", level="debug")
            source_default_report.id = dreport.id
            self.add_to_diff_log(
                f"{dest_application['name']} - Default Report",
                "updated",
                subcomponent="id",
            )
            source_default_report.uid = dreport.uid
            self.add_to_diff_log(
                f"{dest_application['name']} - Default Report",
                "updated",
                subcomponent="uid",
            )
            source_default_report.version = dreport.version
            self.add_to_diff_log(
                f"{dest_application['name']} - Default Report",
                "updated",
                subcomponent="version",
            )
            return self.__update_destination_report(
                source=source_default_report,
                destination=dreport,
                application_name=dest_application["name"],
            )
        else:
            self.log(
                f"Unable to update 'Default' report for application ID '{sreport.applicationIds[0]}'"
                " because that ID does not exist on destination.",
                level="warning",
            )

    def sync_report(self, report: Report):
        if not self._is_in_include_exclude_lists(report.name, "reports"):
            self.log(f"Processing report '{report.name}' ({report.id})")
            if report.name == "Default":
                self.log(f"Checking for 'Default' report for application ID '{report.applicationIds[0]}'")
                default_report = self.destination_instance.get_default_report_by_application_id(
                    report.applicationIds[0]
                )
                if not default_report:
                    default_report = self.destination_instance.get_report(report_id=report.id)
                if default_report:
                    if self.update_reports:
                        if not Base.dry_run:
                            self.log(f"Destination report '{report.name}' has changes that source does not.")
                            dest_report = self.__update_default_report(sreport=report, dreport=default_report)
                            self.destination_instance.update_default_report(dest_report)
                            self.log("Successfully updated 'Default' report.")
                        else:
                            self.add_to_diff_log(report.name, "updated")
                    else:
                        self.log(
                            "Default report was found. If you want to update the default report use"
                            " update_reports=True. Skipping..."
                        )
                else:
                    if not Base.dry_run:
                        self.log(
                            f"Report '{report.name}' for application IDs '{report.applicationIds}' was not found on"
                            " destination. Adding report..."
                        )
                        resp = self.destination_instance.add_report(report)
                        if not resp:
                            raise AddComponentError(model=report, name=report.name)
                        self.log(f"Successfully added report '{report.name}' to destination.")
                    else:
                        self.add_to_diff_log(report.name, "added")
            else:
                dest_report = self.destination_instance.get_report(report_id=report.id)
                if not dest_report:
                    if not Base.dry_run:
                        self.log(
                            f"Report '{report.name}' for application IDs '{report.applicationIds}' was not found on"
                            " destination. Adding report..."
                        )
                        resp = self.destination_instance.add_report(report)
                        if not resp:
                            raise AddComponentError(model=report, name=report.name)
                        self.log(f"Successfully added report '{report.name}' to destination.")
                    else:
                        self.add_to_diff_log(report.name, "added")
                elif self.update_reports:
                    self.log(
                        f"Report '{report.name}' for application IDs '{report.applicationIds}' was found."
                        " Checking difference...."
                    )
                    if report != dest_report:
                        if not Base.dry_run:
                            self.log("Source and destination report are different. Updating ...")
                            dest_report = self.__update_destination_report(source=report, destination=dest_report)
                            self.destination_instance.update_report(report.id, dest_report)
                            self.log(f"Successfully updated report '{report.name}' on destination.")
                        else:
                            self.add_to_diff_log(report.name, "updated")
                    else:
                        self.log(f"No differences found in report '{report.name}'. Skipping...")
                else:
                    self.log(f"Skipping check of report '{report.name}' for changes since update_reports is False.")

    def sync(self):
        """This method is used to sync all reports from a source instance to a destination instance"""
        self.log(f"Attempting to sync reports from '{self.source_host}' to '{self.dest_host}'")
        reports = self.source_instance.get_reports()
        if reports:
            for report in reports:
                self.sync_report(report=report)
