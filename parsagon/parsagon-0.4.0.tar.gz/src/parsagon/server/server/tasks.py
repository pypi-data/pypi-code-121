from __future__ import absolute_import
from celery import shared_task
from django.conf import settings
from server.utils import build_structure

import requests
import datetime
import traceback
import sys


@shared_task
def run_code(pipeline_id, run_id):
    headers = {'Authorization': f'Token {settings.API_KEY}'}
    r = requests.get(f'https://{settings.PARSAGON_HOST}/api/pipelines/{pipeline_id}/code/', headers=headers)
    code = r.json()['code']
    start_time = datetime.datetime.now()
    requests.patch(f'https://{settings.PARSAGON_HOST}/api/pipelines/runs/{run_id}/', headers=headers, json={'status': 'RUNNING'})
    loc = dict(locals(), **globals())
    status = ''
    error = ''
    error_transformer = ''
    try:
        exec(code, loc, loc)
    except Exception as e:
        error = str(traceback.format_exc())
        exc_type, exc_value, exc_traceback = sys.exc_info()
        function_names = (frame.name for frame in traceback.extract_tb(exc_traceback))
        for function_name in function_names:
            # Assumes that no user-supplied functions start with "transformer"
            if function_name.startswith('transformer'):
                error_transformer = function_name
                break

        #requests.post(f'https://{settings.PARSAGON_HOST}/api/pipelines/', headers=headers, json={'message': e, 'state': var_state})
        status = 'ERROR'
    else:
        status = 'FINISHED'
    finally:
        if 'driver' in loc:
            loc['driver'].quit()
        if 'display' in loc:
            loc['display'].stop()
    assert status is not None

    error_info = {} if error is None else {
        'error': error,
        'error_transformer': error_transformer,
    }
    requests.patch(f'https://{settings.PARSAGON_HOST}/api/pipelines/runs/{run_id}/', headers=headers, json={'status': status, **error_info})
