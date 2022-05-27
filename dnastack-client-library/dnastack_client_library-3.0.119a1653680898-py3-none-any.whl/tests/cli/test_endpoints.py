from dnastack.cli.endpoints import EndpointAlreadyExists, InvalidConfigurationProperty, EndpointNotFound
from tests.cli.base import CliTestCase


class TestCommand(CliTestCase):
    def test_happy_path(self):
        # Add a public endpoint.
        self.invoke('endpoints', 'add', 'sample-viral-ai', '-t', 'collections')
        self._configure_endpoint(
            'sample-viral-ai',
            {
                'url': 'https://viral.ai/api/',
            }
        )

        # The first endpoint of each type would become the default endpoint of that type automatically.
        self.assertEqual(self.simple_invoke('endpoints', 'get-defaults')['collections'], 'sample-viral-ai')

        # Adding a new endpoint with the same ID should raise an error.
        self.expect_error_from(['endpoints', 'add', 'sample-viral-ai', '-t', 'collections'],
                               r'^Endpoint already exists: sample-viral-ai')

        # Add the second endpoint of the same type.
        self.invoke('endpoints', 'add', 'sample-viral-ai-secondary', '-t', 'collections')

        # The default endpoint of this type remains the same.
        self.assertEqual(self.simple_invoke('endpoints', 'get-defaults')['collections'], 'sample-viral-ai')

        # The default endpoint is switched to the secondary.
        self.invoke('endpoints', 'set-default', 'sample-viral-ai-secondary')
        self.assertEqual(self.simple_invoke('endpoints', 'get-defaults')['collections'], 'sample-viral-ai-secondary')

        # The default endpoint is switched to the secondary.
        self.invoke('endpoints', 'unset-default', 'sample-viral-ai-secondary')
        self.assertIsNone(self.simple_invoke('endpoints', 'get-defaults').get('collections'))

        # Setting an unknown property of a registered endpoint should raise an error.
        self.expect_error_from(['endpoints', 'set', 'sample-viral-ai', 'foo.bar', 'panda'],
                               error_message='Invalid configuration property: foo.bar')

        # Setting an unknown property of an unregistered endpoint should raise an error.
        self.expect_error_from(['endpoints', 'set', 'snake', 'foo.bar', 'panda'],
                               error_message='Endpoint not found: snake')

        # Add a data connect endpoint with partial authentication information
        self.invoke('endpoints', 'add', 'sample-data-connect', '-t', 'data_connect')
        self._configure_endpoint(
            'sample-data-connect',
            {
                'url': 'https://collection-service.staging.dnastack.com/data-connect/',
                'authentication.type': 'oauth2',
                'authentication.client_id': 'faux-client-id',
                'authentication.client_secret': 'faux-client-secret',
                'authentication.grant_type': 'client_credentials',
            }
        )

        # Setting an unknown "authentication" property of a registered endpoint should raise an error.
        self.expect_error_from(['endpoints', 'set', 'sample-data-connect', 'authentication.foo_bar', 'panda'],
                               error_message='Invalid configuration property: authentication.foo_bar')

        # Remove the data connect endpoint.
        self.invoke('endpoints', 'remove', 'sample-data-connect')
        with self.assertRaises(IndexError):
            # This is to confirm that the endpoint has been removed.
            self._get_endpoint('sample-data-connect')

        # Removing twice should not raise an error.
        self.invoke('endpoints', 'remove', 'sample-data-connect')
