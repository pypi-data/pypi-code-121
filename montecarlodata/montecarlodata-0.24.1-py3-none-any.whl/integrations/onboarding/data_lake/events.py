from typing import Optional

import click

from montecarlodata.common.common import read_as_json_string
from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort, manage_errors
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.integrations.onboarding.fields import EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD
from montecarlodata.queries.onboarding import TOGGLE_EVENT_MUTATION


class EventsOnboardingService(BaseOnboardingService):

    def __init__(self, config: Config, **kwargs):
        super().__init__(config, **kwargs)

    @manage_errors
    def toggle_event_configuration(self, **kwargs) -> Optional[bool]:
        """
        Toggle event configuration (effectively onboarding it if enable is set to true)
        """
        mapping_file = kwargs.pop('mapping_file', None)
        if mapping_file:
            kwargs['mapping'] = read_as_json_string(mapping_file)

        connection_type = kwargs.get('connection_type')
        if connection_type:
            kwargs['connection_type'] = connection_type.lower()

        response = self._request_wrapper.make_request_v2(
            query=TOGGLE_EVENT_MUTATION,
            operation=EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD,
            variables=kwargs
        )
        if response.data.success:
            click.echo(f"Success! {'Enabled' if kwargs['enable'] else 'Disabled'} events.")
            return True
        complain_and_abort(f'Failed to toggle events!')
