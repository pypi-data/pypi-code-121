from simple_rest_client import exceptions

from vgscli.errors import RouteNotValidError
from vgscli.serializers import dump_yaml, update_and_normalize, Literal


def dump_all_routes(api):
    result = api.routes.list()
    body = result.body

    results = normalize(body['data'])

    updated = {
        'version': 1,
        'data': results,
    }

    return dump_yaml(updated)


def sync_all_routes(api, dump_data, route_process_listener=None):
    try:
        route_update_response = update_and_normalize(dump_data,
                                                     route_process_listener,
                                                     lambda route_id, payload: api.routes.update(route_id, body=payload),
                                                     normalize)
        return route_update_response
    except exceptions.ClientError as e:
        error_msg = '\n'.join([error['detail'] for error in e.response.body['errors']])
        raise RouteNotValidError(error_msg)


def normalize(results):
    # https://stackoverflow.com/a/8641732/6084
    # this `literal` function will ensure that we get a multi line string
    for result in results:
        if 'attributes' not in result:
            continue

        for filter_item in result['attributes']['entries']:
            if isinstance(filter_item['operations'], str):
                filter_item['operations'] = Literal(filter_item['operations'])
    return results
