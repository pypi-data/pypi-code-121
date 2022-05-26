from unittest.mock import patch
from uuid import UUID

from sym.shared.cli.tests.helpers.capture import CaptureCommand

from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.helpers.sandbox import Sandbox

JSON = '{"foo": "bar"}'
UUID_VAL = "6fac5fa7-898f-4404-9585-a567104a1a71"


@patch("sym.flow.cli.helpers.boto.uuid4")
@patch("sym.flow.cli.helpers.debug.put_public_fileobj")
def test_upload_terraform_output(
    put_public_fileobj_mock,
    uuid4_mock,
    click_setup,
    capture_command: CaptureCommand,
    sandbox: Sandbox,
):
    uuid4_mock.return_value = UUID(UUID_VAL)

    with click_setup() as runner:
        with capture_command():
            sandbox.create_binary("bin/terraform")
            dir = sandbox.create_dir("foo")
            capture_command.register_output("terraform", JSON)

            result = runner.invoke(
                click_command,
                ["debug", "upload-terraform-output", str(dir)],
            )
            assert result.exit_code == 0
            assert UUID_VAL in result.output

            put_public_fileobj_mock.assert_called_once()
            assert put_public_fileobj_mock.call_args.args[0].getvalue() == JSON.encode()
            assert UUID_VAL in put_public_fileobj_mock.call_args.args[1]
