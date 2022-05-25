from .agent import Agent
from ..base.logger import functionlogger
from ..base.typing import JsonType
# from numbers import Number

import logging


__all__ = [
    "get_user",
    "get_users"
]


@functionlogger
def get_user(agent: Agent, **kwds) -> JsonType:
    """
    Gets the current user information from Carta.

    Parameters
    ----------
    agent : Agent
        Agent to handle communication with the Carta server.

    Returns
    -------
    dict
        Information about the current user:
            id: Unique ID for this user.
            name: Username for this user.
            email: Email for this user.
            firstName: First (Given) name for this user.
            lastName: Last (Family) name for this user.
    """
    response = agent.get("user", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def is_authenticated(agent: Agent, **kwds) -> bool:
    """
    Returns whether the current user is authenticated.

    Returns
    -------
    bool
        True if user is authenticated. False otherwise.
    """
    response = agent.get("user/authenticated", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_users(agent: Agent, *,
    attribute: str=None,
    value: str=None,
    filter: str='equal',
    **kwds
) -> JsonType:
    """
    Get information on all Carta users. The response can be filtered using
    known attributes (see below)

    Parameters
    ----------
    agent : Agent
        Agent to handle communication with the Carta server.
    attribute : str (optional)
        Attribute on which to filter the users. Must be one of:
            UserName
            Email
            FirstName
            LastName
    value : str (optional)
        Value to search for. Must be specified if `attribute` is given.
    filter : str (optional)
        Method of comparison. Must be one of:
            equal
            startswith

    Returns
    -------
    list of dict
        Information about the matching users. Each user contains:
            id: Unique ID for this user.
            name: Username for this user.
            email: Email for this user.
            firstName: First (Given) name for this user.
            lastName: Last (Family) name for this user.

    Examples
    --------

        from getpass import getpass

        token = getpass("Enter your Carta access token: ")
        agent = create_agent(token)
        allUsers = get_users(agent)
        usersStartingWithM = get_users(
            agent,
            attribute="UserName",
            value="m",
            filter="startswith"
        )
    """
    # ##### Validate function parameters ##### #
    # set up the parameters of the API call. This maps:
    #   attribute -> attributeName
    #   value -> attributeValue
    #   method -> attributeFilter
    # to abstract away the parameter names in the API.
    params = dict()
    if attribute or value:
        if not (attribute and value):
            raise ValueError(
                "If either `attribute` or `value` is specified,"
                "then both must be specified."
            )
        # Validate the attribute parameter used to identify on what property
        # filtering should be applied.
        try:
            attribute = {
                "username": "UserName",
                "user": "UserName",
                "email": "Email",
                "firstname": "FirstName",
                "lastname": "LastName"
            }[attribute.lower()]
        except KeyError:
            raise ValueError(
                f"`attribute` = '{attribute}' is not one of "
                "'UserName', "
                "'Email', "
                "'FirstName', or "
                "'LastName'"
            )
        # Validate the method parameter used to identify how comparisons are
        # to be made.
        try:
            filter = {
                "equal": "=",
                "equals": "=",
                "startswith": "^="
            }[filter.lower()]
        except KeyError:
            raise ValueError(
                f"`filter` = {filter} is not one of 'equal' or 'startswith'."
            )
        # Generate the key/value pairs that should be sent as the parameters
        # to the GET request.
        params = {
            "attributeName": attribute,
            "attributeValue": value,
            "attributeFilter": filter
        }
    # ##### Execute API call ##### #
    kwds["params"] = {
        **params,
        **kwds.get("params", dict())
    }
    response = agent.get("user/users", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d",
            __name__,
            response.status_code
        )
        return None
