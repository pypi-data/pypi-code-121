from pydantic import BaseModel, ValidationError, validator

from . import exceptions
from .utils import camelcase

__all__ = ["require"]


class FlatInputData(BaseModel):
    pass


class InputData(FlatInputData):
    class Config:
        alias_generator = camelcase
        # arbitrary_types_allowed = True

    def __contains__(self, attr):
        return attr in self.dict(exclude_unset=True)


class Require:

    FlatInputData = FlatInputData
    InputData = InputData

    def __init__(self):
        pass

    def data(
        self,
        input=InputData,
        output=None,
    ):
        def wrapper(wrapped_handle):
            async def handle(event, **kwargs):
                if input:
                    try:
                        if isinstance(event.data, dict):
                            input_data: InputData = input(**event.data)
                            output_data = await wrapped_handle(
                                event, input=input_data, **kwargs
                            )
                        else:
                            input_data_str: str = event.data
                            output_data = await wrapped_handle(
                                event, input=input_data_str, **kwargs
                            )
                    except ValidationError as e:
                        raise exceptions.BadRequest(e)
                else:
                    output_data = await wrapped_handle(event, **kwargs)

                return output_data

            return handle

        return wrapper

    def user(
        self,
        is_authenticated=None,
        is_verified=None,
        is_anonymous=None,
        is_superadmin=None,
        is_admin=None,
        is_staff=None,
        perms=None,
    ):
        def wrapper(handle):
            async def new_handle(event, **kwargs):

                if is_authenticated is not None:
                    if is_authenticated != event.user.is_authenticated:
                        raise exceptions.NotAuthorized(
                            "insufficient permissions"
                        )

                if is_anonymous is not None:
                    if is_anonymous != event.user.is_anonymous:
                        raise exceptions.NotAuthorized(
                            "insufficient permissions"
                        )

                if is_verified is not None:
                    if is_verified != event.user.is_verified:
                        raise exceptions.NotAuthorized(
                            "insufficient permissions"
                        )

                if is_staff is not None:
                    if is_staff != event.user.is_staff:
                        raise exceptions.NotAuthorized(
                            "insufficient permissions"
                        )

                if is_admin is not None:
                    if is_admin != event.user.is_admin:
                        raise exceptions.NotAuthorized(
                            "insufficient permissions"
                        )

                if is_superadmin is not None:
                    if is_superadmin != event.user.is_superadmin:
                        raise exceptions.NotAuthorized(
                            "insufficient permissions"
                        )

                if perms is not None:
                    if not set(perms).intersection(event.user.perms):
                        raise exceptions.NotAuthorized(
                            "insufficient permissions"
                        )
                return await handle(event, **kwargs)

            return new_handle

        return wrapper


require = Require()
