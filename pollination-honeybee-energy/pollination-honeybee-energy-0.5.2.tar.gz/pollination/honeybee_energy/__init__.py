"""Honeybee Energy plugin for Pollination."""
from pollination_dsl.common import get_docker_image_from_dependency

# set the version for docker image dynamically based on honeybee-radiance version
# in dependencies
image_id = get_docker_image_from_dependency(
    __package__, 'honeybee-energy', 'ladybugtools'
)

__pollination__ = {
    'config': {
        'docker': {
            'image': image_id,
            'workdir': '/home/ladybugbot/run'
        }
    }
}
