from typing import Dict

from .base_models import Name


class OutputArtifact(Name):
    """The OutputArtifact object defines the output artifact specified in the executable definition. Refer to
    :class:`ai_api_client_sdk.models.base_models.Name`, for the object definition
    """
    @staticmethod
    def from_dict(output_artifact_dict: Dict[str, str]):
        """Returns a :class:`ai_api_client_sdk.models.output_artifact.OutputArtifact` object, created from the values
        in the dict provided as parameter

        :param output_artifact_dict: Dict which includes the necessary values to create the object
        :type output_artifact_dict: Dict[str, Any]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.output_artifact.OutputArtifact`
        """
        return OutputArtifact(**output_artifact_dict)
