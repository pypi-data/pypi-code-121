import asyncio
from aiohttp import ClientSession, ClientResponse
import warnings

from .errors import *
from .rate_limits import BucketHandler, ClientRateLimits
from .paths import Paths

class DiscordClient(Paths):
    """
    Parameters
    ----------
    token : str
        The token to use for the request.
    token_type : str, optional
        The type of token provided, by default 'bot'
    prevent_rate_limits : bool, optional
        Whether the client will sleep through ratelimits to prevent 429 errors, by default True
    retry_rate_limits : bool, optional
        Whether the client will sleep and retry after 429 errors, by default True
    api_version : int, optional
        The Discord API version to use, by default 9
    """  
    
    def __init__(self, token: str, token_type: str = 'bot', prevent_rate_limits: bool = True, retry_rate_limits: bool = True, api_version: int = 9):      
        super().__init__(self)
        if token_type == 'bot':
            self.token = f"Bot {token}"
            self.token_type = token_type
        elif token_type == 'bearer':
            self.token = f"Bearer {token}"
            self.token_type = token_type
        elif token_type == 'user':
            warnings.warn("Use a user token at your own risk as (depending on your usage) it could be against Discord's ToS. If you are using this token for a bot, you should use the 'bot' token_type instead.", UserWarning)
            self.token = f"{token}"
            self.token_type = token_type
        else:
            self.token = None
            self.token_type = None

        self._prevent_rate_limits = prevent_rate_limits
        self._retry_rate_limits = retry_rate_limits
        self.rate_limits = ClientRateLimits(prevent_rate_limits=prevent_rate_limits)
        self._base_url = f"https://discord.com/api/v{api_version}"
        self._base_url_len = len(self._base_url)

    def _set_token(self, token: str, token_type: str = 'bot'):
        if token_type == 'bot':
            self.token = f"Bot {token}"
        elif token_type == 'bearer':
            self.token = f"Bearer {token}"
        elif token_type == 'user':
            warnings.warn("Use a user token at your own risk as (depending on your usage) it could be against Discord's ToS. If you are using this token for a bot, you should use the 'bot' token_type instead.", UserWarning)
            self.token = f"{token}"
        else:
            self.token = None

    def _get_bucket_handler(self, bucket: str):
        bucket_handler = self.rate_limits.buckets.get(bucket)
        if bucket_handler is None:
            bucket_handler = self.rate_limits.buckets[bucket] = BucketHandler(bucket=bucket)
        return bucket_handler

    async def _request(self, method: str, path: str, bucket: str, headers: dict = None, json: dict = None, params: dict = None, auth: bool = True):
        if auth:
            if self.token_type is None:
                raise InvalidParams("No token has been set. Please set the auth parameter to False or set a token with _set_token().")
            if headers is None:
                headers = {'Authorization': self.token}
            else:
                headers['Authorization'] = self.token
        cs = ClientSession()
        
        url = self._base_url + path

        request_manager = cs.request(method, url, json=json, params=params, headers=headers)

        bucket_handler = self._get_bucket_handler(bucket)
        bucket_handler.prevent_429 = self._prevent_rate_limits
        async with self.rate_limits.global_limiter:
            async with bucket_handler as bh:
                async with cs:
                    r = await request_manager
                    bh.check_limit_headers(r)  # sets up the bucket rate limit attributes w/ response headers
                    response_data = await r.json()
                try:
                    if await self._check_response(response=r, bucket=bucket):
                        return r
                except TooManyRequests as e:
                    if self._retry_rate_limits is True:
                        timeout = response_data['retry_after'] / 1000 + 1
                        await asyncio.sleep(timeout)
                        # reschedule same request
                        return await self._request(method, path, bucket, headers=headers, json=json, params=params, auth=auth)
                    else:
                        raise e
                except NotFound as e:
                    raise e
                except UnknownError as e:
                    raise e

    async def _check_response(self, response: ClientResponse, bucket: str):
        """Checks API response for errors. Returns True only on 300 > status >= 200"""
        status = response.status
        reason = response.reason
        data = await response.json()

        if 300 > status >= 200:
            return True
        elif status == 429:
            message = data['message']
            if 'global' in data:
                text = f"Global rate limit. {data['message']}"
            elif retry_after == data.get('retry_after'):
                retry_after = int(retry_after) / 1000
                bucket_handler = self._get_bucket_handler(bucket)
                bucket_handler.retry_after = retry_after
                text = f"{message} retry after: {retry_after}s"
            else:
                text = f"{message}"
            raise TooManyRequests(text + f', bucket: {bucket}')
        elif status == 400:
            raise BadRequest(f'Error Code: "{status}" Reason: "{reason}", bucket {bucket}')
        elif status == 401:
            raise Unauthorized(f'Error Code: "{status}" Reason: "{reason}", bucket {bucket}')
        elif status == 403:
            raise Forbidden(f'Error Code: "{status}" Reason: "{reason}", bucket {bucket}')
        elif status == 404:
            raise NotFound(f'Error Code: "{status}" Reason: "{reason}", bucket {bucket}')
        elif status == 500:
            raise InternalServerError(f'Error Code: "{status}" Reason: "{reason}", bucket {bucket}')
        else:
            error_text = f'Error code: "{status}" Reason: "{reason}"'
            if status in api_errors:
                raise api_errors[status](error_text)
            else:
                raise UnknownError(error_text)
