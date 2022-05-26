from abc import ABC, abstractmethod
from typing import Optional, final

from sym.sdk.event import Event
from sym.sdk.exceptions.identity import IdentityNotFound
from sym.sdk.user import User
from sym.sdk.utils import persist_user_identity

from .integration import Integration


class AccessStrategy(ABC):
    """A standardized interface that allows Implementers to define custom Strategies, enabling Sym
    to perform escalations and de-escalations against almost any Internet-accessible service."""

    @final
    def __init__(self, integration: Integration):
        self.integration = integration

    @final
    def get_requester_identity(self, event: Event) -> str:
        """Retrieves the external identity of the user who initiated the request represented by the
        ``event`` parameter; first from stored user information, then by calling
        :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.fetch_remote_identity` as needed.

        This method is meant to be called in implementations of the ``AccessStrategy`` class; e.g.,
        :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.escalate` and
        :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.deescalate`, as a way to resolve
        the mapping of a Sym user to their corresponding identity in the external service being
        interacted with.

        To be clear, this method does not *need* to be called in situations where there is no need
        to maintain a mapping of users to external identities; for example, if the user's email
        address, which is already captured by Sym, is all that is needed by the external service.

        This method's source can also be used as a reference for how the external identity lookup
        process works. It should not be overridden!

        Args:
            event: An object containing information about the current event

        Returns:
            The unique identifier for the user who initiated the request, for the external service
            being interacted with.

        Raises:
            IdentityNotFound: If the user has no identity mapping configured and it could not be
                looked up (``fetch_remote_identity()`` returned ``None``)
        """
        requester: User = event.run.actors["prompt"]
        if requester_id := requester.identity(self.integration.type, self.integration.external_id):
            return requester_id.user_id

        if not (requester_id := self.fetch_remote_identity(requester)):
            raise IdentityNotFound(email=requester.email, service_id=self.integration.external_id)

        persist_user_identity(
            email=requester.email,
            service=self.integration.type,
            service_id=self.integration.external_id,
            user_id=requester_id,
        )
        return requester_id

    @abstractmethod
    def fetch_remote_identity(self, user: User) -> Optional[str]:
        """Fetches the external identity of the requester from the remote service; not meant to be
        called directly.

        This method is used to fetch the external identity of the requester when Sym does not
        already have that information available. Commonly, this is when a user makes a request
        utilizing a given :class:`~sym.sdk.strategies.integration.Integration` for the first time.

        This method should return a string that represents the user's unique user ID in the
        service this Strategy interacts with; or, more specifically, whatever is needed to identify
        the user being escalated or de-escalated in the service that is performing the escalation/
        de-escalation. The user ID value can be any string; it is treated as an opaque value by the
        Sym platform. For example, if the Strategy were interacting with AWS IAM, the user ID
        returned by this method would be the user's ARN.

        If the user's identity cannot be fetched, or this automated remote identity discovery does
        not need to be implemented, this method may return ``None`` instead; however, note that
        ``get_requester_identity()`` will raise an
        :class:`~sym.sdk.exceptions.identity.IdentityNotFound` exception if the requester does not
        already have an identity.

        To be clear, this method does not *need* to be implemented in situations where there is no
        need to maintain a mapping of users to external identities; for example, if the user's email
        address, which is already captured by Sym, is all that is needed by the external service.

        Implementers should not call this method directly; instead, use
        :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.get_requester_identity`,
        which calls this method as needed.

        If this method returns a non-``None`` value, ``get_requester_identity()`` will persist the
        value to the user saved in Sym so that this lookup doesn't need to be performed again.

        Args:
            user: The user to fetch an external service identity for

        Returns:
            An opaque string value representing the user's unique identifier in the external
            service, or ``None`` if this lookup should not or cannot be performed.
        """

    @abstractmethod
    def escalate(self, target_id: str, event: Event) -> Optional[dict]:
        """Perform an escalation in the external service.

        This method is called to perform escalations, and should implement all functionality needed
        to grant access to a user for a resource. For example, an implementation of this method
        might construct a JSON request body and then submit an HTTP POST request to some REST API
        endpoint.

        This method should be idempotent; escalating the same user and target pair multiple times
        must not cause an error. However, errors may be reported by simply raising an exception;
        these exceptions will be handled by Sym's built-in error handling logic. If you wish to
        implement your own exceptions, please refer to
        :class:`~sym.sdk.exceptions.sym_exception.SymException` and
        :class:`~sym.sdk.exceptions.sym_exception.ExceptionWithHint`.

        Args:
            target_id: The ID of the "target" of the escalation, which can be thought of what the
                user is being escalated to. Specified by the Implementer in Terraform, and often
                selected by the requesting user when making the request.
            event: A representation of the escalation event. The ID of the user being escalated can
                be retrieved by calling
                :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.get_requester_identity`
                on ``event``. It also contains other useful values; see the docs for
                :class:`~sym.sdk.event.Event`.

        Returns:
            An optional dictionary of state that should be preserved for de-escalation. This can
            be accessed in :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.deescalate` by
            calling :func:`~sym.sdk.templates.step.get_step_output` in the implementation there.
            This value is also made available to `Hooks <https://docs.symops.com/docs/hooks>`_ in
            Flow implementations, also via ``get_step_output()``. This method can also return an
            empty dict or ``None`` to indicate that no special state needs to be preserved for de-
            escalation or Hooks. **Failure must be indicated by raising an exception.**
        """

    @abstractmethod
    def deescalate(self, target_id: str, event: Event) -> Optional[dict]:
        """Perform a de-escalation in the external service.

        This method is called to perform de-escalations, and should implement all functionality
        needed to revoke access granted by this strategy's
        :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.escalate` method. For example, an
        implementation of this method might construct a JSON request body and then submit an HTTP
        DELETE request to some REST API endpoint.

        This method should be idempotent; de-escalating the same user and target pair multiple times
        (or calling this method on a user who is not escalated at the time of the call) must not
        cause an error. However, errors may be reported by simply raising an exception; these
        exceptions will be handled by Sym's built-in error handling logic. If you wish to implement
        your own exceptions, please refer to
        :class:`~sym.sdk.exceptions.sym_exception.SymException` and
        :class:`~sym.sdk.exceptions.sym_exception.ExceptionWithHint`.

        Args:
            target_id: The ID of the "target" of the de-escalation, which can be thought of what the
                user is being removed from for de-escalation. Specified by the Implementer in
                Terraform, and often was selected by the requesting user when making the request;
                will be the same value as was passed to
                :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.escalate`
            event: A representation of the de-escalation event. The ID of the user being
                de-escalated can be retrieved by calling
                :func:`~sym.sdk.strategies.access_strategy.AccessStrategy.get_requester_identity`
                on ``event``. It also contains other useful values; see the docs for Event.

        Returns:
            An optional dictionary of state that should be made available to
            `Hooks <https://docs.symops.com/docs/hooks>`_ in Flow implementations via
            :func:`~sym.sdk.templates.step.get_step_output`. This method can also return an empty
            dict or ``None`` to indicate that nothing needs to be preserved for Hooks. **Failure
            must be indicated by raising an exception.**
        """
