import re

from nsj_gcf_utils.app_logger import logger
from typing import List


class Router:
    from functools import partialmethod

    def __init__(self, authentication_service=None, nsj_authentication_service=None):
        self.routes = []
        self.authentication_service = authentication_service
        self.nsj_authentication_service = nsj_authentication_service

    def add(self, path, authentication_fn, methods=['GET', 'POST'], required_pars: List[str] = None, allowed_clients: List[str] = None, required_query_args: List[str] = None):
        def route_function(function):
            # Making a regex to path
            regex_path = path.replace('/', '\/')
            matcher = re.compile('(\{([\w-]+)\})')
            args = matcher.findall(regex_path)
            path_args = []
            for arg in args:
                regex_path = regex_path.replace(arg[0], '([\w-]+)')
                path_args.append(arg[1])

            regex_path = '^' + regex_path + '$'

            # Registering path
            route = {
                'path': path,
                'regex_path': regex_path,
                'methods': methods,
                'callable': function,
                'authentication_fn': authentication_fn,
                'required_pars': required_pars,
                'path_args': path_args,
                'allowed_clients': allowed_clients,
                'required_query_args': required_query_args}
            self.routes.append(route)
            return function
        return route_function

    def verify_api_key(self, request) -> str:
        """
        Returns the app_client id, if api_key is valid, or None otherwise.
        """

        api_key = request.headers.get('X-API-Key')

        if api_key is None or api_key == '':
            logger.info("No API Key Provided.")
            return None

        if self.authentication_service is None:
            return None

        return self.authentication_service.verify_api_key(api_key)

    def verify_access_token(self, request) -> str:
        """
        Returns a dict with token info, if access_token is valid, or None otherwise.
        """

        access_token = request.headers.get('Authorization')

        if access_token is None or access_token == '':
            logger.info("No access_token Provided.")
            return None

        if self.nsj_authentication_service is None:
            return None

        return self.nsj_authentication_service.authenticate(access_token)

    def verify_api_key_or_access_token(self, request) -> str:
        """
        Returns api_key or access_token result
        """

        auth_info = self.verify_api_key(request)
        if auth_info is None:
            auth_info = self.verify_access_token(request)

        if auth_info is None or auth_info == '':
            logger.info("No API Key or access_token Provided.")
            return None

        return auth_info

    __call__ = partialmethod(
        add, authentication_fn=lambda self, request: 'not_auth_required')
    auth_api_key = partialmethod(
        add, authentication_fn=verify_api_key)
    auth_access_token = partialmethod(
        add, authentication_fn=verify_access_token)
    auth_api_key_or_access_token = partialmethod(
        add, authentication_fn=verify_api_key_or_access_token)

    def route(self, request):
        path = request.path
        logger.info(f'Routing to {path}')

        # Searching route using regex expression (each route is interpreted like a regex pattern)
        route = None
        path_args = []
        for r in self.routes:
            matcher = re.compile(r['regex_path'])
            match = matcher.search(path)

            if not match:
                continue

            if not request.method in r['methods']:
                continue

            route = r

            # Making a dict of path args (where each regex group is an argument)
            path_args = {}
            for i in range(0, matcher.groups):
                path_key = route['path_args'][i]
                path_args[path_key] = match.group(i+1)

            break

        # Checking if route exists
        if not route:
            return ('{"code": 404, "message": "Resource not found"}', 404, {})

        # Checking authentication
        auth_info = route['authentication_fn'](self, request)
        if not auth_info:
            return ('{"code", "401", "message": "Unauthorized."', 401, {})

        # Checking authorization
        if (
            auth_info != 'not_auth_required'
            and isinstance(auth_info, str)
            and route['allowed_clients']
            and not (auth_info in route['allowed_clients'])
        ):
            return ('{"code", "403", "message": "Forbidden. Client of X-API-Key has no access to this resource."', 403, {})

        # Checking if called HTTP method is acceptable
        if not request.method in route['methods']:
            return ('{"code": 405, "message": "Method not allowed"}', 405, {})

        # Checking required pars
        required_pars = route['required_pars']
        if required_pars:
            req_body = request.get_json()
            if not req_body:
                return ('{' + f'"code": 400, "message": "Missing parameters {required_pars}"' + '}', 400, {})

            missing_pars = []
            for par in required_pars:
                if not(par in req_body):
                    missing_pars.append(par)

            if len(missing_pars) > 0:
                return ('{' + f'"code": 400, "message": "Missing parameters: {missing_pars}"' + '}', 400, {})

        # Checking required query args
        required_query_args = route['required_query_args']
        if required_query_args:
            args = request.args
            if not args or len(args) <= 0:
                return ('{' + f'"code": 400, "message": "Missing query arguments {required_query_args}"' + '}', 400, {})

            missing_args = []
            for par in required_query_args:
                if not(par in args):
                    missing_args.append(par)

            if len(missing_args) > 0:
                return ('{' + f'"code": 400, "message": "Missing query arguments {missing_args}"' + '}', 400, {})

        # Returning original function handler
        if auth_info == 'not_auth_required':
            return route['callable'](request, **path_args)
        else:
            return route['callable'](request, auth_info, **path_args)
