from typing import Optional, List, Set, Iterator, io, Tuple
from urllib.parse import urlparse

import click
from box import Box
from click._compat import get_text_stderr

from montecarlodata.common.common import render_dumped_json, read_files, generate_token
from montecarlodata.common.data import DcResourceProperties, AWSArn, AwsGlueAthenaResourceProperties
from montecarlodata.common.resources import CloudResourceService
from montecarlodata.errors import complain_and_abort, manage_errors


class PolicyDiscoveryService:
    ANY_RESOURCE_KEY = '*'

    # Rel template paths. Full path retrieved via pkgutil.
    CF_ROLE_REL_PATH = '../templates/aws_role.json'
    GLUE_POLICY_REL_PATH = '../templates/glue_policy.json'
    ATHENA_POLICY_REL_PATH = '../templates/athena_policy.json'

    def __init__(self, cloud_resource_service: Optional[CloudResourceService] = None, *args, **kwargs):
        self._abort_on_error = True  # Used in decorator
        self._cloud_resource_service = cloud_resource_service or CloudResourceService(*args, **kwargs)

    @manage_errors
    def generate_cf_role(self, policy_files: List[io], dc_id: Optional[str] = None) -> None:
        """
        Generate a CloudFormation template to create a MC compatible IAM role from one or more IAM policy.
        """
        click.echo('Generating CloudFormation template for creating a role resource.', err=True)
        if not len(policy_files) > 0:
            complain_and_abort('At least one policy is required.')

        collector_arn = AWSArn(self._cloud_resource_service.get_and_validate_active_collector(dc_id=dc_id).stackArn)

        click.echo(
            render_dumped_json(
                path=self.CF_ROLE_REL_PATH,
                collector_account_id=collector_arn.account,
                collector_external_id=generate_token(),
                resource_policies=read_files(policy_files)
            )
        )

    @manage_errors
    def generate_glue_policy(self, **kwargs) -> None:
        """
        Generate an IAM compatible policy for Glue from the specified database names or wildcard sequences.

        Bucket names are derived from the database names if not otherwise provided.
        """
        click.echo('Generating policy for Glue.', err=True)
        glue_properties = self._get_common_glue_athena_props(**kwargs)

        click.echo(
            render_dumped_json(
                path=self.GLUE_POLICY_REL_PATH,
                account_id=glue_properties.dc_resource_props.resources_client.get_caller_identity(),
                region=glue_properties.dc_resource_props.resources_region,
                database_names=glue_properties.database_names,
                data_buckets=glue_properties.bucket_names
            )
        )

    @manage_errors
    def generate_athena_policy(self, *, workgroup_name: str, **kwargs) -> None:
        """
        Generate an IAM compatible policy for Athena from the specified database names or wildcard sequences.

        Bucket names are derived from the database names if not otherwise provided. The results bucket is derived from the workgroup.
        """
        click.echo('Generating policy for Athena.', err=True)
        athena_properties = self._get_common_glue_athena_props(**kwargs)

        result_bucket, result_path = self._get_workgroup_results(
            workgroup_name=workgroup_name,
            dc_resource_props=athena_properties.dc_resource_props
        )

        click.echo(
            render_dumped_json(
                path=self.ATHENA_POLICY_REL_PATH,
                account_id=athena_properties.dc_resource_props.resources_client.get_caller_identity(),
                region=athena_properties.dc_resource_props.resources_region,
                database_names=athena_properties.database_names,
                data_buckets=athena_properties.bucket_names,
                result_bucket=result_bucket,
                result_path=result_path,
                workgroup_name=workgroup_name
            )
        )

    def _get_common_glue_athena_props(self, *,
                                      database_names: List[str],
                                      bucket_names: Optional[List[str]] = None,
                                      dc_id: Optional[str] = None, **kwargs) -> AwsGlueAthenaResourceProperties:
        """
        Get resources that are common to Glue and Athena.
        """
        database_names = self._handle_wildcards(database_names)
        bucket_names = self._handle_wildcards(bucket_names)

        dc_resource_props = self._cloud_resource_service.get_dc_resource_props(
            collector_props=self._cloud_resource_service.get_and_validate_active_collector(dc_id=dc_id),
            get_stack_outputs=False,
            get_stack_params=False,
            **kwargs
        )

        if not bucket_names:
            bucket_names = self._get_buckets(database_names=database_names, dc_resource_props=dc_resource_props)

        return AwsGlueAthenaResourceProperties(
            database_names=database_names,
            bucket_names=bucket_names,
            dc_resource_props=dc_resource_props
        )

    def _get_buckets(self, database_names: Set[str], dc_resource_props: DcResourceProperties) -> Set[str]:
        """
        Derive s3 locations (buckets) from provided databases.
        """
        if self.ANY_RESOURCE_KEY in database_names:
            return {self.ANY_RESOURCE_KEY}

        buckets = set()
        with click.progressbar(database_names, label='Looking up buckets details.', file=get_text_stderr()) as dbs:
            for database_name in dbs:
                page_token = None
                while True:
                    tables = dc_resource_props.resources_client.get_glue_tables(
                        database_name=database_name,
                        page_token=page_token
                    )
                    page_token = tables.next_token
                    buckets.update(self._get_table_locations(tables=tables.table_list))

                    if not page_token:
                        break
        return buckets

    def _handle_wildcards(self, sequence: List[str]) -> Set[str]:
        """
        Get unique records and prioritize any wildcards in the sequence.
        """
        sequence = set(sequence) if sequence else set()
        if self.ANY_RESOURCE_KEY in sequence:
            return {self.ANY_RESOURCE_KEY}
        return sequence

    @staticmethod
    def _get_workgroup_results(workgroup_name: str, dc_resource_props: DcResourceProperties) -> Tuple[str, str]:
        """
        Get workgroup result bucket and path.
        """
        with click.progressbar(length=1, label='Looking up workgroup details.', file=get_text_stderr()) as progress:
            workgroup_details = dc_resource_props.resources_client.get_athena_workgroup(workgroup=workgroup_name)

            url = urlparse(workgroup_details.configuration.result_configuration.output_location)
            progress.update(1)
            return url.netloc, url.path if url.path else '/'

    @staticmethod
    def _get_table_locations(tables: Box, valid_scheme_prefix: Optional[str] = 's3') -> Iterator[str]:
        """
        Get locations from s3 for any valid schemes.
        """
        for table in tables:
            url = urlparse(table.storage_descriptor.location)
            if url.scheme.lower().startswith(valid_scheme_prefix):
                yield url.netloc
