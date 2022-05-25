import json
import traceback
from concurrent.futures import ThreadPoolExecutor

from hestia_earth.extend_bibliography.log import logger
from hestia_earth.extend_bibliography.utils import current_time_ms
from .utils import has_key, MAXIMUM_DISTANCE, find_closest_result, remove_empty_values
import hestia_earth.extend_bibliography.bibliography_apis.wos_rest.client as wos_rest_client
import hestia_earth.extend_bibliography.bibliography_apis.wos_soap.client as wos_soap_client


def extend_title(client, searcher, bibliographies, actors):
    def extend(title: str):
        now = current_time_ms()
        [item, distance] = find_closest_result(title, searcher)
        logger.debug('find in %sms: %s', current_time_ms() - now, title)
        (biblio, authors) = client.create_biblio(title, item if distance <= MAXIMUM_DISTANCE else None)
        logger.debug('found bibliography: %s', json.dumps(biblio, indent=2))
        bibliographies.extend([] if biblio is None else [biblio])
        actors.extend([] if authors is None else authors)
    return extend


def extend_wos(titles, **kwargs):
    try:
        wos_client = wos_rest_client if has_key('wos_api_key', **kwargs) else wos_soap_client

        bibliographies = []
        actors = []

        with wos_client.get_client(**kwargs) as client:
            extender = extend_title(wos_client, wos_client.exec_search(client), bibliographies, actors)
            with ThreadPoolExecutor() as executor:
                executor.map(extender, titles)

        return (remove_empty_values(actors), remove_empty_values(bibliographies))
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())
        return ([], [])
