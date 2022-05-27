from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from minumtium.infra.authentication import AuthenticationService, AuthenticationException
from pydantic import BaseModel

from ..deps import auth_service

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str


@auth_router.post('/login', response_model=AuthResponse)
async def login(login_data: AuthRequest, service: AuthenticationService = Depends(auth_service)):
    try:
        token = service.authenticate(login_data.username, login_data.password)
        return AuthResponse(token=token)
    except AuthenticationException as e:
        raise HTTPException(status_code=401, detail=str(e))
