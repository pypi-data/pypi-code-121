from typing import List

import click

from sym.flow.cli.models.service_type import ServiceType


class ServiceTypeChoice(click.Choice):
    """Custom click.Choice for ServiceType Enums

    Sets the choice to the given list of services (defaults to all), then converts the input str value to the ServiceType Enum
    """

    name = "service_type_choice"

    def __init__(self, choices: List[ServiceType] = None):
        service_choices = choices or ServiceType.public()

        super().__init__(
            choices=[s.value.type_name for s in service_choices], case_sensitive=False
        )

    def convert(self, value, param, ctx) -> ServiceType:
        if isinstance(value, str):
            # Values entered directly as --service-type are passed through as str from click
            service_type_str = super().convert(value, param, ctx)
            # Service Types are defined as all uppercase enums
            return ServiceType[service_type_str.upper()]
        else:
            # Values selected by inquirer are already the correct type
            return value
