from typing import Optional, List


def datastore_currently_creating_datastore(
    name: str, version: str, cluster: str, all_clusters: Optional[List[str]] = None
) -> str:
    res = f"We are creating {name} datastore (version {version}) on cluster {cluster}"
    if all_clusters is not None:
        res += f" not on these clusters: {all_clusters}."
    else:
        res += "."
    res += " Please use `grid datastore` to check the status."
    return res


def datastore_uploaded_successfully(name: str, version: str, cluster: str) -> str:
    return (
        f"Completed uploading {name} datastore (version {version}) on "
        f"cluster {cluster}. Your datastore will be available for use shortly."
    )
