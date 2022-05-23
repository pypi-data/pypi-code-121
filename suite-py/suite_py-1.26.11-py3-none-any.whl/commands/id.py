# -*- coding: utf-8 -*-
import re

from pptree import Node, print_tree

from suite_py.lib import logger
from suite_py.lib.handler.aws_handler import Aws


class ID:
    def __init__(self, project, config, env):
        self._project = project
        self._env = env
        self._aws = Aws(config)

    def run(self):

        clusters_names = self._aws.get_ecs_clusters(self._env)
        n_services = Node("services")

        projects = {"prima": ["web", "consumer-api"], "ab_normal": ["abnormal"]}
        project_names = projects.get(self._project, [self._project])

        for cluster_name in clusters_names:

            services = []
            all_services = self._aws.get_ecs_services(cluster_name)

            for service in all_services:
                if service["status"] == "ACTIVE":
                    for prj in project_names:
                        if prj in service["serviceName"]:
                            services.append(service["serviceName"])

            for service in services:
                container_instances = []
                container_instances = (
                    self._aws.get_container_instances_arn_from_service(
                        cluster_name, service
                    )
                )
                if container_instances:
                    ids = self._aws.get_ids_from_container_instances(
                        cluster_name, container_instances
                    )

                    m = re.search(f"ecs-task-.*-{self._env}-ECSService(.*)-.*", service)
                    if m:
                        n_service = Node(m.group(1), n_services)
                        for _id in ids:
                            Node(_id, n_service)

        if n_services.children:
            print_tree(n_services, horizontal=True)
        else:
            logger.info(
                f"No active tasks for {self._project} in environment {self._env}"
            )
        logger.info("Done!")
