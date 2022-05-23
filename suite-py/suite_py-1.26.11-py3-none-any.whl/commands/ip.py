# -*- coding: utf-8 -*-
import os
import re

from pptree import Node, print_tree

from suite_py.lib import logger
from suite_py.lib.handler.aws_handler import Aws


class IP:
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
                    ips = self._aws.get_ips_from_container_instances(
                        cluster_name, container_instances
                    )

                    m = re.search(f"ecs-task-.*-{self._env}-ECSService(.*)-.*", service)
                    if m:
                        n_service = Node(m.group(1), n_services)
                        for ip in ips:
                            Node(ip, n_service)

        if self._env == "staging" and os.path.isfile("./deploy/values/staging.yml"):
            logger.info(
                "This project has been migrated on k8s, command is no longer available."
            )
            logger.info(
                "Guide on how to setup k8s: https://app.tettra.co/teams/prima-assicurazioni/pages/effettuare-operazioni-su-k8s"
            )
        elif n_services.children:
            print_tree(n_services, horizontal=True)
        else:
            logger.info(
                f"No active tasks for {self._project} in environment {self._env}"
            )
        logger.info("Done!")
