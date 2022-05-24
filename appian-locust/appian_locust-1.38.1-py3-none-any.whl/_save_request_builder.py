from typing import Dict, Any, Union, Optional


def save_builder() -> '_SaveRequestBuilder':
    builder = _SaveRequestBuilder()
    return builder


class _SaveRequestBuilder:
    """
    Builds a save request, that can be used to trigger saves on the UI
    """

    def __init__(self) -> None:
        self._component: Optional[dict] = None
        self._uuid: Optional[str] = None
        self._context: Optional[dict] = None
        self._value: Optional[Union[dict, list]] = None
        self._record_url_stub: Optional[str] = None

    def component(self, component: Dict[str, Any]) -> '_SaveRequestBuilder':
        self._component = component
        return self

    def uuid(self, uuid: str) -> '_SaveRequestBuilder':
        self._uuid = uuid
        return self

    def context(self, context: Dict[str, Any]) -> '_SaveRequestBuilder':
        self._context = context
        return self

    def value(self, value: Union[dict, list]) -> '_SaveRequestBuilder':
        self._value = value
        return self

    def record_url_stub(self, record_url_stub: Optional[str]) -> '_SaveRequestBuilder':
        self._record_url_stub = record_url_stub
        return self

    def build(self) -> Dict[str, Any]:
        if self._component is None:
            raise Exception("Component not set")
        if self._uuid is None:
            raise Exception("uuid not set")
        if self._context is None:
            raise Exception("context not set")

        if self._value is None:
            self._value = self._component["value"]

        if 'saveInto' not in self._component:
            # Support onSubmitSaveInto
            if 'onSubmitSaveInto' in self._component:
                save_into = self._component['onSubmitSaveInto']
            elif 'saveInto' not in self._component.get('contents', {}):
                raise Exception("saveInto not set")
            else:
                save_into = self._component['contents']['saveInto']
        else:
            save_into = self._component['saveInto']

        payload = {
            "#t": "UiConfig",
            "context": self._context,
            "uuid": self._uuid,
            "updates": {
                "#t": "SaveRequest?list",
                "#v": [
                    {
                        "_cId": self._component["_cId"],
                        "model": self._component,
                        "value": self._value,
                        "saveInto": save_into,
                        "saveType": "PRIMARY",
                    }
                ],
            },
        }
        if self._record_url_stub:
            payload.update(
                {"identifier": {
                    "urlStub": self._record_url_stub,
                    "siteUrlStub": "D6JMim",
                    "pageUrlStub": "records",
                    "view": "view",
                    "viewData": "all",
                    "#t": "RecordInstanceListIdentifier"
                }
                }
            )
        return payload
