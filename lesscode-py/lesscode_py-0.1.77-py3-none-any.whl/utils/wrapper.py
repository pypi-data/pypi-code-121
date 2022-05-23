import functools
import json

import tornado.options

from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode


def user_verification(username="admin", **kw):
    def wrapper(func):
        @functools.wraps(func)
        async def run(self, *args, **kwargs):
            if tornado.options.options.running_env != "local":
                user_str = self.request.headers.get("User")
                if user_str:
                    user = json.loads(user_str)
                    if isinstance(user, dict):
                        user_username = user.get("username")
                        if username != user_username:
                            raise BusinessException(StatusCode.ACCESS_DENIED)
                    else:
                        raise BusinessException(StatusCode.ACCESS_DENIED)
                else:
                    raise BusinessException(StatusCode.ACCESS_DENIED)

            return await func(self, *args, **kwargs)

        return run

    return wrapper
