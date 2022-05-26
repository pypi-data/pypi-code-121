"""Library defining the interface to firewall."""

from typing import Any, Optional

import grpc
import simplejson

from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.internal.throttle_queue import ThrottleQueue
from rime_sdk.protos.firewall.firewall_pb2 import (
    Firewall,
    FirewallWriteMask,
    ListFirewallsRequest,
    ListFirewallsResponse,
    UpdateFirewallRequest,
    UpdateFirewallResponse,
)
from rime_sdk.protos.jobs.jobs_pb2 import JobMetadata
from rime_sdk.protos.model_testing.model_testing_pb2 import (
    CustomImage,
    RunFirewallIncrementalDataRequest,
)
from rime_sdk.stress_test_job import RIMEStressTestJob


class RIMEFirewall:
    """RIMEFirewall object wrapper with helpful methods for working with RIME Firewall.

    Attributes:
        backend: RIMEBackend
            The RIME backend used to query about the status of the job.
        firewall_id: str
            How to refer to the FW in the backend.
            Use this attribute to specify the Firewall for tasks in the backend.
    """

    # A throttler that limits the number of model tests to roughly 20 every 5 minutes.
    # This is a static variable for RIMEClient.
    _throttler = ThrottleQueue(desired_events_per_epoch=20, epoch_duration_sec=300)

    def __init__(self, backend: RIMEBackend, firewall_id: str,) -> None:
        """Create a new Firewall wrapper object.

        Arguments:
            backend: RIMEBackend
                The RIME backend used to query about the status of the job.
            firewall_id: str
                The identifier for the RIME job that this object monitors.
        """
        self._backend = backend
        self._firewall_id = firewall_id

    def __str__(self) -> str:
        """Pretty-print the object."""
        res = {"firewall_id": self._firewall_id}
        return f"RIMEFirewall {res}"

    def __eq__(self, obj: Any) -> bool:
        """Check if this FWInstance is equivalent to 'obj'."""
        return isinstance(obj, RIMEFirewall) and self._firewall_id == obj._firewall_id

    def _update_firewall(
        self, firewall_write_mask: FirewallWriteMask, **update_params: Any
    ) -> UpdateFirewallResponse:
        req = UpdateFirewallRequest()
        req.firewall.CopyFrom(Firewall(id=self._firewall_id, **update_params))
        req.mask.CopyFrom(firewall_write_mask)
        try:
            with self._backend.get_firewall_stub() as firewall_tester:
                res = firewall_tester.UpdateFirewall(req)
                return res
        except grpc.RpcError as e:
            raise ValueError(e)

    def update_firewall_stress_test_run(
        self, stress_test_run_id: str
    ) -> UpdateFirewallResponse:
        """Update firewall with stress test run id.

        Arguments:
            stress_test_run_id: Stress Test Run Id to configure new firewall

        Returns:
            None

        Raises:
            ValueError
                If the provided status_filters array has invalid values.
                If the request to the ModelTest service failed.
        """
        firewall_write_mask = FirewallWriteMask(stress_test_run_id=True)
        return self._update_firewall(
            firewall_write_mask, stress_test_run_id=stress_test_run_id
        )

    def get_link(self) -> str:
        """Get the web app URL to the firewall.

        This link directs to your organization's deployment of RIME.
        You can view more detailed information about the firewall
        in the web app, including helpful visualizations, key insights on your
        model's performance, and explanations of test results for each batch.

        Note: this is a string that should be copy-pasted into a browser.
        """
        # Fetch test run metadata and return a dataframe of the single row.
        req = ListFirewallsRequest(firewall_ids=[self._firewall_id])
        try:
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ListFirewallsResponse = firewall_tester.ListFirewalls(req)
                return res.firewalls[0].web_app_url.url
        except grpc.RpcError as e:
            raise ValueError(e)

    def run_firewall_incremental_data(
        self,
        test_run_config: dict,
        disable_firewall_events: bool = True,
        custom_image: Optional[CustomImage] = None,
        rime_managed_image: Optional[str] = None,
        ram_request_megabytes: Optional[int] = None,
        cpu_request_millicores: Optional[int] = None,
    ) -> RIMEStressTestJob:
        """Start a RIME model firewall test on the backend's ModelTesting service.

        This allows you to run Firewall Test job on the RIME
        backend. This will run firewall on a batch of tabular data.

        Arguments:
            test_run_config: dict
                Configuration for the test to be run, which specifies paths to
                the model and datasets to used for the test.
            custom_image: Optional[CustomImage]
                Specification of a customized container image to use running the model
                test. The image must have all dependencies required by your model.
                The image must specify a name for the image and optional a pull secret
                (of type CustomImage.PullSecret) with the name of the kubernetes pull
                secret used to access the given image.
            rime_managed_image: Optional[str]
                Name of a managed image to use when running the model test.
                The image must have all dependencies required by your model. To create
                new managed images with your desired dependencies, use the client's
                ``create_managed_image()`` method.
            ram_request_megabytes: int
                Megabytes of RAM requested for the stress test job. If none
                specified, will default to 4000MB. The limit is 2x the megabytes
                requested.
            cpu_request_millicores: int
                Millicores of CPU requested for the stress test job. If none
                specified, will default to 1500mi. The limit is 2x the millicores
                requested.

        Returns:
            A ``RIMEStressTestJob`` providing information about the model stress test
            job.

        Raises:
            ValueError
                If the request to the ModelTest service failed.

        Example:

        .. code-block:: python

            # This example will likely not work for you because it requires permissions
            # to a specific S3 bucket. This demonstrates how you might specify such a
            # configuration.
            incremental_config = {
                "eval_path": "s3://rime-datasets/
                   fraud_continuous_testing/eval_2021_04_30_to_2021_05_01.csv",
                "timestamp_col": "timestamp"
            }
            # Run the job using the specified config and the default Docker image in
            # the RIME backend. Use the RIME Managed Image "tensorflow115".
            # This assumes you have already created the Managed Image and waited for it
            # to be ready.
            firewall = rime_client.get_firewall("foo")
            job =
                firewall.run_firewall_incremental_data(
                    test_run_config=incremental_config,
                    rime_managed_image="tensorflow115",
                    ram_request_megabytes=8000,
                    cpu_request_millicores=2000)
        """
        # TODO(blaine): Add config validation service.
        if not isinstance(test_run_config, dict):
            raise ValueError("The configuration must be a dictionary")

        if custom_image and rime_managed_image:
            raise ValueError(
                "Cannot specify both 'custom_image' and 'rime_managed_image'"
            )

        req = RunFirewallIncrementalDataRequest(
            firewall_id=self._firewall_id,
            test_run_config=simplejson.dumps(test_run_config).encode(),
            disable_firewall_events=disable_firewall_events,
        )
        if custom_image:
            req.custom_image_type.testing_image.CopyFrom(custom_image)
        if rime_managed_image:
            req.custom_image_type.managed_image.name = rime_managed_image
        if ram_request_megabytes:
            req.ram_request_megabytes = ram_request_megabytes
        if cpu_request_millicores:
            req.cpu_request_millicores = cpu_request_millicores
        try:
            RIMEFirewall._throttler.throttle(  # pylint: disable=W0212
                throttling_msg="Your request is throttled to limit # of model tests."
            )
            with self._backend.get_model_testing_stub() as model_tester:
                job: JobMetadata = model_tester.RunFirewallIncrementalData(
                    request=req
                ).job
                return RIMEStressTestJob(self._backend, job.id)
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)
