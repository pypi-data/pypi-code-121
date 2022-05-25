from sym.sdk.user import UserIdentity


def persist_user_identity(
    *, email: str, service: str, service_id: str, user_id: str
) -> UserIdentity:
    """This function will create or update a :class:`~sym.sdk.user.UserIdentity`
    for a :class:`~sym.sdk.user.User` identified by the provided email.

    If no :class:`~sym.sdk.user.User` matching the provided email exists,
    one will be created.

    Args:
        email: The email of the Sym :class:`~sym.sdk.user.User` to persist a
            :class:`~sym.sdk.user.UserIdentity` for.
        service: The name of the external system providing the identity (e.g. "slack").
        service_id: The ID of the external system providing the identity (e.g. "T123ABC")
            for a Slack Workspace.
        user_id: The :class:`~sym.sdk.user.User`'s identifier in the external system
            (e.g. U12345 for a Slack User ID).

    Returns:
        The :class:`~sym.sdk.user.UserIdentity` that was created or updated.

    Raises:
        :class:`~sym.sdk.exceptions.identity.CouldNotSaveError`: if the identity
            failed to save for any reason.
    """
