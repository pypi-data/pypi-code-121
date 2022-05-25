from io import BytesIO
from pathlib import Path

from benchling_api_client.v2.alpha.models.benchling_app_manifest import BenchlingAppManifest
import yaml


def manifest_to_bytes(manifest: BenchlingAppManifest, encoding: str = "utf-8") -> BytesIO:
    """Write a modeled Benchling App manifest to BytesIO of YAML."""
    manifest_dict = manifest.to_dict()
    yaml_format = yaml.safe_dump(manifest_dict, encoding=encoding, allow_unicode=True, sort_keys=False)
    return BytesIO(yaml_format)


def manifest_from_bytes(manifest: BytesIO) -> BenchlingAppManifest:
    """Read a modeled Benchling App manifest from BytesIO."""
    yaml_format = yaml.safe_load(manifest)
    return BenchlingAppManifest.from_dict(yaml_format)


def manifest_from_file(file_path: Path) -> BenchlingAppManifest:
    """Read a modeled Benchling App manifest from a file."""
    with open(file_path, "rb") as file:
        return manifest_from_bytes(BytesIO(file.read()))
