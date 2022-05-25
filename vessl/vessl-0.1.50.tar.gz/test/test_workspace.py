import pytest
from mock import Mock, patch

import vessl
from test.conftest import USE_MOCK
from vessl.util.exception import InvalidWorkspaceError


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestWorkspace:
    def test_read_workspace(self):
        # Must create first
        pass

    def test_list_workspaces(self):
        vessl.list_workspaces()


def test_backup_workspace():
    # Test fail
    config_instance_mock = Mock()
    config_instance_mock.workspace = None
    config_mock = Mock(return_value=config_instance_mock)

    with patch.object(vessl.workspace, "VesslConfigLoader", config_mock):
        with pytest.raises(InvalidWorkspaceError):
            vessl.backup_workspace()

    # TODO: Add test success


def test_restore_workspace():
    # Test fail
    config_instance_mock = Mock()
    config_instance_mock.workspace = None
    config_mock = Mock(return_value=config_instance_mock)

    with patch.object(vessl.workspace, "VesslConfigLoader", config_mock):
        with pytest.raises(InvalidWorkspaceError):
            vessl.restore_workspace()

    # TODO: Add test success


# def test_connect_workspace_ssh():
#     workspace_id = 1234
#     private_key_path = "/path/to/key"
#
#     # Test fail
#     workspace_mock = Mock()
#     workspace_mock.status = "terminated"
#
#     read_workspace_ = patch.object(
#         vessl.workspace, "read_workspace", return_value=workspace_mock
#     )
#
#     with read_workspace_:
#         with pytest.raises(InvalidWorkspaceError):
#             vessl.connect_workspace_ssh(private_key_path)
#
#     # Test success
#     port = 1234
#     hostname = "tcp.hostname.com"
#
#     workspace_mock = Mock()
#     workspace_mock.status = "running"
#     workspace_mock.endpoints.ssh.endpoint = f"tcp://{hostname}:{port}"
#
#     read_workspace_ = patch.object(
#         vessl.workspace, "read_workspace", return_value=workspace_mock
#     )
#     system_ = patch("vessl.workspace.os.system")
#
#     with read_workspace_, system_:
#         vessl.connect_workspace_ssh(private_key_path)
#         vessl.workspace.os.system.assert_called_with(
#             f"ssh -p {port} -i {private_key_path} vessl@{hostname}"
#         )


# def test_update_vscode_remote_ssh():
#     # Setup
#     ssh_config_path = "test/ssh_config"
#     with open(ssh_config_path, "w+"):
#         pass
#
#     private_key_path = "/path/to/key"
#     name = "vessl_workspace"
#     created_dt = datetime.datetime.now()
#     port = 1234
#     hostname = "tcp.hostname.com"
#     host = f"{name}-{int(created_dt.timestamp())}"
#
#     workspace_mock = Mock()
#     workspace_mock.name = name
#     workspace_mock.created_dt = created_dt
#     workspace_mock.endpoints.ssh.endpoint = f"tcp://{hostname}:{port}"
#
#     list_workspaces_ = patch.object(
#         vessl.workspace, "list_workspaces", return_value=[workspace_mock]
#     )
#     paramiko_ = patch.object(vessl.workspace, "paramiko")
#     ssh_config_format_ = patch.object(
#         vessl.workspace, "SSH_CONFIG_PATH", ssh_config_path
#     )
#
#     with list_workspaces_, paramiko_, ssh_config_format_:
#         vessl.update_vscode_remote_ssh(private_key_path)
#
#     with open(ssh_config_path, "r") as f:
#         assert f.read() == SSH_CONFIG_FORMAT.format(
#             host=host,
#             hostname=hostname,
#             port=port,
#         ) + f'    IdentityFile {private_key_path}\n'
#
#     # Teardown
#     try:
#         os.remove(ssh_config_path)
#     except OSError:
#         pass
