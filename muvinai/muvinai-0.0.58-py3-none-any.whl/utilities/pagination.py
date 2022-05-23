from flask_restful import abort


def construct_pagination(results, url, page, limit, count):
    start = ((page - 1) * limit) + 1
    if count < start or limit < 0:
        abort(400, message="No hay resultados.")
    pagination = dict()
    pagination["data"] = results
    pagination["count"] = count
    pagination["start"] = start
    pagination["limit"] = limit
    if page == 1:
        pagination['previous'] = ''
    else:
        page_copy = page - 1
        limit_copy = start - 1
        pagination['previous'] = url + '?page=%d&limit=%d' % (page_copy, limit_copy)
    # make next url
    if start + limit > count:
        pagination['next'] = ''
    else:
        page_copy = page + 1
        pagination['next'] = url + '?page=%d&limit=%d' % (page_copy, limit)

    return pagination


def get_paginated_list(results, url, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)
    if count < start or limit < 0:
        abort(400, message="No hay resultados.")
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj
