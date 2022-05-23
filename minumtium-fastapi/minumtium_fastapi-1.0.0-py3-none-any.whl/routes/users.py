from typing import List

from fastapi import APIRouter, Depends, HTTPException
from minumtium.modules.idm import (IdmService,
                                   InvalidPasswordException,
                                   EmptyUsernameException,
                                   UserDoesNotExistException)
from pydantic import BaseModel

from ..auth import authenticate
from ..deps import idm_service

users_router = APIRouter(
    prefix='/users',
    tags=['users']
)


class ListUsersResponse(BaseModel):
    users: List


@users_router.get('/', response_model=ListUsersResponse, status_code=200, dependencies=[Depends(authenticate)])
async def list_users(service: IdmService = Depends(idm_service)):
    try:
        users = service.get_all_users_list()
        return ListUsersResponse(users=users)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AddUserRequest(BaseModel):
    username: str
    password: str


class AddUserResponse(BaseModel):
    username: str
    updated: bool


@users_router.put('/', response_model=AddUserResponse, status_code=201, dependencies=[Depends(authenticate)])
async def put_user(request: AddUserRequest, service: IdmService = Depends(idm_service)):
    try:
        updated = service.put_user(request.username, request.password)
        return AddUserResponse(username=request.username, updated=updated)
    except (InvalidPasswordException, EmptyUsernameException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DeleteUserResponse(BaseModel):
    username: str


@users_router.delete('/{username}', response_model=DeleteUserResponse, status_code=200,
                     dependencies=[Depends(authenticate)])
async def delete_user(username: str, service: IdmService = Depends(idm_service)):
    try:
        service.delete_user(username)
        return DeleteUserResponse(username=username)
    except (EmptyUsernameException, UserDoesNotExistException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
