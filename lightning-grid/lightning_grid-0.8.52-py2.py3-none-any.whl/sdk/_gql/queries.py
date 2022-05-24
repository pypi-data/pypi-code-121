from typing import List, Optional

from grid.metadata import __version__
from grid.sdk.client import create_gql_client
from grid.sdk.client.grid_gql import gql_execute


def get_user_basic_info():
    client = create_gql_client()
    query = """
    query {
        getUser {
            userId
            isVerified
            completedSignup
            isBlocked
            username
            firstName
            lastName
            email
        }
    }
    """
    return gql_execute(client, query)['getUser']


def get_user_teams() -> List[dict]:
    client = create_gql_client()
    query = """
        query GetUserTeams {
            getUserTeams {
                success
                message
                teams {
                    id
                    name
                    createdAt
                    role
                    members {
                        id
                        username
                        firstName
                        lastName
                    }
                }
            }
        }
    """
    result = gql_execute(client, query)
    if not result['getUserTeams'] or not result['getUserTeams']['success']:
        raise RuntimeError(result['getUserTeams']["message"])
    return result['getUserTeams']['teams']


def get_user_info():
    """Return basic information about a user."""
    client = create_gql_client()
    query = """
        query {
            getUser {
                username
                firstName
                lastName
                email

            }
        }
    """

    result = gql_execute(client, query)
    if not result['getUser']:
        raise RuntimeError(result['getUser']["message"])
    return result['getUser']
