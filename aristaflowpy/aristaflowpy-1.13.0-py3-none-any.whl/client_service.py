# Default Python Libraries
import base64
from typing import Dict, List, Type, TypeVar

# AristaFlow REST Libraries
import af_execution_manager
from af_execution_manager.api.activity_execution_control_api import ActivityExecutionControlApi
from af_org_model_manager.api.global_security_manager_api import GlobalSecurityManagerApi
from af_org_model_manager.models.auth_data_app_name import AuthDataAppName
from af_org_model_manager.models.auth_data_arbitrary import AuthDataArbitrary
from af_org_model_manager.models.auth_data_org_pos import AuthDataOrgPos
from af_org_model_manager.models.auth_data_password import AuthDataPassword
from af_org_model_manager.models.auth_data_user_name import AuthDataUserName
from af_org_model_manager.models.authentication_data import AuthenticationData
from af_org_model_manager.models.client_session_details import ClientSessionDetails
from af_org_model_manager.models.qualified_agent import QualifiedAgent
from af_remote_html_runtime_manager.api.synchronous_activity_starting_api import (
    SynchronousActivityStartingApi,
)
from af_worklist_manager.models.af_activity_reference import AfActivityReference
from af_worklist_manager.models.worklist_item import WorklistItem
from af_runtime_service import SimpleSessionContext
from aristaflow.absence_service import AbsenceService
from aristaflow.delegation_service import DelegationService
from aristaflow.execution_history_service import ExecutionHistoryService
from aristaflow.image_renderer_service import ImageRendererService
from aristaflow.org_model_service import OrgModelService
from aristaflow.process_service import ProcessService
from aristaflow.service_provider import ServiceProvider
from aristaflow.activity_context import ActivityContext
from .abstract_service import AbstractService

from .activity_service import ActivityService
from .configuration import Configuration
from .remote_html_service import RemoteHtmlService, HtmlSignalHandler
from .worklist_service import WorklistService


T = TypeVar("T")
D = TypeVar("D")


class AristaFlowClientService(object):
    """Client Services for accessing the AristaFlow BPM platform"""

    # the user session id this client service belongs to
    __user_session: str = None
    # authentication
    __csd: ClientSessionDetails = None
    # the AristaFlow configuration
    __af_conf: Configuration = None
    __service_provider: ServiceProvider = None
    __worklist_service: WorklistService = None
    __process_service: ProcessService = None
    __delegation_service: DelegationService = None
    __absence_service: AbsenceService = None
    __execution_history_service: ExecutionHistoryService = None
    __image_renderer_service: ImageRendererService = None
    __org_model_service: OrgModelService = None
    __activity_service: ActivityService = None
    __remote_html_service: RemoteHtmlService = None
    __all_services: List[AbstractService] = []

    def __init__(
        self, configuration: Configuration, user_session: str, service_provider: ServiceProvider
    ):
        self.__af_conf = configuration
        self.__user_session = user_session
        self.__service_provider = service_provider

    def get_service(self, service_type: Type[T]) -> T:
        """
        Returns a service instance for the given service type, e.g.
        get_service(InstanceControlApi)
        @param service_type The class of the requested service.
        """
        return self.__service_provider.get_service(service_type)

    @property
    def client_session_details(self) -> ClientSessionDetails:
        """Returns the client session details of this service
        :return: The client session details of this service
        """
        return self.__csd

    @property
    def is_authenticated(self) -> bool:
        """Returns true, if this client service is already authenticated"""
        return self.__csd is not None

    def authenticate(self, username: str, password: str = None, org_pos_id: int = None):
        if self.__csd is not None:
            raise Exception("Already authenticated")

        auth_data: List[AuthenticationData] = [
            AuthDataUserName(username, sub_class="AuthDataUserName")
        ]
        if org_pos_id is not None:
            auth_data.append(AuthDataOrgPos(org_pos_id, sub_class="AuthDataOrgPos"))
        psk = self.__af_conf.pre_shared_key
        method: str
        # if a password was provided, use it
        if password:
            auth_data.append(AuthDataPassword(password=password, sub_class="AuthDataPassword"))
            method = "UTF-8_PASSWORD"
        # if PSK is configured, use that
        elif psk:
            # get the utf-8 bytes, encode them using base 64 and decode the resulting bytes using ASCII
            psk_encoded = base64.b64encode(bytes(psk, "UTF-8")).decode("ascii")
            auth_data.append(AuthDataArbitrary(data=psk_encoded, sub_class="AuthDataArbitrary"))
            method = "SHARED_UTF-8_KEY"
        else:
            raise Exception("No authentication method left")

        gsm: GlobalSecurityManagerApi = self.get_service(GlobalSecurityManagerApi)

        # use a provided application name
        if self.__af_conf.application_name:
            if org_pos_id is None:
                # if an application name is provided, an org position ID must be used as well
                # get the org positions
                agents: List[QualifiedAgent] = gsm.pre_authenticate_method(method, body=auth_data)
                agent: QualifiedAgent
                # pick the single org position
                if len(agents) == 1:
                    agent = agents[0]
                # none: can't login
                elif len(agents) == 0:
                    raise Exception(
                        f"User does not have an org position {username} (supplied org position id: {org_pos_id})"
                    )
                else:
                    # use the first org position, except there is a agent_name/username match
                    agent = agents[0]
                    for a in agents:
                        if a.agent_name == username:
                            agent = a
                            break
                # set the org position for the actual authentication
                auth_data.append(AuthDataOrgPos(agent.org_pos_id, sub_class="AuthDataOrgPos"))
            # use the application name
            auth_data.append(
                AuthDataAppName(
                    app_name=self.__af_conf.application_name, sub_class="AuthDataAppName"
                )
            )

        csds: List[ClientSessionDetails] = gsm.authenticate_all_method(
            method, self.__af_conf.caller_uri, body=auth_data
        )

        csd: ClientSessionDetails
        if len(csds) == 1:
            csd = csds[0]
        elif len(csds) == 0:
            raise Exception(
                f"User does not have an org position {username} (supplied org position id: {org_pos_id})"
            )
        else:
            # pick the first as default
            csd = csds[0]
            # pick the one where username and org position name are the same
            for entry in csds:
                if entry.agent.agent.org_pos_name == entry.agent.agent.agent_name:
                    csd = entry
                    break

        self.__service_provider.authenticated(csd)
        self.__csd = csd

    def is_html_activity(self, item: WorklistItem) -> bool:
        return RemoteHtmlService.is_html_activity(item)

    @property
    def worklist_service(self):
        if self.__worklist_service is None:
            self.__worklist_service = WorklistService(self.__service_provider, self.__af_conf)
            self.__all_services.append(self.__worklist_service)
        return self.__worklist_service

    @property
    def process_service(self):
        if self.__process_service is None:
            self.__process_service = ProcessService(self.__service_provider, self.__af_conf)
            self.__all_services.append(self.__process_service)
        return self.__process_service

    @property
    def delegation_service(self):
        if self.__delegation_service is None:
            self.__delegation_service = DelegationService(self.__service_provider)
            self.__all_services.append(self.__delegation_service)
        return self.__delegation_service

    @property
    def absence_service(self):
        if self.__absence_service is None:
            self.__absence_service = AbsenceService(self.__service_provider)
            self.__all_services.append(self.__absence_service)
        return self.__absence_service

    @property
    def execution_history_service(self):
        if self.__execution_history_service is None:
            self.__execution_history_service = ExecutionHistoryService(self.__service_provider)
            self.__all_services.append(self.__execution_history_service)
        return self.__execution_history_service

    @property
    def image_renderer_service(self):
        if self.__image_renderer_service is None:
            self.__image_renderer_service = ImageRendererService(self.__service_provider)
            self.__all_services.append(self.__image_renderer_service)
        return self.__image_renderer_service

    @property
    def org_model_service(self):
        if self.__org_model_service is None:
            self.__org_model_service = OrgModelService(self.__service_provider)
            self.__all_services.append(self.__org_model_service)
        return self.__org_model_service

    @property
    def activity_service(self):
        if self.__activity_service is None:
            self.__activity_service = ActivityService(self.__service_provider)
            self.__all_services.append(self.__activity_service)
        return self.__activity_service

    @property
    def remote_html_service(self):
        if self.__remote_html_service is None:
            self.__remote_html_service = RemoteHtmlService(self.__service_provider)
            self.__all_services.append(self.__remote_html_service)
        return self.__remote_html_service

    def start_html_activity(self, item: WorklistItem, callback_url: str = None,
                            signal_handler: HtmlSignalHandler = None):
        """
        Starts the given HTML GUI worklist item using the Remote HTML Runtime Manager
        """
        return self.remote_html_service.start_html_activity(item, callback_url=callback_url,
                                                            signal_handler=signal_handler)

    def get_html_activity_starting(self) -> SynchronousActivityStartingApi:
        """
        Returns the Remote HTML Runtime Manager Synchronous Activity Starting, ensuring logon to the Runtime Manager
        """
        return self.remote_html_service.get_html_activity_starting()

    def reset_activity(self, item: WorklistItem):
        """Resets the given worklist item."""
        if item.state != "STARTED":
            # nothing to do
            return
        # TODO check for a "local" activity for a soft reset
        ar: AfActivityReference = item.act_ref
        ebp_ir = af_execution_manager.EbpInstanceReference(
            ar.type,
            ar.instance_id,
            ar.instance_log_id,
            ar.base_template_id,
            ar.node_id,
            ar.node_iteration,
            ar.execution_manager_uris,
            ar.runtime_manager_uris,
        )
        aec: ActivityExecutionControlApi = self.get_service(ActivityExecutionControlApi)
        aec.reset_to_prev_savepoint(body=ebp_ir, force=True)

    def deserialize(self, data, klass: Type[D]) -> D:
        """Deserialize data using the given class of the generated OpenAPI models."""
        return self.__service_provider.deserialize(data, klass)

    def serialize(self, obj) -> Dict:
        """Serialize REST model object"""
        return self.__service_provider.serialize(obj)

    def parse_ac_to_dict(self, ac: ActivityContext) -> dict:
        """
        Parses the context data required to recreate an ActivityContext
        to a json serializable dict
        """
        return {
            "token": ac.token,
            "ssc": self.serialize(ac.ssc)
        }

    def get_ac_from_dict(self,context_data: dict) -> ActivityContext:
        """
        Creates a new ActivityContext from a dict provided by parse_ac_to_dict
        """
        ac = ActivityContext()
        ac.token = context_data["token"]
        ac.ssc = self.deserialize(context_data["ssc"], SimpleSessionContext)
        return ac

    @property
    def autostart_timeout_seconds(self) -> int:
        """Wait time in seconds for auto start signals"""
        return self.__af_conf.autostart_timeout_seconds

    def disconnect(self):
        """ Disconnect all services"""
        for service in self.__all_services:
            try:
                service.disconnect()
            except Exception as e:
                print("Exception on disconnecting service", e)
