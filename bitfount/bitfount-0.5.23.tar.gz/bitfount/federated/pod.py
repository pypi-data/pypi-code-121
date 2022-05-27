"""Pods for responding to tasks."""
import asyncio
import os
import threading
from typing import (
    Callable,
    Coroutine,
    Iterable,
    List,
    MutableSequence,
    Optional,
    Tuple,
    Union,
    cast,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from requests import HTTPError, RequestException

from bitfount.config import BITFOUNT_STORAGE_PATH
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.schema import BitfountSchema
from bitfount.federated.aggregators.secure import _is_secure_share_task_request
from bitfount.federated.authorisation_checkers import (
    _IDENTITY_VERIFICATION_METHODS_MAP,
    IdentityVerificationMethod,
    _AuthorisationChecker,
    _OIDCAuthorisationCode,
    _OIDCDeviceCode,
    _SAMLAuthorisation,
    check_identity_verification_method,
)
from bitfount.federated.exceptions import PodNameError, PodRegistrationError
from bitfount.federated.helper import (
    _check_and_update_pod_ids,
    _create_and_connect_pod_mailbox,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.pod_keys_setup import PodKeys, _get_pod_keys
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.pod_vitals import _PodVitals, _PodVitalsHandler
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.task_requests import _TaskRequestMessage
from bitfount.federated.transport.base_transport import _run_func_and_listen_to_mailbox
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
)
from bitfount.federated.transport.pod_transport import _PodMailbox
from bitfount.federated.transport.worker_transport import (
    _InterPodWorkerMailbox,
    _WorkerMailbox,
)
from bitfount.federated.types import (
    AggregatorType,
    SerializedProtocol,
    _PodResponseType,
)
from bitfount.federated.worker import _Worker
from bitfount.hub.api import BitfountAM, BitfountHub, PodPublicMetadata
from bitfount.hub.authentication_flow import (
    _DEFAULT_USER_DIRECTORY,
    _get_auth_environment,
)
from bitfount.hub.helper import (
    _create_access_manager,
    _create_bitfounthub,
    _get_pod_public_keys,
)
from bitfount.runners.config_schemas import (
    POD_NAME_REGEX,
    PodDataConfig,
    PodDetailsConfig,
)
from bitfount.transformations.dataset_operations import (
    CleanDataTransformation,
    NormalizeDataTransformation,
)
from bitfount.transformations.processor import TransformationProcessor
from bitfount.types import _JSONDict
from bitfount.utils import _is_notebook

logger = _get_federated_logger(__name__)


class Pod:
    """Makes data and computation available remotely and responds to tasks.

    The basic component of the Bitfount network is the `Pod` (Processor of Data). Pods
    are co-located with data, check users are authorized to do given operations on the
    data and then do any approved computation. Creating a `Pod` will register the pod
    with Bitfount Hub.

    ```python title="Example usage:"
    import bitfount as bf

    pod = bf.Pod(
        name="really_cool_data",
        data="/path/to/data",
    )
    pod.start()
    ```

    Args:
        name: Name of the pod. This will appear on `Bitfount Hub` and `Bitfount AM`.
            This is also used for the name of the table in a single-table `_BaseSource`.
        datasource: A concrete instance of the `_BaseSource` object.
        username: Username of the user who is registering the pod. Defaults to None.
        data_config: Configuration for the data. Defaults to None.
        schema: Schema for the data. This can be a `BitfountSchema` object or a Path
            to a serialized `BitfountSchema`. This will generated automatically if not
            provided. Defaults to None.
        pod_details_config: Configuration for the pod details. Defaults to None.
        bitfount_hub: Bitfount Hub to register the pod with. Defaults to None.
        ms_config: Configuration for the message service. Defaults to None.
        access_manager: Access manager to use for checking access. Defaults to None.
        pod_keys: Keys for the pod. Defaults to None.
        approved_pods: List of other pod identifiers this pod is happy
            to share a training task with. Required if the protocol uses the
            `SecureAggregator` aggregator.
        pod_dp: Differential privacy configuration for the pod. Defaults to None.

    Attributes:
        data: Data that the pod encapsulates.
        name: Name of the pod.
        pod_identifier: Identifier of the pod.
        private_key: Private key of the pod.
        public_key: Public key of the pod.
        public_metadata: Public metadata about the pod.
        schema: Schema for the data.

    Raises:
        PodRegistrationError: If the pod could not be registered for any reason.

    :::tip

    Once you start a `Pod`, you can just leave it running in the background. It will
    automatically respond to any tasks without any intervention required.

    :::
    """

    def __init__(
        self,
        name: str,
        datasource: _BaseSource,
        username: Optional[str] = None,
        data_config: Optional[PodDataConfig] = None,
        schema: Optional[Union[str, os.PathLike, BitfountSchema]] = None,
        pod_details_config: Optional[PodDetailsConfig] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        access_manager: Optional[BitfountAM] = None,
        pod_keys: Optional[PodKeys] = None,
        approved_pods: Optional[List[str]] = None,
        pod_dp: Optional[DPPodConfig] = None,
    ):
        self.name = name
        if not data_config:
            data_config = PodDataConfig()
        # Create datasource
        self.datasource = datasource

        # Load schema if necessary
        if schema and not isinstance(schema, BitfountSchema):
            schema = BitfountSchema.load_from_file(schema)

        # If the schema was a path, it should be loaded by here, so we can cast:
        schema = cast(Optional[BitfountSchema], schema)
        self.schema = self._setup_schema(schema=schema, data_config=data_config)

        pod_details_config = (
            pod_details_config
            if pod_details_config is not None
            else self._get_default_pod_details_config()
        )
        self.public_metadata = self._get_public_metadata(
            pod_details_config, self.schema
        )

        self._hub = (
            bitfounthub
            if bitfounthub is not None
            else _create_bitfounthub(username=username)
        )
        self._session = self._hub.session

        self._access_manager = (
            access_manager
            if access_manager is not None
            else _create_access_manager(self._session)
        )
        self._access_manager_public_key = self._access_manager.get_access_manager_key()

        self.private_key, self.pod_public_key = self._get_default_pod_keys(pod_keys)

        self.pod_identifier = f"{self._session.username}/{self.name}"
        if approved_pods is None:
            approved_pods = []
        _check_and_update_pod_ids([*approved_pods, self.pod_identifier], self._hub)
        self.approved_pods = approved_pods

        self._pod_dp = pod_dp
        self._pod_vitals = _PodVitals()

        # Connecting the pod to the message service must happen AFTER registering
        # it on the hub as the message service uses hub information to verify that
        # the relevant message queue is available.
        self._register_pod()
        self._ms_config: Optional[MessageServiceConfig] = ms_config
        self._mailbox: Optional[_PodMailbox] = None

        # Marker for when initialization is complete
        self._initialised: bool = False

    @property
    def name(self) -> str:
        """Pod name property."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Validate Pod's name matches POD_NAME_REGEX."""
        if _name := POD_NAME_REGEX.fullmatch(name):
            self._name = _name.string
        else:
            raise PodNameError(
                f"Invalid Pod name: {name}. "
                f"Pod names must match: {POD_NAME_REGEX.pattern}"
            )

    def _setup_schema(
        self,
        data_config: PodDataConfig,
        schema: Optional[BitfountSchema] = None,
    ) -> BitfountSchema:
        """Generate pod schema."""
        self.datasource.load_data()
        logger.info("Generating the schema ...")
        # Create schema if not provided
        if not schema:
            schema = BitfountSchema()

        # Add _BaseSource to schema
        schema.add_datasource_tables(
            datasource=self.datasource,
            table_name=self.name,
            force_stypes=data_config.force_stypes,
        )

        # Auto-tidy if specified and datasource is not multi-table
        if data_config.auto_tidy and self.datasource.multi_table:
            logger.warning("Can't autotidy multi-table data.")
        elif data_config.auto_tidy:
            clean_data = CleanDataTransformation()
            # Normalization is applied to all float columns if `auto-tidy` is true
            normalize = NormalizeDataTransformation()
            processor = TransformationProcessor(
                [clean_data, normalize],
                schema.get_table_schema(self.name),
            )
            self.datasource.data = processor.transform(self.datasource.data)

            # Add _BaseSource to schema again because features will have changed by
            # auto-tidying
            schema.add_datasource_tables(
                datasource=self.datasource,
                table_name=self.name,
                force_stypes=data_config.force_stypes,
            )

        # Freeze schema
        schema.freeze()
        return schema

    def _get_default_pod_details_config(self) -> PodDetailsConfig:
        """Get default pod details config."""
        return PodDetailsConfig(display_name=self.name, description=self.name)

    def _get_public_metadata(
        self, pod_details_config: PodDetailsConfig, schema: BitfountSchema
    ) -> PodPublicMetadata:
        """Get PodPublicMetadata."""
        return PodPublicMetadata(
            self.name,
            pod_details_config.display_name,
            pod_details_config.description,
            schema.to_json(),
            pod_details_config.is_public,
        )

    def _get_default_pod_keys(
        self, pod_keys: Optional[PodKeys]
    ) -> Tuple[RSAPrivateKey, RSAPublicKey]:
        """Get default pod keys."""
        if pod_keys is None:
            user_storage_path = BITFOUNT_STORAGE_PATH / _DEFAULT_USER_DIRECTORY
            pod_directory = user_storage_path / "pods" / self.name
            pod_keys = _get_pod_keys(pod_directory)
        return pod_keys.private, pod_keys.public

    def _register_pod(self) -> None:
        """Register pod with Bitfount Hub.

        If Pod is already registered, will update pod details if anything has changed.

        Raises:
            PodRegistrationError: if registration fails for any reason
        """
        try:
            logger.info("Registering/Updating details on Bitfount Hub.")
            self._hub.register_pod(
                self.public_metadata,
                self.pod_public_key,
                self._access_manager_public_key,
            )
        except HTTPError as ex:
            logger.critical(f"Failed to register with hub: {ex}")
            raise PodRegistrationError("Failed to register with hub") from ex
        except RequestException as ex:
            logger.critical(f"Could not connect to hub: {ex}")
            raise PodRegistrationError("Could not connect to hub") from ex

    async def _initialise(self) -> None:
        """Initialises the pod.

        Sets any attributes that could not be created at creation time.
        """
        if not self._initialised:
            # Create mailbox. Cannot be done in __init__ due to async nature.
            self._mailbox = await _create_and_connect_pod_mailbox(
                pod_name=self.name, session=self._session, ms_config=self._ms_config
            )

            # Set initialised state
            self._initialised = True
        else:
            logger.warning("Pod._initialise() called twice. This is not allowed.")

    def _secure_aggregation_other_workers_response(
        self, other_worker_names: MutableSequence[str]
    ) -> Optional[List[str]]:
        """Checks if secure aggregation can be performed with given other workers.

        Args:
            other_worker_names (List[str]): list of other worker names

        Returns:
            Optional[List[str]]:
                unapproved workers (if they exist in other_worker_names)
        """
        unapproved_pods = [
            worker for worker in other_worker_names if worker not in self.approved_pods
        ]
        logger.debug(
            f"Modeller requested aggregation"
            f" with non-approved pods: {unapproved_pods}"
        )

        if unapproved_pods:
            logger.info(
                "Modeller requested aggregation with"
                " pods that this pod has not approved."
            )
            return unapproved_pods

        logger.debug("All pods requested by modeller for aggregation are approved.")
        return None

    def _check_for_unapproved_pods(
        self,
        pods_involved_in_task: Iterable[str],
        serialized_protocol: SerializedProtocol,
    ) -> Optional[List[str]]:
        """Returns the pods that we're not happy to work with.

        If secure aggregation has been requested then this will
        identify any pods that we've not approved.

        In any other case it returns None, as there's no concern
        around security with other pods.

        Args:
            pods_involved_in_task: A list of other pods that have been contacted by
                the modeller for this task.
            serialized_protocol: The decrypted serialized protocol portion of the task
                request.

        Returns:
            Either a list of unapproved pods or `None` if all are approved or if secure
            aggregation not in use.
        """
        unapproved_workers = None

        # Create mutable version of pods_involved_in_task
        other_pods: List[str] = list(pods_involved_in_task)

        # We don't need to check if we're approved to work with our self.
        try:
            other_pods.remove(self.pod_identifier)
        except ValueError:  # if not in list to remove
            pass

        aggregator = serialized_protocol.get("aggregator")
        if (
            aggregator
            and aggregator["class_name"] == AggregatorType.SecureAggregator.value
        ):
            logger.info(
                "Secure aggregation is in use, checking responses from other pods."
            )
            unapproved_workers = self._secure_aggregation_other_workers_response(
                other_pods
            )

        return unapproved_workers

    async def _new_task_request_handler(self, message: _BitfountMessage) -> None:
        """Called on new task request being received from message service."""
        logger.info(f"Training task request received from '{message.sender}'")
        try:
            await self._create_and_run_worker(message)
        except asyncio.TimeoutError:
            logger.info("Ready for next task...")
            return

    async def _create_and_run_worker(self, message: _BitfountMessage) -> None:
        """Creates and runs a worker instance."""
        # `_initialise` is always called before this method, so we can assume
        # that the mailbox is initialised. Reassuring mypy that this is True.
        assert isinstance(self._mailbox, _PodMailbox)  # nosec

        # Unpack task details from received message
        logger.info("Unpacking task details from message...")
        task_request_message: _TaskRequestMessage = _TaskRequestMessage.deserialize(
            message.body
        )
        auth_type: IdentityVerificationMethod = check_identity_verification_method(
            task_request_message.auth_type
        )
        authoriser_cls = _IDENTITY_VERIFICATION_METHODS_MAP[auth_type]
        task_request = authoriser_cls.unpack_task_request(
            message.body, self.private_key
        )

        # If we are using secure aggregation we check for unapproved workers; if
        # we are not, `unapproved_workers` will be `None`.
        other_pods = [
            pod_id
            for pod_id in message.pod_mailbox_ids
            if pod_id != self.pod_identifier
        ]
        unapproved_workers = self._check_for_unapproved_pods(
            other_pods, task_request.serialized_protocol
        )

        # If we are dealing with secure aggregation (and hence need inter-pod
        # communication) we create an appropriate mailbox as long as there are no
        # unapproved workers.
        # If there are, the task will be rejected, so we can just create a normal
        # mailbox (as don't need inter-pod communication to reject the task).
        # Similarly, if we're not using secure aggregation we just create a normal
        # mailbox as inter-pod communication won't be needed.
        worker_mailbox: _WorkerMailbox
        mailbox_kwargs: _JSONDict = dict(
            pod_identifier=self.pod_identifier,
            modeller_mailbox_id=message.sender_mailbox_id,
            modeller_name=message.sender,
            aes_encryption_key=task_request.aes_key,
            message_service=self._mailbox.message_service,
            pod_mailbox_ids=message.pod_mailbox_ids,
        )
        if _is_secure_share_task_request(task_request) and not unapproved_workers:
            logger.debug("Creating mailbox with inter-pod support.")

            other_pod_public_keys = _get_pod_public_keys(other_pods, self._hub)

            worker_mailbox = _InterPodWorkerMailbox(
                **mailbox_kwargs,
                pod_public_keys=other_pod_public_keys,
                private_key=self.private_key,
            )
        else:
            logger.debug("Creating modeller<->worker-only mailbox.")
            worker_mailbox = _WorkerMailbox(**mailbox_kwargs)

        # TODO: [BIT-1045] Move the secure aggregation allowed check to the access
        #       manager once we support configuring or storing it there.
        if unapproved_workers:
            # There are pods we're explicitly not happy to work with (i.e. we're
            # using secure aggregation) we reject the task.
            logger.info(f"Task from '{message.sender}' rejected.")
            authorisation_errors = _PodResponseMessage(
                message.sender, self.pod_identifier
            )
            authorisation_errors.add(
                _PodResponseType.SECURE_AGGREGATION_WORKERS_NOT_AUTHORISED,
                unapproved_workers,
            )
            await worker_mailbox.reject_task(authorisation_errors.messages)
            return

        logger.debug("Creating authorisation checker.")
        authorisation_checker = self._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=message.sender,
            worker_mailbox=worker_mailbox,
        )

        logger.debug("Creating worker.")
        worker = _Worker(
            datasource=self.datasource,
            mailbox=worker_mailbox,
            bitfounthub=self._hub,
            authorisation=authorisation_checker,
            pod_vitals=self._pod_vitals,
            pod_dp=self._pod_dp,
            pod_identifier=self.pod_identifier,
            serialized_protocol=task_request.serialized_protocol,
        )
        # Run the worker and the mailbox listening simultaneously
        await _run_func_and_listen_to_mailbox(worker.run(), worker_mailbox)

    def _create_authorisation_checker(
        self,
        task_request_message: _TaskRequestMessage,
        sender: str,
        worker_mailbox: _WorkerMailbox,
    ) -> _AuthorisationChecker:
        """Create appropriate Authorisation Checker.

        Determines checker to create based on supplied auth_type.

        Args:
            task_request_message: The full task request message.
            sender: The sender (i.e. modeller) of the request.
            worker_mailbox: Worker mailbox for communication with modeller.

        Returns:
            An authorisation checker.
        """
        auth_type: IdentityVerificationMethod = check_identity_verification_method(
            task_request_message.auth_type
        )
        authorisation_checker_cls = _IDENTITY_VERIFICATION_METHODS_MAP[auth_type]

        task_request = authorisation_checker_cls.unpack_task_request(
            task_request_message, self.private_key
        )
        serialized_protocol = task_request.serialized_protocol

        pod_response_message = _PodResponseMessage(
            modeller_name=sender,
            pod_identifier=self.pod_identifier,
        )

        authorisation_checker: _AuthorisationChecker

        # TODO: [BIT-1291] Uncomment when key-based validation enabled again
        # if auth_type == IdentityVerificationMethod.KEYS:
        #     # Public Key Signature authorisation
        #     packed_request = (
        #         authorisation_checker_cls.extract_from_task_request_message(
        #             task_request_message
        #         )
        #     )
        #
        #     authorisation_checker = _SignatureBasedAuthorisation(
        #         pod_response_message=pod_response_message,
        #         encrypted_task_request=packed_request.encrypted_request,
        #         signature=packed_request.signature,
        #         serialized_protocol=serialized_protocol,
        #     )
        # elif auth_type == IdentityVerificationMethod.OIDC_ACF_PKCE:
        if auth_type == IdentityVerificationMethod.OIDC_ACF_PKCE:
            # OIDC Authorization Code Flow
            auth_env = _get_auth_environment()
            authorisation_checker = _OIDCAuthorisationCode(
                pod_response_message=pod_response_message,
                access_manager=self._access_manager,
                mailbox=worker_mailbox,
                serialized_protocol=serialized_protocol,
                _auth_domain=auth_env.auth_domain,
                _client_id=auth_env.client_id,
            )
        elif auth_type == IdentityVerificationMethod.OIDC_DEVICE_CODE:
            # OIDC Device Code flow
            auth_env = _get_auth_environment()
            authorisation_checker = _OIDCDeviceCode(
                pod_response_message=pod_response_message,
                access_manager=self._access_manager,
                mailbox=worker_mailbox,
                serialized_protocol=serialized_protocol,
                _auth_domain=auth_env.auth_domain,
                _client_id=auth_env.client_id,
            )
        else:
            # Default to SAML Authorisation
            authorisation_checker = _SAMLAuthorisation(
                pod_response_message=pod_response_message,
                access_manager=self._access_manager,
                mailbox=worker_mailbox,
                serialized_protocol=serialized_protocol,
            )
        return authorisation_checker

    @staticmethod
    async def _repeat(interval: int, func: Callable[..., Coroutine]) -> None:
        """Run coroutine func every interval seconds.

        If func has not finished before *interval*, will run again
        immediately when the previous iteration finished.

        Args:
            interval: run interval in seconds
            func: function to call which returns a coroutine to await
        """
        while True:
            await asyncio.gather(func(), asyncio.sleep(interval))

    async def _pod_heartbeat(self) -> None:
        """Makes a pod heartbeat to the hub."""
        try:
            self._hub.do_pod_heartbeat(self.name, self.pod_public_key)
        except HTTPError as ex:
            logger.warning(f"Failed to reach hub for status: {ex}")
        except RequestException as ex:
            logger.warning(f"Could not connect to hub for status: {ex}")

    def _run_pod_heartbeat_task(self) -> None:
        """Makes 10-second interval pod heartbeats to the hub."""
        if _is_notebook():
            # We need to create a new event loop here for jupyter
            # As it's run in a new thread and can't be patched by nest_asyncio
            asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.run(self._repeat(10, self._pod_heartbeat))

    def _pod_vitals_server(self, vitals_handler: _PodVitalsHandler) -> None:
        """Run _PodVitals webserver."""
        # The Pod Vitals webserver should run until the
        # pod itself it shut down. asyncio.run would handle
        # the event loop for us however it would also
        # shutdown the loop (and the webserver) on completion
        # so instead we directly interact with the
        # event loop here to ensure it is run_forever.
        pod_vitals_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(pod_vitals_loop)
        vitals_handler.start(pod_vitals_loop)
        pod_vitals_loop.run_forever()

    def _run_pod_vitals_server(self) -> Optional[_PodVitalsHandler]:
        """Create _PodVitalsHandelr and run _PodVitals webserver."""
        # Check that we have not initialized the Pod from a notebook
        if not _is_notebook():
            # Setup pod vitals webserver
            vitals_handler = _PodVitalsHandler(self._pod_vitals)
            logger.debug("Starting Pod Vitals interface...")
            threading.Thread(
                daemon=True, target=self._pod_vitals_server, args=(vitals_handler,)
            ).start()
            return vitals_handler
        else:
            return None

    async def start_async(self) -> None:
        """Starts a pod instance, listening for tasks.

        Whenever a task is received, a worker is created to handle it. Runs continuously
        and asynchronously orchestrates training whenever a task arrives i.e. multiple
        tasks can run concurrently.
        """
        # Do post-init initialization work
        await self._initialise()

        # `_initialise` has just been called which sets the mailbox so we can assume
        # that the mailbox is initialised. Reassuring mypy that this is True.
        assert isinstance(self._mailbox, _PodMailbox)  # nosec

        # Setup heartbeat to hub
        logger.info(f"Starting pod {self.name}...")
        threading.Thread(daemon=True, target=self._run_pod_heartbeat_task).start()

        # Start pod vitals webserver
        vitals_handler = self._run_pod_vitals_server()

        # Attach handler for new tasks
        self._mailbox.register_handler(
            _BitfountMessageType.JOB_REQUEST, self._new_task_request_handler
        )

        # Start pod listening for messages
        logger.info("Pod started... press Ctrl+C to stop")
        await self._mailbox.listen_for_messages()

        logger.info(f"Pod {self.name} stopped.")

        # Shutdown pod vitals webserver
        if vitals_handler:
            await vitals_handler.runner.cleanup()

    def start(self) -> None:
        """Starts a pod instance, listening for tasks.

        Whenever a task is received, a worker is created to handle it. Runs continuously
        and asynchronously orchestrates training whenever a task arrives i.e. multiple
        tasks can run concurrently.
        """
        asyncio.run(self.start_async())
