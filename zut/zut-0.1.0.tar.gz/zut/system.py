import os

_is_docker = None

def is_docker():
    global _is_docker
    
    if _is_docker is None:
        if os.path.exists('/.dockerenv'):
            _is_docker = True
            return _is_docker
        
        path = '/proc/self/cgroup'
        if os.path.isfile(path):
            with open(path) as f:
                for line in f:
                    if 'docker' in line:
                        _is_docker = True
                        return _is_docker
        
        _is_docker = False
        return _is_docker

    return _is_docker
