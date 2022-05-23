import logging


from typing import Callable, Any

from functools import wraps

from flask import make_response, Response, request
from flask_login import current_user  # type: ignore


from JuMonC import settings
from JuMonC.authentication import tokens


logger = logging.getLogger(__name__)


def check_auth(neededScope: int) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    def no_auth() -> Response:
        return make_response("You are not allowed to access this link, login using `/login` and your token. You can see the access level "
                             + "allowed with your token using `/scope` or supply a valid token using the token parameter", 401)
    
    def wrap(func: Callable[..., Response]) -> Callable[..., Response]:
        @wraps(func)
        def decorated_function(*args: Any, **kwargs: Any) -> Response:
            if settings.ENABLE_AUTH:
                # see if a token is supplied for this action
                token = request.args.get('token', default = None, type = str)
                if token is not None:
                    temp_user = tokens.getTokenScope(token)
                    if temp_user is not None and hasattr(temp_user,'id'):
                        if  tokens.tokens[temp_user.id] >= neededScope:
                            logging.debug("scope_temp_user: %s" , str(tokens.tokens[temp_user.id]))
                            logging.debug("scopeNeeded: %s", str(neededScope))
                            return func(*args, **kwargs)
                # see if the user is signed in
                if hasattr(current_user, 'id'):
                    if tokens.tokens[current_user.id] >= neededScope:
                        logging.debug("scope_logined_user: %s", str(tokens.tokens[current_user.id]))
                        logging.debug("scopeNeeded: %s", str(neededScope))
                        return func(*args, **kwargs)
                return no_auth()
            return func(*args, **kwargs)
            
        return decorated_function
    return wrap