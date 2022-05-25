from simple_rest_client.api import API
from simple_rest_client.resource import Resource
from vgscli._version import __version__
import vgscli.accounts_api as accounts_api


class RouteResource(Resource):
    actions = {
        'retrieve': {'method': 'GET', 'url': 'rule-chains/{}'},
        'create': {'method': 'POST', 'url': 'rule-chains'},
        'list': {'method': 'GET', 'url': 'rule-chains'},
        'delete': {'method': 'DELETE', 'url': 'rule-chains/{}'},
        'update': {'method': 'PUT', 'url': 'rule-chains/{}'},
    }


def create_api(ctx, vault_id, environment, token):
    api = API(
        api_root_url=__resolve_api_url(ctx, vault_id, environment, token),
        params={},  # default params
        headers={
            'VGS-Tenant': vault_id,
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json',
            'User-Agent': 'VGS CLI {}'.format(__version__),
            'Authorization': 'Bearer {}'.format(token)
        },  # default headers
        timeout=50,  # default timeout in seconds
        append_slash=False,  # append slash to final url
        json_encode_body=True,  # encode body as json
    )
    api.add_resource(resource_name='routes', resource_class=RouteResource)
    return api


def __resolve_api_url(ctx, vault_id, environment, token):
    vault_management_api = accounts_api.create_api(token, environment)
    return accounts_api.get_api_url(ctx, vault_id, vault_management_api)
