"""Pod Response Message."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.types import _RESPONSE_MESSAGES, _PodResponseType

logger = _get_federated_logger(__name__)


@dataclass
class _PodResponseMessage:
    """A pod response message."""

    modeller_name: str
    pod_identifier: str
    messages: Dict[str, List[str]] = field(default_factory=dict)

    def add(
        self,
        response_type: _PodResponseType,
        additional_messages: Optional[List[str]] = None,
    ) -> None:
        """Adds `response_type` to `response_dict` and logs the relevant warning.

        Args:
            response_type: The response type.
            additional_messages: Any additional messages to log.
        """
        if response_type != _PodResponseType.ACCEPT:
            msg = []
            log_msg = (
                f"Task request from {self.modeller_name} rejected. "
                + f"{_RESPONSE_MESSAGES[response_type]}"
            )

            if additional_messages:
                msg.extend(additional_messages)
                log_msg += ", ".join(additional_messages)

            self.messages[response_type.name] = msg
            logger.info(log_msg)
