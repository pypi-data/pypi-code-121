from typing import Any

from fastapi import Depends
from minumtium.infra.authentication import AuthenticationAdapter, AuthenticationService
from minumtium.infra.database import DatabaseAdapter
from minumtium.modules.idm import UserRepository, IdmService
from minumtium.modules.posts import PostRepository, PostService

context = {}


def inject_into_context(dependency_ref: Any, value: Any):
    context[dependency_ref] = value


def clean_context():
    global context
    context = {}


def __instantiate_database_adapter(table_name: str):
    from minumtium_sqlite import MinumtiumSQLiteAdapterConfig, MinumtiumSQLiteAdapter
    config = MinumtiumSQLiteAdapterConfig(schema_name='minumtium')
    return MinumtiumSQLiteAdapter(config, table_name)


async def database_adapter_posts() -> DatabaseAdapter:
    if database_adapter_posts not in context:
        context[database_adapter_posts] = __instantiate_database_adapter('posts')
    return context[database_adapter_posts]


async def posts_repository(adapter: DatabaseAdapter = Depends(database_adapter_posts)) -> PostRepository:
    if posts_repository not in context:
        context[posts_repository] = PostRepository(adapter)
    return context[posts_repository]


async def posts_service(repo: PostRepository = Depends(posts_repository)) -> PostService:
    if posts_service not in context:
        context[posts_service] = PostService(repo)
    return context[posts_service]


async def database_adapter_users() -> DatabaseAdapter:
    if database_adapter_users not in context:
        context[database_adapter_users] = __instantiate_database_adapter('users')
    return context[database_adapter_users]


async def user_repo(adapter: DatabaseAdapter = Depends(database_adapter_users)):
    if user_repo not in context:
        context[user_repo] = UserRepository(adapter)
    return context[user_repo]


async def auth_adapter(adapter: DatabaseAdapter = Depends(database_adapter_users)):
    if auth_adapter not in context:
        from minumtium_simple_jwt_auth import MinumtiumSimpleJwtAuthentication, MinumtiumSimpleJwtAuthenticationConfig
        config = MinumtiumSimpleJwtAuthenticationConfig(jwt_key='not a reliable key, change that quickly',
                                                        session_duration_hours=1)
        context[auth_adapter] = MinumtiumSimpleJwtAuthentication(config, adapter)
    return context[auth_adapter]


async def auth_service(adapter: AuthenticationAdapter = Depends(auth_adapter)):
    if auth_service not in context:
        context[auth_service] = AuthenticationService(adapter)
    return context[auth_service]


async def idm_service(adapter: AuthenticationAdapter = Depends(auth_adapter),
                      repository: UserRepository = Depends(user_repo)):
    if idm_service not in context:
        context[idm_service] = IdmService(adapter, repository)
    return context[idm_service]
