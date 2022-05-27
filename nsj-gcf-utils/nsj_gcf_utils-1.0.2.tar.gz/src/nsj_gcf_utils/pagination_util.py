import urllib.parse
import uuid

from nsj_gcf_utils.exception import PaginationException
from typing import Any, List


def page_body(
    base_url: str,
    limit: int,
    current_after: uuid.UUID,
    current_before: uuid.UUID,
    result: List[Any],
    id_field: str = 'id'
):

    if current_after is not None and current_before is None:
        return _page_body_after(
            base_url=base_url,
            limit=limit,
            current_after=current_after,
            result=result,
            id_field=id_field
        )
    elif current_after is None and current_before is not None:
        return _page_body_before(
            base_url=base_url,
            limit=limit,
            current_before=current_before,
            result=result,
            id_field=id_field
        )
    elif current_after is not None and current_before is not None:
        raise PaginationException(
            'Não é permitido usar os parâmetros "after" (ou "offset") e "before" simultâneamente.')

    # Checking has next and previous
    has_next = len(result) >= limit

    # Preparing previous and next URLs
    url = base_url
    if '?' in base_url:
        url += '&'
    else:
        url += '?'

    last = -1 if limit >= len(result) else limit-1
    if has_next:
        params_next = {
            'after': result[last][id_field],
            'limit': limit
        }
        params_next = urllib.parse.urlencode(params_next, doseq=True)
        url_next = url + params_next
    else:
        url_next = None

    url_previous = None

    # Returning pagination body
    return {
        'next': url_next,
        'prev': url_previous,
        'result': result[0:limit]
    }


def _page_body_after(
    base_url: str,
    limit: int,
    current_after: uuid.UUID,
    result: List[Any],
    id_field: str = 'id'
):
    # Checking has next and previous
    has_next = len(result) >= limit
    has_prev = True

    # Preparing previous and next URLs
    url = base_url
    if '?' in base_url:
        url += '&'
    else:
        url += '?'

    last = -1 if limit >= len(result) else limit-1
    if has_next:
        params_next = {
            'after': result[last][id_field],
            'limit': limit
        }
        params_next = urllib.parse.urlencode(params_next, doseq=True)
        url_next = url + params_next
    else:
        url_next = None

    if has_prev:
        params_prev = {
            'before': current_after,
            'limit': limit
        }
        params_prev = urllib.parse.urlencode(params_prev, doseq=True)
        url_previous = url + params_prev
    else:
        url_previous = None

    # Returning pagination body
    return {
        'next': url_next,
        'prev': url_previous,
        'result': result[0:limit]
    }


def _page_body_before(
    base_url: str,
    limit: int,
    current_before: uuid.UUID,
    result: List[Any],
    id_field: str = 'id'
):
    # Checking has next and previous
    has_next = True
    has_prev = len(result) >= limit

    # Preparing previous and next URLs
    url = base_url
    if '?' in base_url:
        url += '&'
    else:
        url += '?'

    if has_next:
        params_next = {
            'after': current_before,
            'limit': limit
        }
        params_next = urllib.parse.urlencode(params_next, doseq=True)
        url_next = url + params_next
    else:
        url_next = None

    first = 0 if limit > len(result) else -1*limit
    if has_prev:
        params_prev = {
            'before': result[first][id_field],
            'limit': limit
        }
        params_prev = urllib.parse.urlencode(params_prev, doseq=True)
        url_previous = url + params_prev
    else:
        url_previous = None

    # Returning pagination body
    return {
        'next': url_next,
        'prev': url_previous,
        'result': result[first:]
    }
