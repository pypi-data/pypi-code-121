from minumtium.infra.authentication import AuthenticationAdapter
from minumtium.infra.database import DatabaseAdapter

from . import deps


def get_minumtium_fastapi(database_adapter_posts: DatabaseAdapter = None,
                          database_adapter_users: DatabaseAdapter = None,
                          authentication_adapter: AuthenticationAdapter = None,
                          include_user_endpoints=True):
    """
    Creates a FastAPI instance for the minumtium_fastapi application that can either be started as an stand-alone
    application using a wrapper like or can be integrated as a sub-app into a bigger fastapi application.

    :param authentication_adapter: an adapter that implements the AuthenticationAdapter interface.
    :param database_adapter_users: an adapter that implements the DatabaseAdapter interface and is setup to use the
                                   'users' table/collection.
    :param database_adapter_posts: an adapter that implements the DatabaseAdapter interface and is setup to use the
                                   'posts' table/collection.
    :param include_user_endpoints: defines if the user management endpoints should be added to the minumtium_fastapi
                                   application routes. It can be suppressed if you are using a custom authentication
                                   adapter and do not need the minumtium_fastapi user management features.
    :return: an instance of FastAPI that can be embedded into another FastAPI app, or run stand-alone using a wrapper
             like uvicorn.
    """
    from fastapi import FastAPI
    from .routes.posts import posts_router
    from .routes.auth import auth_router

    deps.clean_context()

    minumtium = FastAPI()

    if database_adapter_posts:
        deps.inject_into_context(deps.database_adapter_posts, database_adapter_posts)

    if database_adapter_users:
        deps.inject_into_context(deps.database_adapter_users, database_adapter_users)

    if authentication_adapter:
        deps.inject_into_context(deps.auth_adapter, authentication_adapter)

    minumtium.include_router(posts_router)
    minumtium.include_router(auth_router)

    if include_user_endpoints:
        from .routes.users import users_router
        minumtium.include_router(users_router)

    return minumtium
