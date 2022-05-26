from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Enumeration of all valid Terraform resource types, with values matching
# the corresponding Sym API entity name.
class ResourceType(str, Enum):
    SYM_FLOW = "flows"
    SYM_TARGET = "access-targets"
    SYM_INTEGRATION = "integrations"
    SYM_SECRET = "secrets"
    SYM_SECRETS = "secret-sources"
    SYM_STRATEGY = "access-strategies"
    SYM_LOG_DESTINATION = "log-destinations"
    SYM_ENVIRONMENT = "environments"
    SYM_RUNTIME = "runtimes"
    SYM_ERROR_LOGGER = "error-loggers"

    @classmethod
    def options(cls) -> List[str]:
        """Returns a list of valid resource types represented as their Terraform names."""
        return [tf_name.lower() for tf_name, _ in cls.__members__.items()]


class TerraformResource(BaseModel):
    """A model for parsing generic Terraform resources from the API."""

    identifier: UUID = Field(alias="id")
    slug: str
    srn: str
    sub_type: Optional[str] = Field(
        alias="type", default=None
    )  # e.g. "slack" for integrations
