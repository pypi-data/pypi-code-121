"""Library to initiate backend RIME service requests."""
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple, Union

import grpc
import simplejson
from google.protobuf.json_format import MessageToDict

from rime_sdk.firewall import RIMEFirewall
from rime_sdk.image_builder import RIMEImageBuilder
from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.internal.file_upload import FileUploadModule
from rime_sdk.internal.throttle_queue import ThrottleQueue
from rime_sdk.protos.firewall.firewall_pb2 import (
    BatchMetadata,
    ConvertIDsRequest,
    ConvertIDsResponse,
    CreateFirewallRequest,
    CreateFirewallResponse,
    Firewall,
    FirewallConvIDType,
    ListFirewallsRequest,
    ListFirewallsResponse,
)
from rime_sdk.protos.image_registry.image_registry_pb2 import (
    CreateImageRequest,
    ListImagesRequest,
    ManagedImage,
)
from rime_sdk.protos.jobs.jobs_pb2 import JobMetadata, JobStatus, JobType
from rime_sdk.protos.model_testing.model_testing_pb2 import (
    CustomImage,
    ListTestJobsRequest,
    StartFirewallFromReferenceRequest,
    StartStressTestRequest,
)
from rime_sdk.protos.project.project_pb2 import (
    CreateProjectRequest,
    GetProjectRequest,
    ListProjectsRequest,
)
from rime_sdk.protos.results_upload.results_upload_pb2 import DataType
from rime_sdk.stress_test_job import RIMEStressTestJob


def get_job_status_enum(job_status: str) -> "JobStatus.V":
    """Get job status enum value from string."""
    if job_status == "pending":
        return JobStatus.JOB_STATUS_PENDING
    elif job_status == "running":
        return JobStatus.JOB_STATUS_RUNNING
    elif job_status == "failed":
        return JobStatus.JOB_STATUS_FAILED
    elif job_status == "succeeded":
        return JobStatus.JOB_STATUS_SUCCEEDED
    else:
        raise ValueError(
            f"Got unknown job status ({job_status}), "
            f"should be one of: `pending`, `running`, `failing`, `succeeded`"
        )


def get_data_type_enum(data_type: str) -> "DataType.V":
    """Get data type enum value from string."""
    if data_type == "tabular":
        return DataType.TABULAR
    elif data_type == "nlp":
        return DataType.NLP
    elif data_type == "images":
        return DataType.IMAGES
    else:
        raise ValueError(
            f"Got unknown data type ({data_type}), "
            f"should be one of: `tabular`, `nlp`, `images`"
        )


class RIMEProject(NamedTuple):
    """This object describes a project in the RIME backend."""

    project_id: str
    """How to refer to the project in the backend.

    Use this attribute to specify the project for the backend in
    ``start_stress_`test_job()`` and ``list_stress_test_jobs()``.

    """
    name: str
    """Name of the project."""
    description: str
    """Description of the project"""


class RIMEClient:
    """The `RIMEClient` provides an interface to RIME's backend\
        services for creating projects, starting stress test jobs,\
        and querying the backend for current stress test jobs.

    To initialize the RIMEClient, provide the address of your RIME instance.

    Args:
        domain: str
            The base domain/address of the RIME service.
        api_key: str
            The api key providing authentication to RIME services.
        channel_timeout: float
            The amount of time in seconds to wait for channels to become ready
            when opening connections to gRPC servers.

    Raises:
        ValueError
            If a connection cannot be made to a backend service within `timeout`.

    Example:

    .. code-block:: python

        rime_client = RIMEClient("my_vpc.rime.com", "api-key")
    """

    # A throttler that limits the number of model tests to roughly 20 every 5 minutes.
    # This is a static variable for RIMEClient.
    _throttler = ThrottleQueue(desired_events_per_epoch=20, epoch_duration_sec=300)

    def __init__(
        self,
        domain: str,
        api_key: str = "",
        channel_timeout: float = 5.0,
        disable_tls: bool = False,
    ) -> None:
        """Create a new RIMEClient connected to the services available at `domain`.

        Args:
            domain: str
                The base domain/address of the RIME service.+
            api_key: str
                The api key providing authentication to RIME services
            channel_timeout: float
                The amount of time in seconds to wait for channels to become ready
                when opening connections to gRPC servers.
            disable_tls: bool
                Whether to disable tls when connecting to the backend.

        Raises:
            ValueError
                If a connection cannot be made to a backend service within `timeout`.
        """
        self._domain = domain
        if disable_tls:
            print(
                "WARNING: disabling tls is not recommended."
                " Please ensure you are on a secure connection to your servers."
            )
        self._backend = RIMEBackend(
            domain, api_key, channel_timeout=channel_timeout, disable_tls=disable_tls
        )

    def __str__(self) -> str:
        """Pretty-print the object."""
        return f"RIME Client [{self._domain}]"

    # TODO(QuantumWombat): do this check server-side
    def _project_exists(self, project_id: str) -> bool:
        """Check if `project_id` exists.

        Args:
            project_id: the id of the project to be checked.

        Returns:
            whether or not project_id is a valid project.

        Raises:
            grpc.RpcError if the server has an error while checking the project.
        """
        verify_req = GetProjectRequest(project_id=project_id)
        try:
            with self._backend.get_project_manager_stub() as project_manager:
                project_manager.GetProject(verify_req)
                return True
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise rpc_error

    def create_project(self, name: str, description: str) -> RIMEProject:
        """Create a new RIME project in RIME's backend.

        Projects allow you to organize stress test runs as you see fit.
        A natural way to organize stress test runs is to create a project for each
        specific ML task, such as predicting whether a transaction is fradulent.

        Args:
            name: str
                Name of the new project.
            description: str
                Description of the new project.

        Returns:
            A ``RIMEProject`` that describes the created project.
            Its ``project_id`` attribute can be used in ``start_stress_test()``
            and ``list_stress_test_jobs()``.

        Raises:
            ValueError
                If the request to the Upload service failed.

        Example:

        .. code-block:: python

            project = rime_client.create_project(name='foo', description='bar')
        """
        req = CreateProjectRequest(name=name, description=description)
        try:
            with self._backend.get_project_manager_stub() as project_manager:
                res = project_manager.CreateProject(request=req)
                return RIMEProject(
                    project_id=res.project.id,
                    name=res.project.name,
                    description=res.project.description,
                )
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    def create_managed_image(
        self, name: str, requirements: List[ManagedImage.PipRequirement]
    ) -> RIMEImageBuilder:
        """Create a new managed Docker image with the desired\
        PIP requirements to run RIME on.

        These managed Docker images are managed by the RIME backend and will
        automatically be upgraded when you update your version of RIME.
        Note: Images take a few minutes to be built.

        This method returns an object that can be used to track the progress of the
        image building job. The new custom image is only available for use in a stress
        test once it has status ``READY``.

        Args:
            name: str
                The (unique) name of the new managed image. This acts as the unique
                identifier of the managed image. The call will fail if an image with
                the specified name already exists.
            requirements: List[ManagedImage.PipRequirement]
                List of additional pip requirements to be installed on the managed
                image. A ``ManagedImage.PipRequirement`` can be created with the helper
                method ``RIMEClient.pip_requirement``.
                The first argument is the name of the library (e.g. ``tensorflow`` or
                ``xgboost``) and the second argument is a valid pip
                `version specifier <https://www.python.org/dev/peps/pep-0440/#version-specifiers>`_
                (e.g. ``>=0.1.2`` or ``==1.0.2``).

        Returns:
            A ``RIMEImageBuilder`` object that provides an interface for monitoring
            the job in the backend.

        Raises:
            ValueError
                If the request to the ImageRegistry service failed.

        Example:

        .. code-block:: python

           requirements = [
                # Fix the version of `xgboost` to `1.0.2`.
                rime_client.pip_requirement("xgboost", "==1.0.2"),
                # We do not care about the installed version of `tensorflow`.
                rime_client.pip_requirement("tensorflow")
            ]

           # Start a new image building job
           builder_job = rime_client.create_managed_image("xgboost102_tensorflow",
           requirements)

           # Wait until the job has finished and print out status information.
           # Once this prints out the `READY` status, your image is available for
           # use in stress tests.
           builder_job.get_status(verbose=True, wait_until_finish=True)
        """
        req = CreateImageRequest(name=name, pip_requirements=requirements)
        try:
            with self._backend.get_image_registry_stub() as image_registry:
                image: ManagedImage = image_registry.CreateImage(request=req).image
                return RIMEImageBuilder(self._backend, image.name, requirements)
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    @staticmethod
    def pip_requirement(
        name: str, version_specifier: Optional[str] = None,
    ) -> ManagedImage.PipRequirement:
        """Construct a PipRequirement object for use in ``create_managed_image()``."""
        if not isinstance(name, str) or (
            version_specifier is not None and not isinstance(version_specifier, str)
        ):
            raise ValueError(
                (
                    "Proper specification of a pip requirement has the name"
                    "of the library as the first argument and the version specifier"
                    "string as the second argument"
                    '(e.g. `pip_requirement("tensorflow", "==0.15.0")` or'
                    '`pip_requirement("xgboost")`)'
                )
            )
        res = ManagedImage.PipRequirement(name=name)
        if version_specifier is not None:
            res.version_specifier = version_specifier
        return res

    @staticmethod
    def pip_library_filter(
        name: str, fixed_version: Optional[str] = None,
    ) -> ListImagesRequest.PipLibraryFilter:
        """Construct a PipLibraryFilter object for use in ``list_managed_images()``."""
        if not isinstance(name, str) or (
            fixed_version is not None and not isinstance(fixed_version, str)
        ):
            raise ValueError(
                (
                    "Proper specification of a pip library filter has the name"
                    "of the library as the first argument and the semantic version"
                    "string as the second argument"
                    '(e.g. `pip_libary_filter("tensorflow", "1.15.0")` or'
                    '`pip_library_filter("xgboost")`)'
                )
            )
        res = ListImagesRequest.PipLibraryFilter(name=name)
        if fixed_version is not None:
            res.version = fixed_version
        return res

    def list_managed_images(
        self,
        pip_library_filters: Optional[List[ListImagesRequest.PipLibraryFilter]] = None,
        page_token: str = "",
        page_size: int = 100,
    ) -> Tuple[List[Dict], str]:
        """List all the managed Docker images.

        This is where the true power of the managed images feature lies.
        You can search for images with specific pip libraries installed so that you
        do not have to create a new managed image every time you need to run a
        stress test.

        Args:
            pip_library_filters: Optional[List[ListImagesRequest.PipLibraryFilter]]
                Optional list of pip libraries to filter by.
                Construct each ListImagesRequest.PipLibraryFilter object with the
                ``pip_library_filter`` convenience method.
            page_token: str = ""
                This identifies to the page of results to retrieve, and used for
                paginating the API results. To get access to the next page of results,
                use the second value in the tuple returned by the previous call.
                Leave empty to retrieve the first page of results. used for paginating
                the API results.
            page_size: int = 100
                This is the limit on the size of the page of results.
                The default value is to return at most 100 managed images.

        Returns:
            A ``Tuple[List[Dict], str]`` of the list of managed images as
            dicts and the next page token.

        Raises:
            ValueError
                If the request to the ImageRegistry service failed or the list of
                pip library filters is improperly specified.

        Example:

        .. code-block:: python

            # Filter for an image with catboost1.0.3 and tensorflow installed.
            filters = [
                rime_client.pip_library_filter("catboost", "1.0.3"),
                rime_client.pip_library_filter("tensorflow"),
            ]

            # Query for the images.
            images, next_page_token = rime_client.list_managed_images(
                pip_library_filters=filters)

            # List comprehension to get all the names of the images.
            names = [x["name"] for x in images]
        """
        if pip_library_filters is None:
            pip_library_filters = []

        req = ListImagesRequest(page_token=page_token, page_size=page_size)
        req.pip_libraries.extend(pip_library_filters)

        try:
            with self._backend.get_image_registry_stub() as image_registry:
                res = image_registry.ListImages(request=req)
                return (
                    [
                        MessageToDict(image, preserving_proto_field_name=True)
                        for image in res.images
                    ],
                    res.next_page_token,
                )
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    def list_projects(
        self, page_token: str = "", page_size: int = 100,
    ) -> Tuple[List[RIMEProject], str]:
        """List projects in a paginated form.

        Args:
            page_token: str = ""
                This identifies to the page of results to retrieve, and used for
                paginating the API results. To get access to the next page of results,
                use the second value in the tuple returned by the previous call.
                Leave empty to retrieve the first page of results. used for paginating
                the API results.
            page_size: int = 200
                This is the limit on the size of the page of results.
                The default value is to return at most 200 projects.

        Returns:
            A ``Tuple[List[RIMEProject], str]`` of the list of projects and
            the next page token.

        Raises:
            ValueError
                If the request to the ProjectManager service fails.

        Example:

        .. code-block:: python

            # Query for 100 projects.
            projects, next_page_token, number = rime_client.list_projects()

        """
        req = ListProjectsRequest(page_token=page_token, page_size=page_size)

        try:
            with self._backend.get_project_manager_stub() as project_manager:
                res = project_manager.ListProjects(request=req)
                return (
                    [
                        RIMEProject(
                            project_id=annotated_project.project.id,
                            name=annotated_project.project.name,
                            description=annotated_project.project.description,
                        )
                        for annotated_project in res.projects
                    ],
                    res.next_page_token,
                )
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    def start_stress_test(
        self,
        test_run_config: dict,
        project_id: Optional[str] = None,
        custom_image: Optional[CustomImage] = None,
        rime_managed_image: Optional[str] = None,
        ram_request_megabytes: Optional[int] = None,
        cpu_request_millicores: Optional[int] = None,
        data_type: str = "tabular",
    ) -> RIMEStressTestJob:
        """Start a RIME model stress test on the backend's ModelTesting service.

        Args:
            test_run_config: dict
                Configuration for the test to be run, which specifies paths to
                the model and datasets to used for the test.
            project_id: Optional[str]
                Identifier for the project where the resulting test run will be stored.
                If not specified, the results will be stored in the default project.
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
                `create_managed_image()` method.
            ram_request_megabytes: int
                Megabytes of RAM requested for the stress test job.
                The limit is 2x the megabytes requested.
            cpu_request_millicores: int
                Millicores of CPU requested for the stress test job.
                The limit is 2x the millicores requested.
            data_type: str
                Type of data this firewall test is to be run on. Should be one of
                `tabular`, `nlp`, `images`. Defaults to `tabular`.

        Returns:
            A RIMEStressTestJob providing information about the model stress test job.

        Raises:
            ValueError
                If the request to the ModelTest service failed.

        Example:

            This example will likely not work for you because it requires permissions
            to a specific S3 bucket. This demonstrates how you might specify such a
            configuration.

        .. code-block:: python

            config = {
                "run_name": "Titanic",
                "data_info": {
                    "label_col": "Survived",
                    "ref_path": "s3://rime-datasets/titanic/titanic_example.csv",
                    "eval_path": "s3://rime-datasets/titanic/titanic_example.csv"
                },
                "model_info": {
                    "path": "s3://rime-models/titanic_s3_test/titanic_example_model.py"
                }
            }

        Run the job using the specified config and the default Docker image in the
        RIME backend. Store the results under project ID ``foo``. Use the RIME Managed
        Image ``tensorflow115``. This assumes you have already created the Managed
        Image and waited for it to be ready.

        .. code-block:: python

           job = rime_client.start_stress_test_job(
            test_run_config=config, project_id="foo",
            rime_managed_image="tensorflow115")
        """
        # TODO(blaine): Add config validation service.
        if not isinstance(test_run_config, dict):
            raise ValueError("The configuration must be a dictionary")

        if custom_image and rime_managed_image:
            raise ValueError(
                "Cannot specify both 'custom_image' and 'rime_managed_image'"
            )

        if project_id and not self._project_exists(project_id):
            raise ValueError("Project id {} does not exist".format(project_id))

        proto_data_type = get_data_type_enum(data_type)
        req = StartStressTestRequest(
            test_run_config=simplejson.dumps(test_run_config).encode(),
            data_type=proto_data_type,
        )
        if project_id:
            req.project_id = project_id
        if custom_image:
            req.custom_image_type.testing_image.CopyFrom(custom_image)
        if rime_managed_image:
            req.custom_image_type.managed_image.name = rime_managed_image
        if ram_request_megabytes:
            req.ram_request_megabytes = ram_request_megabytes
        if cpu_request_millicores:
            req.cpu_request_millicores = cpu_request_millicores
        try:
            RIMEClient._throttler.throttle(
                throttling_msg="Your request is throttled to limit # of model tests."
            )
            with self._backend.get_model_testing_stub() as model_tester:
                job: JobMetadata = model_tester.StartStressTest(request=req).job
                return RIMEStressTestJob(self._backend, job.id)
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    def list_stress_test_jobs(
        self,
        status_filters: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> List[RIMEStressTestJob]:
        """Query the backend for a list of jobs filtered by status and project ID.

        This is a good way to recover `RIMEStressTestJob` objects.
        Note that this only returns jobs from the last two days, because the
        time-to-live of job objects in the backend is set at two days.

        Args:
            status_filters: Optional[List[str]] = None
                Filter for selecting jobs by a union of statuses.
                The following list enumerates all acceptable values.
                ['pending', 'running', 'failing', 'succeeded']
                If omitted, jobs will not be filtered by status.
            project_id: Optional[str] = None
                Filter for selecting jobs by project ID.
                If omitted, jobs from all projects will be returned.

        Returns:
            A list of ``RIMEStressTestJob`` objects.
            These are not guaranteed to be in any sorted order.

        Raises:
            ValueError
                If the provided status_filters array has invalid values.
                If the request to the ModelTest service failed.

        Example:

        .. code-block:: python

            # Get all running and succeeded jobs for project 'foo'
            jobs = rime_client.list_stress_test_jobs(
                status_filters=['JOB_STATUS_PENDING', 'JOB_STATUS_SUCCEEDED'],
                project_id='foo',
            )
        """
        req = ListTestJobsRequest()
        if status_filters:
            # This throws a ValueError if status is invalid.
            req.selected_statuses.extend(
                [get_job_status_enum(status) for status in status_filters]
            )
        if project_id and not self._project_exists(project_id):
            raise ValueError("Project id {} does not exist".format(project_id))
        if project_id:
            req.project_id = project_id
        # Filter only for stress testing jobs.
        req.selected_types.extend([JobType.JOB_TYPE_MODEL_STRESS_TEST])
        try:
            with self._backend.get_model_testing_stub() as model_tester:
                res = model_tester.ListTestJobs(req)
                return [RIMEStressTestJob(self._backend, job.id) for job in res.jobs]
        except grpc.RpcError as e:
            raise ValueError(e)

    def create_firewall(
        self, name: str, bin_size_seconds: int, test_run_id: str, project_id: str
    ) -> RIMEFirewall:
        """Create a Firewall for a given project.

        Args:
            name: str
                FW name.
            bin_size_seconds: int
                Bin size in seconds. Only supports daily or hourly.
            test_run_id: str
                ID of the stress test run that firewall will be based on.
            project_id: str
                ID of the project this FW belongs to.

        Returns:
            A ``RIMEFirewall`` object.

        Raises:
            ValueError
                If the provided status_filters array has invalid values.
                If the request to the ModelTest service failed.

        Example:

        .. code-block:: python

            # Create FW based on foo stress test in bar project.
            firewall = rime_client.create_firewall(
                "firewall name", 86400, "foo", "bar")
        """
        batch_metadata = BatchMetadata(bin_size_in_seconds=bin_size_seconds)
        firewall = Firewall(
            name=name,
            stress_test_run_id=test_run_id,
            project_id=project_id,
            batch_metadata=batch_metadata,
        )
        req = CreateFirewallRequest(firewall=firewall)
        try:
            with self._backend.get_firewall_stub() as firewall_tester:
                res: CreateFirewallResponse = firewall_tester.CreateFirewall(req)
                return RIMEFirewall(self._backend, res.firewall_id)
        except grpc.RpcError as e:
            raise ValueError(e)

    def get_firewall(self, firewall_id: str) -> RIMEFirewall:
        """Get a firewall if it exists.

        Query the backend for a `RIMEFirewall` which can be used to perform Firewall
        operations. If the FW you are trying to fetch does not exist,
        this will error.

        Args:
            firewall_id: ID of the FW instance to fetch.

        Returns:
            a ``RIMEFirewall`` Object

        Raises:
            ValueError
                If the FW Instance does not exist.

        Example:

        .. code-block:: python

            # Get FW foo if it exists.
            firewall = rime_client.get_firewall("foo")
        """
        req = ListFirewallsRequest(firewall_ids=[firewall_id])
        try:
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ListFirewallsResponse = firewall_tester.ListFirewalls(req)
                return RIMEFirewall(self._backend, res.firewalls[0].id)
        except grpc.RpcError as e:
            raise ValueError(e)

    def get_firewall_for_project(self, project_id: str) -> RIMEFirewall:
        """Get the active fw for a project if it exists.

        Query the backend for an active `RIMEFirewall` in a specified project which
        can be used to perform Firewall operations. If there is no active
        Firewall for the project, this call will error.

        Args:
            project_id: ID of the project which contains a Firewall.

        Returns:
            A ``RIMEFirewall`` object.

        Raises:
            ValueError
                If the Firewall does not exist.

        Example:

        .. code-block:: python

            # Get FW in foo-project if it exists.
            firewall = rime_client.get_firewall_for_project("foo-project")
        """
        src_type = FirewallConvIDType.FIREWALL_CONV_ID_TYPE_PROJECT_ID
        dst_type = FirewallConvIDType.FIREWALL_CONV_ID_TYPE_FIREWALL_ID
        req = ConvertIDsRequest(
            src_type=src_type, dst_type=dst_type, src_ids=[project_id]
        )
        try:
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ConvertIDsResponse = firewall_tester.ConvertIDs(req)
                mapping = res.src_dst_id_mapping
                return RIMEFirewall(self._backend, mapping[project_id])
        except grpc.RpcError as e:
            raise ValueError(e)

    def start_firewall_from_reference(
        self,
        test_run_config: dict,
        disable_firewall_events: bool = True,
        project_id: Optional[str] = None,
        custom_image: Optional[CustomImage] = None,
        rime_managed_image: Optional[str] = None,
        ram_request_megabytes: Optional[int] = None,
        cpu_request_millicores: Optional[int] = None,
        data_type: str = "tabular",
    ) -> RIMEStressTestJob:
        """Start a RIME Firewall from reference on the backend's\
        ModelTesting service.

        This allows you to start an AI Firewall job on the RIME backend. This
        will run a stress test, create a firewall, and then run firewall
        tests on your dataset.

        Args:
            test_run_config: dict
                Configuration for the test to be run, which specifies paths to
                the model and datasets to used for the test.
            project_id: Optional[str]
                Identifier for the project where the resulting test run will be stored.
                If not specified, the results will be stored in the default project.
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
            data_type: str
                Type of data this firewall test is to be run on. Should be one of
                `tabular`, `nlp`, `images`. Defaults to `tabular`.

        Returns:
            A ``RIMEStressTestJob`` providing information about the model stress test
            job.

        Raises:
            ValueError
                If the request to the ModelTest service failed.

        Example:

        .. code-block:: python

            # This example will likely not work for you because it requires
            # permissions to a specific S3 bucket.
            # This demonstrates how you might specify such a configuration.
            config_from_reference = {
            "run_name": "Five Day Fraud Detection",
            "data_info": {
                "label_col": "is_fraud",
                "pred_col": "is_fraud_preds",
                "ref_path": "s3://rime-datasets/fraud_continuous_testing/ref.csv",
                "eval_path": "s3://rime-datasets/fraud_continuous_testing/
                              eval_2021_04_01_to_2021_04_06.csv"
            },
            "monitoring_info": {
                "timestamp_col": "timestamp",
                "bin_size": "day"
            },
            }
            # Run the job using the specified config and the default Docker image in
            # the RIME backend.vStore the results under project ID ``foo``
            # Use the RIME Managed Image ``tensorflow115``.
            # This assumes you have already created the Managed Image and waited for
            # it to be ready.
            job = rime_client.start_firewall_from_reference(
                test_run_config=config_from_reference,
                project_id="foo",
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

        if project_id and not self._project_exists(project_id):
            raise ValueError("Project id {} does not exist".format(project_id))
        proto_data_type = get_data_type_enum(data_type)
        req = StartFirewallFromReferenceRequest(
            test_run_config=simplejson.dumps(test_run_config).encode(),
            disable_firewall_events=disable_firewall_events,
            data_type=proto_data_type,
        )
        if project_id:
            req.project_id = project_id
        if custom_image:
            req.custom_image_type.testing_image.CopyFrom(custom_image)
        if rime_managed_image:
            req.custom_image_type.managed_image.name = rime_managed_image
        if ram_request_megabytes:
            req.ram_request_megabytes = ram_request_megabytes
        if cpu_request_millicores:
            req.cpu_request_millicores = cpu_request_millicores
        try:
            RIMEClient._throttler.throttle(
                throttling_msg="Your request is throttled to limit # of model tests."
            )
            with self._backend.get_model_testing_stub() as model_tester:
                job: JobMetadata = model_tester.StartFirewallFromReference(
                    request=req
                ).job
                return RIMEStressTestJob(self._backend, job.id)
        except grpc.RpcError as e:
            # TODO(blaine): differentiate on different error types.
            raise ValueError(e)

    def upload_dataset_file(self, file_path: Union[Path, str]) -> str:
        """Upload a dataset file to make it accessible to RIME's backend.

        The uploaded file is stored with RIME's backend in a blob store
        using its file name.

        Args:
            file_path: Union[Path, str]
                Path to the file to be uploaded to RIME's blob store.

        Returns:
            A reference to the uploaded file's location in the blob store. This
            reference can be used to refer to that object when writing RIME configs.
            Please store this reference for future access to the file.

        Raises:
            FileNotFoundError:
                If the path ``file_path`` does not exist.
            IOError:
                If ``file_path`` is not a file.
            ValueError:
                If there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
                In the scenario the file fails to upload, the incomplete file will
                NOT automatically be deleted.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with self._backend.get_file_upload_stub() as file_uploader:
            fum = FileUploadModule(file_uploader)
            return fum.upload_dataset_file(file_path)

    def upload_model_directory(
        self, dir_path: Union[Path, str], upload_hidden: bool = False
    ) -> str:
        """Upload a model directory to make it accessible to RIME's backend.

        The uploaded directory is stored within RIME's backend in a blob store.
        All files contained within ``dir_path`` and its subdirectories are uploaded
        according to their relative paths within ``dir_path``. However, if
        upload_hidden is False, all hidden files and subdirectories beginning with
        a '.' are not uploaded.

        Args:
            dir_path: Union[Path, str]
                Path to the directory to be uploaded to RIME's blob store.
            upload_hidden: bool = False
                Whether or not to upload hidden files or subdirectories
                (ie. those beginning with a '.').

        Returns:
            A reference to the uploaded directory's location in the blob store. This
            reference can be used to refer to that object when writing RIME configs.
            Please store this reference for future access to the directory.

        Raises:
            FileNotFoundError:
                If the directory ``dir_path`` does not exist.
            IOError:
                If ``dir_path`` is not a directory or contains no files.
            ValueError:
                If there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``dir_path`` to RIME's blob store.
                In the scenario the directory fails to upload, files will NOT
                automatically be deleted.
        """
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
        with self._backend.get_file_upload_stub() as file_uploader:
            fum = FileUploadModule(file_uploader)
            return fum.upload_model_directory(dir_path, upload_hidden=upload_hidden)
