import shutil
import tempfile
from io import BytesIO
from pathlib import Path

from sym.shared.cli.decorators import require_bins, run_subprocess

from sym.flow.cli.helpers.global_options import GlobalOptions

from .boto import path_for_uploading, put_public_fileobj


@require_bins("terraform")
@run_subprocess
def terraform_output(directory: str):
    yield ("terraform", f"-chdir={directory}", "output", "-json")


def do_upload_terraform_output(dir: str, options: GlobalOptions) -> str:
    directory = Path(dir).resolve()
    output = terraform_output(
        directory,
        run_subprocess_options_=options,
        capture_output_=True,
    )
    txid, object_path = path_for_uploading(directory / "output", "json")
    put_public_fileobj(BytesIO(output[0].encode()), object_path)
    return txid


def do_upload_directory(dir: str) -> str:
    directory = Path(dir).resolve()
    txid, object_path = path_for_uploading(directory, "zip")
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir) / txid
        shutil.make_archive(str(path), format="zip", root_dir=str(directory))
        put_public_fileobj(path.with_suffix(".zip").open("rb"), object_path)
        return txid


def do_upload_file(file: str) -> str:
    path = Path(file).resolve()
    txid, object_path = path_for_uploading(path, path.suffix)
    put_public_fileobj(path.open("rb"), object_path)
    return txid
