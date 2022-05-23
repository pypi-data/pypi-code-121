import json
import logging
import os
import uuid
from shlex import quote

import allure

from api_manager.settings import LIBRARY_ROOT


def logging_response(response):
    """
    :param response:
    :return:
    """
    if not hasattr(response, 'request'):
        return response

    try:
        message = response_log_message(response)
    except Exception as error:
        logging.error(f'Logger was unable to attach log. Error happened {error}')
        return

    with open(f'{uuid.uuid4()}.html', 'w') as file:
        file.write(message)

    try:
        allure.attach.file(
            file.name,
            name='Response content',
            attachment_type=allure.attachment_type.HTML
        )
    except KeyError:
        pass

    os.remove(file.name)

    return response


def to_curl(request, compressed=False, verify=True) -> str:
    """
    Returns string with curl command by provided request object

    Parameters
    ----------
    compressed : bool
        If `True` then `--compressed` argument will be added to result

    :param verify:
    :param compressed:
    :param request:
    """
    parts = [
        ('curl', None),
        ('-X', request.method),
    ]

    for k, v in sorted(request.headers.items()):
        parts += [('-H', '{0}: {1}'.format(k, v))]

    if request.body:
        body = request.body
        if isinstance(body, bytes):
            try:
                body = body.decode('utf-8')
            except UnicodeDecodeError:
                body = {}

        parts += [('-d', body)]

    if compressed:
        parts += [('--compressed', None)]

    if not verify:
        parts += [('--insecure', None)]

    parts += [(None, request.url)]

    flat_parts = []
    for k, v in parts:
        if k:
            flat_parts.append(quote(k))
        if v:
            flat_parts.append(quote(v))

    return ' '.join(flat_parts)


def response_log_message(response):
    """
    :param response:
    :return:
    """
    try:
        response_content = response.json()
    except json.JSONDecodeError:
        response_content = response.content

    payload = {
        'request_url': response.request.url,
        'request_method': response.request.method,
        'request_headers': response.request.headers,
        'request_content': response.request.body,
        'response_headers': response.headers,
        'cookies': response.cookies,
        'response_content': response_content,
        'status_code': response.status_code,
        'reason': response.reason,
        'curl': to_curl(response.request, verify=False)
    }

    with open(LIBRARY_ROOT + '/templates/log_template.html', 'r') as template:
        return str(template.read()).format(**payload)
