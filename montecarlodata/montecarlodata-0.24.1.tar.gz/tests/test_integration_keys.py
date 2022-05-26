import click
from box import BoxList, Box
from montecarlodata.common.data import MonolithResponse
from montecarlodata.common.user import UserService
from montecarlodata.config import Config
from montecarlodata.integrations.keys import IntegrationKeyScope, IntegrationKeyService, Queries
from montecarlodata.utils import GqlWrapper
from unittest import TestCase
from unittest.mock import Mock, patch


class IntegrationKeyServiceTests(TestCase):

    config = Config(
        mcd_id='12345',
        mcd_token='67890',
        mcd_api_endpoint='https://api.getmontecarlo.com/graphql'
    )

    def setUp(self) -> None:
        self._request_wrapper = Mock(autospec=GqlWrapper)
        self._user_service = Mock(autospec=UserService)
        self._service = IntegrationKeyService(
            config=self.config,
            gql=self._request_wrapper,
            user_service=self._user_service
        )

    @patch.object(click, 'echo')
    def test_create_spark_key(self, echo: Mock):
        # given
        description = 'test key'
        scope = 'spark'
        warehouses = [{
            'uuid': 'lake',
            'connectionType': 'DATA_LAKE'
        }, {
            'uuid': 'snowflake',
            'connectionType': 'SNOWFLAKE'
        }]
        key = {
            'id': 'key-id',
            'secret': 'key-secret'
        }

        self._user_service.warehouses = warehouses
        self._request_wrapper.make_request_v2.return_value = MonolithResponse(
            data=Box({'key': key}),
            errors=None
        )

        # when
        self._service.create(
            description=description,
            scope=scope
        )

        # then
        self._request_wrapper.make_request_v2.assert_called_once_with(
            query=Queries.create.query,
            variables={
                'description': description,
                'scope': scope,
                'warehouseIds': [warehouses[0]['uuid']]
            },
            operation=Queries.create.operation
        )

        echo_calls = echo.call_args_list
        self.assertEqual(2, len(echo_calls))
        self.assertEqual(f"Key id: {key['id']}", echo_calls[0][0][0])
        self.assertEqual(f"Key secret: {key['secret']}", echo_calls[1][0][0])

    @patch.object(click, 'echo')
    def test_create_spark_key_with_multiple_lakes(self, echo: Mock):
        # given
        description = 'test key'
        scope = 'spark'
        warehouses = [{
            'uuid': 'lake-1',
            'connectionType': 'DATA_LAKE'
        }, {
            'uuid': 'lake-2',
            'connectionType': 'DATA_LAKE'
        }]
        key = {
            'id': 'key-id',
            'secret': 'key-secret'
        }

        self._user_service.warehouses = warehouses
        self._request_wrapper.make_request_v2.return_value = MonolithResponse(
            data=Box({'key': key}),
            errors=None
        )

        # when
        with self.assertRaises(click.Abort):
            self._service.create(
                description=description,
                scope=scope)

        # then
        self._request_wrapper.make_request_v2.assert_not_called()
        echo.assert_called_once_with(
            'Error - Unable to resolve data lake connection: multiple lake connections found.',
            err=True
        )

    @patch.object(click, 'echo')
    def test_create_spark_key_with_no_lake(self, echo: Mock):
        # given
        description = 'test key'
        scope = 'spark'
        warehouses = [{
            'uuid': 'snowflake',
            'connectionType': 'SNOWFLAKE'
        }]
        key = {
            'id': 'key-id',
            'secret': 'key-secret'
        }

        self._user_service.warehouses = warehouses
        self._request_wrapper.make_request_v2.return_value = MonolithResponse(
            data=Box({'key': key}),
            errors=None
        )

        # when
        with self.assertRaises(click.Abort):
            self._service.create(
                description=description,
                scope=scope)

        # then
        self._request_wrapper.make_request_v2.assert_not_called()
        echo.assert_called_once_with(
            'Error - Unable to resolve data lake connection: no lake connection found.',
            err=True
        )

    @patch.object(click, 'echo')
    def test_key_deleted(self, echo: Mock):
        # given
        key_id = 'key-1'

        self._request_wrapper.make_request_v2.return_value = MonolithResponse(
            data=Box({'deleted': True}),
            errors=None
        )

        # when
        self._service.delete(key_id)

        # then
        self._request_wrapper.make_request_v2.assert_called_once_with(
            query=Queries.delete.query,
            variables = {
                'keyId': key_id
            },
            operation=Queries.delete.operation
        )

        echo.assert_called_once_with('Key has been deleted.')

    @patch.object(click, 'echo')
    def test_key_not_deleted(self, echo: Mock):
        # given
        key_id = 'key-1'

        self._request_wrapper.make_request_v2.return_value = MonolithResponse(
            data=Box({'deleted': False}),
            errors=None
        )

        # when
        self._service.delete(key_id)

        # then
        self._request_wrapper.make_request_v2.assert_called_once_with(
            query=Queries.delete.query,
            variables = {
                'keyId': key_id
            },
            operation=Queries.delete.operation
        )

        echo.assert_called_once_with('Key was not deleted.')

    @patch.object(click, 'echo')
    def test_get_all(self, echo: Mock):
        self._request_wrapper.make_request_v2.return_value = MonolithResponse(
            data=BoxList([{
                'id': 'key-id',
                'description': 'test key',
                'scope': 'spark',
                'createdTime': '2021-01-01T00:00:00Z',
                'createdBy': {
                    'id': 'user-id',
                    'firstName': 'Bilbo',
                    'lastName': 'Baggins',
                    'email': 'bilbo@theshire.com'
                }
            }]),
            errors=None
        )

        # when
        self._service.get_all()

        # then
        self._request_wrapper.make_request_v2.assert_called_once_with(
            query=Queries.get_all.query,
            operation=Queries.get_all.operation
        )

        echo.assert_called_once_with(
            '╒════════╤═══════════════╤═════════╤══════════════════════╤═══════════════╕\n'
            '│ Id     │ Description   │ Scope   │ Created              │ Created By    │\n'
            '╞════════╪═══════════════╪═════════╪══════════════════════╪═══════════════╡\n'
            '│ key-id │ test key      │ spark   │ 2021-01-01T00:00:00Z │ Bilbo Baggins │\n'
            '╘════════╧═══════════════╧═════════╧══════════════════════╧═══════════════╛'
        )
