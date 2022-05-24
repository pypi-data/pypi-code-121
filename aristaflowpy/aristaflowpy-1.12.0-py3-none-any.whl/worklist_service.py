# -*- coding: utf-8 -*-
# Default Python Libraries
import asyncio
import json
import traceback
import warnings
from asyncio import sleep
from threading import Lock
from typing import Generator, List, Set, Union

# Third Party Libraries
from requests import ConnectionError

# AristaFlow REST Libraries
from af_worklist_manager.api.inc_client_worklists_api import IncClientWorklistsApi
from af_worklist_manager.api.inc_worklist_update_api import IncWorklistUpdateApi
from af_worklist_manager.api.worklist_update_manager_api import WorklistUpdateManagerApi
from af_worklist_manager.models.client_worklist_item import ClientWorklistItem
from af_worklist_manager.models.client_worklist_item_update import ClientWorklistItemUpdate
from af_worklist_manager.models.client_worklist_rest_callback_data import (
    ClientWorklistRestCallbackData,
)
from af_worklist_manager.models.client_worklist_sse_callback_data import (
    ClientWorklistSseCallbackData,
)
from af_worklist_manager.models.inc_client_worklist_data import IncClientWorklistData
from af_worklist_manager.models.inc_worklist_update_data import IncWorklistUpdateData
from af_worklist_manager.models.initial_inc_client_worklist_data import InitialIncClientWorklistData
from af_worklist_manager.models.initial_inc_worklist_update_data import InitialIncWorklistUpdateData
from af_worklist_manager.models.update_interval import UpdateInterval
from af_worklist_manager.models.worklist_revision import WorklistRevision
from af_worklist_manager.models.worklist_update import WorklistUpdate
from af_worklist_manager.models.worklist_update_configuration import WorklistUpdateConfiguration

from af_execution_manager import ActivityStartingApi
from af_worklist_manager import WorklistItem, AfActivityReference
from af_runtime_service import EbpInstanceReference

from .abstract_service import AbstractService
from .configuration import Configuration
from .service_provider import ServiceProvider
from .worklist_model import Worklist


# signature for worklist updates
def __update_listener(updates: List[ClientWorklistItemUpdate]):
    pass


def __worklist_callback_provider(worklist: Worklist) -> str:
    return None


WorklistUpdateListener = type(__update_listener)
"""
    Type for callback function for retrieving worklist updates
"""

WorklistCallbackProvider = type(__worklist_callback_provider)
"""
    Type for callback function for providing worklist callback URLs
"""


class WorklistService(AbstractService):
    # The fetch size for incremental worklists / updates. If None, the
    # server-side default will be used
    fetch_count: int = None
    __worklist: Worklist = None
    __items: List[ClientWorklistItem] = None
    __worklist_callback: str = None
    __worklist_callback_provider: WorklistCallbackProvider = None
    __worklist_update_listeners: Set[WorklistUpdateListener] = None
    __af_conf: Configuration = None
    __push_sse_client = None
    __value_lock: Lock = None

    def __init__(self, service_provider: ServiceProvider, configuration: Configuration):
        self.__items = []
        self.__worklist_update_listeners = set()
        self.__af_conf = configuration
        self.__value_lock = Lock()
        super().__init__(service_provider=service_provider)

    def create_worklist_update_configuration(self, push: bool) -> WorklistUpdateConfiguration:
        """Creates a default worklist update configuration
        :param bool push: If set to true, create a worklist update configuration for push notifications.
        """
        update_intervals: list[UpdateInterval] = []
        if push:
            update_intervals.append(UpdateInterval(0, 200))

        # worklistFilter: NO_TL or TL_ONLY
        # notify_only: if set to true, SSE push will send notifications instead of the updates themselves
        wuc = WorklistUpdateConfiguration(
            update_mode_threshold=0,
            update_intervals=update_intervals,
            worklist_filter="NO_TL",
            notify_only=False,
        )
        return wuc

    def get_worklist(self, worklist_callback: str = None, worklist_callback_provider: WorklistCallbackProvider = None,
                     skip_update: bool = False, skip_callback: bool = False) -> List[ClientWorklistItem]:
        """
        Updates and returns the worklist of the current user
        :param str worklist_callback: Optionally an URL implementing the callback endpoint for push updates
        :param WorklistCallbackProvider worklist_callback_provider: Optionally a callback for generating
            callback URLs for push updates
        :param bool skip_update: Skip the update if already connected but no callback options are enabled.
        """
        # use a lock to prevent concurrent initialization of the worklist
        with self.__value_lock:
            if self.__worklist is None:

                wum: WorklistUpdateManagerApi = self._service_provider.get_service(
                    WorklistUpdateManagerApi
                )
                update_conf: WorklistUpdateConfiguration = self.create_worklist_update_configuration(True)
                wlit: InitialIncClientWorklistData
                if self.fetch_count is not None:
                    wlit = wum.logon_and_create_client_worklist(body=update_conf, count=self.fetch_count)
                else:
                    wlit = wum.logon_and_create_client_worklist(body=update_conf)

                # currently no items in the worklist
                if wlit is None:
                    return self.__items

                self.__iterate(self.__items, wlit)

                # remember the current worklist meta data
                self.__worklist = Worklist(
                    wlit.worklist_id, wlit.revision, wlit.client_worklist_id, update_conf, wlit.agent
                )

                if not skip_callback:
                    self.enable_callback_updates(worklist_callback)

                return self.__items
        # /value_lock end

        # self.__worklist is not none here
        # simply return the items if push notifications are enabled
        if worklist_callback is not None or worklist_callback_provider is not None:
            # ensure the callback is registered
            self.enable_callback_updates(worklist_callback=worklist_callback,
                                         worklist_callback_provider=worklist_callback_provider)
            return self.__items
        # simply return the items if push notifications are enabled
        if self.__worklist_callback is not None or self.__worklist_callback_provider is not None:
            # ensure the callback is still registered
            self.enable_callback_updates(worklist_callback=self.__worklist_callback,
                                         worklist_callback_provider=self.__worklist_callback_provider)
            return self.__items
        if self.__push_sse_client:
            return self.__items
        # perform update
        if not skip_update:
            return self.update_worklist()
        else:
            return self.__items

    def force_worklist_reload(self) -> List[ClientWorklistItem]:
        """
        Forces the reworklist to be reloaded and registrations for push updates, if any, renewed.
        """
        if self.__worklist is None:
            return self.get_worklist()

        wum: WorklistUpdateManagerApi = self._service_provider.get_service(
            WorklistUpdateManagerApi
        )
        worklist_callback = self.__worklist_callback
        if not worklist_callback and self.__worklist_callback_provider:
            worklist_callback = self.__worklist_callback_provider()

        # if callback are enabled, de-register and re-register
        if worklist_callback:
            is_registered = wum.is_registered_for_updates(self.__worklist.worklist_id,
                                                          self.__worklist.client_worklist_id)
            if is_registered:
                wum.unregister_client_worklist_callback(worklist_id=self.__worklist.worklist_id,
                                                        client_worklist_id=self.__worklist.client_worklist_id)
            self._clear_worklist()
            # register again
            self.enable_callback_updates(worklist_callback=self.__worklist_callback,
                                         worklist_callback_provider=self.__worklist_callback_provider,
                                         client_worklist_id=self.__worklist.client_worklist_id)
        # if SSE is enabled, close the connection and re-enable
        elif self.__push_sse_client:
            self.__push_sse_client.close()
            self.__push_sse_client = None
            self._clear_worklist()
            self.pull_and_apply_worklist_updates()
            self.enable_push_updates()
        # no push mechanism: simply clear the worklist and re-fetch it
        else:
            self._clear_worklist()
            self.update_worklist()

    def _clear_worklist(self):
        """
        Clears the worklist, i.e. empties the items list and resets the revision information.
        """
        self.__items.clear()
        self.__worklist.revision.update_count = 0
        self.__worklist.revision.initialisation_date = 1

    def enable_callback_updates(self, worklist_callback: str = None,
                                worklist_callback_provider: WorklistCallbackProvider = None,
                                client_worklist_id: int = None):
        """
        Enable automatic worklist updates using SSE push notifications.
        """
        if worklist_callback is not None or worklist_callback_provider is not None:
            wum: WorklistUpdateManagerApi = self._service_provider.get_service(
                WorklistUpdateManagerApi
            )
            is_registered = wum.is_registered_for_updates(self.__worklist.worklist_id, self.__worklist.client_worklist_id)
            # print(f'Callback for {self.__worklist.worklist_id} registration status: {is_registered}')
            if not is_registered:
                if client_worklist_id is None:
                    client_worklist_id = self.__worklist.client_worklist_id
                callback_data = ClientWorklistRestCallbackData(
                    worklist_callback=worklist_callback if worklist_callback else worklist_callback_provider(self.__worklist),
                    sub_class="ClientWorklistRestCallbackData",
                    id=self.__worklist.worklist_id,
                    client_worklist_id=client_worklist_id,
                    agent=self.__worklist.agent,
                    revision=self.__worklist.revision,
                    wu_conf=self.__worklist.wu_conf,
                )
                wum.register_client_worklist_callback(callback_data)
                self.__worklist_callback = worklist_callback
                self.__worklist_callback_provider = worklist_callback_provider

    def enable_push_updates(self):
        """
        Enable automatic worklist updates using SSE push notifications.
        """
        if self.__push_sse_client is not None:
            return
        # ensure the worklist has been fetched once
        # NOTE: this does not help, if the worklist is empty (BPM-3581)
        if self.__worklist is None:
            self.get_worklist()
        if self.__worklist is None:
            warnings.warn(
                "The worklist could not be initialized, probably due to BPM-3581. SSE push will not work."
            )
        self._service_provider.thread_pool.submit(self._process_push_updates)

    def _process_push_updates(self):
        """
        Coroutine retrieving SSE push notifications for the worklist, handling registration and reconnects
        """
        while not self._disconnected:
            print("WorklistService establishing SSE connection...")
            try:
                sse_connection_id, sse_client = self._service_provider.connect_sse(
                    WorklistUpdateManagerApi
                )
                while True:
                    print("WorklistService SSE connection established, registering for worklist push...")
                    callback_data = ClientWorklistSseCallbackData(
                        sse_conn=sse_connection_id,
                        sub_class="ClientWorklistSseCallbackData",
                        id=self.__worklist.worklist_id,
                        client_worklist_id=self.__worklist.client_worklist_id,
                        agent=self.__worklist.agent,
                        revision=self.__worklist.revision,
                        wu_conf=self.__worklist.wu_conf,
                    )
                    wum: WorklistUpdateManagerApi = self._service_provider.get_service(
                        WorklistUpdateManagerApi
                    )
                    wum.register_client_worklist_sse(callback_data)
                    print("Worklist registered for SSE push")
                    self.__push_sse_client = sse_client
                    for event in sse_client:
                        if event.event == "SseConnectionEstablished":
                            # print('SSE session was re-established, re-registering..')
                            callback_data.sse_conn = event.data
                            callback_data.revision = self.__worklist.revision
                            wum.register_client_worklist_sse(callback_data)
                            # print("Worklist registered again for SSE push")
                        elif event.event == "client-worklist-update":
                            # print("Worklist update received")
                            try:
                                update_dict = json.loads(event.data)
                                update: WorklistUpdate = self._service_provider.deserialize(
                                    update_dict, WorklistUpdate
                                )
                                self.apply_worklist_update(update)
                            except Exception as e:
                                print("Couldn't deserialize and apply update: ", event, e)
                        else:
                            print(f"Unknown worklist SSE push event {event.event} received")
            except ConnectionError:
                # re-establish connection after some wait time
                # print("SSE disconnected...")
                sleep(self.__af_conf.sse_connect_retry_wait)
            except Exception as e:
                print("Unknown exception caught during SSE handling", e.__class__)
                traceback.print_exc()
                raise
            finally:
                self.__push_sse_client = None

    def add_update_listener(self, listener: WorklistUpdateListener):
        """
        Adds a listener which is called after a worklist update was received and applied.
        """
        self.__worklist_update_listeners.add(listener)

    def remove_update_listener(self, listener: WorklistUpdateListener):
        """
        Removes the given worklist update listener
        """
        self.__worklist_update_listeners.remove(listener)

    def _notify_worklist_update_listeners(self, updates: List[ClientWorklistItemUpdate]):
        """
        Notifies all registered worklist update listeners
        """
        for listener in self.__worklist_update_listeners:
            try:
                listener(updates)
            except Exception as e:
                print("Caught exception while notifying listener:", e)
                traceback.print_exc()

    def worklist_meta_data(self) -> Worklist:
        """
        Returns the worklist meta data, like ID, current revision etc., don't modify.
        """
        if self.__worklist is None:
            self.get_worklist()
        return self.__worklist

    def __iterate(
        self,
        items: List[ClientWorklistItem],
        inc: Union[InitialIncClientWorklistData, IncClientWorklistData],
    ):
        """Consumes an incremental client worklist until its iterator is used up
        @param items The items list to fill with the update(s)
        @param inc The first or next iteration to consume and append to items.
        """
        if inc is None:
            return
        # append the items
        if inc.items_flat:
            items += inc.items_flat
        else:
            return
        # iterator is used up
        if inc.dropped:
            return

        # fetch next
        inc_cl: IncClientWorklistsApi = self._service_provider.get_service(IncClientWorklistsApi)
        next_it: IncClientWorklistData = inc_cl.inc_client_wl_get_next(inc.inc_wl_id)
        self.__iterate(items, next_it)

    def update_worklist(self) -> List[ClientWorklistItem]:
        """Updates the user's worklist and returns the items"""
        if self.__worklist is None:
            return self.get_worklist()

        if self.__push_sse_client is not None \
                or self.__worklist_callback is not None\
                or self.__worklist_callback_provider is not None:
            return self.__items

        self.pull_and_apply_worklist_updates()

        return self.__items

    def pull_and_apply_worklist_updates(self):
        """
        Pulls worklist updates from the server and applies them to the worklist. Using this method while having
        push updates enabled via SSE or callback, may lead to an inconsistent state in the local list of items.
        """
        if self.__worklist is None:
            return self.get_worklist()
        wu: WorklistUpdateManagerApi = self._service_provider.get_service(WorklistUpdateManagerApi)
        inc_updts: InitialIncWorklistUpdateData = wu.get_worklist_updates(
            self.__worklist.worklist_id,
            body=self.__worklist.revision,
            filter=self.__worklist.wu_conf.worklist_filter,
        )

        if inc_updts is not None:
            updates: List[ClientWorklistItemUpdate] = []
            self.__iterate_updates(updates, inc_updts)
            self.__apply_worklist_updates(
                inc_updts.source_revision, inc_updts.target_revision, updates
            )
            self._notify_worklist_update_listeners(updates)

    # TODO define fitting return value
    def select_activity(
        self, item: WorklistItem #, signal_handler: SignalHandler = None
    ) -> bool:
        """
        Assigns the current user to the provided activity
        """
        asa: ActivityStartingApi = self._service_provider.get_service(
            ActivityStartingApi
        )
        
        ar: AfActivityReference = item.act_ref
        ebp_ir = EbpInstanceReference(
            ar.type,
            ar.instance_id,
            ar.instance_log_id,
            ar.base_template_id,
            ar.node_id,
            ar.node_iteration,
            ar.execution_manager_uris,
            ar.runtime_manager_uris,
        )

        asa.select_activity(body=ebp_ir)

        return True

    def __iterate_updates(
        self, updates: List[ClientWorklistItemUpdate], inc: IncWorklistUpdateData
    ):
        """Consumes the given worklist update iterator and appends all retrieved updates to the provided updates list."""
        if inc is None:
            return
        if inc.item_updates:
            updates += inc.item_updates
        else:
            return
        if inc.dropped:
            return

        # fetch next
        iwua: IncWorklistUpdateApi = self._service_provider.get_service(IncWorklistUpdateApi)
        next_it: IncWorklistUpdateData = iwua.inc_wl_updt_get_next(inc.inc_upd_id)
        self.__iterate_updates(updates, next_it)

    def apply_worklist_update(self, update: WorklistUpdate):
        """ Apply the provided worklist update to the worklist
        """
        self.__apply_worklist_updates(
            update.source_revision,
            update.target_revision,
            update.item_updates,
        )
        # call the listeners
        self._notify_worklist_update_listeners(update.item_updates)

    def __apply_worklist_updates(
        self,
        source_revision: WorklistRevision,
        target_revision: int,
        updates: List[ClientWorklistItemUpdate],
    ):
        """Applies the provided worklist updates to self.__items. Checks the consistency to the source revision,
        and performs a full update if the state does not fit. Sets the new target revision in self.__worklist.
        """
        if (
            self.__worklist.revision.update_count != source_revision.update_count
            or self.__worklist.revision.initialisation_date != source_revision.initialisation_date
        ):
            # out of order update, clear and re-fetch everything
            self.__items.clear()
            self.__worklist = None
            self.get_worklist()
            return

        # print(f'Applying {len(updates)} updates')
        # print(updates)

        for update in updates:
            self.__apply_worklist_update(update)

        # remember the update count for the next update
        self.__worklist.revision.update_count = target_revision

    def __apply_worklist_update(self, update: ClientWorklistItemUpdate):
        """Applies the given update to __items"""
        update_type = update.update_type
        item = update.item
        if update_type == "CHANGED":
            self.__replace_or_add_item(item)
        elif update_type == "ADDED":
            self.__items += [item]
        elif update_type == "REMOVED":
            self.__remove_item(item)
        elif update_type == "ADDED_OR_CHANGED":
            self.__replace_or_add_item(item)
        elif update_type == "REMOVED_OR_NOTHING":
            self.__remove_item(item)
        else:
            raise RuntimeError("Unknown update type: " + update_type)

    def __replace_or_add_item(self, item: ClientWorklistItem):
        """Replaces or adds the given worklist item in self.__items"""
        # print('__replace_or_add_item: __items=', self.__items)
        for i in range(len(self.__items)):
            val = self.__items[i]
            if item.id == val.id:
                self.__items[i] = item
                return
        # not found above, append it
        self.__items.append(item)

    def __remove_item(self, item: ClientWorklistItem):
        """Removes the given worklist item from self.__items"""
        for val in self.__items:
            if item.id == val.id:
                self.__items.remove(val)
                return

    def find_item_by_id(self, item_id: str) -> ClientWorklistItem:
        """Finds a worklist item by its worklist item id. Returns none, if not in the worklist of the user."""
        # print(f'Finding item with id {item_id}')
        self.get_worklist()
        # print(self.__items)
        for item in self.__items:
            if item.id == item_id:
                # print('Found')
                return item
        return None

    def find_item_by_ref(self, ebp_ir: EbpInstanceReference) -> ClientWorklistItem:
        """
        Finds a worklist item by its activity's EBP Instance Reference.
        Returns none, if not in the worklist of the user.
        """
        self.get_worklist()
        for item in self.__items:
            ar: AfActivityReference = item.act_ref
            if ar.instance_id == ebp_ir.instance_id\
                    and ar.instance_log_id == ebp_ir.instance_log_id\
                    and ar.node_id == ebp_ir.node_id\
                    and ar.node_iteration == ebp_ir.node_iteration:
                return item
        return None


    def update_worklist_item(self, item: ClientWorklistItem):
        wum: WorklistUpdateManagerApi = self._service_provider.get_service(
            WorklistUpdateManagerApi
        )
        wum.update_individual_settings(item)

    def disconnect(self):
        AbstractService.disconnect(self)
        # close the SSE connection if any
        if self.__push_sse_client:
            self.__push_sse_client.close()
