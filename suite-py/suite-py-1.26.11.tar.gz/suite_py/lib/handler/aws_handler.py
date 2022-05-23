# -*- encoding: utf-8 -*-
import os
import sys
import time

import boto3
from halo import Halo

from suite_py.lib import logger


class Aws:
    def __init__(self, config):
        self._profile = ""
        if "profile" in config.aws:
            self._profile = config.aws["profile"]
        if os.getenv("AWS_PROFILE", None):
            self._profile = os.getenv("AWS_PROFILE", None)

        if not self._profile:
            logger.warning(
                "Please update your config file:\n'aws:\n    profile: <aws profile name>' "
            )
            logger.warning("Or set 'AWS_PROFILE=<aws profile name>'")
            sys.exit(-1)

        self._session = boto3.session.Session(profile_name=self._profile)
        self._cloudformation = self._session.client(
            "cloudformation", region_name="eu-west-1"
        )
        self._cloudfront = self._session.client("cloudfront", region_name="eu-west-1")
        self._ecs = self._session.client("ecs", region_name="eu-west-1")
        self._ec2 = self._session.client("ec2", region_name="eu-west-1")

    def update_stack(self, stack_name, version):
        params = self.update_template_params(stack_name, version)
        if params:
            logger.info(f"Updating cloudformation template {stack_name}")
            self._cloudformation.update_stack(
                StackName=stack_name,
                TemplateBody=self.get_template_from_stack_name(stack_name),
                Parameters=params,
                RoleARN="arn:aws:iam::001575623345:role/rollback-service-role-clo-CloudformationRollbackRo-MTC7E4N9PXOK",
            )
        else:
            logger.error(f"No parameter found on the stack {stack_name}")
            sys.exit(-1)

    def update_template_params(self, stack_name, version):
        new_parameter = []
        ReleaseVersionFound = False
        current_parameters = self.get_parameters_from_stack_name(stack_name)

        for param in current_parameters:
            if param["ParameterKey"] == "ReleaseVersion":
                new_parameter.append(
                    {"ParameterKey": param["ParameterKey"], "ParameterValue": version}
                )
                ReleaseVersionFound = True
            else:
                new_parameter.append(
                    {"ParameterKey": param["ParameterKey"], "UsePreviousValue": True}
                )

        if ReleaseVersionFound:
            return new_parameter
        return None

    def get_parameters_from_stack_name(self, stack_name):
        return self._cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0][
            "Parameters"
        ]

    def get_template_from_stack_name(self, stack_name):
        return self._cloudformation.get_template(StackName=stack_name)["TemplateBody"]

    def get_stacks_name(self, repo):
        stacks_name = []
        base_stacks_name = [
            f"ecs-task-{repo}-production",
            f"ecs-task-{repo}-vpc-production",
            f"ecs-job-{repo}-production",
            f"batch-job-{repo}-production",
        ]

        for stack_name in base_stacks_name:
            if self.stack_exists(stack_name):
                stacks_name.append(stack_name)

        return stacks_name

    def stack_exists(self, stack_name):
        try:
            self._cloudformation.describe_stacks(StackName=stack_name)
            return True
        except Exception:
            return False

    def get_stack_status(self, stack_name):
        return self._cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0][
            "StackStatus"
        ]

    def get_artifacts_from_s3(self, bucket_name, prefix):
        # pylint has issues with boto3...
        # pylint: disable=no-member
        with Halo(text="Loading releases...", spinner="dots", color="magenta"):
            s3 = boto3.resource("s3")
            bucket_artifacts = s3.Bucket(bucket_name)
            artifacts = []

            for bucket_object in bucket_artifacts.objects.filter(Prefix=prefix):
                artifacts.append(bucket_object.key.replace(prefix, ""))

        return artifacts

    def is_cloudfront_distribution(self, repo):
        with Halo(text="Loading releases...", spinner="dots", color="magenta"):
            distributions = self._cloudfront.list_distributions()["DistributionList"][
                "Items"
            ]
            for distribution in distributions:
                if (
                    f"prima-prod-{repo}.s3.amazonaws.com"
                    == distribution["Origins"]["Items"][0]["DomainName"]
                ):
                    return True
        return False

    def get_tag_from_s3_artifact(self, bucket_name, prefix, artifact):
        s3 = boto3.client("s3")

        return s3.get_object_tagging(Bucket=bucket_name, Key=f"{prefix}{artifact}")[
            "TagSet"
        ]

    def stack_update_completed(self, stack_name):
        with Halo(text="Rollback in progress...", spinner="dots", color="magenta"):
            for _ in range(0, 60):
                stack_status = self.get_stack_status(stack_name)
                if stack_status == "UPDATE_COMPLETE":
                    return True
                if "FAILED" in stack_status or "ROLLBACK" in stack_status:
                    break
                time.sleep(10)
        return False

    def update_stacks(self, stacks_name, version):
        for stack_name in stacks_name:
            self.update_stack(stack_name, version)

        for stack_name in stacks_name:
            if not self.stack_update_completed(stack_name):
                logger.error(
                    f"Error updating CloudFormation stack {stack_name}. Contact the DevOps team."
                )
                sys.exit(-1)

    def get_ecs_services(self, cluster_name):
        with Halo(text="Loading services...", spinner="dots", color="magenta"):
            done = False
            services = []
            options = {"cluster": cluster_name, "maxResults": 10}
            nextToken = None

            while not done:
                if nextToken:
                    options["nextToken"] = nextToken
                list_services = self._ecs.list_services(**options)

                if (
                    "nextToken" in list_services.keys()
                    and list_services["nextToken"] != "null"
                ):
                    nextToken = list_services["nextToken"]
                else:
                    done = True

                if not list_services["serviceArns"]:
                    return []

                list_services_description = self._ecs.describe_services(
                    cluster=cluster_name, services=list_services["serviceArns"]
                )

                services = services + list_services_description["services"]

            return services

    def get_ids_from_container_instances(self, cluster_name, container_instances):
        ids = []

        container_instances_description = self._ecs.describe_container_instances(
            cluster=cluster_name, containerInstances=container_instances
        )

        for c in container_instances_description["containerInstances"]:
            ids.append(c["ec2InstanceId"])

        return ids

    def get_ips_from_container_instances(self, cluster_name, container_instances):
        instances_id = []
        ips = []

        container_instances_description = self._ecs.describe_container_instances(
            cluster=cluster_name, containerInstances=container_instances
        )

        for c in container_instances_description["containerInstances"]:
            instances_id.append(c["ec2InstanceId"])

        instances_description = self._ec2.describe_instances(InstanceIds=instances_id)

        for reservation in instances_description["Reservations"]:
            for instance in reservation["Instances"]:
                ips.append(instance["PrivateIpAddress"])

        return ips

    def get_container_instances_arn_from_service(self, cluster_name, service_name):
        container_instances_arn = []
        tasks = self._ecs.list_tasks(
            cluster=cluster_name,
            desiredStatus="RUNNING",
            serviceName=service_name,
        )["taskArns"]

        if tasks:
            tasks_descriptions = self._ecs.describe_tasks(
                cluster=cluster_name, tasks=tasks
            )

            for task in tasks_descriptions["tasks"]:
                container_instances_arn.append(task["containerInstanceArn"])

        return container_instances_arn

    def get_ecs_clusters(self, env):
        clusters = []
        list_clusters = self._ecs.list_clusters()
        for c in list_clusters["clusterArns"]:
            if f"-{env}-" in c and "-ci-" not in c:
                clusters.append(c)
        return clusters
