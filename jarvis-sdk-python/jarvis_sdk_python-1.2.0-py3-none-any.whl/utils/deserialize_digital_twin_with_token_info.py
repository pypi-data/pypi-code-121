from jarvis_sdk.model.digital_twin import DigitalTwin
from jarvis_sdk.model.token_info import TokenInfo

def deserialize_digital_twin_with_token_info(response):
    if not response:
        return None

    dt_result = {}

    if response.HasField('digital_twin'):
        dt_result["digitalTwin"] = DigitalTwin.deserialize(response.digital_twin)

    if response.HasField('token_info'):
        dt_result["tokenInfo"] = TokenInfo.deserialize(response.token_info)

    return dt_result
