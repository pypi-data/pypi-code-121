import shutil
import tempfile
from pathlib import Path
import requests_mock

from rebotics_sdk.providers import FVMProvider

RESOURCES_FOLDER = Path(__file__).parent / 'resources'

DATA_VIRTUAL = {
        'filename': 'qwerty.csv',
        'id': 1,
        'destination': {
            'url': 'http://minio:9005/demo-bucket',
            'fields': {
                'key': 'virtual_uploads/1/qwerty.csv',
                'AWSAccessKeyId': 'access_key',
                'policy': 'eyJleHBpcmF0aW9uIjogIjIwMjEtMTAtMDdUMDc6NDI6MDBaIiwgImNvbm'
                          'RpdGlvbnMiOiBbeyJidWNrZXQiOiAiZGVtby1idWNrZXQifSwgeyJrZXkiOi'
                          'AidmlydHVhbF91cGxvYWRzLzEvcXdlcnR5LmNzdiJ9XX0=',
                'signature': 'zF2lZqmQPeMwEod1+pMOHjObYVE='
            }
        }
    }
DATA_FINISH = {
    'id': 1,
    'file': 'http://minio:9005/demo-bucket/example_TEi7koV.jpg?'
            'AWSAccessKeyId=access_key&Signature=3J01a4yIbiVeUqCppBD4AKGkY%2FE%3D&Expires=1633598295',
    'file_key': 'example_TEi7koV.jpg'

}


def test_create_virtual_upload_success(runner, mocker):
    from unittest.mock import Mock
    process_role_mock = mocker.patch("rebotics_sdk.cli.utils.process_role")
    process_role_mock.return_value = None
    provider_mock = Mock(spec=FVMProvider)
    mocker.patch('rebotics_sdk.cli.utils.ReboticsCLIContext.provider', new=provider_mock)
    provider_mock.create_virtual_upload.side_effect = lambda *args: DATA_VIRTUAL
    provider_mock.finish.side_effect = lambda *args: DATA_FINISH
    from rebotics_sdk.cli.fvm import api
    with requests_mock.Mocker() as m:
        m.post('http://minio:9005/demo-bucket', status_code=200)
        with tempfile.TemporaryDirectory() as base_dir:
            base_dir_path = Path(base_dir)
            filename = base_dir_path.absolute() / 'qwerty.csv'
            shutil.copy(RESOURCES_FOLDER / 'qwerty.csv', filename)

            result = runner.invoke(
                api,
                [
                    'file',
                    '-f', str(filename),
                ]
            )
        provider_mock.create_virtual_upload.assert_called_once_with(
            str(filename)
        )
    assert result.exit_code == 0
    assert not result.exception
    assert "Successfully finished uploading" in result.output.strip()


def test_create_virtual_upload_missing_option(runner, mocker):
    from unittest.mock import Mock
    process_role_mock = mocker.patch("rebotics_sdk.cli.utils.process_role")
    process_role_mock.return_value = None
    provider_mock = Mock(spec=FVMProvider)
    mocker.patch('rebotics_sdk.cli.utils.ReboticsCLIContext.provider', new=provider_mock)
    provider_mock.create_virtual_upload.side_effect = lambda *args: DATA_VIRTUAL
    provider_mock.finish.side_effect = lambda *args: DATA_FINISH
    from rebotics_sdk.cli.fvm import api
    result = runner.invoke(
        api,
        [
            'file'
        ]
    )
    assert result.exit_code == 2
    assert result.exception
    assert "Missing option" in result.output


def test_fv_api_create_virtual_upload_no_file(runner, mocker):
    from unittest.mock import Mock
    process_role_mock = mocker.patch("rebotics_sdk.cli.utils.process_role")
    process_role_mock.return_value = None
    provider_mock = Mock(spec=FVMProvider)
    mocker.patch('rebotics_sdk.cli.utils.ReboticsCLIContext.provider', new=provider_mock)
    provider_mock.create_virtual_upload.side_effect = lambda *args: DATA_VIRTUAL
    provider_mock.finish.side_effect = lambda *args: DATA_FINISH
    from rebotics_sdk.cli.fvm import api
    result = runner.invoke(
        api,
        [
            'file',
            '-f', 'lol',
        ]
    )
    assert result.exit_code == 1
    assert result.exception
