from pydantic import BaseModel
from jwtserver.app import app
from fastapi import Response


class LogoutResponseModel(BaseModel):
    status: str


@app.get("/api/v1/logout/", response_model=LogoutResponseModel, tags=["Authorization"],
         description="Removes token from cookie")
async def logout(response: Response):
    """If the exit, delete the token and that's it
    :param response: fastapi.Response
    :return LogoutResponse
    """
    response.delete_cookie(key='refresh_token')
    return {"status": 'logout'}
