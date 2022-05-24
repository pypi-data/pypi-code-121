# -*- coding: utf-8 -*-
# Default Python Libraries
import asyncio
import json
import threading
import traceback
from asyncio import sleep
from threading import Lock
from typing import Dict

# AristaFlow REST Libraries
import sseclient
from af_runtime_service import (
    ActivitySseCallbackData,
    EbpInstanceReference,
    ExecutionMessage,
    RemoteActivityStartingApi,
    RemoteRuntimeEnvironmentApi,
    SimpleSessionContext, ActivityRestCallbackData,
)
from af_runtime_service.rest import ApiException
from af_worklist_manager import AfActivityReference, WorklistItem
from aristaflow.abstract_service import AbstractService
from aristaflow.activity_context import ActivityContext
from aristaflow.service_provider import ServiceProvider


class SignalHandler(object):
    """
    Default signal handler, extend this class for customizations
    """

    _ac: ActivityContext = None

    @property
    def ac(self) -> ActivityContext:
        return self._ac

    @ac.setter
    def ac(self, ac: ActivityContext):
        self._ac = ac

    def signal(self, msg: ExecutionMessage) -> bool:
        """
        The given execution message has arrived for this activity
        :param ExecutionMessage msg: The execution message
        :return bool: True, for acknowledging the signal (default).
        """
        return True


class ActivityService(AbstractService):
    """
    Helper methods for executing activities
    """

    __push_sse_client: sseclient.SSEClient = None
    __push_sse_connection_id: str = None
    __signal_handlers: Dict[str, SignalHandler] = None
    __value_lock: Lock = None

    def __init__(self, service_provider: ServiceProvider):
        AbstractService.__init__(self, service_provider)
        self.__signal_handlers = {}
        self.__value_lock = threading.Lock()

    def start_sse(
        self, item: WorklistItem, signal_handler: SignalHandler = None
    ) -> ActivityContext:
        return self.start(item=item, signal_handler=signal_handler)

    def get_ebp_ir(self, item: WorklistItem) -> EbpInstanceReference:
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
        return ebp_ir

    def start(
        self, item: WorklistItem, signal_handler: SignalHandler = None, callback_url:str = None
    ) -> ActivityContext:
        if signal_handler is None:
            signal_handler = SignalHandler()

        ebp_ir = self.get_ebp_ir(item)

        # start the activity using REST
        ras: RemoteActivityStartingApi = self._service_provider.get_service(
            RemoteActivityStartingApi
        )

        if callback_url is not None:
            callback_data: ActivityRestCallbackData = ActivityRestCallbackData(
                sub_class="ActivityRestCallbackData",
                notification_callback=callback_url,
                activity=ebp_ir,
            )
        else:
            # ensure SSE event loop is started
            self._register_sse()
            callback_data: ActivitySseCallbackData = ActivitySseCallbackData(
                sse_conn=self.__push_sse_connection_id,
                sub_class="ActivitySseCallbackData",
                activity=ebp_ir,
            )

        # check state and handle start/resume
        ssc: SimpleSessionContext
        ac = ActivityContext()
        resume = item.state in ["ENQUIRED", "SUSPENDED"]
        with self.__value_lock:
            try:
                if resume:
                    if callback_url is not None:
                        ssc = ras.resume_activity_callback(body=callback_data)
                    else:
                        ssc = ras.resume_activity_sse(body=callback_data)
                else:
                    if callback_url is not None:
                        ssc = ras.start_activity_callback(body=callback_data)
                    else:
                        ssc = ras.start_activity_sse(body=callback_data)
            except ApiException as e:
                if e.body:
                    e_dict = json.loads(e.body)
                    if e_dict["subClass"] == "InvalidActivityStateException":
                        # state seems to have changed in the meantime
                        # try resume instead of start or vice versa
                        resume = not resume
                        if resume:
                            if callback_url is not None:
                                ssc = ras.resume_activity_callback(body=callback_data)
                            else:
                                ssc = ras.resume_activity_sse(body=callback_data)
                        else:
                            if callback_url is not None:
                                ssc = ras.start_activity_callback(body=callback_data)
                            else:
                                ssc = ras.start_activity_sse(body=callback_data)
                    else:
                        raise
                else:
                    raise
            token = self.__get_security_token(ras)
            ac.token = token
        ac.ssc = ssc
        signal_handler.ac = ac
        self.__signal_handlers[ssc.session_id] = signal_handler
        return ac

    def __get_security_token(self, service) -> str:
        """Reads the security token used by the given service"""
        return service.api_client.default_headers["x-AF-Session-ID"]

    def __set_security_token(self, service, token: str):
        """Sets the security token to be used by the given service"""
        service.api_client.default_headers["x-AF-Session-ID"] = token

    def activity_closed(self, ac: ActivityContext):
        rre: RemoteRuntimeEnvironmentApi = self._service_provider.get_service(
            RemoteRuntimeEnvironmentApi
        )
        with self.__value_lock:
            self.__set_security_token(rre, ac.token)
            rre.application_closed(session_id=ac.session_id, body=ac.ssc.data_context)

        self._drop_signal_handler(ac)

    def activity_reset(self, ac: ActivityContext, force_reset: bool = False):
        """Resets the activity or suspends it if it was resumed. If force reset is set to True, the activity will
        be reset also if it was resumed before.
        """
        rre: RemoteRuntimeEnvironmentApi = self._service_provider.get_service(
            RemoteRuntimeEnvironmentApi
        )
        # handle reset to save point if it was resumed
        with self.__value_lock:
            self.__set_security_token(rre, ac.token)
            if not force_reset and ac.ssc.resumed:
                rre.application_reset_to_previous_savepoint(
                    session_id=ac.session_id, body=ac.ssc.data_context
                )
            else:
                rre.application_reset(session_id=ac.session_id, body=ac.ssc.data_context)
        self._drop_signal_handler(ac)

    def set_savepoint(
        self, ac: ActivityContext, flush=True, state: str = None, savepoint_id="savepoint"
    ):
        rre: RemoteRuntimeEnvironmentApi = self._service_provider.get_service(
            RemoteRuntimeEnvironmentApi
        )
        with self.__value_lock:
            self.__set_security_token(rre, ac.token)
            if state is not None:
                rre.set_application_state(session_id=ac.session_id, body=state)
            rre.set_savepoint(
                savepoint_id=savepoint_id,
                session_id=ac.session_id,
                flush=flush,
                body=ac.ssc.data_context,
            )

    def activity_suspended(self, ac: ActivityContext):
        rre: RemoteRuntimeEnvironmentApi = self._service_provider.get_service(
            RemoteRuntimeEnvironmentApi
        )
        with self.__value_lock:
            self.__set_security_token(rre, ac.token)
            rre.application_suspended(ac.session_id, body=ac.ssc.data_context)
        self._drop_signal_handler(ac)

    def activity_failed(
        self, ac: ActivityContext, error_code=1000000, state="Failed", msg="Failed"
    ):
        rre: RemoteRuntimeEnvironmentApi = self._service_provider.get_service(
            RemoteRuntimeEnvironmentApi
        )
        with self.__value_lock:
            self.__set_security_token(rre, ac.token)
            rre.application_failed(
                error_code=error_code,
                session_id=ac.session_id,
                body=ac.ssc.data_context,
                state=state,
                msg=msg,
            )
        self._drop_signal_handler(ac)

    def get_ssc(
        self, item: WorklistItem, signal_handler: SignalHandler = None
    ) -> ActivityContext:
        # TODO add signal handler code
        # I don't know how/why
        ras: RemoteActivityStartingApi = self._service_provider.get_service(
            RemoteActivityStartingApi
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

        ssc: SimpleSessionContext
        ac = ActivityContext()

        # TODO missing error handling if activity
        # is in illegal state for operaton 
        ssc = ras.get_simple_session_context(body=ebp_ir)

        ac.ssc = ssc
        return ac

    def _drop_signal_handler(self, ac: ActivityContext):
        """
        Drops the signal handler for the given session
        """
        if ac.ssc.session_id in self.__signal_handlers:
            del self.__signal_handlers[ac.ssc.session_id]

    def _register_sse(self):
        """
        Registers at the runtime service' SSE endpoint and starts the event handling loop.
        """
        if self.__push_sse_client is not None:
            return
        print('ActivityService initial SSE connection')
        self.__push_sse_connection_id, self.__push_sse_client = self._service_provider.connect_sse(
            RemoteActivityStartingApi
        )
        print(f'ActivityService SSE connection ready, got id {self.__push_sse_connection_id}')
        self._service_provider.thread_pool.submit(self._process_push_updates)

    def _process_push_updates(self):
        """
        Coroutine retrieving SSE push notifications for the activities, handling registration and reconnects
        """
        print('ActivityService starting push update processing')
        while not self._disconnected:
            try:
                if self.__push_sse_client is None:
                    print("ActivityService Establishing SSE connection...")
                    (
                        self.__push_sse_connection_id,
                        self.__push_sse_client,
                    ) = self._service_provider.connect_sse(RemoteActivityStartingApi)
                print(f"ActivityService SSE connection established, id is {self.__push_sse_connection_id}")
                while True:
                    for event in self.__push_sse_client:
                        # print(f"ActivityService Event {event.event} received: {event.data}")
                        if event.event == "SseConnectionEstablished":
                            # print('SSE session was re-established, re-registering..')
                            self.__push_sse_connection_id = event.data
                            # TODO notify activities / lack of re-registration possibility?
                            print("ActivityService Runtime SSE connection was re-established!!!")
                        elif event.event == "execution-message":
                            # print("Worklist update received")
                            try:
                                data_dict = json.loads(event.data)
                                data: ExecutionMessage = self._service_provider.deserialize(
                                    data_dict, ExecutionMessage
                                )
                                # call the listeners
                                if data.session_id in self.__signal_handlers:
                                    try:
                                        signal_handler = self.__signal_handlers[data.session_id]
                                        signal_handler.signal(data)
                                    except Exception as e:
                                        print(
                                            f"Caught an exception signalling activity {data.session_id}, {e}"
                                        )
                                        traceback.print_exc()
                                # self._notify_worklist_update_listeners(data)
                            except Exception as e:
                                print("ActivityService couldn't deserialize and apply sse event: ", event, e)
                        else:
                            print(f"ActivityService Unknown worklist SSE push event {event.event} received")
                    pass
            except ConnectionError:
                # re-establish connection after some wait time
                # print("SSE disconnected...")
                sleep(self.__af_conf.sse_connect_retry_wait)
            except Exception as e:
                print("Unknown exception caught during SSE handling", e.__class__)
                raise
            finally:
                self.__push_sse_client = None

    def disconnect(self):
        AbstractService.disconnect(self)
        # close the SSE connection
        for _, signal_handler in self.__signal_handlers:
            # TODO implement some "suspend if resumed" logic and only suspend if formerly resumed
            self.activity_suspended(signal_handler.ac)
        # close the SSE connection if any
        if self.__push_sse_client:
            self.__push_sse_client.close()
