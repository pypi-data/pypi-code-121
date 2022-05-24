# -*- coding: utf-8 -*-
# Default Python Libraries
import asyncio
import json
import traceback
from asyncio import sleep
from typing import List, Optional, Set, Union

# AristaFlow REST Libraries
import sseclient
from af_execution_manager import InstanceCreationSseData, InstanceStateData
from af_execution_manager.api.instance_control_api import InstanceControlApi
from af_execution_manager.api.templ_ref_remote_iterator_rest_api import (
    TemplRefRemoteIteratorRestApi,
)
from af_execution_manager.models.data_container import DataContainer
from af_execution_manager.models.instance_creation_data import InstanceCreationData
from af_execution_manager.models.instance_creation_rest_data import InstanceCreationRestData
from af_execution_manager.models.parameter_value import ParameterValue
from af_execution_manager.models.templ_ref_initial_remote_iterator_data import (
    TemplRefInitialRemoteIteratorData,
)
from af_execution_manager.models.templ_ref_remote_iterator_data import TemplRefRemoteIteratorData
from af_execution_manager.models.template_reference import TemplateReference
from af_process_manager.api.instance_manager_api import InstanceManagerApi
from af_process_manager.models.instance_reference import InstanceReference
from aristaflow.abstract_service import AbstractService
from aristaflow.configuration import Configuration
from aristaflow.service_provider import ServiceProvider
from aristaflow.utils import VERSION


def __instance_state_listener(instance_state: InstanceStateData):
    pass


InstanceStateListener = type(__instance_state_listener)
""" Type for callback listeners"""


class ProcessService(AbstractService):
    """Process related methods"""

    __instance_state_listeners: Set[InstanceStateListener] = None
    __push_sse_client: sseclient.SSEClient = None
    _sse_id: str = None
    __af_conf: Configuration = None

    def __init__(self, service_provider: ServiceProvider, configuration: Configuration):
        self.__instance_state_listeners = set()
        self.__af_conf = configuration
        super().__init__(service_provider=service_provider)

    def __tpl_version_key(self, tpl: TemplateReference) -> int:
        return VERSION.key(tpl.version)

    def get_instantiable_template_by_type(self, process_type: str) -> Optional[TemplateReference]:
        """Finds the first instantiable template of the given process Type"""
        tpls = self.get_instantiable_templates()
        tpls_of_type = []
        for tpl in tpls:
            if tpl.process_type == process_type:
                tpls_of_type += [tpl]
        # empty result

        if len(tpls_of_type) == 0:
            return None
        # reverse sort by version
        tpls_of_type = sorted(tpls_of_type, key=self.__tpl_version_key, reverse=True)
        # return first entry
        return tpls_of_type[0]

    def get_instantiable_templates(self) -> List[TemplateReference]:
        """Retrieves the instantiable templates from the server
        :return: List[TemplateReference] The instantiable templates for the current user
        """
        ic: InstanceControlApi = self._service_provider.get_service(InstanceControlApi)
        initial: TemplRefInitialRemoteIteratorData = ic.get_instantiable_templ_refs()
        tpls: List[TemplateReference] = []
        self.__iterate(tpls, initial)
        return tpls

    def __iterate(
        self,
        tpls: List[TemplateReference],
        inc: Union[TemplRefInitialRemoteIteratorData, TemplRefRemoteIteratorData],
    ):
        """Consumes an template reference remote iterator until it is used up
        @param tpls The tpls list to fill with the template references
        @param inc The first or next iteration to consume and append to tpls.
        """
        if inc is None:
            return
        # append the tpls
        if inc.templ_refs:
            tpls += inc.templ_refs
        else:
            return
        # iterator is used up
        if inc.dropped:
            return

        # fetch next
        tref_rest: TemplRefRemoteIteratorRestApi = self._service_provider.get_service(
            TemplRefRemoteIteratorRestApi
        )
        next_it: TemplRefRemoteIteratorData = tref_rest.templ_ref_get_next(inc.iterator_id)
        self.__iterate(tpls, next_it)

    def start_by_type(
        self, process_type: str, callback_uri: str = None, input_data: dict = None
    ) -> str:
        """Starts the newest version of the given process type, returns the logical ID of the started instance."""
        tpl = self.get_instantiable_template_by_type(process_type)
        if tpl is None:
            raise Exception("Unknown process type: " + process_type)
        return self.start_by_id(tpl.id, callback_uri, input_data)

    def start_by_id(
        self, template_id: str, callback_uri: str = None, input_data: dict = None
    ) -> str:
        """Starts a process given by the template id. Returns the logical ID of the started instance.
        If an InstanceStateListener is registered, instance state changes (and autostart pending events) are
        listened to using SSE. In that case, no callback_uri can be used.
        """
        ic: InstanceControlApi = self._service_provider.get_service(InstanceControlApi)
        if callback_uri is not None and self._sse_id is not None:
            raise Exception("Can not use Callbacks and SSE listener at the same time")
        elif self._sse_id is not None:
            inst_creation_data = InstanceCreationSseData(
                sub_class="InstanceCreationSseData", sse_conn=self._sse_id
            )
            inst_creation_data.dc = self.__create_instance_container(ic, template_id, input_data)
            return ic.create_and_start_instance_sse(templ_id=template_id, body=inst_creation_data)
        elif callback_uri is not None:
            inst_creation_data = InstanceCreationRestData(
                sub_class="InstanceCreationRestData", notification_callback=callback_uri
            )
            inst_creation_data.dc = self.__create_instance_container(ic, template_id, input_data)
            return ic.create_and_start_instance_callback(
                body=inst_creation_data, templ_id=template_id
            )
        else:
            # no callback url, no SSE
            inst_creation_data = InstanceCreationData(sub_class="InstanceCreationData")
            inst_creation_data.dc = self.__create_instance_container(ic, template_id, input_data)
            return ic.create_and_start_instance(template_id, body=inst_creation_data)

    def __create_instance_container(
        self, ic: InstanceControlApi, template_id: str, input_data: dict
    ) -> DataContainer:
        """Creates an instance data container for the given template, if required"""
        idc = None
        if input_data is not None and len(input_data) != 0:
            idc = ic.create_instance_data_container(template_id)
            pv: ParameterValue
            for pv in idc.values:
                if pv.name in input_data:
                    value = input_data[pv.name]
                    pv.value = value
        return idc

    def _enable_sse_instance_state_notification(self):
        """
        Enable propagation of instance state changes using SSE push notifications.
        """
        if self.__push_sse_client is not None:
            return
        # print("ProcessService: Enabling SSE")
        self._service_provider.thread_pool.submit(self._process_push_instance_state_changes)

        # Default Python Libraries
        import time

        # wait and check for sse_id to be set
        i = 0
        while i < 20 and self._sse_id is None:
            time.sleep(0.1)
            i = i + 1
        # print(f"SSE available after {i/10} seconds  ID is {self._sse_id}")

    def _process_push_instance_state_changes(self):
        """
        Coroutine retrieving SSE push notifications instance state changes
        """
        # print(f'ProcessService starting push update processing')
        while not self._disconnected:
            # print("Establishing SSE connection...")
            try:
                sse_connection_id, sse_client = self._service_provider.connect_sse(
                    InstanceControlApi
                )
                self._sse_id = sse_connection_id
                # print(f'ProcessService: SSE connection establised, id {self._sse_id}')
                while True:
                    self.__push_sse_client = sse_client
                    for event in sse_client:
                        if event.event == "SseConnectionEstablished":
                            print("ProcessService SSE session was re-established.")
                            self._sse_id = event.data
                            # callback_data.sse_conn = event.data
                        else:
                            # print("Instance state data received")
                            try:
                                instance_state_dict = json.loads(event.data)
                                instance_state: InstanceStateData = (
                                    self._service_provider.deserialize(
                                        instance_state_dict, InstanceStateData
                                    )
                                )
                                # call the listeners
                                self._notify_instance_state_listeners(instance_state)
                            except Exception as e:
                                print("Couldn't deserialize and apply update: ", event, e)
            #                        else:
            #                            print(f"Unknown worklist SSE push event {event.event} received")
            except ConnectionError:
                # re-establish connection after some wait time
                print("ProcessService SSE disconnected...")
                sleep(self.__af_conf.sse_connect_retry_wait)
            except Exception as e:
                print("Unknown exception caught during SSE handling", e.__class__)
                raise
            finally:
                print("ProcessService: SSE disconnected")
                self.__push_sse_client = None
                self._sse_id = None

    def add_instance_state_listener(self, listener: InstanceStateListener):
        """
        Adds a listener which is called whenever an instance state change event occurs. This only applies for instances
        started by this service and enables SSE.
        """
        self._enable_sse_instance_state_notification()
        self.__instance_state_listeners.add(listener)

    def remove_instance_state_listener(self, listener: InstanceStateListener):
        """
        Removes the given instance state listener
        """
        self.__instance_state_listeners.remove(listener)

    def _notify_instance_state_listeners(self, instance_state: InstanceStateData):
        """
        Notifies all registered instance state listeners
        """
        for listener in self.__instance_state_listeners:
            try:
                listener(instance_state)
            except Exception as e:
                print("Caught exception while notifying listener:", e)
                traceback.print_exc()

    def get_instance_ref(self, inst_id: str) -> InstanceReference:
        """
        Finds the instance reference for the given instance ID (logical or log ID)
        """
        im: InstanceManagerApi = self._service_provider.get_service(InstanceManagerApi)
        try:
            return im.get_instance_refs(body=[inst_id]).inst_refs[0]
        except Exception:
            logicl_id = im.get_logical_instance_ids(body=[inst_id]).inst_ids[0]
            return im.get_instance_refs(body=[logicl_id]).inst_refs[0]

    def disconnect(self):
        AbstractService.disconnect(self)
        # close the SSE connection if any
        if self.__push_sse_client:
            self.__push_sse_client.close()
