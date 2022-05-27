import os
from ..task_args import get_cmd_arg

# Checks if a service is running on Edge
def running_on_edge():
    if "running_on_edge" in os.environ:
        if os.environ.get('running_on_edge')=="True":
            return True
    else:
        return False

def get_group_id():
    return get_cmd_arg("spring.cloud.stream.bindings.input.group")
