import typing as t

from taktile_types.enums.endpoint import EndpointKinds

from tktl.future.monitor import verify_tracking_config

from .abc import Endpoint, XType, YType


class GenericEndpoint(Endpoint):
    kind: EndpointKinds = EndpointKinds.GENERIC

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.track_inputs:
            verify_tracking_config(self.X, self.track_inputs)
        if self.track_outputs:
            verify_tracking_config(self.y, self.track_outputs)

    @staticmethod
    def supported(
        *,
        X: XType = None,
        y: YType = None,
        profile: t.Optional[str] = None,
    ) -> bool:
        return profile is None and X is None and y is None
