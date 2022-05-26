# -*- coding: utf-8 -*-
from collections import OrderedDict

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..utils.exceptions import GetComponentError
from .workflows import Workflows
from .workspaces import Workspaces


class Applications(Base):

    """Used to sync applications from a source instance to a destination instance of Swimlane"""

    __applications_needing_updates = []

    def __filter_out_field_from_layout(self, layout, field):
        if isinstance(layout, list):
            return [
                self.__filter_out_field_from_layout(element, field)
                for element in layout
                if not element.get("fieldId") or element.get("fieldId") and element["fieldId"] != field["id"]
            ]
        elif isinstance(layout, dict):
            return {key: self.__filter_out_field_from_layout(value, field) for key, value in layout.items()}
        else:
            return layout

    def __add_fields(self, source: dict, destination: dict):
        self.log(f"Checking application '{source['name']}' application for missing fields.")
        update_layout = False
        for sfield in source["fields"]:
            if sfield.get("fieldType") and sfield["fieldType"].lower() == "tracking":
                continue
            if sfield not in destination["fields"]:
                if sfield.get("reverseValueMap"):
                    sfield.pop("reverseValueMap")
                # if reverseValueMap is removed and that field is still not in the destination fields then
                # lets update it as we should. reverseValueMap was available in previous versions of Swimlane like
                # 10.5.0 but removed in 10.5.2
                if sfield not in destination["fields"]:
                    dfield_exists = False
                    for dfield in destination["fields"]:
                        if sfield["id"] == dfield["id"]:
                            dfield_exists = True
                    if not dfield_exists:
                        update_layout = True
                        self.log(f"Field '{sfield['name']}' not in destination application.")
                        destination["fields"].append(sfield)
                        self.log(f"Successfully added '{sfield['name']}' to destination application")
                        if Base.dry_run:
                            self.add_to_diff_log(source["name"], "added", subcomponent="field", value=sfield["name"])
        if update_layout:
            destination["layout"] = source["layout"]
            self.add_to_diff_log(source["name"], "updated", subcomponent="layout")
        return destination

    def __remove_fields(self, source: dict, destination: dict):
        self.log(f"Checking application '{source['name']}' application for fields to remove.")
        for dfield in destination["fields"]:
            if dfield.get("fieldType") and dfield["fieldType"].lower() == "tracking":
                continue
            if dfield not in source["fields"]:
                sfield_exists = False
                for sfield in source["fields"]:
                    if dfield["id"] == sfield["id"]:
                        sfield_exists = True
                if not sfield_exists:
                    self.log(f"Removing field '{dfield['name']}' from '{destination['name']}' application layout.")
                    destination["layout"] = self.__filter_out_field_from_layout(destination["layout"], dfield)
                    if Base.dry_run:
                        self.add_to_diff_log(source["name"], "moved", subcomponent="field", value=dfield["name"])
                        self.add_to_diff_log(source["name"], "removed", subcomponent="layout", value=dfield["name"])
        return destination

    def _remove_tracking_field(self, application: dict):
        """This method removes an applications tracking field since
        Swimlane automatically generates this for every new application.

        Args:
            application (dict): A Swimlane application to remove the tracking field from
        """
        return_dict = {}
        for field in application.get("fields"):
            if field.get("fieldType") and field["fieldType"].lower() == "tracking":
                if not Base.dry_run:
                    application["fields"].remove(field)
                    return_dict = field
                else:
                    self.add_to_diff_log(application["name"], "removed", subcomponent="tracking-field")
        return return_dict

    def _process_workspaces(self, application):
        if application.get("workspaces") and application["workspaces"]:
            for workspace in application["workspaces"]:
                workspace_ = self.source_instance.get_workspace(workspace_id=workspace)
                if not workspace_:
                    raise GetComponentError(name="workspace", id=workspace)
                if workspace_ and not self.destination_instance.get_workspace(workspace_id=workspace):
                    Workspaces().sync_workspace(workspace=workspace_)

    def get_reference_app_order(self):
        """This method creates an order of applications to be added or updated on a destination
        instance based on most to least reference relationships. For example, a source application
        that references 5 applications will be before an application which has 3 references to applications.

        Returns:
            dict: An reference application ordered (sorted) application dictionary
        """
        reference_dict = {}
        for application in self.source_instance.get_applications():
            if application:
                application_ = self.source_instance.get_application(application_id=application["id"])
                if application_["id"] not in reference_dict:
                    reference_dict[application_["id"]] = []
                for field in application_["fields"]:
                    if field.get("$type") and field["$type"] == "Core.Models.Fields.Reference.ReferenceField, Core":
                        reference_dict[application_["id"]].append(field["targetId"])

        return_dict = OrderedDict()
        for item in sorted(reference_dict, key=lambda k: len(reference_dict[k]), reverse=True):
            return_dict[item] = reference_dict[item]
        return return_dict

    def sync_application(self, application_id: str):
        """This method syncs a single application from a source instance to a destination instance.

        Once an application_id on a source instance is provided we retrieve this application JSON.
        Next we remove the tracking_field from the application since Swimlane automatically generates
        a unique value for this field.

        If workspaces are defined in the application and do not currently exist will attempt to create
        or update them using the Workspaces class.

        If the source application does not exist on the destination, we will create it with the same IDs for
            1. application
            2. fields
            3. layout
            4. etc.

        By doing this, syncing of applications (and their IDs) is much easier.

        If the application exists, we proceed to remove specific fields that are not needed.

        Next, we check for fields which have been added to the source application but do not
        exist on the destination instance. If fields are found we add them to the destination
        object.

        Next, we check to see if the destination has fields which are not defined in the source instance.
        If fields are found, we then remove them from the layout view of the source application. This equates
        to moving them to the "hidden" field section within the application builder so they can still be retrieved
        and reorganized as needed.

        Finally, we update the application on the destination instance.

        After updating the application we then check to ensure that the workflow of that application is up to date
        and accurate.

        Args:
            application_id (str): A source application ID.
        """
        application = self.source_instance.get_application(application_id=application_id)
        if not application:
            raise GetComponentError(name="application", id=application_id)

        self._process_workspaces(application=application)
        source_tracking_field = self._remove_tracking_field(application)
        self.scrub(application)
        if not self._is_in_include_exclude_lists(application["name"], "applications"):
            dest_application = self.destination_instance.get_application(application["id"])
            if not dest_application:
                if not Base.dry_run:
                    self.log(f"Adding application '{application['name']}' on destination.")
                    dest_application = self.destination_instance.add_application(application)
                    self.__applications_needing_updates.append(application_id)
                    self.log(f"Successfully added application '{application['name']}' on destination.")
                    # Setting tracking_id_map just in case tasks are added and need updating
                    # Tasks would need updating if they use an applications 'Tracking Id' field as an
                    # input or output since Swimlane randomizes the Tracking ID when created
                    self.tracking_id_map = (source_tracking_field["id"], dest_application["trackingFieldId"])
                else:
                    self.add_to_diff_log(application["name"], "added")
            else:
                for item in ["createdByUser", "modifiedByUser", "permissions"]:
                    if dest_application.get(item):
                        dest_application.pop(item)
                dest_application = self.__add_fields(application, dest_application)
                dest_application = self.__remove_fields(application, dest_application)
                if not Base.dry_run:
                    self.log(f"Updating application '{dest_application['name']}' on destination.")
                    self.destination_instance.update_application(dest_application)
                    self.__applications_needing_updates.append(application_id)
                    self.log(f"Successfully updated application '{dest_application['name']}' on destination.")
                else:
                    self.add_to_diff_log(application["name"], "updated")
            self.log(f"Checking for changes in workflow for application '{application['name']}'")
            Workflows().sync_workflow(application_name=application["name"])
        else:
            self.log(f"Skipping application '{application['name']}' since it is excluded.")

    def sync(self):
        """This method will sync all applications on a source instance with a destination instance."""
        self.log(f"Starting to sync 'Applications' from '{self.source_host}' to '{self.dest_host}'")
        for application_id, values in self.get_reference_app_order().items():
            self.sync_application(application_id=application_id)

        # Checking if we need to update applications reference fields that contain old (source instance)
        # tracking-ids in their columns. If so we remove them and update it with the new ones on the destination.
        if self.__applications_needing_updates:
            for application_id in self.__applications_needing_updates:
                dest_application = self.destination_instance.get_application(application_id)
                needs_update = False
                for field in dest_application["fields"]:
                    if field.get("columns"):
                        column_list = []
                        for column in field["columns"]:
                            if self.tracking_id_map.get(column):
                                self.log(
                                    f"Removing old tracking-id '{column}' from application "
                                    f"'{dest_application['name']}' field '{field['key']}'"
                                )
                                column_list.append(self.tracking_id_map[column])
                                self.log(
                                    f"Adding new tracking-id '{self.tracking_id_map[column]}' to application "
                                    f"'{dest_application['name']}' field '{field['key']}'"
                                )
                                needs_update = True
                            else:
                                column_list.append(column)
                        field["columns"] = column_list
                if needs_update:
                    self.log(f"Updating application '{dest_application['name']}' on destination with new.")
                    dest_application = self.destination_instance.update_application(dest_application)
                    self.log(f"Successfully updated application '{dest_application['name']}' on destination.")
