from rebotics_sdk.providers.utils import is_valid_url
from .base import ReboticsBaseProvider, remote_service, ProviderHTTPClientException


class AdminProvider(ReboticsBaseProvider):
    @remote_service('/version/')
    def version(self):
        return self.session.get()

    @remote_service('/admin/', json=False)
    def admin_ping(self, **kwargs):
        return self.session.get()

    def get_retailer_tf_models(self, codename=None):
        if codename is not None and not self.is_retailer_identifier_used():
            return self.get_retailer_tf_models_by_codename(codename)
        elif self.is_retailer_identifier_used():
            return self.get_retailer_tf_models_by_retailer_authentication()
        else:
            raise ProviderHTTPClientException('You did not use any of the authentication methods to get configurations')

    @remote_service('/nn_models/tf/models/')
    def get_retailer_tf_models_by_retailer_authentication(self, **kwargs):
        return self.session.get()

    @remote_service('/nn_models/tf/models/{codename}/')
    def get_retailer_tf_models_by_codename(self, codename, **kwargs):
        return self.session.get(codename=codename)

    @remote_service('/retailers/host/')
    def get_retailer(self, retailer_codename, **kwargs):
        response = self.session.post(data={
            'company': retailer_codename
        })
        return response

    def get_retailer_host(self, retailer_codename):
        return self.get_retailer(retailer_codename)['host']

    @remote_service('/retailers/')
    def get_retailer_list(self, **kwargs):
        return self.session.get()

    @remote_service('/retailers/host/{codename}/')
    def update_host(self, codename, host, **kwargs):
        if not is_valid_url(host):
            raise ProviderHTTPClientException('%s is not a valid url' % host, host=host)
        return self.session.patch(codename=codename, data={
            'host': host
        })

    def set_retailer_identifier(self, retailer_codename, retailer_secret_key):
        self.headers['x-retailer-codename'] = retailer_codename
        self.headers['x-retailer-secret-key'] = retailer_secret_key

    @remote_service('/api/token-auth/', raw=True)
    def token_auth(self, username, password, verification_code=None, **kwargs):
        payload = {
            'username': username,
            'password': password,
        }

        if verification_code is not None:
            payload['verification_code'] = verification_code

        response = self.session.post(data=payload)
        self.set_token(response.json()['token'])
        return response

    def get_configurations(self, codename=None):
        """
        Should call this with codename and provided token authentication,
        or
        with provided retailer identifier
        :param codename:
        :return:
        """
        if codename is not None and not self.is_retailer_identifier_used():
            return self.get_configurations_by_codename(codename)
        elif self.is_retailer_identifier_used():
            return self.get_configurations_by_retailer_authentication()
        else:
            raise ProviderHTTPClientException('You did not use any of the authentication methods to get configurations')

    @remote_service('/retailers/host/{codename}/configurations/')
    def get_configurations_by_codename(self, codename, **kwargs):
        return self.session.get(codename=codename)

    @remote_service('/retailers/configurations/')
    def get_configurations_by_retailer_authentication(self, **kwargs):
        return self.session.get()

    # deprecated
    @remote_service('/api/classification_data/import/')
    def create_classification_database_import(self, retailer, model, extension='zip', **kwargs):
        allowed_extensions = ['rcdb', 'zip']
        if extension not in allowed_extensions:
            raise ValueError("Extension should be on of {} not {}".format(
                allowed_extensions, extension
            ))
        return self.session.post(json={
            'retailer': retailer,
            'model': model,
            'extension': extension
        })

    # deprecated
    @remote_service('/api/classification_data/task/export_feature_database/{id}/complete/')
    def notify_classification_database_import_done(self, id, **kwargs):
        return self.session.post(
            id=id,
        )

    # deprecated
    @remote_service('/api/classification_data/task/export_feature_database/{id}/complete/')
    def notify_classification_database_import_failed(self, id, error_message='', **kwargs):
        return self.session.post(
            id=id,
            json={
                'error': error_message
            }
        )

    @remote_service('/api/classification_data/rcdb/')
    def rcdb_create(self, data, **kwargs):
        return self.session.post(json=data)

    @remote_service('/api/classification_data/rcdb/{id}/')
    def rcdb_update(self, id_, data, **kwargs):
        return self.session.patch(id=id_, json=data)

    @remote_service('/api/classification_data/rcdb/{id}/')
    def rcdb_get(self, id_, **kwargs):
        return self.session.get(id=id_)

    @property
    def rcdb(self):
        """

        :return: ReboticsClassificationDatabase utility tools. Higher level of provider
        :rtype: ReboticsClassificationDatabase
        """
        from ..advanced.flows import ReboticsClassificationDatabase
        return ReboticsClassificationDatabase(provider=self)

    @remote_service('/core/core-callback/{id}/')
    def get_core_callback_data(self, pk):
        return self.session.get(id=pk)

    @remote_service('/core-test/cases/')
    def create_core_test_case(self, yaml_template, title, group, description):
        return self.session.post(json={
            'title': title,
            'group': group,
            'description': description,
            'yaml_template': yaml_template,
        })

    @remote_service('/core-test/core-test-case/payload/')
    def retrieve_core_test_case_data(self, yaml_template, title, group, description):
        return self.session.post(json={
            'title': title,
            'group': group,
            'description': description,
            'yaml_template': yaml_template,
        })

    @remote_service('/core-test/cases/{id}/')
    def get_core_test_case(self, id_):
        return self.session.get(id=id_)

    @remote_service('/core-test/cases/')
    def list_core_test_cases(self, **params):
        """
        Expected params are: `group`, `title`
        """
        return self.session.get(params=params)
