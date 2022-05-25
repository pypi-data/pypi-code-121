#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Any, Dict, Iterator, List, Optional

from psym.client import SymphonyClient
from psym.common.constant import SUPERUSER_ROLE, USER_ROLE
from psym.common.data_class import User, organization
from psym.common.data_enum import Entity


from ..exceptions import EntityNotFoundError, assert_ok
from ..graphql.enum.user_role import UserRole
from ..graphql.enum.user_status import UserStatus
from ..graphql.input.edit_user_input import EditUserInput
from ..graphql.mutation.edit_user import EditUserMutation
from ..graphql.query.user import UserQuery
from ..graphql.query.users import UsersQuery



def get_user(client: SymphonyClient, email: str) -> User:
    """Returns `psym.common.data_class.User` object by its email
    :param email: Email address the user registered with
    :type email: str
    :raises:
        * :class:`~psym.exceptions.EntityNotFoundError`: the user was not found
        * FailedOperationException: Internal symphony error
    :return: User object
    :rtype: :class:`~psym.common.data_class.User`
    **Example**
    .. code-block:: python
        user = client.get_user(email="user@test.com")
    """
    user = UserQuery.execute(client, email)
    if user is None:
        raise EntityNotFoundError(entity=Entity.User, entity_name=email)
    return User(
        id=user.id,
        auth_id=user.authID,
        email=user.email,
        status=user.status,
        role=user.role,
        firstName=user.firstName,
        lastName=user.lastName, 
        organization=user.organizationFk
        
    )


def add_user(client: SymphonyClient, 
email: str, 
password: str,
firstName: Optional[str] = None,
lastName: Optional[str] = None,
organization: Optional[str] = None,


) -> User:
    """Adds new user to inventory with its email and password
    :param email: Email address of the user
    :type email: str
    :param password: Password the user would connect with
    :type password: str
    :raises:
        * :class:`~psym.exceptions.EntityNotFoundError`: the user was not created
        * FailedOperationException: Internal symphony error
        * AssertionError: The user was not created
        * HTTPError: Connection error
    :return: User object
    :rtype: :class:`~psym.common.data_class.User`
    **Example**
    .. code-block:: python
        user = client.add_user(email="user@test.com", password="P0ssW!rd0f43")
    """
    resp = client.post(
        "/user/async/",
        {
        
        "email": email, 
        "password": password,
        "role": USER_ROLE, 
        "networkIDs": [], 
        "firstName": firstName,
        "lastName": lastName,
        "organization": organization,
        },
    )
    assert_ok(resp)
    return get_user(client=client, email=email)


def edit_user(
    client: SymphonyClient,
    user_id: str,
    new_organization: Optional[str] = None,
    firstName: Optional[str] = None,
    lastName: Optional[str] = None,
    new_role: Optional[UserRole] = None,
    new_status: Optional[UserRole] = None,

) -> User: 
    """Lists a specific user according to email address
    :param user: User object
    :type user: :class:`~psym.common.data_class.User`
    :raises:
        FailedOperationException: Internal symphony error
    :rtype: None
    **Example**
    .. code-block:: python
        user_email = client.get_user_by_email(email="user@test.com")
        user_Edited= client.edit_user(
            id=user_email.id,
            firstName="firstName",
            lastName="lastName",

        )

    """

    user_ = get_user_by_id(client=client, id=user_id)
    firstName = user_.firstName if firstName is None else firstName
    lastName = user_.lastName if lastName is None else lastName
    new_role = user_.role if new_role is None else new_role
    new_status = user_.status if new_status is None else new_status
  
    
    edit_user_input = EditUserInput(
        id=user_id,
        role=new_role,
        status=new_status,
        firstName=firstName,
        lastName=lastName,
        organizationFk=new_organization,
    )
    result = EditUserMutation.execute(client, edit_user_input)
    return User(
    id=result.id,
    auth_id=result.authID,
    firstName=result.firstName, 
    lastName=result.lastName, 
    organization=result.organizationFk,
    status=result.status,
    role=result.role,
    email=result.email
    )




def edit_user_for_password_and_role(
    client: SymphonyClient,
    user: User,
    new_password: Optional[str] = None,
    new_role: Optional[UserRole] = None,

) -> None:
    """Edit user password and role
    :param user: User object
    :type user: :class:`~psym.common.data_class.User`
    :param new_password: New password the user would connect with
    :type new_password: str, optional
    :param new_role: New user role
    :type new_role: str
    :raises:
        * FailedOperationException: Internal symphony error
        * AssertionError: The user was not edited
        * HTTPError: Connection error
    :rtype: None
    **Example**
    .. code-block:: python
        user = client.add_user(email="user@test.com", password="P0ssW!rd0f43")
        client.edit_user(
            user=user,
            new_password="New_Password4Ever",
            new_role=UserRole.ADMIN,
        )
    """
    params: Dict[str, Any] = {}
    if new_password is not None:
        params.update({"password": new_password})
    if new_role is not None:
        params.update(
            {"role": USER_ROLE if new_role == UserRole.USER else SUPERUSER_ROLE}
        )
    resp = client.put(f"/user/set/{user.email}", params)
    assert_ok(resp)
    if new_role is not None:
        EditUserMutation.execute(client, input=EditUserInput(id=user.id, role=new_role))


def deactivate_user(client: SymphonyClient, user: User) -> None:
    """Deactivate the user which would prevent the user from login in to symphony
    Users in symphony are never deleted. Only de-activated.
     :param user: User object
     :type user: :class:`~psym.common.data_class.User`
     :raises:
         FailedOperationException: Internal symphony error
     :rtype: None
     **Example**
     .. code-block:: python
         user = client.get_user(email="user@test.com")
         client.deactivate_user(user=user)
    """
    EditUserMutation.execute(
        client, input=EditUserInput(id=user.id, status=UserStatus.DEACTIVATED)
    )


def activate_user(client: SymphonyClient, user: User) -> None:
    """Activate the user which would allow the user to login again to symphony
    :param user: User object
    :type user: :class:`~psym.common.data_class.User`
    :raises:
        FailedOperationException: Internal symphony error
    :rtype: None
    **Example**
    .. code-block:: python
        user = client.get_user(email="user@test.com")
        client.activate_user(user=user)
    """
    EditUserMutation.execute(
        client, input=EditUserInput(id=user.id, status=UserStatus.ACTIVE)
    )


def get_users(client: SymphonyClient) -> Iterator[User]:
    """Get the list of users in the system (both active and deactivate)
    :raises:
        FailedOperationException: Internal symphony error
    :return: Users Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.User` ]
    **Example**
    .. code-block:: python
        users = client.get_users()
        for user in users:
            print(user.email)
    """
    result = UsersQuery.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield User(
                id=node.id,
                auth_id=node.authID,
                email=node.email,
                firstName=node.firstName ,
                lastName= node.lastName,
                status=node.status,
                role=node.role,
                organization=node.organizationFk
            )

def get_user_by_email(client: SymphonyClient, email: str) -> User:
    """Lists a specific user according to email address
    :param user: User object
    :type user: :class:`~psym.common.data_class.User`
    :raises:
        FailedOperationException: Internal symphony error
    :rtype: None
    **Example**
    .. code-block:: python
        user_email = client.get_user_by_email(email="user@test.com")
        print(user_email)

    """
    user_email = get_users(client=client)
    for user_ in user_email:
        if user_.email == email:
            return user_
    raise EntityNotFoundError(entity=Entity.User, entity_email=email)

def get_user_by_id(client: SymphonyClient, id: str) -> User:
    """Lists a specific user according to id
    :param user: User object
    :type user: :class:`~psym.common.data_class.User`
    :raises:
        FailedOperationException: Internal symphony error
    :rtype: None
    **Example**
    .. code-block:: python
        user = client.get_user_by_email(id=123456789)
        print(user)

    """
    user_id = get_users(client=client)
    for user_ in user_id:
        if user_.id == id:
            return user_
    raise EntityNotFoundError(entity=Entity.User, entity_id=id)



def get_active_users(client: SymphonyClient) -> List[User]:
    """Get the list of the active users in the system
    :raises:
        FailedOperationException: Internal symphony error
    :return: Users List
    :rtype: List[ :class:`~psym.common.data_class.User` ]
    **Example**
    .. code-block:: python
        users = client.get_active_users()
        for user in users:
            print(user.email)
    """
    users = get_users(client=client)
    return [user for user in users if user.status == UserStatus.ACTIVE]