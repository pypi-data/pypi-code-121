from .agent import Agent
from ..base.logger import functionlogger
from ..base.typing import JsonType

import logging


__all__ = [
    "get_meta",
    "get_actors",
    "get_selectors",
    "get_schema"
]


@functionlogger
def get_meta(agent: Agent, **kwds) -> JsonType:
    """
    Gets documentation about the Carta API.

    Parameters
    ----------
    agent : pycarta.api.Agent
        The agent that handles communication with the Carta server.

    Returns
    -------
    dict
        JSON-formatted documentation on the API.
    """
    response = agent.get("meta", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_actors(agent: Agent, **kwds) -> JsonType:
    """
    Gets the actors (operators) available through the Carta API.

    Parameters
    ----------
    agent : pycarta.api.Agent
        The agent that handles communication with the Carta server.

    Returns
    -------
    dict
        JSON-formatted collection of actors.

    Examples
    --------
        from getpass import getpass

        auth = getpass("Enter your Carta authentication token: ")
        agent = Agent(auth)
        response = get_actors(agent)
    """
    response = agent.get("meta/actors", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_selectors(agent: Agent, **kwds) -> JsonType:
    """
    Gets the selectors available through the Carta API.

    Parameters
    ----------
    agent : pycarta.api.Agent
        The agent that handles communication with the Carta server.

    Returns
    -------
    dict
        JSON-formatted collection of actors.

    Examples
    --------
        from getpass import getpass

        auth = getpass("Enter your Carta authentication token: ")
        agent = Agent(auth)
        response = get_selectors(agent)
    """
    response = agent.get("meta/actors", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_schema(agent: Agent, name: str, **kwds) -> JsonType:
    """
    Gets the schema for a given actor (operator) or selector available
    through the Carta API.

    Parameters
    ----------
    agent : pycarta.api.Agent
        The agent that handles communication with the Carta server.
    name : str
        The name of the object whose schema is to be retrieved.

    Returns
    -------
    dict
        JSON-formatted document describing the API access options and
        requirements for a given actor or selector.
    """
    import asyncio

    async def _get_actor():
        return agent.get("meta/actors/{}/schema".format(name), **kwds)

    async def _get_selector():
        return agent.get("meta/selectors/{}/schema".format(name), **kwds)

    async def _run():
        actor = asyncio.create_task(_get_actor())
        selector = asyncio.create_task(_get_selector())

        return (await actor, await selector)

    actor, selector = asyncio.run(_run())

    # get the response and return one (or both) actors and selectors that
    # match the requested name
    response = actor or selector
    if response:
        if actor and selector:
            return [ actor.json(), selector.json() ]
        else:
            return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None
