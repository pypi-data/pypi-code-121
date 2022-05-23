from typing import Optional, Dict, Tuple


from flask import Request
from flask_login import UserMixin  # type: ignore


from JuMonC.handlers import base
from JuMonC.helpers.generateToken import generateToken
from JuMonC.authentication import scopes, scope_name
from JuMonC import settings


        
def parseUserToken(text: str) -> Tuple[str,int]:
    parts = text.split(":")
    return (parts[0], int(parts[1]))


tokens: Dict[str,int]= {}


if settings.USER_DEFINED_TOKEN is not None:
    user_tokens = settings.USER_DEFINED_TOKEN.split(";")
    for user_token in user_tokens:
        (token, scope) = parseUserToken(user_token)
        tokens[token] = scope


for scope in scopes.values():
    while True:
        token = generateToken()
        if token in tokens:
            pass
        break
    tokens[token] = scope
        



for (token, scope) in tokens.items():
    print(scope_name[scope] + ": " + token)

class Authenticated(UserMixin):
    pass



@base.login_manager.user_loader
def user_loader(tokenScope: str) -> Optional[Authenticated]:
    if tokenScope not in tokens:
        return None

    auth = Authenticated()
    auth.id = tokenScope
    return auth


def getTokenScope(token: Optional[str]) -> Optional[Authenticated]:
    if token not in tokens:
        return None
    
    auth = Authenticated()
    auth.id = token
    
    #auth.is_authenticated = True
    
    return auth


@base.login_manager.request_loader
def request_loader(request: Request) -> Optional[Authenticated]:
    token = request.args.get('token', default = None, type = str)
    return getTokenScope(token)


@base.login_manager.unauthorized_handler
def unauthorized_handler() -> str:
    return 'Unauthorized'