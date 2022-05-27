"""Helper functions."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable, List, Mapping, Optional, Sequence, Union

from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _PRODUCTION_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from bitfount.data.exceptions import BitfountSchemaError
from bitfount.data.schema import BitfountSchema
from bitfount.federated.aggregators.aggregator import Aggregator
from bitfount.federated.aggregators.base import _BaseAggregatorFactory
from bitfount.federated.aggregators.secure import SecureAggregator
from bitfount.federated.exceptions import PodNameError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.secure import SecureShare
from bitfount.federated.transport.config import (
    _DEV_MESSAGE_SERVICE_PORT,
    _DEV_MESSAGE_SERVICE_TLS,
    _DEV_MESSAGE_SERVICE_URL,
    _STAGING_MESSAGE_SERVICE_URL,
    MessageServiceConfig,
)
from bitfount.federated.transport.message_service import _MessageService
from bitfount.federated.transport.pod_transport import _PodMailbox
from bitfount.hub.api import _DEV_IDP_URL, _PRODUCTION_IDP_URL, _STAGING_IDP_URL
from bitfount.hub.helper import get_pod_schema
from bitfount.runners.config_schemas import POD_NAME_REGEX, USERNAME_REGEX

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub
    from bitfount.hub.authentication_flow import BitfountSession

logger = _get_federated_logger(__name__)


def _create_aggregator(
    secure_aggregation: bool,
    weights: Optional[Mapping[str, Union[int, float]]] = None,
) -> _BaseAggregatorFactory:
    """Creates aggregator for Federated Averaging.

    Args:
        model: The model used in aggregation.
        secure_aggregation: Boolean denoting whether aggregator should be secure.
        weights: Per-pod update weighting to use when aggregating updates,
            or None if equal weighting required.

    Raises:
        TypeError: If model is not compatible with Federated Averaging.

    Returns:
        The aggregator to be used.
    """
    if secure_aggregation and weights:
        # TODO: [BIT-1486] Remove this constraint
        raise NotImplementedError("SecureAggregation does not support update weighting")

    if secure_aggregation:
        sec_share = SecureShare()
        return SecureAggregator(secure_share=sec_share)
    return Aggregator(weights=weights)


def _get_idp_url() -> str:
    """Helper function for defining idp url based on environment."""
    environment = _get_environment()
    if environment == _STAGING_ENVIRONMENT:
        idp_url = _STAGING_IDP_URL
    elif environment == _DEVELOPMENT_ENVIRONMENT:
        idp_url = _DEV_IDP_URL
    elif environment == _PRODUCTION_ENVIRONMENT:
        idp_url = _PRODUCTION_IDP_URL
    return idp_url


def _create_message_service(
    session: BitfountSession, ms_config: Optional[MessageServiceConfig] = None
) -> _MessageService:
    """Helper function to create MessageService object.

    Args:
        session (BitfountSession): bitfount session
        ms_config (Optional[MessageServiceConfig], optional): message service config.
            Defaults to None.

    Returns:
        MessageService object
    """
    if ms_config is None:
        ms_config = MessageServiceConfig()

        environment = _get_environment()
        if environment == _STAGING_ENVIRONMENT:
            ms_config.url = _STAGING_MESSAGE_SERVICE_URL
        elif environment == _DEVELOPMENT_ENVIRONMENT:
            ms_config.url = _DEV_MESSAGE_SERVICE_URL
            ms_config.port = _DEV_MESSAGE_SERVICE_PORT
            ms_config.tls = _DEV_MESSAGE_SERVICE_TLS

    if ms_config.use_local_storage:
        logger.warning(
            "Messages will contain local file references. "
            + "Ensure all pods have access to your local file system. "
            + "Otherwise your task will hang.",
        )

    return _MessageService(session, ms_config)


async def _create_and_connect_pod_mailbox(
    pod_name: str,
    session: BitfountSession,
    ms_config: Optional[MessageServiceConfig] = None,
) -> _PodMailbox:
    """Creates pod mailbox and connects it to the message service.

    Args:
        pod_name: Name of pod.
        session: Bitfount session.
        ms_config: Optional. Message service config, defaults to None.

    Returns:
        The created pod mailbox.
    """
    message_service = _create_message_service(session, ms_config)
    mailbox = await _PodMailbox.connect_pod(
        pod_name=pod_name, message_service=message_service
    )
    return mailbox


def _check_and_update_pod_ids(
    pod_identifiers: Iterable[str], hub: BitfountHub
) -> List[str]:
    """Add username from hub to pod identifiers if not already provided."""
    # TODO: [BIT-991] check if pod id exists
    pod_id_regex = re.compile(USERNAME_REGEX.pattern + "/" + POD_NAME_REGEX.pattern)
    updated_pod_ids = []
    for pod_id in pod_identifiers:
        if pod_id_regex.fullmatch(pod_id):
            updated_pod_ids.append(pod_id)
        elif "/" not in pod_id:
            if POD_NAME_REGEX.fullmatch(pod_id):
                updated_pod_ids.append(f"{hub.username}/{pod_id}")
            else:
                raise PodNameError(
                    f"Invalid Pod name : {pod_id}"
                    "Pod name must consist of lower case alphanumeric "
                    "characters optionally seperated by '-'."
                )
        else:
            raise PodNameError(
                f"Invalid Pod name : {pod_id}"
                "Pod name must be a have the format "
                "<username>/<pod_name>. Pod name must consist "
                "of lower case alphanumeric "
                "characters optionally seperated by '-'."
            )

    return updated_pod_ids


def combine_pod_schemas(pod_names: Sequence[str]) -> BitfountSchema:
    """Combines the schemas of multiple pods into a single schema.

    Simply aggregates all the tables in the schemas of the pods into a single
    schema.

    Args:
        pod_names: The names of the pods whose schemas will be combined.

    Returns:
        The combined schema.

    Raises:
        BitfountSchemaError: If the schemas of the pods are incompatible.
    """
    combined_schema = BitfountSchema()
    for pod_name in pod_names:
        pod_schema: BitfountSchema = get_pod_schema(pod_name)
        combined_schema.tables.extend(pod_schema.tables)

    if len(combined_schema.table_names) != len(set(combined_schema.table_names)):
        raise BitfountSchemaError("Multiple tables found with the same name.")

    return combined_schema
