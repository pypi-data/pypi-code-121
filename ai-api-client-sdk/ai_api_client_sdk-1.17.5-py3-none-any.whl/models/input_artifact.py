from typing import Dict

from .base_models import Name


class InputArtifact(Name):
    """The InputArtifact object defines the input artifact specified in the executable definition. Refer to
    :class:`ai_api_client_sdk.models.base_models.Name`, for the object definition
    """
    @staticmethod
    def from_dict(input_artifact_dict: Dict[str, str]):
        """Returns a :class:`ai_api_client_sdk.models.input_artifact.InputArtifact` object, created from the values
        in the dict provided as parameter

        :param input_artifact_dict: Dict which includes the necessary values to create the object
        :type input_artifact_dict: Dict[str, Any]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.input_artifact.InputArtifact`
        """
        return InputArtifact(**input_artifact_dict)
