from datetime import timedelta
from typing import TYPE_CHECKING

import pydantic

AZURE_QUANTUM_RESOURCE_ID_REGEX = r"^/subscriptions/([a-fA-F0-9-]*)/resourceGroups/([^\s/]*)/providers/Microsoft\.Quantum/Workspaces/([^\s/]*)$"  # noqa: F722

_IONQ_API_KEY_LENGTH: int = 32
INVALID_API_KEY: str = _IONQ_API_KEY_LENGTH * "a"
MAX_EXECUTION_TIMEOUT_SECONDS = timedelta(hours=4).total_seconds()

if TYPE_CHECKING:
    pydanticExecutionTimeout = int
    pydanticAwsRoleArn = str
    pydanticS3BucketKey = str
    pydanticS3BucketName = str
    pydanticAzureResourceIDType = str
    pydanticIonQApiKeyType = str
    pydanticArgumentNameType = str
else:
    # TODO Simplify regular expressions in this file

    pydanticAwsRoleArn = pydantic.constr(
        strip_whitespace=True,
    )

    pydanticS3BucketName = pydantic.constr(strip_whitespace=True, min_length=3)

    pydanticS3BucketKey = pydantic.constr(strip_whitespace=True, min_length=1)

    pydanticAzureResourceIDType = pydantic.constr(regex=AZURE_QUANTUM_RESOURCE_ID_REGEX)

    pydanticIonQApiKeyType = pydantic.constr(
        regex=f"[A-Za-z0-9]{{{_IONQ_API_KEY_LENGTH}}}"
    )
    pydanticExecutionTimeout = pydantic.conint(gt=0, le=MAX_EXECUTION_TIMEOUT_SECONDS)

    pydanticArgumentNameType = pydantic.constr(regex="[_a-zA-Z][_a-zA-Z0-9]*")
