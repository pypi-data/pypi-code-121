"""Library defining the interface to image builder jobs."""

import time
from typing import Any, Dict, List, Optional

import grpc
from google.protobuf.json_format import MessageToDict

from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.protos.image_registry.image_registry_pb2 import (
    GetImageRequest,
    ManagedImage,
)


class RIMEImageBuilder:
    """An interface to a RIME image builder."""

    def __init__(
        self,
        backend: RIMEBackend,
        name: str,
        requirements: Optional[List[ManagedImage.PipRequirement]] = None,
    ) -> None:
        """Create a new RIME image builder.

        Args:
            backend: RIMEBackend
                The RIME backend used to query about the status of the image building.
            name: str
                The name of the RIME managed image that this object monitors.
            requirements: Optional[List[ManagedImage.PipRequirement]] = None
                Optional list of pip requirements to be installed on this image.
        """
        self._backend = backend
        self._name = name
        self._requirements = requirements

    def __eq__(self, obj: Any) -> bool:
        """Check if this builder is equivalent to 'obj'."""
        return isinstance(obj, RIMEImageBuilder) and self._name == obj._name

    def __str__(self) -> str:
        """Pretty-print the object."""
        ret = {"name": self._name}
        if self._requirements:
            ret["requirements"] = str(
                [f"{req.name}{req.version_specifier}" for req in self._requirements]
            )
        return f"RIMEImageBuilder {ret}"

    def get_status(
        self,
        verbose: bool = False,
        wait_until_finish: bool = False,
        poll_rate_sec: float = 5.0,
    ) -> Dict:
        """Query the ImageRegistry service for the image's build status.

        This query includes an option to wait until the image build is finished.
        It will either have succeeded or failed.

        Arguments:
            verbose: bool
                whether or not to print diagnostic information such as logs.
            wait_until_finish: bool
                whether or not to block until the image is READY or FAILED.
            poll_rate_sec: float
                the frequency with which to poll the image's build status.

        Returns:
            A dictionary representing the image's state.
        """
        # Create backend client stubs to use for the remainder of this session.
        with self._backend.get_image_registry_stub() as image_registry:
            get_req = GetImageRequest(name=self._name)
            image = ManagedImage(status=ManagedImage.Status.STATUS_UNSPECIFIED)
            if verbose:
                print("Querying for RIME managed image '{}':".format(self._name))
            # Do not repeat if the job is finished or blocking is disabled.
            repeat = True
            while repeat and not image.status in (
                ManagedImage.Status.STATUS_FAILED,
                ManagedImage.Status.STATUS_OUTDATED,
                ManagedImage.Status.STATUS_READY,
            ):
                try:
                    image = image_registry.GetImage(get_req).image
                except grpc.RpcError as e:
                    # TODO(QuantumWombat): distinguish other special errors
                    if e.code() == grpc.StatusCode.UNAVAILABLE:
                        if verbose:
                            print("reconnecting to the RIME backend...")
                        continue
                    raise ValueError(e)
                if verbose:
                    print("Status: {}".format(ManagedImage.Status.Name(image.status)))
                if wait_until_finish:
                    time.sleep(poll_rate_sec)
                else:
                    repeat = False

            # TODO(blaine): Add ability to get and print logging information from a
            # failed build.

        return MessageToDict(image, preserving_proto_field_name=True)
