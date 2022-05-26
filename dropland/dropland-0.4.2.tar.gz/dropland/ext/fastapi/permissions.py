from abc import ABC
from typing import List

from fastapi import HTTPException, params
from starlette import status
from starlette.requests import Request

from dropland.permissions import BasePermission, PermissionChecker, PermissionType


class HttpPermission(BasePermission, ABC):
    error_msg = 'Forbidden'
    status_code = status.HTTP_403_FORBIDDEN


class PermDepends(params.Depends, PermissionChecker):
    def __init__(self, permissions: List[PermissionType]):
        params.Depends.__init__(self, dependency=self.__call__)
        PermissionChecker.__init__(self, permissions)

    def __call__(self, request: Request):
        res, error_callable = super().__call__(request)
        if not res:
            if isinstance(error_callable, HttpPermission):
                raise HTTPException(status_code=error_callable.status_code, detail=error_callable.error_msg)
            else:
                raise HTTPException(status_code=HttpPermission.status_code, detail=HttpPermission.error_msg)


class Authenticated(HttpPermission):
    error_msg = 'You must be authenticated'

    @classmethod
    def has_permissions(cls, request: Request):
        return request.user.is_authenticated


class Admin(HttpPermission):
    error_msg = 'Admin area'
    depends_on = [Authenticated]

    @classmethod
    def has_permissions(cls, request: Request):
        return bool(request.user.admin)
