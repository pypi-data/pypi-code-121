from typing import Optional

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.utils import get_or_prompt
from sym.flow.cli.models.service import BaseService, Service
from sym.flow.cli.models.service_type import ServiceType


def get_or_prompt_service(
    api: SymAPI, service_type: Optional[str] = None, external_id: Optional[str] = None
) -> Service:
    """Given optional _service_type and _external_id inputs, return a BaseService that exists in the organization

    If _service_type or _external_id are not provided, prompts the user for input.
    Validates that the provided service type + external ID correspond with a Service in the organization
    """
    # Get only services that are already registered with the organization
    services = api.get_services(service_types=ServiceType.all_public_names())
    existing_service_types = list(set(s.service_type for s in services))

    # Prompt the user for an existing service or validate their input
    service_type = get_or_prompt(
        service_type, "Which service type?", existing_service_types
    )

    # Prompt the user for the external ID of the requested service or validate their input
    external_ids = list(
        set(s.external_id for s in services if s.service_type == service_type)
    )
    external_id = get_or_prompt(
        external_id, f"Which {service_type} service?", external_ids
    )

    return next(
        s
        for s in services
        if s.service_type == service_type and s.external_id == external_id
    )
