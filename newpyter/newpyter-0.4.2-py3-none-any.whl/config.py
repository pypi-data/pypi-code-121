from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Tuple, Any

import toml

from newpyter.storage import AbstractStorage, Encryptor, SSHStorage, S3Storage, LocalStorage, MemoryMockStorage


class NewpyterConfigError(RuntimeError):
    pass


def _get_storage_parameters(notebook_filename: Path, storage_url: str = None) -> Tuple[str, str, Dict[str, Any]]:
    """
    Parses settings and finds any additional configuration parameters for the storage
    If storage url is known, will return parameters for it, otherwise will
    """
    nb_path = Path(notebook_filename)
    local_cache_dir = None
    # local is always available
    storages = {'local': {}}

    found_config_files = []
    possible_config_paths = [p.joinpath('.newpyter_config.toml') for p in [*nb_path.parents, Path.home()]]
    for config_path in possible_config_paths:
        if config_path.exists():
            found_config_files.append(config_path)
            with config_path.open() as f:
                try:
                    config = toml.load(f).get('newpyter', {})
                except BaseException as e:
                    raise NewpyterConfigError(f'Error loading config {config_path}: {e}')

                if storage_url is None:
                    storage_url = config.get('default_storage', None)
                if local_cache_dir is None:
                    local_cache_dir = config.get('local_cache_dir', None)
                # already known storages have precedence
                storages = {**config.get('storages', {}), **storages}

        if storage_url is not None and storage_url in storages and local_cache_dir is not None:
            # no need to traverse further, we already ide
            storage_settings = storages[storage_url]
            return storage_url, local_cache_dir, storage_settings

    if storage_url is not None and local_cache_dir is not None:
        # storage is set, but no additional parameters were found
        return storage_url, local_cache_dir, {}

    def format_paths_absolute(paths: List[Path]) -> str:
        result = ''
        for p in paths:
            result += f'  {p.absolute()}\n'
        return result

    message = f"""
Newpyter could not locate any storage. Following shouldn't be None: 
default_storage = {storage_url};
local_cache_dir = {local_cache_dir};

Make sure you have properly setup .newpyter_config.toml

Scanned following locations:
{format_paths_absolute(possible_config_paths)} 

Found following locations:
{format_paths_absolute(found_config_files)}

Parsed settings: 

default storage: {storage_url}
found storages: 
{list(storages)}
"""

    raise NewpyterConfigError(message)


class HashableDict:
    def __init__(self, d: Dict):
        self.internals = frozenset(d.items())

    def __hash__(self):
        return hash(self.internals)

    def to_dict(self):
        return dict(list(self.internals))


@lru_cache(typed=True)
def _get_storage(url: str, local_cache_dir: str, other_params: HashableDict) -> AbstractStorage:
    """
    Storage for parameters, intentionally cached to keep the same storage object
    if parameters were not updated
    """
    other_params = other_params.to_dict()
    password = other_params.pop('password', None)
    encryptor = Encryptor(password=password)
    local_cache_dir = Path(local_cache_dir).expanduser()
    if url.startswith('ssh://'):
        return SSHStorage(url, encryptor=encryptor, local_cache=local_cache_dir, **other_params)
    if url.startswith('s3://'):
        return S3Storage(url, encryptor=encryptor, local_cache=local_cache_dir, **other_params)
    if url == 'local':
        return LocalStorage(encryptor=encryptor, local_cache=local_cache_dir, **other_params)
    if url == ':MemoryMockStorage:':
        return MemoryMockStorage()
    raise NewpyterConfigError(f"Did not recognize URL for storage manager: {url}")


def get_storage_for_notebook(notebook_filename: Path, storage_url: str = None) -> AbstractStorage:
    """
    :param notebook_filename:
        path to notebook on FS.
        It is important as config files are search for in parent folders
    :param storage_url:
        if storage URL is known, configs are parsed for additional parameters.
        otherwise, URL is found by looking for default storage and corresponding parameters
    """
    url, local_cache_dir, other_params = _get_storage_parameters(notebook_filename, storage_url=storage_url)
    return _get_storage(url, local_cache_dir=local_cache_dir, other_params=HashableDict(other_params))
