import os
import pathlib
from typing import Optional, Dict
from unittest import TestCase
from unittest.mock import Mock

import click
from box import Box

from montecarlodata.common.common import read_as_json_string
from montecarlodata.common.data import MonolithResponse
from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.data_lake.events import EventsOnboardingService
from montecarlodata.integrations.onboarding.fields import EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD, \
    GLUE_CONNECTION_TYPE
from montecarlodata.queries.onboarding import TOGGLE_EVENT_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG, _SAMPLE_DW_ID


class EventsOnboardingTest(TestCase):
    _SAMPLE_CONNECTION_ID = '43'

    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = EventsOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    def test_toggle_events_when_successful(self):
        self.assertTrue(self._test_event_toggle(toggle=True))

    def test_toggle_events_with_mapping_file(self):
        mapping_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'sample_mapping.json')

        options = {'enable': True, 'mapping_file': mapping_file}
        expected_variables = {'enable': True, 'mapping': read_as_json_string(mapping_file)}

        self.assertTrue(self._test_event_toggle(options=options, expected_variables=expected_variables))

    def test_toggle_events_with_connection_type_upper_case(self):
        options = {'enable': True, 'connection_type': 'GLUE'}
        expected_variables = {'enable': True, 'connection_type': GLUE_CONNECTION_TYPE}

        self.assertTrue(self._test_event_toggle(options=options, expected_variables=expected_variables))

    def test_toggle_events_with_connection_id(self):
        options = {'enable': True, 'connection_id': self._SAMPLE_CONNECTION_ID}

        self.assertTrue(self._test_event_toggle(options=options, expected_variables=options))

    def test_toggle_events_when_unsuccessful(self):
        with self.assertRaises(click.exceptions.Abort):
            self._test_event_toggle(toggle=False, success=False)

    def _test_event_toggle(self, toggle: Optional[bool] = True, success: Optional[bool] = True,
                           options: Optional[Dict] = None, expected_variables: Optional[Dict] = None) -> Optional[bool]:
        # Helper to test event toggle with sample configuration
        if not options:
            options = {**_SAMPLE_BASE_OPTIONS, **{'enable': toggle}}
        if not expected_variables:
            expected_variables = {**options, }

        self._user_service_mock.warehouses = [{'uuid': _SAMPLE_DW_ID}]
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data=Box({'success': success}))

        status = self._service.toggle_event_configuration(**options)

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=TOGGLE_EVENT_MUTATION,
            operation=EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD,
            variables=expected_variables
        )
        return status
