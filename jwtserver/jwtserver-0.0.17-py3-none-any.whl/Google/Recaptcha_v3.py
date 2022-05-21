import httpx
from typing import Literal
from loguru import logger
from fastapi import HTTPException, Body
from pydantic import BaseModel
from starlette import status


class RecaptchaConfig(BaseModel):
    secret_key: str
    score: float
    for_tests: bool


class Recaptcha:
    """Recaptcha v3
    :raises HTTPException:
    https://www.google.com/recaptcha/admin/create"""

    def __init__(self, _config, recaptcha_token, environment):
        self.config: RecaptchaConfig = _config
        self.environment = environment
        self.action_name = None
        self.success = False
        self.action_valid = False
        self.r_json = None
        self.recaptcha_token = recaptcha_token

    def set_action_name(self, name) -> 'Recaptcha':
        """Set google action name"""
        self.action_name = name
        return self

    async def greenlight(self) -> Literal[True]:
        """If the recaptcha is ok, then the light is green.
        our minimum checks
        :return: True or raise HTTPException
        """

        def bad_request(detail: str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail,
            )

        await self.check()
        if not self.r_json['success']:
            logger.critical("invalid reCAPTCHA token")
            bad_request('server error: invalid reCAPTCHA token for your site')

        if not self.r_json['action'] == self.action_name:
            bad_request('hm... u r hacker?')

        if self.r_json['score'] <= self.config.score:
            bad_request('hm... u r bot?')

        return True

    async def check(self) -> 'Recaptcha':
        """send post and save response json to self.r_json"""
        if self.environment == 'tests':
            self.r_json = {
                "success": self.recaptcha_token.split(":")[0],
                "action": self.recaptcha_token.split(":")[1],
                "score": float(self.recaptcha_token.split(":")[2]),
            }
            return self
        data = {
            'secret': self.config.secret_key,
            'response': self.recaptcha_token,
        }
        async with httpx.AsyncClient() as client:
            r: httpx.Response = await client.post(
                'https://www.google.com/recaptcha/api/siteverify', data=data)
            self.r_json = r.json()
        return self
