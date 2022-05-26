"""Main module."""

from pathlib import Path
from typing import Optional

from pulumi import ComponentResource, ResourceOptions
from pulumi.asset import FileArchive
from pulumi_gcp.cloudfunctions import Function, FunctionIamMember
from pulumi_gcp.compute import AwaitableGetImageResult, Disk, get_image
from pulumi_gcp.config import project, zone  # type: ignore
from pulumi_gcp.storage import Bucket, BucketObject


class PufferPanel(ComponentResource):
    """Pulumi ComponentResource for running PufferPanel - https://github.com/PufferPanel/PufferPanel.

    Attributes:
        code_bucket (Bucket): Bucket containing code used for cloud function
        code_bucket_object (BucketObject): Object containing code archive used for cloud function
        function (Function): Cloud function used to associate created server with a dns name.
        machine_disk (Disk): Disk used for created machines.
        machine_image (AwaitableGetImageResult): Base image used for created disk.

    """

    AVAILABLE_MEMORY_MB = 128
    FUNCTION_RUNTIME = "python39"
    IMAGE_FAMILY = "debian-11"
    IMAGE_PROJECT = "debian-cloud"
    INGRESS_SETTINGS = "ALLOW_ALL"

    def __init__(
        self,
        name: str,
        dns_name: str,
        dns_zone: str,
        disk_size: int = 30,
        disk_type: str = "pd-standard",
        machine_type: str = "e2-medium",
        server_name: str = "pufferpanel-server",
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """Create infra for the open source game server management tool PufferPanel.

        Args:
            dns_name (str): The domain name to bind to.
            dns_zone (str): The zone the dns_name falls into.
            disk_size (int): The disk size to create for the preemptible compute instance.
            disk_type (str): The disk type to create for the preemptible compute instance.
            machine_type (str): The machine type to use for the preemptible compute instance.
            name (str): The unique name for this resource.
            opts (Optional[ResourceOptions]): Optional pulumi resource options for
                this created resource.
            server_name (str): The name to use for the preemptible compute instance.
        """
        super().__init__(t="PufferPanel", name=name, opts=opts)
        self._code_bucket = self.__create_code_bucket()
        self._code_bucket_object = self.__create_code_bucket_object(bucket=self._code_bucket)
        self._dns_name = dns_name
        self._dns_zone = dns_zone
        self._disk_size = disk_size
        self._disk_type = disk_type
        self._machine_image = self.__get_image(
            image_family=self.IMAGE_FAMILY, image_project=self.IMAGE_PROJECT
        )
        self._machine_disk = self.__create_disk(
            disk_size=self._disk_size, disk_type=self._disk_type, image=self._machine_image
        )
        self._machine_type = machine_type
        self._server_name = server_name

        self._function = self.__create_function(
            available_memory_mb=self.AVAILABLE_MEMORY_MB,
            bucket=self._code_bucket,
            bucket_object=self._code_bucket_object,
            disk=self._machine_disk,
            dns_name=self._dns_name,
            dns_zone=self._dns_zone,
            function_runtime=self.FUNCTION_RUNTIME,
            ingress_settings=self.INGRESS_SETTINGS,
            machine_type=self._machine_type,
            server_name=self._server_name,
        )
        self._anonymous_function_access = self.__give_anonymous_function_access(self.function)

    @property
    def code_bucket(self) -> Bucket:
        """Return bucket containing code used for cloud function."""
        return self._code_bucket

    @property
    def code_bucket_object(self) -> BucketObject:
        """Return object containing code archive used for cloud function."""
        return self._code_bucket_object

    @property
    def function(self) -> Function:
        """Return cloud function used to associate created server with a dns name."""
        return self._function

    @property
    def machine_disk(self) -> Disk:
        """Return disk used for created machines."""
        return self._machine_disk

    @property
    def machine_image(self) -> AwaitableGetImageResult:
        """Return base image used for created disk."""
        return self._machine_image

    def __get_image(self, image_family: str, image_project: str) -> AwaitableGetImageResult:
        return get_image(family=image_family, project=image_project)

    def __create_disk(
        self, disk_size: int, disk_type: str, image: AwaitableGetImageResult
    ) -> Disk:
        return Disk(
            resource_name="pufferpanel-disk",
            image=image.name,
            size=disk_size,
            type=disk_type,
        )

    def __create_code_bucket(self) -> Bucket:
        return Bucket("pufferpanel-bucket", force_destroy=True, location="US")

    def __create_code_bucket_object(self, bucket: Bucket) -> BucketObject:
        return BucketObject(
            "pufferpanel-bucket-object",
            bucket=bucket.name,
            source=FileArchive(str(Path(__file__).parent.resolve().joinpath("cloud_function"))),
        )

    def __create_function(
        self,
        available_memory_mb: int,
        bucket: Bucket,
        bucket_object: BucketObject,
        disk: Disk,
        dns_name: str,
        dns_zone: str,
        function_runtime: str,
        ingress_settings: str,
        machine_type: str,
        server_name: str,
    ) -> Function:
        return Function(
            "pufferpanel-toggler",
            available_memory_mb=available_memory_mb,
            entry_point="http",
            environment_variables={
                "DISK_ID": disk.id,
                "DNS_NAME": dns_name,
                "DNS_ZONE": dns_zone,
                "GCP_PROJECT": project,
                "MACHINE_TYPE": machine_type,
                "SERVER_NAME": server_name,
                "ZONE": zone,
            },
            ingress_settings=ingress_settings,
            max_instances=1,
            name="toggle-pufferpanel-server",
            runtime=function_runtime,
            source_archive_bucket=bucket.name,
            source_archive_object=bucket_object.name,
            trigger_http=True,
        )

    def __give_anonymous_function_access(self, function: Function) -> FunctionIamMember:
        return FunctionIamMember(
            "pufferpanel-server-toggler-public",
            cloud_function=function.name,
            role="roles/cloudfunctions.invoker",
            member="allUsers",
        )
