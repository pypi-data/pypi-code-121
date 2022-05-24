import os
from functools import lru_cache

import yaml

from polidoro_cli import CLI


class Docker(CLI):
    @staticmethod
    @lru_cache
    def get_main_docker_compose_service():
        for name, info in Docker._gel_all_docker_compose_services().items():
            if 'build' in info:
                return name

    @staticmethod
    @lru_cache
    def _gel_all_docker_compose_services():
        for docker_compose_file in ['docker-compose.yml', 'docker-compose.yaml']:
            if os.path.exists(docker_compose_file):
                with open(docker_compose_file) as file:
                    return yaml.safe_load(file)['services']
        return {}

    @staticmethod
    def command_interceptor(command, args, kwargs):
        if 'service' in kwargs and kwargs['service'] not in Docker._gel_all_docker_compose_services():
            args.append(kwargs['service'])
            kwargs['service'] = Docker.get_main_docker_compose_service()
        return command, args, kwargs
