import os

from .config import ConfigFileParser
from .matchers import matcher_classes


class RequestHeaderMatcher:
    def __init__(self, name: str, value: str, value_matcher: str) -> None:
        self.name = name.lower()  # RFC 2616
        self.matcher = matcher_classes[value_matcher](value)

    def matches(self, name: str, value: str) -> bool:
        has_name_match = self.name == name.lower()
        has_value_match = self.matcher.matches(value)
        has_match = has_name_match and has_value_match
        return has_match


class RequestQueryParameterMatcher:
    def __init__(self, name: str, value: str, value_matcher: str) -> None:
        self.name = name
        self.matcher = matcher_classes[value_matcher](value)

    def matches(self, name: str, value: str) -> bool:
        has_name_match = self.name == name
        has_value_match = self.matcher.matches(value)
        has_match = has_name_match and has_value_match
        return has_match


class RequestBodyMatcher:
    def __init__(self, value: str, value_matcher: str) -> None:
        self.matcher = matcher_classes[value_matcher](value)

    def matches(self, value: str) -> bool:
        has_match = self.matcher.matches(value)
        return has_match


class AnyRequestBodyMatcher(RequestBodyMatcher):
    def __init__(self):
        self.matcher = None

    def matches(self, value: str) -> bool:
        return True


class RequestMatcher:
    def __init__(self,
                 path: str,
                 method: str,
                 headers: 'list[RequestHeaderMatcher]',
                 query: 'list[RequestQueryParameterMatcher]',
                 body: RequestBodyMatcher) -> None:
        self.path = path
        self.method = method
        self.headers = headers
        self.query = query
        self.body = body

    def matches(self, path: str, method: str, headers: 'dict[str, str]', query: 'dict[str, str]', body: str) -> bool:
        has_path_match = self.path == path
        has_method_match = self.method == method
        has_headers_match = self.__matches_headers(headers)
        has_query_match = self.__matches_query(query)
        has_body_match = self.body.matches(body)
        has_match = (
                has_path_match
                and has_method_match
                and has_headers_match
                and has_query_match
                and has_body_match
        )
        return has_match

    def __matches_headers(self, headers: 'dict[str, str]'):
        has_match = True
        for header in self.headers:
            if not any(header.matches(name, value) for (name, value) in headers.items()):
                has_match = False
                break
        return has_match

    def __matches_query(self, query: 'dict[str, str]'):
        has_match = True
        for param in self.query:
            if not any(param.matches(name, value) for (name, value) in query.items()):
                has_match = False
                break
        return has_match


class StubResponse:
    def __init__(self, status: int, headers: 'dict[str, str]' = None, body: str = None) -> None:
        if headers is None:
            headers = {}

        if body is None:
            body = ''

        self.status = status
        self.headers = headers
        self.body = body

    @classmethod
    def make_default(cls) -> 'StubResponse':
        status = 418  # I'm a teapot
        headers = {'Content-Type': 'text/html'}
        body = '<!DOCTYPE html>' \
               '<html>' \
               '<body>' \
               '<h1>Default simulation</h1>' \
               '<p>You are seeing this page because simulator could not find a suitable simulation.</p>' \
               '</body>' \
               '</html>' \
               '\n'
        return cls(status, headers, body)


class Simulation:
    def __init__(self, request_matcher: RequestMatcher, stub_response: StubResponse) -> None:
        self.request_matcher = request_matcher
        self.stub_response = stub_response

    @classmethod
    def from_config(cls, path: str) -> 'Simulation':
        parsed_config = ConfigFileParser.parse(path)
        request = parsed_config['request']
        response = parsed_config['response']

        request_path = request['path']
        request_method = request['method']

        request_headers = request.get('headers') or []
        request_query = request.get('query') or []
        request_body = request.get('body')

        request_headers_matchers = [
            RequestHeaderMatcher(**request_header) for request_header in request_headers
        ]
        request_query_matchers = [
            RequestQueryParameterMatcher(**request_query_matcher) for request_query_matcher in request_query
        ]
        if request_body is not None:
            request_body_matcher = RequestBodyMatcher(**request_body)
        else:
            request_body_matcher = AnyRequestBodyMatcher()

        request_matcher = RequestMatcher(
            request_path,
            request_method,
            request_headers_matchers,
            request_query_matchers,
            request_body_matcher,
        )

        if response.get('headers') is not None:
            response['headers'] = {item['name']: item['value'] for item in response['headers']}

        stub_response = StubResponse(**response)

        return cls(request_matcher, stub_response)

    def matches(self, path: str, method: str, headers: 'dict[str, str]', query: 'dict[str, str]', body: str) -> bool:
        has_match = self.request_matcher.matches(path, method, headers, query, body)
        return has_match


class WebApiSimulator:
    def __init__(self, simulations: 'list[Simulation]') -> None:
        self._simulations: 'list[Simulation]' = simulations

    @classmethod
    def from_simulations_directory(cls, directory: str) -> 'WebApiSimulator':
        simulations = []
        for filename in os.listdir(directory):
            absolute_path = os.path.join(directory, filename)
            if os.path.isfile(absolute_path):
                simulation = Simulation.from_config(absolute_path)
                simulations.append(simulation)

        return cls(simulations)

    def request(self,
                path: str,
                method: str,
                url_params: 'dict[str, str]',
                headers: 'dict[str, str]', body: str) -> 'tuple[int, dict[str, str], str]':
        stub_response = None

        for simulation in self._simulations:
            if simulation.matches(path, method, headers, url_params, body):
                stub_response = simulation.stub_response
                break

        if stub_response is None:
            stub_response = StubResponse.make_default()

        return (
            stub_response.status,
            stub_response.headers,
            stub_response.body,
        )
