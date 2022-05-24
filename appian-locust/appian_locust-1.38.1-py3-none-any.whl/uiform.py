import datetime
import enum
import errno
import json
import os
import random
import warnings
from typing import Any, Dict, List, Union, Optional
from urllib.parse import quote, urlparse

from appian_locust.records_helper import _is_grid

from . import logger
from ._grid_interactor import GridInteractor
from ._interactor import _Interactor
from ._locust_error_handler import raises_locust_error
from ._task_opener import _TaskOpener
from ._ui_reconciler import UiReconciler
from .exceptions import ComponentNotFoundException, InvalidComponentException, ChoiceNotFoundException
from .helper import (extract_all_by_label, find_component_by_attribute_and_index_in_dict,
                     find_component_by_attribute_in_dict, find_component_by_index_in_dict,
                     find_component_by_label_and_type_dict, find_component_by_type_and_attribute_and_index_in_dict)
from .records_helper import (get_record_header_response,
                             get_record_summary_view_response,
                             get_url_stub_from_record_list_url_path)

KEY_UUID = "uuid"
KEY_CONTEXT = "context"
START_PROCESS_LINK_TYPE = 'StartProcessLink'
PROCESS_TASK_LINK_TYPE = 'ProcessTaskLink'
COMPONENTS_THAT_CAN_BE_FILLED = ["ParagraphField", "TextField"]

log = logger.getLogger(__name__)


class ClientMode(enum.Enum):
    TEMPO = 'TEMPO'
    DESIGN = 'DESIGN'


class SailUiForm:
    def __init__(self, interactor: _Interactor, state: Dict[str, Any], url: str, breadcrumb: str = "SailUi"):
        """
        UIForm Class used to interact with a SAIL form used in an action, record, etc..

        Args:
            base: Action, Record, etc.. interactor object
            state: JSON representation of the initial form
            latest_state: JSON representation of the last to the the form
            url: Url to make updates to the form
            breadcrumbs: Path used to create locust labels

        """
        self.interactor: _Interactor = interactor
        self.task_opener: _TaskOpener = _TaskOpener(self.interactor)
        self.state: Dict[str, Any] = state
        self.form_url = url
        if any(key not in self.state for key in (KEY_CONTEXT, KEY_UUID)):
            return None
        self.context: dict = self.state[KEY_CONTEXT]
        self.uuid: str = self.state[KEY_UUID]
        self.grid_interactor: GridInteractor = GridInteractor()
        self.reconciler: UiReconciler = UiReconciler()
        self.breadcrumb = breadcrumb

        # Cache data types on opening new form
        self.interactor.datatype_cache.cache(self.state)

    def get_response(self) -> Optional[Dict[str, Any]]:
        """
        Latest state response

        Returns (dict): The last recorded response

        """
        warnings.warn("The method 'get_response' is deprecated, just do 'self.state' to get the latest returned value")
        return self.state

    @property
    def latest_state(self) -> Optional[Dict[str, Any]]:
        """
        Latest state response

        Returns (dict): The last recorded response

        """
        warnings.warn("The method 'latest_state' is deprecated, just do 'self.state' on the last returned value")
        return self.state

    def get_latest_form(self) -> 'SailUiForm':
        """
        Latest ui form

        Returns (dict): The ui form with its current ui

        """
        warnings.warn("The method 'get_latest_form' is deprecated, "
                      "ui is now updated on each call, you can just chain methods without calling `get_latest_form`")
        return self

    def __str__(self) -> str:
        return f"self_state={json.dumps(self.state,indent=4)}"

    @raises_locust_error
    def fill_field_by_attribute_and_index(self, attribute: str, attribute_value: str, fill_value: str, index: int = 1, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects a Field by "attribute" and its value provided "attribute_value" and an index if more than one Field is found
        and fills it with text "fill_value"

        Args:
            attribute(str): Name of the field to fill
            attribute_value(str): Value for the attribute passed in to this function
            fill_value(str): Value to fill in the field

        Keyword Args:
            index(int): Index of the field to fill if more than one match the attribute and attribute_value criteria (default: 1)
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.fill_field_by_attribute_and_index("label", "Write a comment", "Hello, Testing")
            # selects the first Component with the "label" attribute having "Write a comment" value
            # and fills it with "Hello, Testing"

            >>> form.fill_field_by_attribute_and_index("label", "Write a comment", "Hello, Testing", 2)
            # selects the second Component with the "label" attribute having "Write a comment" value
            # and fills it with "Hello, Testing"

        """
        component = find_component_by_attribute_and_index_in_dict(attribute, attribute_value, index, self.state)

        if component.get("#t", "") not in COMPONENTS_THAT_CAN_BE_FILLED:
            raise Exception(f"The Component with '{attribute}' = '{attribute_value}' is not a component that can be filled")

        reeval_url = self._get_update_url_for_reeval(self.state)
        locust_label = locust_request_label or f"{self.breadcrumb}.FillTextFieldByAttribute.{attribute}"
        new_state = self.interactor.fill_textfield(
            reeval_url, component, fill_value, self.context, self.uuid, label=locust_label)
        if not new_state:
            raise Exception(f"No response returned when trying to update the field with '{attribute}' = '{attribute_value}' at index '{index}'")

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def fill_text_field(self, label: str, value: str, is_test_label: bool = False, locust_request_label: str = "", index: int = 1) -> 'SailUiForm':
        """
        Fills a field on the form, if there is one present with the following label (case sensitive)
        Otherwise throws a NotFoundException

        Args:
            label(str): Label of the field to fill out
            value(str): Value to fill the field with

        Keyword Args:
            is_test_label(bool): If you are filling a text field via a test label instead of a label, set this boolean to true
            locust_request_label(str): Label used to identify the request for locust statistics
            index(int): Index of the field to fill if more than one match the label criteria (default: 1)

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.fill_text_field('Title','My New Novel')

        """
        attribute_to_find = 'testlabel' if is_test_label else 'label'
        return self.fill_field_by_attribute_and_index(attribute_to_find, label, value, index, locust_request_label)

    @raises_locust_error
    def fill_field_by_index(self, type_of_component: str, index: int, text_to_fill: str, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects a Field by its index and fills it with a text value

        Args:
            type_of_component(str): Name of the component to fill
            index(int): Index of the field on the page (is it the first one found, or second etc.)
            value(int): Value to fill in the field of type 'type_of_component'

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.fill_field_by_index("ParagraphField", 1, "Hello, Testing")
            # selects the first ParagraphField with the value "Hello, Testing"

        """
        component = find_component_by_index_in_dict(type_of_component, index, self.state)
        reeval_url = self._get_update_url_for_reeval(self.state)
        locust_label = locust_request_label or f"{self.breadcrumb}.FillTextFieldByIndex.{index}"
        new_state = self.interactor.fill_textfield(
            reeval_url, component, text_to_fill, self.context, self.uuid, label=locust_label)
        if not new_state:
            raise Exception(
                f'''
                    No response returned when trying to fill: '{text_to_fill}' in the component: '{type_of_component}'
                    with index: '{index}' on the current page")
                ''')

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def fill_field_by_any_attribute(self, attribute: str, value_for_attribute: str, text_to_fill: str, locust_request_label: str = "", index: int = 1) -> 'SailUiForm':
        """
        Selects a Field by "attribute" and its value provided "value_for_attribute"
        and fills it with text "text_to_fill"

        Args:
            attribute(str): Name of the component to fill
            value_for_attribute(str): Value for the attribute passed in to this function
            text_to_fill(str): Value to fill the field with

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics
            index(int): Index of the field to fill if more than one match the label criteria (default: 1)

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.fill_field_by_any_attribute("placeholder", "Write a comment", "Hello, Testing")
            # selects the Component with the "placeholder" attribute having "Write a comment" value
            # and fills it with "Hello, Testing"

        """
        return self.fill_field_by_attribute_and_index(attribute, value_for_attribute, text_to_fill, index, locust_request_label)

    # Aliases for fill_text_field() function
    fill_paragraph_field = fill_text_field

    @raises_locust_error
    def fill_picker_field(self, label: str, value: str, identifier: str = 'id',
                          fill_request_label: str = "", pick_request_label: str = "") -> 'SailUiForm':
        """
        Enters the value in the picker widget and selects one of the suggested items
        if the widget is present with the following label (case sensitive)

        If there is more than one suggestion, this method will select a random one out of the list

        Otherwise this throws a NotFoundException

        The mechanism it uses to find a pickerWidget is prefixing the picker field label with test- and looking for a testLabel

        Args:
            label(str): Label of the field to fill out
            value(str): Value to update the label to

        Keyword Args:
            identifier(str): Key to select the field to filter on, defaults to 'id'
            fill_request_label(str): Label to associate in locust statistics with filling the picker field
            pick_request_label(str): Label to associate in locust statistics with selecting the picker suggestion

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.fill_picker_field('Title','My New Novel')
            >>> form.fill_picker_field('People','Jeff George')
            >>> form.fill_picker_field('Customer', 'GAC Guyana', identifier='code')

        """
        # pickerFieldCustom will add a test-Label at the level where the suggestions/saveInto exist
        test_label = f'test-{label}'
        component = find_component_by_label_and_type_dict('testLabel', test_label, 'PickerWidget', self.state)

        locust_label = fill_request_label or f"{self.breadcrumb}.FillPickerField.{label}"
        new_state = self.interactor.fill_pickerfield_text(
            self.form_url, component, value, self.context, self.uuid, label=locust_label)

        if not new_state:
            raise Exception(f"No response returned when trying to update field with label '{label}'")

        component = find_component_by_label_and_type_dict('testLabel', test_label, 'PickerWidget', new_state)

        suggestions_list = extract_all_by_label(component, 'suggestions')

        if not suggestions_list:
            raise Exception(f"No suggestions returned when '{value}' was entered in the picker field.")

        identifiers = extract_all_by_label(suggestions_list, 'identifier')

        if not identifiers:
            raise Exception(f"No identifiers found when '{value}' was entered in the picker field.")

        # Introspect to see if there's an ID
        index_by_id = identifiers[0].get(identifier) is not None
        id_index = identifier if index_by_id else '#v'

        v_or_id = [identifier.get(id_index) for identifier in identifiers if identifier.get(id_index)]

        if not v_or_id:
            raise Exception(f"Could not extract picker values '{id_index}' from suggestions_list {suggestions_list}")

        v_choice = random.choice(range(len(v_or_id)))

        dict_value = identifiers[v_choice]

        locust_label = pick_request_label or f"{self.breadcrumb}.SelectPickerSuggestion.{label}"
        newer_state = self.interactor.select_pickerfield_suggestion(
            self.form_url, component, dict_value, self.context, self.uuid, label=locust_label)

        if not newer_state:
            raise Exception(f"No response returned when trying to update field with label '{label}'")

        return self._reconcile_state(newer_state)

    @raises_locust_error
    def click(self, label: str, is_test_label: bool = False, locust_request_label: str = "", index: int = 1) -> 'SailUiForm':
        """
        Clicks on a component on the form, if there is one present with the following label (case sensitive)
        Otherwise throws a NotFoundException

        Can also be called as 'click_link' or 'click_button' to convey intent

        This can also click StartProcessLinks or ProcessTaskLinks

        Args:
            label(str): Label of the component to click
            is_test_label(bool): If you are clicking a button or link via a test label instead of a label, set this boolean to true

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics
            index(int): Index of the component to click if more than one match the label criteria (default: 1)

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.click('Submit')
            >>> form.click('SampleTestLabel', is_test_label = True)

        """
        locust_label = locust_request_label or f"{self.breadcrumb}.Click.{label}"
        return self._click(label, is_test_label=is_test_label, locust_request_label=locust_label, index=index)

    @raises_locust_error
    def click_button(self, label: str, is_test_label: bool = False, locust_request_label: str = "", index: int = 1) -> 'SailUiForm':
        """
        Clicks on a component on the form, if there is one present with the following label (case sensitive)
        Otherwise throws a NotFoundException

        This can also click StartProcessLinks or ProcessTaskLinks

        Args:
            label(str): Label of the component to click
            is_test_label(bool): If you are clicking a button via a test label instead of a label, set this boolean to true

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics
            index(int): Index of the component to click if more than one match the label criteria (default: 1)

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.click_button('Save')
            >>> form.click_link('Update')

        """
        locust_label = locust_request_label or f"{self.breadcrumb}.ClickButton.{label}"
        return self._click(label, is_test_label=is_test_label, locust_request_label=locust_label, index=index)

    @raises_locust_error
    def click_link(self, label: str, is_test_label: bool = False, locust_request_label: str = "", index: int = 1) -> 'SailUiForm':
        """
        Clicks on a component on the form, if there is one present with the following label (case sensitive)
        Otherwise throws a NotFoundException

        This can also click StartProcessLinks or ProcessTaskLinks

        Args:
            label(str): Label of the component to click
            is_test_label(bool): If you are clicking a link via a test label instead of a label, set this boolean to true

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics
            index(int): Index of the component to click if more than one match the label criteria (default: 1)

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.click_link('Update')

        """
        locust_label = locust_request_label or f"{self.breadcrumb}.ClickLink.{label}"
        return self._click(label, is_test_label=is_test_label, locust_request_label=locust_label, index=index)

    def _click(self, label: str, is_test_label: bool = False, locust_request_label: str = "", index: int = 1) -> 'SailUiForm':
        """
        Internal function wrapped by various click methods
        """
        attribute_to_find = 'testLabel' if is_test_label else 'label'

        component = find_component_by_attribute_and_index_in_dict(attribute_to_find, label, index, self.state)

        locust_label = locust_request_label or f"{self.breadcrumb}.Click.{label}"
        new_state = self._dispatch_click(component=component, locust_label=locust_label)

        # get the re-eval URI from links object of the response (new_state)
        reeval_url = self._get_update_url_for_reeval(new_state)

        if not new_state:
            raise Exception(f"No response returned when trying to click button with label '{label}'")
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def click_card_layout_by_index(self, index: int, locust_request_label: str = "") -> 'SailUiForm':
        """
        Clicks a card layout link by index.
        This method will find the CardLayout component on the UI by index and then perform
        the click behavior on its Link component.

        Args:
            index(int): Index of the card layout on which to click. (first found card layout , or second etc.)
                        (Indices start from 1)

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:
            This finds link field on the 2nd card layout on the page and clicks it. It handles StartProcessLink as well, so
            no need to call click_start_process_link() when it is on a CardLayout.

            >>> form.click_card_layout_by_index(2)

        """
        component = find_component_by_index_in_dict("CardLayout", index, self.state)

        if not component.get("link"):
            raise Exception(f"CardLayout found at index: {index} does not have a link on it")

        link_component = component.get('link')
        locust_label = locust_request_label or f"{self.breadcrumb}.ClickCardLayout.Index.{index}"
        if link_component["#t"] == "StartProcessLink":
            site_name = link_component["siteUrlStub"] or "D6JMim"
            page_name = link_component["sitePageUrlStub"]
            new_state = self._click_start_process_link(site_name, page_name, False, link_component, locust_request_label=locust_label)
        else:
            new_state = self.interactor.click_component(self.form_url, link_component, self.context, self.uuid, label=locust_label)

        if not new_state:
            raise Exception(f"No response returned when trying to click card layout at index '{index}'")

        reeval_url = self._get_update_url_for_reeval(new_state)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def click_record_link_by_attribute_and_index(self, attribute: str = "", attribute_value: str = "", index: int = 1, locust_request_label: str = "") -> 'SailUiForm':
        """
        Click the index'th record link on the form if there is one present with an attribute matching attribute_value
        If no attribute is provided, the index'th record link is selected from all record links in the form
        Otherwise throws a ComponentNotFoundException

        Keyword Args:
            attribute(str): Attribute to check for 'attribute_value' (default: "")
            attribute_value(str): Attribute value of record link to click (default: "")
            index(int): Index of record link to click (default: 1)
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The record form (feed) for the linked record.

        """
        component_type = 'RecordLink'
        component = find_component_by_type_and_attribute_and_index_in_dict(self.state, component_type, attribute, attribute_value, index)
        locust_label = locust_request_label or f"{self.breadcrumb}.ClickRecordLink"
        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.click_record_link(reeval_url, component, self.context, self.uuid,
                                                      locust_label=locust_label)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def click_record_link(self, label: str, is_test_label: bool = False, locust_request_label: str = "") -> 'SailUiForm':
        """
        Click a record link on the form if there is one present with the following label (case sensitive)
        Otherwise throws a ComponentNotFoundException

        Args:
            label(str): Label of the record link to click
            is_test_label(bool): If you are clicking a record link via a test label instead of a label, set this boolean to true

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The record form (feed) for the linked record.

        """
        attribute_to_find = 'testLabel' if is_test_label else 'label'
        return self.click_record_link_by_attribute_and_index(attribute=attribute_to_find, attribute_value=label, locust_request_label=locust_request_label)

    @raises_locust_error
    def click_record_link_by_index(self, index: int, locust_request_label: str = "") -> 'SailUiForm':
        """
        Click the index'th record link on the form
        Otherwise throws a ComponentNotFoundException

        Args:
            index(int): Index of the record link to click (1-based)

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The record form (feed) for the linked record.

        """
        return self.click_record_link_by_attribute_and_index(index=index, locust_request_label=locust_request_label)

    @raises_locust_error
    def click_start_process_link(self, label: str, site_name: str, page_name: str, is_mobile: bool = False, locust_request_label: str = "") -> 'SailUiForm':
        """
        Clicks a start process link on the form by label
        If no link is found, throws a ComponentNotFoundException

        Args:
            label(str): Label of the link
            site_name(str): Name of the site (i.e. the Sites feature)
            page_name(str): Name of the page within the site

        Keyword Args:
            is_mobile(bool): Boolean to use the mobile form of the request
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:
            >>> form.click_start_process_link('Request upgrade')

        """

        component = find_component_by_label_and_type_dict('label', label, START_PROCESS_LINK_TYPE, self.state)

        locust_label = locust_request_label or f"{self.breadcrumb}.ClickStartProcessLink.{label}"
        new_state = self._click_start_process_link(site_name, page_name, is_mobile, component, locust_request_label=locust_label)

        # get the re-eval URI from links object of the response (new_state)
        reeval_url = self._get_update_url_for_reeval(new_state)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def click_start_process_link_on_mobile(self, label: str, site_name: str, page_name: str, locust_request_label: str = "") -> 'SailUiForm':
        """
        Clicks a start process link on the form by label (for Mobile)
        If no link is found, throws a ComponentNotFoundException

        Args:
            label(str): Label of the link
            site_name(str): Name of the site (i.e. the Sites feature)
            page_name(str): Name of the page within the site

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.click_start_process_link_on_mobile('Open Issue')

        """
        locust_label = locust_request_label or f"{self.breadcrumb}.ClickStartProcessLink.Mobile.{label}"
        return self.click_start_process_link(label, site_name, page_name, is_mobile=True, locust_request_label=locust_label)

    def _click_start_process_link(self, site_name: str, page_name: str, is_mobile: bool,
                                  component: Dict[str, Any], locust_request_label: str) -> Dict[str, Any]:
        """
        This internal function is called by both click_start_process_link() and click_card_layout_by_index().
        It takes parameters needed for making a start process lnik call to the server and calls the interactor to do that.
        """
        process_model_opaque_id = component.get("processModelOpaqueId", "")
        cache_key = component.get("cacheKey", "")
        if not process_model_opaque_id:
            raise Exception(f"StartProcessLink component does not have process model opaque id set.")
        elif not cache_key:
            raise Exception(f"StartProcessLink component does not have cache key set.")

        return self.interactor.click_start_process_link(component=component, process_model_opaque_id=process_model_opaque_id,
                                                        cache_key=cache_key, site_name=site_name, page_name=page_name, is_mobile=is_mobile,
                                                        locust_request_label=locust_request_label)

    def _dispatch_click(self, component: Dict[str, Any], locust_label: str) -> Dict[str, Any]:
        """
        Dispatches the appropriate link interaction based on the link type if appropriate

        Args:
            link_component (Dict[str, Any]): Link component to interact with
            locust_label (str): Label used to identify the request for locust statistics

        Returns:
            Dict[str, Any]: State returned by the interaction
        """
        component_type = component.get('#t')
        # Check if component is already a supported link
        if component_type in [START_PROCESS_LINK_TYPE, PROCESS_TASK_LINK_TYPE]:
            link_component = component
            link_type = component_type
        else:
            link_component = component.get('link', {})
            link_type = link_component.get('#t')

        if link_type == START_PROCESS_LINK_TYPE:
            site_name = link_component["siteUrlStub"] or "D6JMim"
            page_name = link_component["sitePageUrlStub"]
            new_state = self._click_start_process_link(site_name, page_name, False, link_component, locust_request_label=locust_label)
        elif link_type == PROCESS_TASK_LINK_TYPE:
            task_name = link_component.get('label') or 'Unnammed Task'
            task_id = link_component.get('opaqueTaskId')
            if not task_id:
                raise Exception(f"No task id found for task with name '{task_name}'")
            site_name = link_component.get("siteUrlStub") or "D6JMim"
            page_name = link_component.get("sitePageUrlStub")
            headers = {
                'X-Site-UrlStub': site_name,
                'X-Page-UrlStub': page_name,
                'X-Client-Mode': 'SITES'
            }
            new_state = self.task_opener.visit_by_task_id(task_name, task_id, extra_headers=headers)
        elif link_component:
            new_state = self.interactor.click_component(self.form_url, link_component, self.context, self.uuid, label=locust_label)
        else:
            new_state = self.interactor.click_component(self.form_url, component, self.context, self.uuid, label=locust_label)
        return new_state

    @raises_locust_error
    def click_related_action(self, label: str, locust_request_label: str = "") -> 'SailUiForm':
        """
        Clicks a related action (either a related action button or link) on the form by label
        If no link is found, throws a ComponentNotFoundException

        Args:
            label(str): Label of the related action

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:
            How to use click_related_action():

            Use records function - visit_record_instance_and_get_feed_form() to get Record Instance SailUiForm, then get the header response
            and finally click on the related action by label.

            >>> feed_form = records.visit_record_instance_and_get_feed_form()

            We need to get the header response or view response  depending on if the related action is under the related actions dashboard
            or if it is a related action link on the summary view UI (which opens in a dialog).

            >>> header_form = feed_form.get_record_header_form() or feed_form.get_record_view_form()

            >>> header_form.click_related_action('Request upgrade')

        """
        component = find_component_by_attribute_in_dict('label', label, self.state)

        # Support scenario where related action label is found within outer "ButtonWidget" rather than directly in "RelatedActionLink" component
        if "source" not in component:
            component = component.get("link", "")
        component_source = component.get("source", "")
        record_type_stub = component_source.get("recordTypeStub", "")
        opaque_related_action_id = component_source.get("opaqueRelatedActionId", "")
        open_actions_in = component.get("openActionsIn", "")
        open_action_in_a_dialog = open_actions_in == "DIALOG"

        opaque_identifier_key = "opaqueRecordRef" if open_action_in_a_dialog else "opaqueRecordId"
        opaque_record_id = component_source.get(opaque_identifier_key, "")

        if not record_type_stub or not opaque_record_id or not opaque_related_action_id:
            raise Exception(f'''
                            Related Action link component does not have recordTypeStub or opaqueRecordId or opaqueRelatedActionId set.
                            ''')
        locust_label = locust_request_label or f"{self.breadcrumb}.ClickRelatedActionLink.{label}"

        new_state = self.interactor.click_related_action(component, record_type_stub=record_type_stub, opaque_record_id=opaque_record_id,
                                                         opaque_related_action_id=opaque_related_action_id,
                                                         locust_request_label=locust_label, open_in_a_dialog=open_action_in_a_dialog)
        # get the re-eval URI from links object of the response (new_state)
        reeval_url = self._get_update_url_for_reeval(new_state)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def get_dropdown_items(self, label: str, is_test_label: bool = False) -> List[str]:
        """
        Gets all dropdown items for the dropdown label provided on the form
        If no dropdown found, throws a NotFoundException

        Args:
            label(str): Label of the dropdown
            is_test_label(bool): If you are interacting with a dropdown via a test label instead of a label, set this boolean to true.
                                 User filters on a record instance list use test labels.

        Returns (List): A list of all the choices in the dropdown

        Examples:

            >>> form.get_dropdown_items('MyDropdown')

        """
        attribute_to_find = 'testLabel' if is_test_label else 'label'
        component = find_component_by_attribute_in_dict(
            attribute_to_find, label, self.state)

        choices: list = component.get('choices')
        if choices is None or not isinstance(choices, list):
            raise InvalidComponentException(f"No choices found for component {label}, is the component a Dropdown?")
        return choices

    @raises_locust_error
    def select_dropdown_item(self, label: str, choice_label: str, locust_request_label: str = "", is_test_label: bool = False) -> 'SailUiForm':
        """
        Selects a dropdown item on the form
        If no dropdown found, throws a NotFoundException
        If no element found, throws a ChoiceNotFoundException

        Args:
            label(str): Label of the dropdown
            choice_label(str): Label of the dropdown item to select
            is_test_label(bool): If you are interacting with a dropdown via a test label instead of a label, set this boolean to true.
                                 User filters on a record instance list use test labels.

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.select_dropdown_item('MyDropdown', 'My First Choice')

        """
        attribute_to_find = 'testLabel' if is_test_label else 'label'
        component = find_component_by_attribute_in_dict(
            attribute_to_find, label, self.state)

        choices: list = component.get('choices')
        if not choices:
            raise InvalidComponentException(f"No choices found for component {label}, is the component a Dropdown?")
        if not isinstance(choice_label, list) and choice_label not in choices:
            raise ChoiceNotFoundException(f"Choice {choice_label} not found for component {label}, valid choices were {choices}")

        index = choices.index(choice_label) + 1  # Appian is _sigh_ one indexed
        locust_label = locust_request_label or f'{self.breadcrumb}.SelectDropdownWithLabel.{label}'
        reeval_url = self._get_update_url_for_reeval(self.state)

        # Opting to use this field, rather than self.form_url, because 'sail-application-url' is the same between web and mobile
        url = self.state.get('sail-application-url')
        # url_stub should only be populated if the page is a record list
        url_stub = get_url_stub_from_record_list_url_path(url)

        new_state = self.interactor.send_dropdown_update(
            reeval_url, component, self.context, self.uuid, index=index, label=locust_label, url_stub=url_stub)
        if not new_state:
            raise Exception(
                f"No response returned when trying to click button with label '{label}'")

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def select_multi_dropdown_item(self, label: str, choice_label: List[str], locust_request_label: str = "", is_test_label: bool = False) -> 'SailUiForm':
        """
        Selects a multiple dropdown item on the form
        If no multiple dropdown found, throws a NotFoundException
        If no element found, throws a ChoiceNotFoundException

        Args:
            label(str): Label of the dropdown
            choice_label([str]): Label(s) of the multiple dropdown item to select
            is_test_label(bool): If you are interacting with a multiple dropdown via a test label instead of a label, set this boolean to true.
                                 User filters on a record instance list use test labels.

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.select_multi_dropdown_item('MyMultiDropdown', ['My First Choice','My Second Choice'])

        """
        attribute_to_find = 'testLabel' if is_test_label else 'label'
        component = find_component_by_attribute_in_dict(
            attribute_to_find, label, self.state)

        choices: list = component.get('choices')
        if not choices:
            raise InvalidComponentException(f"No choices found for component {label}, is the component a Dropdown?")
        if not isinstance(choice_label, list) and choice_label not in choices:
            raise ChoiceNotFoundException(f"Choice {choice_label} not found for component {label}, valid choices were {choices}")
        index_multi = [choices.index(current_label) + 1 for current_label in choice_label]  # Appian is _sigh_ one indexed
        locust_label = locust_request_label or f'{self.breadcrumb}.SelectMultupleDropdownWithLabel.{choice_label}'
        reeval_url = self._get_update_url_for_reeval(self.state)

        # Opting to use this field, rather than self.form_url, because 'sail-application-url' is the same between web and mobile
        url = self.state.get('sail-application-url')
        # url_stub should only be populated if the page is a record list
        url_stub = get_url_stub_from_record_list_url_path(url)

        new_state = self.interactor.send_multiple_dropdown_update(
            reeval_url, component, self.context, self.uuid, index=index_multi, label=locust_label, url_stub=url_stub)
        if not new_state:
            raise Exception(
                f"No response returned when trying to click button with label '{label}'")

        return self._reconcile_state(new_state, form_url=reeval_url)

    def _check_checkbox_by_attribute(self, attribute: str, value_for_attribute: str, indices: List[int], locust_request_label: str = "") -> 'SailUiForm':
        """
        Function that checks checkboxes.
        It finds checkboxes by the attribute and its value provided.

        Args:
            attribute(str): attribute to use to find the checkbox
            value_for_attribute(str): Value of the attribute used to find the checkbox
            indices(str): Indices of the checkbox to check. Pass None or empty to uncheck all

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm
        """
        component = find_component_by_attribute_in_dict(attribute, value_for_attribute, self.state,
                                                        throw_attribute_exception=True)

        locust_label = locust_request_label or f'{self.breadcrumb}.CheckCheckboxByAttribute.{attribute}'
        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.select_checkbox_item(
            reeval_url, component, self.context, self.uuid, indices=indices, context_label=locust_label)
        if not new_state:
            raise Exception(f'''No response returned when trying to check checkbox which was found with attribute: '{attribute}'
                            and its value: '{value_for_attribute}' on the current page
                            ''')

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def check_checkbox_by_test_label(self, test_label: str, indices: List[int], locust_request_label: str = "") -> 'SailUiForm':
        """
        Checks a checkbox by its testLabel attribute
        Indices are positions to be checked

        Args:
            test_label(str): Value for the testLabel attribute of the checkbox
            indices(str): Indices of the checkbox to check. Pass None or empty to uncheck all

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.check_checkbox_by_test_label('myTestLabel', [1])  # checks the first item
            >>> form.check_checkbox_by_test_label('myTestLabel', None) # unchecks

        """
        if not test_label:
            raise Exception(f"No testLabel provided to select a checkbox")

        locust_label = locust_request_label or f'{self.breadcrumb}.CheckCheckboxByTestLabel.{test_label}'
        return self._check_checkbox_by_attribute('testLabel', test_label, indices, locust_request_label=locust_label)

    @raises_locust_error
    def check_checkbox_by_label(self, label: str, indices: List[int], locust_request_label: str = "") -> 'SailUiForm':
        """
        Checks a checkbox by its label
        Indices are positions to be checked

        Args:
            label(str): Value for label of the checkbox
            indices(str): Indices of the checkbox to check. Pass None or empty to uncheck all

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.check_checkbox_by_label('myLabel', [1])  # checks the first item
            >>> form.check_checkbox_by_label('myLabel', None) # unchecks

        """
        if not label:
            raise Exception(f"No label provided to select a checkbox")

        locust_label = locust_request_label or f'{self.breadcrumb}.CheckCheckboxByLabel.{label}'
        return self._check_checkbox_by_attribute('label', label, indices, locust_request_label=locust_label)

    @raises_locust_error
    def click_tab_by_label(self, tab_label: str, tab_group_test_label: str, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects a Tab by its label and its tab group's testLabel

        Args:
            tab_label(str): Label of the tab to select
            tab_group_test_label(str): Test Label of the tab group (tab is part of a tab group)

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

        """
        # find the TabButtonGroup, which is the  model we need for the SaveRequest
        reeval_url = self._get_update_url_for_reeval(self.state)

        tab_group_component = find_component_by_attribute_in_dict('testLabel', tab_group_test_label, self.state)
        new_state = self.interactor.click_selected_tab(
            reeval_url, tab_group_component, tab_label, self.context, self.uuid)
        if not new_state:
            raise Exception(
                f'''No response returned when trying to click a tab with label: '{tab_label}'
                inside the TabButtonGroup component with testLabel: '{tab_group_test_label}'''
            )

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def upload_document_to_upload_field(self, label: str, file_path: Union[str, List], locust_request_label: str = "") -> 'SailUiForm':
        """
        Uploads a document to a named upload field
        There are two steps to this which can fail, one is the document upload, the other
        is finding the component and applying the update.

        Args:
            label(str): Label of the upload field
            file_path(str): File path to the document

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.upload_document_to_upload_field('Upload File', "/usr/local/appian/File.zip")
            >>> form.upload_document_to_upload_field('Upload Properties', "/usr/local/appian/File.properties")

        """
        component = find_component_by_attribute_in_dict(
            'label', label, self.state)

        # Inner component can be the upload field
        if component.get('#t') != 'FileUploadWidget' and 'contents' in component:
            component = component['contents']

        # Check again to see if the wrong component
        if component.get('#t') != 'FileUploadWidget':
            if component.get('#t') == "MultipleFileUploadWidget":
                print("Selected FileUploadWidget is instead MultipleFileUploadWidget, continuing automatically")
                return self.upload_documents_to_multiple_file_upload_field(label, [file_path], locust_request_label)
            else:
                raise Exception(f"Provided component was not a FileUploadWidget, was instead of type '{component.get('#t')}'")

        if type(file_path) != str:
            raise Exception(f"Provided file_path {file_path} was not a string, was instead of type '{type(file_path)}'")

        is_encrypted = component.get("isEncrypted", False)

        if not os.path.exists(str(file_path)):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
        doc_id = self.interactor.upload_document_to_server(str(file_path), is_encrypted=is_encrypted)
        locust_label = locust_request_label or f"{self.breadcrumb}.FileUpload.{label}"
        new_state = self.interactor.upload_document_to_field(
            self.form_url, component, self.context, self.uuid, doc_id=doc_id, locust_label=locust_label)
        if not new_state:
            raise Exception(
                f"No response returned when trying to upload file to field '{label}'")
        return self._reconcile_state(new_state)

    @raises_locust_error
    def upload_documents_to_multiple_file_upload_field(self, label: str, file_paths: List[str], locust_request_label: str = "") -> 'SailUiForm':
        """
        Uploads multiple documents to a named upload field
        There are two steps to this which can fail, one is the document uploads, the other
        is finding the component and applying the update.

        Args:
            label(str): Label of the upload field
            file_paths(list): List of document file paths in string form

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Example:

            >>> form.multi_upload_document_to_upload_field('Upload Files', ["/usr/local/appian/File1.zip", "/usr/local/appian/File2.zip"])

        """
        component = find_component_by_attribute_in_dict(
            'label', label, self.state)

        # Inner component can be the upload field
        if component.get('#t') != 'MultipleFileUploadWidget' and 'contents' in component:
            component = component['contents']

        # Check again to see if the wrong component
        if component.get('#t') != 'MultipleFileUploadWidget':
            if component.get('#t') == "FileUploadWidget":
                print("Selected MultipleFileUploadWidget is instead FileUploadWidget, continuing automatically")
                return self.upload_document_to_upload_field(label, file_paths[0], locust_request_label)
            raise Exception(f"Provided component was not a MultipleFileUploadWidget, was instead of type '{component.get('#t')}'")

        is_encrypted = component.get("isEncrypted", False)

        doc_ids: List[int] = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
            doc_ids.append(self.interactor.upload_document_to_server(file_path, is_encrypted=is_encrypted))
        locust_label = locust_request_label or f"{self.breadcrumb}.MultiFileUpload.{label}"
        new_state = self.interactor.upload_document_to_field(
            self.form_url, component, self.context, self.uuid, doc_id=doc_ids, locust_label=locust_label)
        if not new_state:
            raise Exception(
                f"No response returned when trying to upload file(s) to field '{label}'")
        return self._reconcile_state(new_state)

    @raises_locust_error
    def fill_date_field(self, label: str, date_input: datetime.date, locust_request_label: str = "") -> 'SailUiForm':
        """
        Fills a date field with the specified date

        Args:
            label(str): Label of the date field
            date_input(date): Date used to fill the field

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.fill_date_field('Today', datetime.date.today())
            >>> form.fill_date_field('Date of Birth', datetime.date(1992, 12, 30))

        """
        if not isinstance(date_input, datetime.date):
            raise Exception("Input must be of type datetime.date")
        field_type = 'DatePickerField'
        date_field = find_component_by_label_and_type_dict('label', label, field_type, self.state)

        locust_label = locust_request_label or f'{self.breadcrumb}.FillDateField'
        reeval_url = self._get_update_url_for_reeval(self.state)

        new_state = self.interactor.update_date_field(
            reeval_url, date_field, date_input, self.context, self.uuid, locust_label=locust_label)
        if not new_state:
            raise Exception(f'''No response returned when trying to update: '{label}'
                            with its value: '{date_input}' on the current page
                            ''')

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def fill_datetime_field(self, label: str, datetime_input: datetime.datetime, locust_request_label: str = "") -> 'SailUiForm':
        """
        Fills a datetime field with the specified datetime

        NOTE: this does one api call for both the date and time, whereas filling the elements on screen requires
        two separate evaluations, one to fill the date field and one to fill the time field. This is the
        way the request would look if one of the fields were already filled.

        Args:
            label(str): Label of the datetime field
            datetime_input(date): Date time used to fill the field

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.fill_datetime_field('Now', datetime.datetime.now())
            >>> form.fill_datetime_field('Date and Time of Birth', datetime.datetime(1992, 12, 30, 12, 30, 5))

        """
        if not isinstance(datetime_input, datetime.datetime):
            raise Exception("Input must be of type datetime.datetime")
        field_type = 'DateTimePickerField'
        datetime_field = find_component_by_label_and_type_dict('label', label, field_type, self.state)

        locust_label = locust_request_label or f'{self.breadcrumb}.FillDateTimeField'
        reeval_url = self._get_update_url_for_reeval(self.state)

        new_state = self.interactor.update_datetime_field(
            reeval_url, datetime_field, datetime_input, self.context, self.uuid, locust_label=locust_label)
        if not new_state:
            raise Exception(f'''No response returned when trying to update: '{label}'
                            with its value: '{datetime_input}' on the current page
                            ''')

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def select_rows_in_grid(self, rows: List[int], label: str = None, index: int = None, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects rows in a grid
        Either a label or an index is required, indices are useful if there is no title for the grid

        Args:
            rows(List[int]): The rows to select
            label(str): Label of the grid
            index(int): Index of the grid

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.select_rows_in_grid(rows=[1], label='my nice grid')
        """
        grid = self.grid_interactor.find_grid_by_label_or_index(self.state, label=label, index=index)
        grid_label = self.grid_interactor.format_grid_display_label(grid)

        new_grid_save = self.grid_interactor.select_rows(grid, rows)
        context_label = locust_request_label or f"{self.breadcrumb}.Grid.SelectRows.{grid_label}"

        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.update_grid_from_sail_form(reeval_url, grid, new_grid_save,
                                                               self.context, self.uuid, context_label=context_label)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def move_to_end_of_paging_grid(self, label: str = None, index: int = None, locust_request_label: str = "") -> 'SailUiForm':
        """
        Moves to the end of a paging grid, if possible
        Either a label or an index is required, indices are useful if there is no title for the grid

        Args:
            label(str): Label of the grid
            index(int): Index of the grid

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.move_to_end_of_paging_grid(label='my nice grid')
        """
        grid = self.grid_interactor.find_grid_by_label_or_index(self.state, label=label, index=index)
        grid_label = self.grid_interactor.format_grid_display_label(grid)

        new_grid_save = self.grid_interactor.move_to_last_page(grid)
        context_label = locust_request_label or f"{self.breadcrumb}.Grid.MoveToEnd.{grid_label}"

        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.update_grid_from_sail_form(reeval_url, grid, new_grid_save,
                                                               self.context, self.uuid, context_label=context_label)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def move_to_beginning_of_paging_grid(self, label: str = None, index: int = None, locust_request_label: str = "") -> 'SailUiForm':
        """
        Moves to the beginning of a paging grid, if possible
        Either a label or an index is required, indices are useful if there is no title for the grid

        Args:
            label(str): Label of the grid
            index(int): Index of the grid

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.move_to_beginning_of_paging_grid(label='my nice grid')
        """
        grid = self.grid_interactor.find_grid_by_label_or_index(self.state, label=label, index=index)
        grid_label = self.grid_interactor.format_grid_display_label(grid)

        new_grid_save = self.grid_interactor.move_to_first_page(grid)
        context_label = locust_request_label or f"{self.breadcrumb}.Grid.MoveToBeginning.{grid_label}"

        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.update_grid_from_sail_form(reeval_url, grid, new_grid_save,
                                                               self.context, self.uuid, context_label=context_label)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def move_to_left_in_paging_grid(self, label: str = None, index: int = None, locust_request_label: str = "") -> 'SailUiForm':
        """
        Moves to the left in a paging grid, if possible
        It might require getting the state of the grid if you've moved to the end/ previous part of the grid
        Either a label or an index is required, indices are useful if there is no title for the grid

        Args:
            label(str): Label of the grid
            index(int): Index of the grid

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.move_to_left_in_paging_grid(label='my nice grid')
        """
        grid = self.grid_interactor.find_grid_by_label_or_index(self.state, label=label, index=index)
        grid_label = self.grid_interactor.format_grid_display_label(grid)

        new_grid_save = self.grid_interactor.move_to_the_left(grid)
        context_label = locust_request_label or f"{self.breadcrumb}.Grid.MoveLeft.{grid_label}"

        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.update_grid_from_sail_form(reeval_url, grid, new_grid_save,
                                                               self.context, self.uuid, context_label=context_label)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def move_to_right_in_paging_grid(self, label: str = None, index: int = None, locust_request_label: str = "") -> 'SailUiForm':
        """
        Moves to the right in a paging grid, if possible
        It might require getting the state of the grid if you've moved within the grid
        Either a label or an index is required, indices are useful if there is no title for the grid

        Args:
            label(str): Label of the grid
            index(int): Index of the grid

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.move_to_right_in_paging_grid(index=0) # move to right in first grid on the page
        """
        grid = self.grid_interactor.find_grid_by_label_or_index(self.state, label=label, index=index)
        grid_label = self.grid_interactor.format_grid_display_label(grid)

        new_grid_save = self.grid_interactor.move_to_the_right(grid)
        context_label = locust_request_label or f"{self.breadcrumb}.Grid.MoveRight.{grid_label}"

        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.update_grid_from_sail_form(reeval_url, grid, new_grid_save,
                                                               self.context, self.uuid, context_label=context_label)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def sort_paging_grid(self, label: str = None, index: int = None, field_name: str = "", ascending: bool = False, locust_request_label: str = "") -> 'SailUiForm':
        """
        Sorts a paging grid by the field name, which is not necessarily the same as the label of the column
        And might require inspecting the JSON to determine what the sort field is

        Sorts by ascending = False by default, override to set it to True

        Either a label or an index is required, indices are useful if there is no title for the grid

        Args:
            label(str): Label of the grid
            index(int): Index of the grid
            field_name(str): Field to sort on (not necessarily the same as the displayed one)
            ascending(bool): Whether to sort ascending, default is false

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.sort_paging_grid(index=0,field_name='Total',ascending=True)
        """
        if not field_name:
            raise Exception("Field to sort cannot be blank when sorting a grid")
        grid = self.grid_interactor.find_grid_by_label_or_index(self.state, label=label, index=index)
        grid_label = self.grid_interactor.format_grid_display_label(grid)

        new_grid_save = self.grid_interactor.sort_grid(field_name=field_name, paging_grid=grid, ascending=ascending)
        context_label = locust_request_label or f"{self.breadcrumb}.Grid.Sort.{grid_label}.{field_name}"

        reeval_url = self._get_update_url_for_reeval(self.state)
        new_state = self.interactor.update_grid_from_sail_form(reeval_url, grid, new_grid_save,
                                                               self.context, self.uuid, context_label=context_label)
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def select_radio_button_by_test_label(self, test_label: str, index: int, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects a radio button by its test label
        Index is position to be selected

        Args:
            test_label(str): Label of the radio button field
            index(int): Index of the radio button to select

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.select_radio_button_by_test_label('myTestLabel', 1)  # selects the first item

        """
        component = find_component_by_attribute_in_dict(
            'testLabel', test_label, self.state)

        reeval_url = self._get_update_url_for_reeval(self.state)
        context_label = locust_request_label or f"{self.breadcrumb}.RadioButton.SelectByTestLabel.{test_label}"
        new_state = self.interactor.select_radio_button(
            reeval_url, component, self.context, self.uuid, index=index, context_label=context_label)
        if not new_state:
            raise Exception(
                f"No response returned when trying to select radio button with testLabel '{test_label}'")
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def select_radio_button_by_label(self, label: str, index: int, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects a radio button by its label
        Index is position to be selected

        Args:
            label(str): Label of the radio button field
            index(int): Index of the radio button to select

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.select_radio_button_by_label('myLabel', 1)  # selects the first item

        """
        component = find_component_by_attribute_in_dict(
            'label', label, self.state)

        reeval_url = self._get_update_url_for_reeval(self.state)
        context_label = locust_request_label or f"{self.breadcrumb}.RadioButton.SelectByLabel.{label}"
        new_state = self.interactor.select_radio_button(
            reeval_url, component, self.context, self.uuid, index=index, context_label=context_label)
        if not new_state:
            raise Exception(
                f"No response returned when trying to select radio button with label '{label}'")
        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def select_nav_card_by_index(self, nav_group_label: str, index: int, is_test_label: bool = False, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects an element of a navigation card group by its index

        Args:
            nav_group_label(str): Label of the navigation card group
            index(int): Index of the element

        Keyword Args:
            is_test_label (bool): If this label is a test label
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm
        """
        if is_test_label:
            return self.select_radio_button_by_test_label(nav_group_label, index, locust_request_label)
        return self.select_radio_button_by_label(nav_group_label, index, locust_request_label)

    @raises_locust_error
    def select_radio_button_by_index(self, field_index: int, index: int, locust_request_label: str = "") -> 'SailUiForm':
        """
        Selects a radio button by its field index
        Index is position to be selected

        Args:
            field_index(int): Index of the radio button field on the page
            index(int): Index of the radio button to select

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.select_radio_button_by_index(1, 1)  # selects the first item in the first radio button field

        """
        component = find_component_by_index_in_dict(
            'RadioButtonField', field_index, self.state)

        reeval_url = self._get_update_url_for_reeval(self.state)
        context_label = locust_request_label or f"{self.breadcrumb}.RadioButton.SelectByIndex.{index}"
        new_state = self.interactor.select_radio_button(
            reeval_url, component, self.context, self.uuid, index=index, context_label=context_label)
        if not new_state:
            raise Exception(
                f"No response returned when trying to select radio button with index '{field_index}'")
        return self._reconcile_state(new_state, form_url=reeval_url)

    def go_to_next_record_grid_page(self, locust_request_label: str = "") -> 'SailUiForm':
        context_label = locust_request_label or f"{self.breadcrumb}.NextPage"
        headers = self.interactor.setup_request_headers()
        headers["Accept"] = "application/vnd.appian.tv.ui+json"
        reeval_url = self._get_update_url_for_reeval(self.state)
        label = 'NEXT'
        if not _is_grid(self.state):
            raise Exception("Not a grid record list")
        component = find_component_by_attribute_in_dict(
            'label', label, self.state)
        new_state = self.interactor.interact_with_record_grid(
            post_url=reeval_url, grid_component=component, context=self.context, uuid=self.uuid, context_label=context_label)
        if not new_state:
            raise Exception(
                f"No response returned when navigating to next page on record list '{reeval_url}'")
        return self._reconcile_state(new_state, form_url=reeval_url)

    def get_record_header_form(self) -> 'SailUiForm':
        """
        Extracts the embedded record header form from a record "feed" form to enable interaction with components in the record header.

        Returns (SailUiForm): The record header UiForm embedded within a record "feed" form.

        Examples:

            >>> form.get_record_header_form()

        """
        # self in this case is a record form (feed) containing embedded forms (header and view form)
        record_header_response = get_record_header_response(self.state)

        # record "feed" form has no breadcrumb - set up a breadcrumb
        self.breadcrumb = "Record.HeaderForm.SailUi"

        return SailUiForm(self.interactor, json.loads(record_header_response), self.form_url,
                          breadcrumb=self.breadcrumb)

    def get_record_view_form(self) -> 'SailUiForm':
        """
        Extracts the embedded record view form from a record "feed" form to enable interaction with components in the record view.

        Returns (SailUiForm): The record view UiForm embedded within a record "feed" form.

        Examples:

            >>> form.get_record_view_form()

        """
        record_view_response = get_record_summary_view_response(self.state)

        # record "feed" form has no breadcrumb - set up a breadcrumb
        self.breadcrumb = "Record.ViewForm.SailUi"

        return SailUiForm(self.interactor, json.loads(record_view_response), self.form_url, breadcrumb=self.breadcrumb)

    def filter_records_using_searchbox(self, search_term: str = "", locust_request_label: str = "") -> 'SailUiForm':
        """
        This method allows you to Filter the Record Type List (displaying record instance for a specific record type)
        which makes the same request when typing something in the search box and reloading the page.
        More interactions (with the filtered list) can be performed on the returned SailUiForm Object.

        Note: This is different from how an end user interacts with the SearchBox. In that case you would type something in the box
        and when you would unfocus from the box a reevaluation happens and then you click the 'Search' button which returns the filtered
        results.

        Examples:

            >>> form.filter_records_using_searchbox('Donuts')

        Returns (SailUiForm): The record type list UiForm with the filtered results.
        """
        context_label = locust_request_label or f"{self.breadcrumb}.RecordType.SearchByText"
        search_uri = f"{self.form_url}?searchTerm={quote(search_term)}"

        headers = self.interactor.setup_sail_headers()
        response = self.interactor.get_page(uri=search_uri, headers=headers, label=context_label)
        return SailUiForm(self.interactor, response.json(), self.form_url, breadcrumb=context_label)

    def assert_no_validations_present(self) -> 'SailUiForm':
        """
        Raises an exception if there are validations present on the form, otherwise, returns the form as is

        Returns (SailUiForm): Form as it was when validations were asserted
        """
        validations: list = extract_all_by_label(self.state, "validations")
        validation_present = False
        for validation in validations:
            if validation:
                log.error(f'Validations were found in the form {self.breadcrumb}, validation: {validation}')
                validation_present = True
        if validation_present:
            raise Exception(f"At least one validation was found in the form {self.breadcrumb}")
        return self

    @raises_locust_error
    def refresh_after_record_action(self, label: str, locust_request_label: str = "") -> 'SailUiForm':
        """
        Refreshes a form after the completion of a record action.

        Args:
            label(str): Label of the record action that has just been completed

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> initial_form = copy(form)
            >>> form.click('Request upgrade')
            >>> ...
            >>> form.click('Submit')
            >>> initial_form.refresh_after_record_action('Request upgrade')

        """

        record_action_component = find_component_by_attribute_in_dict(
            'label', label, self.state)

        record_action_trigger_component = find_component_by_attribute_in_dict(
            '_actionName', 'sail:record-action-trigger', self.state)

        reeval_url = self._get_update_url_for_reeval(self.state)
        locust_label = locust_request_label or f"{self.breadcrumb}.RefreshAfterRecordAction.{label}"
        new_state = self.interactor.refresh_after_record_action(
            reeval_url, record_action_component, record_action_trigger_component, self.context, self.uuid, label=locust_label)

        if not new_state:
            raise Exception(f"No response returned when trying to refresh after record action '{label}'")

        return self._reconcile_state(new_state, form_url=reeval_url)

    @raises_locust_error
    def click_record_search_button_by_index(self, index: int = 1, locust_request_label: str = "") -> 'SailUiForm':
        """
        Clicks the Search button of a record grid.

        Args:
            index(int): Index of the record search button on the form

        Keyword Args:
            locust_request_label(str): Label used to identify the request for locust statistics

        Returns (SailUiForm): The latest state of the UiForm

        Examples:

            >>> form.click_record_search_button_by_index(1)

        """
        component = find_component_by_index_in_dict("SearchBoxWidget", index, self.state)

        reeval_url = self._get_update_url_for_reeval(self.state)
        locust_label = locust_request_label or f"{self.breadcrumb}.ClickRecordSearchButtonByIndex.{index}"
        new_state = self.interactor.click_record_search_button(
            reeval_url, component, self.context, self.uuid, label=locust_label)

        if not new_state:
            raise Exception(f"No response returned when trying to click record search button at index '{index}'")

        return self._reconcile_state(new_state, form_url=reeval_url)

    def _reconcile_state(self, new_state: dict, form_url: str = "") -> 'SailUiForm':
        self.interactor.datatype_cache.cache(new_state)
        self.state = self.reconciler.reconcile_ui(self.state, new_state)
        self.form_url = form_url or self.form_url
        self.uuid = self.state.get(KEY_UUID) or self.uuid
        self.context = self.state.get(KEY_CONTEXT) or self.context
        return self

    def _get_update_url_for_reeval(self, state: Dict[str, Any]) -> str:
        """
        This function looks at the links object in a SAIL response
        and finds the URL for "rel"="update", which is then used to do other
        interactions on the form.
        """

        # If state is None (usually for tests) we return empty string for re-eval url
        if not state:
            return ""
        # get the re-eval URI from links object of the response (new_state)
        list_of_links = state["links"]
        reeval_url = self.form_url
        for link_object in list_of_links:
            if link_object.get("rel") == "update":
                reeval_url = urlparse(link_object.get("href", "")).path
                break
        return reeval_url
