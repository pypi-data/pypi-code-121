from unittest import TestCase
from unittest.mock import patch, call

import click

from montecarlodata.common.data import MonolithResponse
from montecarlodata.errors import echo_error, complain_and_abort, manage_errors, abort_on_gql_errors, prompt_connection
from tests.helpers import capture_function


class HasErrors:
    def __init__(self):
        self._abort_on_error = True

    @manage_errors
    def function_with_errors(self):
        raise ZeroDivisionError


class ErrorTest(TestCase):
    @patch('montecarlodata.errors.click')
    def test_echo_error(self, click_mock):
        message = 'foo'
        echo_error(message=message)
        click_mock.assert_has_calls([call.echo(f'Error - {message}', err=True)])

    def test_complain_and_abort(self):
        with self.assertRaises(click.exceptions.Abort):
            complain_and_abort('test')

    def test_manage_errors(self):
        with self.assertRaises(click.exceptions.Abort):
            HasErrors().function_with_errors()

    @patch('montecarlodata.errors.click')
    def test_abort_on_gql_errors(self, click_mock):
        message = 'foo'
        click_mock.echo.side_effect = click.Abort()

        with self.assertRaises(click.exceptions.Abort):
            abort_on_gql_errors(response=MonolithResponse(errors=[{'message': message}]))
        click_mock.assert_has_calls([call.echo('Error - foo', err=True)])

    @patch('montecarlodata.errors.click')
    def test_prompt_connection(self, click_mock):
        message = 'Hello, world!'
        prompt_connection(message=message, skip_prompt=False)
        click_mock.confirm.assert_called_once_with(message, abort=True)

    @patch('montecarlodata.errors.click')
    def test_prompt_connection_with_decline(self, click_mock):
        click_mock.confirm.side_effect = click.Abort

        with self.assertRaises(click.exceptions.Abort):
            prompt_connection(message='Hello, world!', skip_prompt=False)
