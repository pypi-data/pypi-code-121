from datetime import datetime
from typing import Literal
from urllib.parse import urlencode


class ListEndpoint:
    """Lists represent groupings of contacts, messages, and more.
    Listrak's Email API is list-centric, just like Listrak's application.
    Most resources available through this API are associated with a specific list.
    https://api.listrak.com/email#tag/List
    """
    def __init__(self, root_endpoint, session):
        self._endpoint = root_endpoint + "/email/v1/List"
        self._session = session

    def get_all_lists(self) -> list:
        """Returns your account's collection of lists.
        https://api.listrak.com/email#operation/List_GetListCollection
        """
        r = self._session.get(self._endpoint)
        try:
            r.raise_for_status()
            return r.json().get("data")
        except self._session.exceptions.HTTPError as e:
            print(e)

    def create_a_list(
        self,
        list_name: str,
        bounce_handling: Literal["None", "Standard", "Aggressive"] = "None",
        bounce_unsubscribe_count: int = 1
        ) -> dict:
        """Creates a new list in your account.
        https://api.listrak.com/email#operation/List_PostListResource

        Args:
            list_name (str): Name of the list.
            bounce_handling (str, optional): Bounce handling method for the list.
                Allowed values are 'None', 'Standard', and 'Aggressive'.
            bounce_unsubscribe_count (int, optional): The number of bounces that are allowed before being automatically unsubscribed.

        Returns:
            dict: If success dict will contain 'status':int and 'resourceId':str keys.
                If fail dict will 'status':int code, 'error':string, and 'message':string keys.
        """
        data = {
            "list_name": list_name,
            "bounceHandling": bounce_handling,
            "bounceUnsubscribeCount": bounce_unsubscribe_count,
        }
        r = self._session.post(self._endpoint, data=body)
        try:
            r.raise_for_status()
            return r.json()
        except self._session.exceptions.HTTPError as e:
            print(e)

    def get_a_list(self, list_id: int) -> dict:
        """Returns the specified list.
        https://api.listrak.com/email#operation/List_GetListResourceById
        Args:
            list_id (int): Identifier used to locate the list.

        Returns:
            dict: If success dict will contain 'status':int and 'data':dict keys.
                If fail dict will 'status':int code, 'error':string, and 'message':string keys.
        """
        r = self._session.get(self._endpoint + f"/{list_id}")
        try:
            r.raise_for_status()
            return r.json().get("data")
        except self._session.exceptions.HTTPError as e:
            print(e)

    def update_a_list(
        self,
        list_id,
        list_name: str,
        bounce_handling: Literal["None", "Standard", "Aggressive"] = "None",
        bounce_unsubscribe_count: int = 1,
        ) -> dict:
        """Returns your account's collection of lists.
        https://api.listrak.com/email#operation/List_PutListResource
        Args:
            list_name (str): Name of the list.
            bounce_handling (str, optional): Bounce handling method for the list.
                Allowed values are 'None', 'Standard', and 'Aggressive'.
            bounce_unsubscribe_count (int, optional): The number of bounces that are allowed before being automatically unsubscribed.

        Returns:
            dict: If success dict will contain 'status':int and 'resourceId':str keys.
                If fail dict will 'status':int code, 'error':string, and 'message':string keys.
        """
        data = {
            "list_name": list_name,
            "bounceHandling": bounce_handling,
            "bounceUnsubscribeCount": bounce_unsubscribe_count,
        }
        r = self._session.put(self._endpoint + f"/{list_id}", data=body)
        try:
            r.raise_for_status()
            return r.json()
        except self._session.exceptions.HTTPError as e:
            print(e)

    def delete_a_list(self, list_id: int) -> dict:
        """Deletes the specified list.
        https://api.listrak.com/email#operation/List_DeleteListResource

        Args:
            list_id (int): Identifier used to locate the list.

        Returns:
            dict: If success dict will contain 'status':int key.
                If fail dict will 'status':int code, 'error':string, and 'message':string keys.
        """
        r = self._session.delete(self._endpoint + f"/{list_id}")
        try:
            r.raise_for_status()
            return r.json()
        except self._session.exceptions.HTTPError as e:
            print(e)


class ListImportEndpoint:
    """The List Import resource is used to supply an import file in order to import data to a list.
    https://api.listrak.com/email#tag/ListImport
    """
    def __init__(self, root_endpoint, session):
        self._endpoint = root_endpoint + "/email/v1/List"
        self._session = session

    def get_all_list_imports(self, list_id) -> dict:
        """Retrieves the collection of list imports associated with the specified list.
        https://api.listrak.com/email#operation/ListImport_GetListImportCollection
        """
        r = self._session.get(self._endpoint + f"/{list_id}/ListImport")
        try:
            r.raise_for_status()
            return r.json().get("data")
        except self._session.exceptions.HTTPError as e:
            print(e)

    def start_a_list_import(
        self,
        list_id: int,
        file_stream: str,
        file_mappings_segmentation_field_id: int,
        file_mappings_default_value: str,
        file_mappings_file_column: int = 0,
        file_mappings_file_column_type: Literal["Email", "SegmentationField", "Event"] = "Email",
        file_delimiter: str = ",",
        file_name: str = str(datetime.now())[0:16].replace(" ", "@").replace(":", ""),
        has_column_names: bool = True,
        import_type: Literal["AddSubscribers", "AddSubscribersAndSegmentationData", "RemoveSubscribers", "UpdateSubscribers"] = "AddSubscribers",
        segentation_import_type: Literal["Update", "Append", "Overwrite"] = "",
        suppress_email_notifications: bool = False,
        text_qualifier: str = '"'
        ) -> str:
        """Creates and starts a new import for the specified list.
        https://api.listrak.com/email#operation/ListImport_GetListImportCollection

        Returns the 'resourceId': An identifier used to locate a resource.
        """
        body = {
            "fileDelimiter": file_delimiter,
            "fileMappings": {
                "segmentationFieldId": file_mappings_segmentation_field_id,
                "defaultValue": file_mappings_default_value,
                "fileColumn": file_mappings_file_column,
                "fileColumnType": file_mappings_file_column_type
            },
            "fileName": file_name,
            "fileStream": file_stream,
            "hasColumnNames": has_column_names,
            "importType": import_type,
            "segmentationImportType": segentation_import_type,
            "suppressEmailNotifications": suppress_email_notifications,
            "textQualifier": text_qualifier
        }

        r = self._session.post(self._endpoint + f"/{list_id}/ListImport", data=body)
        try:
            r.raise_for_status()
            return r.json().get("resourceId")
        except self._session.exceptions.HTTPError as e:
            print(e)


class ContactEndpoint:
    """The Contact resource is used to add, update and remove new contacts to a List. This resource also exposes the ability to set a contact's profile fields and subscription state.
    https://api.listrak.com/email#tag/Contact
    """
    def __init__(self, root_endpoint, session):
        self._endpoint = root_endpoint + "/email/v1/List"
        self._session = session

    def get_all_contacts(self, list_id: int) -> list:
        """Returns the collection of contacts associated with the specified list.
        https://api.listrak.com/email#operation/Contact_GetContactCollection

        TODO: Add parameter query filters, see Listrak documentation
        """
        all_contacts = []

        endpoint = self._endpoint + f"/{list_id}/Contact"
        r = self._session.get(endpoint)
        all_contacts.extend(r.json()["data"])
        next_page_cursor = r.json()["nextPageCursor"]

        while next_page_cursor is not None:
            r = self._session.get(endpoint + f"?cursor={next_page_cursor}")
            try:
                r.raise_for_status()
                all_contacts.extend(r.json()["data"])
                next_page_cursor = r.json()["nextPageCursor"]
            except self._session.exceptions.HTTPError as e:
                print(e)

        return all_contacts

    def create_or_update_a_contact(
        self,
        list_id: int,
        email_address: str,
        subscription_state: Literal["Subscribed", "Unsubscribed"] = "Subscribed",
        external_contact_id: str = None,
        segmentation_field_values: [{"segmentationFieldId": int,"value": str}] = None,
        event_ids: str = None,
        override_unsubscribe: bool = False,
        subscribed_by_contact: bool = False,
        send_double_opt_in: bool = False,
        update_type: Literal["Update", "Append", "Overwrite"] = "Update",
        new_email_address: str = None,
        ) -> str:
        """Creates or updates a contact on the specified list.
        https://api.listrak.com/email#operation/Contact_PostContactResource

        Returns:
            str: 'resourceId' which is an identifier used to locate the updated resource.
        """
        body = {
            "emailAddress": email_address,
            "segmentationFieldValues": segmentation_field_values
        }
        if subscription_state:
            body["subscriptionState"] = subscription_state
        if external_contact_id:
            body["externalContactID"] = external_contact_id

        params = {
            "overrideUnsubscribe": override_unsubscribe,
            "subscribedByContact": subscribed_by_contact,
            "sendDoubleOptIn": send_double_opt_in,
            "updateType": update_type,
        }
        if event_ids:
            params["eventIds"] = event_ids
        if new_email_address:
            params["newEmailAddress"] = new_email_address
        query_params = "?" + urlencode(params)

        endpoint = self._endpoint + f"/{list_id}/Contact/{query_params}"
        r = self._session.post(endpoint, json=body)
        try:
            r.raise_for_status()
            return r.json()["resourceId"]
        except self._session.exceptions.HTTPError as e:
            print(e)

    def get_a_contact(
        self,
        list_id: int,
        contact_identifier: str,
        segmentation_field_values: list = None
        ) -> dict:
        """Returns a contact by email address or by Listrak email key.
        https://api.listrak.com/email#operation/Contact_GetContactResourceByIdentifier

        Args:
            list_id (int): Identifier used to locate the list.
            contact_identifier (str): Identifier used to locate the contact. You may specify either an email address or a Listrak email key.
            segmentation_field_values (list): Comma-separated list of profile field IDs to retrieve. Up to 30 fields may be included.

        Returns:
            dict: Attributes related to contact tied to 'contact_identifier'
        """
        endpoint = self._endpoint + f"/{list_id}/Contact/{contact_identifier}"
        r = self._session.get(endpoint)
        try:
            r.raise_for_status()
            return r.json()["data"]
        except self._session.exceptions.HTTPError as e:
            print(e)



class SegmentationFieldEndpoint:
    """A Profile Field is used to store data about a contact so that it can be filtered in the future.
    https://api.listrak.com/email#tag/SegmentationField
    """
    def __init__(self, root_endpoint, session):
        self._endpoint = root_endpoint + "/email/v1/List"
        self._session = session

    def get_all_profile_fields(
        self,
        list_id: int,
        segmentation_field_group_id: int
        ) -> list:
        """Returns the collection of profile fields that exist for the specified profile field group.
        https://api.listrak.com/email#operation/SegmentationField_GetSegmentationFieldCollection

        Args:
            list_id (int): Identifier used to locate the list.
            segmentation_field_group_id (str): Identifier used to locate the profile field group.

        Returns:
            dict: Returns the collection of profile fields that exist for the specified profile field group.
        """
        endpoint = self._endpoint + f"/{list_id}/SegmentationFieldGroup/{segmentation_field_group_id}/SegmentationField"
        r = self._session.get(endpoint)
        try:
            r.raise_for_status()
            return r.json()["data"]
        except self._session.exceptions.HTTPError as e:
            print(e)


class SegmentationFieldGroupEndpoint:
    """A Profile Field Group is used to group the profile fields for a given list.
    https://api.listrak.com/email#tag/SegmentationFieldGroup
    """
    def __init__(self, root_endpoint, session):
        self._endpoint = root_endpoint + "/email/v1/List"
        self._session = session

    def get_all_profile_field_groups(self, list_id: int) -> list:
        """Returns the collection of profile fields that exist for the specified profile field group.
        https://api.listrak.com/email#operation/SegmentationField_GetSegmentationFieldCollection

        Args:
            list_id (int): Identifier used to locate the list.

        Returns:
            dict: Returns a collection of profile field groups for the specified list.
        """
        endpoint = self._endpoint + f"/{list_id}/SegmentationFieldGroup"
        r = self._session.get(endpoint)
        try:
            r.raise_for_status()
            return r.json()["data"]
        except self._session.exceptions.HTTPError as e:
            print(e)
