import secrets
import string
from typing import List

from django.contrib.auth.models import Permission, User
from esi.models import Token

from ..backends import EveSSOBackend


def create_fake_token(
    character_id: int,
    character_name: str,
    user: User = None,
    character_owner_hash: str = None,
) -> Token:
    """Create a fake token."""
    if not character_owner_hash:
        character_owner_hash = random_string(28)
    return Token.objects.create(
        access_token=random_string(28),
        refresh_token=random_string(28),
        user=user,
        character_id=character_id,
        character_name=character_name,
        character_owner_hash=character_owner_hash,
    )


def create_fake_user(
    character_id: int,
    character_name: str,
    owner_hash: str = None,
    permissions: List[str] = None,
) -> User:
    """Create fake user from given eve character details.

    Args:
        character_id: Eve ID of the character
        character_name: Name of the character
        owner_hash: SSO owner hash
        permissions: List of permission strings

    Returns:
        New User object
    """
    token = create_fake_token(
        character_id=character_id,
        character_name=character_name,
        character_owner_hash=owner_hash,
    )
    user = EveSSOBackend.create_user_from_token(token)
    token.user = user
    token.save()
    if permissions:
        perm_objs = [permission_by_name(perm) for perm in permissions]
        user = add_permissions_to_user(perm_objs=perm_objs, user=user)

    return user


def random_string(length: int) -> int:
    """Create random string consisting of lower case ascii characters and digits."""
    return "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )


def add_permission_to_user_by_name(perm_name: str, user: User) -> User:
    """Add permission as string to given user

    Args:
        perm: Permission name as 'app_label.codename'
        user: user object

    Returns:
        updated user object
    """
    perm = permission_by_name(perm_name)
    return add_permissions_to_user(perm_objs=[perm], user=user)


def add_permissions_to_user(perm_objs: List[Permission], user: User) -> User:
    """Add permissions to given user

    Args:
        perm_objs: List of permission objects
        user: user object

    Returns:
        updated user object
    """
    user.user_permissions.add(*perm_objs)
    user = User.objects.get(pk=user.pk)  # reload permission cache
    return user


def permission_by_name(perm: str) -> Permission:
    """returns permission specified by qualified name

    Args:
        perm: Permission name as 'app_label.codename'

    Returns:
        Permission object or throws exception if not found
    """
    perm_parts = perm.split(".")
    if len(perm_parts) != 2:
        raise ValueError("Invalid format for permission name")
    return Permission.objects.get(
        content_type__app_label=perm_parts[0], codename=perm_parts[1]
    )
