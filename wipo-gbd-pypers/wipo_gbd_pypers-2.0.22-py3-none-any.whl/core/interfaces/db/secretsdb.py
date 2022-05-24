import os
import boto3
from .test import MockDBLogger


_secrets = None


def get_secrets():
    global _secrets
    if _secrets is None:
        _secrets = SecretsManager()
    return _secrets


class SecretsManager:

    def __init__(self, *args, **kwargs):
        self._prefix = '/gbd/secrets'
        if os.environ.get('KSTR_URL', None):
            endpoint_url = os.environ['KSTR_URL']
        else:
            endpoint_url = None
        if os.environ.get("GITHUB_TOKEN", None):
            self.client = MockDBLogger()
        else:
            self.client = boto3.client('ssm',
                                       endpoint_url=endpoint_url)
        self.secrets = {}
        self.refresh()
        self.secretes_revers = {v: k for k, v in self.secrets.items()}

    def refresh(self):
        paginator = self.client.get_paginator('describe_parameters')
        pager = paginator.paginate(
            ParameterFilters=[
                dict(Key="Path", Option="Recursive", Values=[self._prefix])
            ]
        )

        for page in pager:
            for p in page['Parameters']:
                path = p['Name'][len(self._prefix)+1:]
                self.secrets[path] = None
        for secret in self.secrets.keys():
            abs_key = "%s/%s" % (self._prefix, secret)
            parameter = self.client.get_parameter(Name=abs_key, WithDecryption=True)['Parameter']
            self.secrets[secret] = parameter['Value']

    def key_from_value(self, value):
        if value in self.secretes_revers.keys():
            return '${%s}' % self.secretes_revers[value]
        return value

    def get(self, key, default=''):
        return self.secrets.get(key, default)

    def put(self, secret, value):
        full_name = self._prefix + '/' + secret
        if value is None:
            return
        params = {
            "Description": "Pipeline secret for " + secret,
            "Name": full_name,
            "Value": value,
            "Type": 'SecureString',
            "Overwrite": True
        }
        self.client.put_parameter(**params)
