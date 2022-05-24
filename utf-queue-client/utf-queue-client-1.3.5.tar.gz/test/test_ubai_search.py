from utf_queue_client.scripts.ubai_search_cli import cli
from otel_extensions import instrumented, inject_context_to_env
import os
import subprocess
import sys


@instrumented
def test_ubai_search_cli():
    metadata = [
        ("app_name", "ubai_unit_test"),
        ("branch", "master"),
        ("stack", "ble"),
        ("build_number", "b140"),
        ("target", "brd4180b"),
    ]

    @inject_context_to_env
    def call_cli():
        results = cli("test", ".hex", metadata)
        assert len(results) == 1

    call_cli()


@instrumented
def test_ubai_search_cli_script():
    metadata = [
        ("app_name", "ubai_unit_test"),
        ("branch", "master"),
        ("stack", "ble"),
        ("build_number", "b140"),
        ("target", "brd4180b"),
    ]

    args = ["--name", "test", "--extension", ".hex"]
    for k, v in metadata:
        args += ["--metadata", k, v]

    @inject_context_to_env
    def call_cli_script():
        assert "TRACEPARENT" in os.environ
        process = subprocess.Popen(
            [
                sys.executable,
                os.path.join("utf_queue_client", "scripts", "ubai_search_cli.py"),
            ]
            + args,
            stdout=subprocess.PIPE,
        )
        output, _ = process.communicate()
        assert process.poll() == 0
        assert output.decode().strip() == "15d8ebfd-4c14-4d95-b21c-a73a76f1f3a5"

    call_cli_script()
