import os
import json
import traceback
from concurrent.futures import ThreadPoolExecutor

from hestia_earth.extend_bibliography.log import logger
from hestia_earth.extend_bibliography.utils import current_time_ms
from .utils import has_key, MAXIMUM_DISTANCE, find_closest_result, remove_empty_values
import hestia_earth.extend_bibliography.bibliography_apis.mendeley_api.client as mendeley_api_client
import hestia_earth.extend_bibliography.bibliography_apis.mendeley_sdk.client as mendeley_sdk_client


DEFAULT_KEY = 'title'
MAX_TITLE_BY_API = int(os.getenv('MENDELEY_API_LIMIT', '20'))


def extend_title(functions, searcher, key, bibliographies, actors):
    def extend(value: str):
        now = current_time_ms()
        [item, distance] = find_closest_result(value, searcher) if key == DEFAULT_KEY else [searcher(value), 0]
        logger.debug('find by %s in %sms: %s', key, current_time_ms() - now, value)
        (biblio, authors) = functions.create_biblio(item if distance <= MAXIMUM_DISTANCE else None, key, value)
        logger.debug('found bibliography: %s', json.dumps(biblio, indent=2))
        bibliographies.extend([] if biblio is None else [biblio])
        actors.extend([] if authors is None else authors)
    return extend


def extend_mendeley(functions, client, values, key=DEFAULT_KEY):
    try:
        bibliographies = []
        actors = []

        extender = extend_title(functions, functions.exec_search(client, key), key, bibliographies, actors)
        with ThreadPoolExecutor() as executor:
            executor.map(extender, values)

        return (remove_empty_values(actors), remove_empty_values(bibliographies))
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())
        return ([], [])


def get_client(num_values: int, **kwargs):
    use_api = num_values < MAX_TITLE_BY_API and has_key('mendeley_api_url', **kwargs)
    mendeley_client = mendeley_api_client if use_api else mendeley_sdk_client
    return mendeley_client, mendeley_client.get_client(**kwargs)
