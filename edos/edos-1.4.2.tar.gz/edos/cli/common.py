from typing import Iterable

from click.shell_completion import CompletionItem

from edos.cache import cache
from edos.services.database_service import DatabaseService


def create_completion_from_names(names: Iterable[str], incomplete: str):
    return [
        CompletionItem(name)
        for name in names
        if name.lower().startswith(incomplete.lower())
    ]


def cluster_id_completion(ctx, args, incomplete):
    @cache.memoize(expire=10)
    def get_names():
        return [*DatabaseService().get_clusters()]

    return create_completion_from_names(get_names(), incomplete)


def get_new_secret_name(old_name: str):
    """
    secret names are typically in this format:
        <secret>-<version> where version is a number
    this function will get a new secret with incremented version
    if version is not present, append it
    :param old_name: <secret>-<version>
    :return: <secret>-<version+1>
    """
    split_secret = old_name.rsplit("-", 1)
    if "-" not in old_name or not split_secret[1].isnumeric():
        return old_name + "-1"
    new_secret_version = int(split_secret[1]) + 1
    return f"{split_secret[0]}-{new_secret_version}"
