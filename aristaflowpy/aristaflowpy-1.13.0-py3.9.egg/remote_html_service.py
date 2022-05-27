import asyncio
import json
import threading
import traceback
from asyncio import sleep

import sseclient
from af_remote_html_runtime_manager import SynchronousActivityStartingApi, ActivityExecData, ActivitySseCallbackData
from af_worklist_manager import AfActivityReference, WorklistItem

from .service_provider import ServiceProvider
from .abstract_service import AbstractService

from af_remote_html_runtime_manager.api.runtime_manager_api import RuntimeManagerApi
from af_remote_html_runtime_manager.models.activity_rest_callback_data import (
    ActivityRestCallbackData,
)
from af_remote_html_runtime_manager.models.ebp_instance_reference import EbpInstanceReference
from af_remote_html_runtime_manager.models.gui_context import GuiContext
from .html_gui_context import HtmlGuiContext


class HtmlSignalHandler(object):
    """
    Default signal handler, extend this class for customizations
    """

    _gui_context: HtmlGuiContext = None

    @property
    def gui_context(self) -> HtmlGuiContext:
        return self._gui_context

    @gui_context.setter
    def gui_context(self, gui_context: HtmlGuiContext):
        self._gui_context = gui_context

    def signal(self, activity_signal: str, msg: ActivityExecData):
        """
        To be overridden by sub classes
        The activity has terminated with the given signal which is one of:
        activity-closed
        activity-suspended
        activity-timed-suspended
        activity-resumed
        activity-reset
        activity-signalled
        activity-failed
        :param str activity_signal: The signal
        :param ActivityExecData msg: The execution message
        :return bool: True, for acknowledging the signal (default).
        """


class RemoteHtmlService(AbstractService):
    """
    Helper methods for starting activities via RemoteHTMLRuntimeManager
    """
    __push_sse_client : sseclient.SSEClient = None
    __push_sse_connection_id: str = None
    __value_lock: threading.Lock = None

    def __init__(self, service_provider: ServiceProvider):
        AbstractService.__init__(self, service_provider)
        self.__signal_handlers = {}
        self.__value_lock = threading.Lock()

    @staticmethod
    def is_html_activity(item: WorklistItem) -> bool:
        """
        Returns true, if the given worklist item can be executed as Remote HTML activity
        """
        return (
            item.act_ref.gui_context_id == "HTMLContext"
            or item.act_ref.executable_component_name == "de.aristaflow.form.Form"
            or item.act_ref.executable_component_name == "de.aristaflow.form.GeneratedForm"
        )

    def start_html_activity(self, item: WorklistItem, callback_url: str = None,
                            signal_handler: HtmlSignalHandler = None):
        """
        Starts the given HTML GUI worklist item using the Remote HTML Runtime Manager
        :param WorklistItem item: The worklist item to be started
        :param str callback_url: Use this and the URL will be called on activity signals
        :param HtmlSignalHandler signal_handler: Use this to receive signals via SSE connection
        """
        if item is None:
            raise Exception("No worklist item provided")
        # accept user form and HTMLContext based activities
        if not (self.is_html_activity(item)):
            raise Exception(f"Not an HTML activity: {item.act_ref.gui_context_id}")
        if item.state == "STARTED":
            raise Exception("Item is already started")
        sas = self.get_html_activity_starting()
        gc: GuiContext
        ar: AfActivityReference = item.act_ref
        # print('Starting activity...')
        ebp_ir: EbpInstanceReference = EbpInstanceReference(
            ar.type,
            ar.instance_id,
            ar.instance_log_id,
            ar.base_template_id,
            ar.node_id,
            ar.node_iteration,
            ar.execution_manager_uris,
            ar.runtime_manager_uris,
        )
        # "AVAILABLE", "ASSIGNED", "STARTED", "SUSPENDED", "ENQUIRED"
        if item.state == "AVAILABLE" or item.state == "ASSIGNED":
            if callback_url is not None:
                cb_data = ActivityRestCallbackData(
                    sub_class="ActivityRestCallbackData",
                    notification_callback=callback_url,
                    activity=ebp_ir,
                )
                gc = sas.start_activity_callback(body=cb_data)
            elif signal_handler is not None:
                # ensure SSE connection
                self._register_sse()
                sse_data = ActivitySseCallbackData(
                    sub_class="ActivitySseCallbackData",
                    sse_conn=self.__push_sse_connection_id,
                    activity=ebp_ir,
                )
                gc = sas.start_activity_sse(body=sse_data)
            else:
                gc = sas.start_activity(body=ebp_ir)
        else:
            if callback_url is not None:
                cb_data = ActivityRestCallbackData(
                    sub_class="ActivityRestCallbackData",
                    notification_callback=callback_url,
                    activity=ebp_ir,
                )
                gc = sas.resume_activity_callback(body=cb_data)
            elif signal_handler is not None:
                # ensure SSE connection
                self._register_sse()
                sse_data = ActivitySseCallbackData(
                    sub_class="ActivitySseCallbackData",
                    sse_conn=self.__push_sse_connection_id,
                    activity=ebp_ir,
                )
                gc = sas.resume_activity_sse(body=sse_data)
            else:
                gc = sas.resume_activity(body=ebp_ir)
        hgc = HtmlGuiContext(gc)
        if signal_handler is not None:
            signal_handler.gui_context = hgc
            self.__signal_handlers[gc.session_id] = signal_handler
        return hgc

    def get_html_activity_starting(self) -> SynchronousActivityStartingApi:
        """
        Returns the Remote HTML Runtime Manager Synchronous Activity Starting, ensuring logon to the Runtime Manager
        """
        sas: SynchronousActivityStartingApi = self._service_provider.get_service(SynchronousActivityStartingApi)
        rm: RuntimeManagerApi = self._service_provider.get_service(RuntimeManagerApi)
        # always logon again, since the server might have been restarted in the meantime
        rm.logon(body=self._service_provider.csd)
        return sas

    def _register_sse(self):
        """
        Registers at the runtime service' SSE endpoint and starts the event handling loop.
        """
        if self.__push_sse_client is not None:
            return
        print('RemoteHtmlService register SSE')
        self.__push_sse_connection_id, self.__push_sse_client = self._service_provider.connect_sse(
            SynchronousActivityStartingApi
        )
        print('RemoteHtmlService register SSE, got id ' + self.__push_sse_connection_id)
        self._service_provider.thread_pool.submit(self._process_push_updates)

    def _process_push_updates(self):
        print('RemoteHtmlService starting push update processing')
        """
        Coroutine retrieving SSE push notifications for the activities, handling registration and reconnects
        """
        while not self._disconnected:
            try:
                if self.__push_sse_client is None:
                    print("Establishing SSE connection...")
                    (
                        self.__push_sse_connection_id,
                        self.__push_sse_client,
                    ) = self._service_provider.connect_sse(SynchronousActivityStartingApi)
                print(f"RemoteHtmlService SSE connection established, id is {self.__push_sse_connection_id}")
                while True:
                    for event in self.__push_sse_client:
                        print(f"Event {event.event} received: {event.data}")
                        activity_signal: str = None
                        if event.event == 'SseConnectionEstablished':
                            # print('SSE session was re-established, re-registering..')
                            self.__push_sse_connection_id = event.data
                            # TODO notify waiters / lack of re-registration possibility?
                            print("Runtime SSE connection was re-established!!!")
                        elif event.event == 'activity-closed':
                            activity_signal = 'activity-closed'
                        elif event.event == 'activity-suspended':
                            activity_signal = 'activity-suspended'
                        elif event.event == 'activity-timed-suspended':
                            activity_signal = 'activity-timed-suspended'
                        elif event.event == 'activity-resumed':
                            activity_signal = 'activity-resumed'
                        elif event.event == 'activity-reset':
                            activity_signal = 'activity-reset'
                        elif event.event == 'activity-signalled':
                            activity_signal = 'activity-signalled'
                        elif event.event == 'activity-failed':
                            activity_signal = 'activity-failed'
                        else:
                            print(f"Unknown worklist SSE push event {event.event} received")

                        if activity_signal is not None:
                            print("Remote HTML activity signal received")
                            try:
                                data_dict = json.loads(event.data)
                                data: ActivityExecData = self._service_provider.deserialize(
                                    data_dict, ActivityExecData
                                )
                                # call the listeners
                                if data.session_id in self.__signal_handlers:
                                    try:
                                        signal_handler = self.__signal_handlers[data.session_id]
                                        signal_handler.signal(activity_signal, data)
                                    except Exception as e:
                                        print(
                                            f"Caught an exception signalling activity {data.session_id}, {e}"
                                        )
                                        traceback.print_exc()
                                # self._notify_worklist_update_listeners(data)
                            except Exception as e:
                                print("Couldn't deserialize and apply update: ", event, e)
                    pass
            except ConnectionError:
                # re-establish connection after some wait time
                print("SSE disconnected...")
                sleep(self.__af_conf.sse_connect_retry_wait)
            except Exception as e:
                print("Unknown exception caught during SSE handling", e.__class__)
                raise
            finally:
                self.__push_sse_client = None

    def disconnect(self):
        AbstractService.disconnect(self)
        # close the SSE connection if any
        if self.__push_sse_client:
            self.__push_sse_client.close()
