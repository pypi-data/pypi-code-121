import pytest

from utf_queue_client.scripts.ubai_upload_cli import cli
from otel_extensions import inject_context_to_env, instrumented
import os
import subprocess
import sys


@pytest.fixture
def metadata():
    yield [
        ("app_name", "ubai_unit_test"),
        ("branch", "master"),
        ("stack", "ble"),
        ("build_number", "b140"),
        ("target", "brd4180b"),
    ]


@instrumented
def test_ubai_upload_cli(request, metadata):
    file = os.path.join(os.path.dirname(__file__), "test.hex")

    username = os.environ["UTF_QUEUE_USERNAME"]
    password = os.environ["UTF_QUEUE_PASSWORD"]
    client_id = request.node.name

    @inject_context_to_env
    def call_cli():
        cli(file, metadata, username, password, client_id)

    call_cli()


@pytest.mark.parametrize("use_queue", [True, False, None])
@instrumented
def test_ubai_upload_cli_script(request, metadata, use_queue):
    file = os.path.join(os.path.dirname(__file__), "test.hex")
    base_dir = os.path.dirname(os.path.dirname(__file__))

    client_id = request.node.name
    args = ["--file-path", file, "--client-id", client_id]
    for k, v in metadata:
        args += ["--metadata", k, v]
    if use_queue is not None:
        args += ["--queue" if use_queue else "--no-queue"]

    @inject_context_to_env
    def call_cli_script():
        assert "TRACEPARENT" in os.environ
        process = subprocess.Popen(
            [
                sys.executable,
                os.path.join(
                    base_dir, "utf_queue_client", "scripts", "ubai_upload_cli.py"
                ),
            ]
            + args,
        )
        process.communicate()
        assert process.poll() == 0

    call_cli_script()
