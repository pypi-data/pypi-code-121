import logging

import requests

from pylimiter.backend.interface import Backend

logging.basicConfig(level=logging.INFO)


class DefaultBackend(Backend):
    def __init__(self, project_id, opts):
        self.project_id = project_id
        self.api_token = opts.get('api_token')
        self.backend_url = opts.get(
            'backend_url', 'https://www.applimiter.com/api/v1')

    def _do_request(self, path, data):
        headers = {'Authorization': self.api_token}
        r = requests.post(f'{self.backend_url}{path}',
                          data=data, headers=headers)
        r.raise_for_status()
        return r.json()

    def bind(self, plan_id, user_id):
        return self._do_request('/bind', {'user_id': user_id, 'project_id': self.project_id, 'plan_id': plan_id})

    def feature(self, feature_id, user_id):
        resp = self._do_request('/feature', {'user_id': user_id,
                                             'project_id': self.project_id, 'feature_id': feature_id})
        if resp['reason']:
            logging.info(resp['reason'])
        return resp['allow']

    def increment(self, feature_id, user_id):
        return self._do_request('/increment', {'user_id': user_id,
                                               'project_id': self.project_id, 'feature_id': feature_id})

    def decrement(self, feature_id, user_id):
        return self._do_request('/decrement', {'user_id': user_id,
                                               'project_id': self.project_id, 'feature_id': feature_id})

    def set(self, feature_id, user_id, value):
        return self._do_request('/set', {'user_id': user_id,
                                         'project_id': self.project_id, 'feature_id': feature_id, 'value': value})

    def feature_matrix(self):
        return self._do_request('/feature-matrix', {'project_id': self.project_id})

    def usage(self, user_id):
        return self._do_request('/usage', {'user_id': user_id,
                                           'project_id': self.project_id})
